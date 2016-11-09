# coding: utf-8
import settings
from libraries.eweb import Macros
from libraries.PyAutoTestCase import *    # import test case template
from tests.energy_reports.Data import DataSetup    # import testing data
from libraries.eweb.DataObjects.WebGroup import WebGroupDBObj
from libraries.eweb.PageObjects.Header import HeaderPageObj
from libraries.eweb.PageObjects.AdminFrame import AdminFrameObj
from libraries.eweb.PageObjects.UnitsFrame import UnitsFrameObj
import os, time


class TC0101_Base_Units(TestCaseTemplate):
    def setUp(self):
        super(TC0101_Base_Units, self).setUp()
        self.Browser = settings.BROWSER
        self.Host = settings.HOST
        self.Username = settings.USERNAME
        self.Password = settings.PASSWORD
        Macros.LoadEnteliWEB(self.Host, self.Browser, self.Username, self.Password)

        # page object model under test
        self.baseUnitsFrame = UnitsFrameObj()
        
        self.elements = {
                          'Outdoor Temp'            : UnitsFrameObj.outdoorTemp,
                          'Electricity Consumption' : UnitsFrameObj.electricityConsumption,
                          'Electricity Demand'      : UnitsFrameObj.electricityDemand,
                          'Apparent Consumption'    : UnitsFrameObj.apparentConsumption,
                          'Apparent Demand'         : UnitsFrameObj.apparentDemand,
                          'Gas Consumption'         : UnitsFrameObj.gasConsumption,
                          'Gas Demand'              : UnitsFrameObj.gasDemand,
                          'Energy Consumption'      : UnitsFrameObj.energyConsumption,
                          'Energy Demand'           : UnitsFrameObj.energyDemand,
                          'Fuel Consumption'        : UnitsFrameObj.fuelConsumption,
                          'Fuel Demand'             : UnitsFrameObj.fuelDemand,
                          'Water Consumption'       : UnitsFrameObj.waterConsumption,
                          'Water Demand'            : UnitsFrameObj.waterDemand,
                          'Thermal Consumption'     : UnitsFrameObj.thermalConsumption,
                          'Thermal Demand'          : UnitsFrameObj.thermalDemand,
                          'Steam Consumption'       : UnitsFrameObj.steamConsumption,
                          'Steam Demand'            : UnitsFrameObj.steamDemand,
                          'Carbon Emission'         : UnitsFrameObj.carbonEmission,
                          'Currency'                : UnitsFrameObj.currency
                        }

        # Base Unit configuration frame data
        xmlFilePath = os.path.dirname(DataSetup.__file__)
        self.BaseUnitFrameData = DataSetup.BaseUnits(xmlFilePath + '\BaseUnits.xml')
        

    def tearDown(self):
        super(TC0101_Base_Units, self).tearDown()
        Macros.CloseEnteliWEB()

        self.BaseUnitFrameData = None


    #@unittest.skip("")
    def test01_verifyBaseUnitConfiguraionPage(self):
        
        # go to Administration main frame
        Macros.GoToAdministrationPage()
        # load Base Units Configuration Frame
        Macros.GoToBaseUnitsConfiguration()
        
        # verify the required element in Base Unit Configuration page
        elements = [self.baseUnitsFrame.headerTitle,
                    self.baseUnitsFrame.setDefaultMetric,
                    self.baseUnitsFrame.setDefaultImperial,
                    self.baseUnitsFrame.outdoorTemp,
                    self.baseUnitsFrame.electricityConsumption,
                    self.baseUnitsFrame.electricityDemand,
                    self.baseUnitsFrame.apparentConsumption,
                    self.baseUnitsFrame.apparentDemand,
                    self.baseUnitsFrame.gasConsumption,
                    self.baseUnitsFrame.gasDemand,
                    self.baseUnitsFrame.energyConsumption,
                    self.baseUnitsFrame.energyDemand,
                    self.baseUnitsFrame.fuelConsumption,
                    self.baseUnitsFrame.fuelDemand,
                    self.baseUnitsFrame.waterConsumption,
                    self.baseUnitsFrame.waterDemand,
                    self.baseUnitsFrame.thermalConsumption,
                    self.baseUnitsFrame.thermalDemand,
                    self.baseUnitsFrame.steamConsumption,
                    self.baseUnitsFrame.steamDemand,
                    self.baseUnitsFrame.carbonEmission,
                    self.baseUnitsFrame.currency,
                    self.baseUnitsFrame.save]
        for elem in elements:
            result = elem.isDisplayed()
            errMessage = "Verify web element '%s' is displayed"%elem
            self.verify_IsTrue(result, errMessage, HaltOnErr=False)
        
        # verify click the drop down box to display the list and 
        # verify the available units for each drop down
        elements = self.elements
        for name, elem in elements.iteritems():
            current = self.baseUnitsFrame.getDropDownListContent(elem)
            expected = self.BaseUnitFrameData.getPointType(name).getUnits()
            errMessage = "Verify drop down box content for '%s'"%name
            self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
            
            
    #@unittest.skip("")            
    def test02_verifyDefaultUnits(self):
        
        # go to Administration main frame
        Macros.GoToAdministrationPage()
        # load Base Units Configuration Frame
        Macros.GoToBaseUnitsConfiguration()
       
        # click set default metric button
        self.baseUnitsFrame.setDefaultMetric.click()
        # click save button
        self.baseUnitsFrame.saveChange()
        # verify base Units page is loaded
        result = self.baseUnitsFrame.isLoaded()
        errMessage = "Verify Base Unit Configuration Frame is reloaded"
        self.verify_IsTrue(result, errMessage)
        
        # define testing elements
        elements = self.elements
        # verify set default metric
        for name, elem in elements.iteritems():
            expected = self.BaseUnitFrameData.getPointType(name).getDefault('DefaultMetric').Value
            current = self.baseUnitsFrame.getContent(elem)
            errMessage = "Verify default metric for '%s'"%name
            self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
        
        # click set default imperial button
        self.baseUnitsFrame.setDefaultImperial.click()
        # click save button
        self.baseUnitsFrame.saveChange()
        # verify base Units page is loaded
        result = self.baseUnitsFrame.isLoaded()
        errMessage = "Verify Base Unit Configuration Frame is reloaded"
        self.verify_IsTrue(result, errMessage)
        
        # verify set default imperial
        for name, elem in elements.iteritems():
            expected = self.BaseUnitFrameData.getPointType(name).getDefault('DefaultImperial').Value
            current = self.baseUnitsFrame.getContent(elem)
            errMessage = "Verify default Imperial for '%s'" %name
            self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
        
        
    #@unittest.skip("")   
    def test03_verifyPageRedirect(self):

        # delete base units from webgroup.settings_global table
        myDBConn = WebGroupDBObj()
        myDBConn.cursor.execute("DELETE FROM settings_global WHERE Type = ?", 'BaseUnit')
        myDBConn.cnxn.commit()
        del myDBConn
        
        # go to Administration main frame
        Macros.GoToAdministrationPage()
                
        # click meters link under Meter and Rates Section
        adminFrame = AdminFrameObj()
        adminFrame.meters.click()
        time.sleep(3)

        # Verify page redirected to Base Unit configuration frame
        result = self.baseUnitsFrame.isLoaded()
        errMessage = "Verify redirect to Base Unit Configuration Frame"
        self.verify_IsTrue(result, errMessage)

        # verify alert message showing up in base unit configuration frame
        expected = 'Base Units must be defined before meters can be configured'
        current = self.baseUnitsFrame.getContent(UnitsFrameObj.alertMessage)
        errMessage = "Verify alert message showing up"
        self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
        

        # define testing elements
        elements = self.elements
        # verify the unit drop down box is default empty
        for name, elem in elements.iteritems():
            current = self.baseUnitsFrame.getContent(elem)
            result = (current == '')
            errMessage = "Verify no item is selected for '%s'"%name
            self.verify_IsTrue(result, errMessage, HaltOnErr=False)
    
        
    #@unittest.skip("")    
    def test04_verifyRequiredFields(self):
        
        # delete base units from webgroup.settings_global table
        myDBConn = WebGroupDBObj()
        myDBConn.cursor.execute("DELETE FROM settings_global WHERE Type = ?", 'BaseUnit')
        myDBConn.cnxn.commit()
        del myDBConn
        
        # go to Administration main frame
        Macros.GoToAdministrationPage()
        # load Base Units Configuration Frame
        Macros.GoToBaseUnitsConfiguration()
        # click save button without select any units
        self.baseUnitsFrame.saveChange()

        # define testing elements
        elements = self.elements
        # verify units dropdown box in invalid state
        for name, elem in elements.iteritems():
            result = elem.isInvalid()
            errMessage = "Verify field is red highlighted for '%s'"%name
            self.verify_IsTrue(result, errMessage, HaltOnErr=False)
            
        # define testing elements
        elements = {
                     'Outdoor Temp'            : "units.outdoor_temp.invalid_icon",
                     'Electricity Consumption' : "units.electricity_consumption.invalid_icon",
                     'Electricity Demand'      : "units.electricity_demand.invalid_icon",
                     'Apparent Consumption'    : "units.apparent_consumption.invalid_icon",
                     'Apparent Demand'         : "units.apparent_demand.invalid_icon",
                     'Gas Consumption'         : "units.gas_consumption.invalid_icon",
                     'Gas Demand'              : "units.gas_demand.invalid_icon",
                     'Energy Consumption'      : "units.energy_consumption.invalid_icon",
                     'Energy Demand'           : "units.energy_demand.invalid_icon",
                     'Fuel Consumption'        : "units.fuel_consumption.invalid_icon",
                     'Fuel Demand'             : "units.fuel_demand.invalid_icon",
                     'Water Consumption'       : "units.water_consumption.invalid_icon",
                     'Water Demand'            : "units.water_demand.invalid_icon",
                     'Thermal Consumption'     : "units.thermal_consumption.invalid_icon",
                     'Thermal Demand'          : "units.thermal_demand.invalid_icon",
                     'Steam Consumption'       : "units.steam_consumption.invalid_icon",
                     'Steam Demand'            : "units.steam_demand.invalid_icon",
                     'Carbon Emission'         : "units.carbon_emission.invalid_icon",
                     'Currency'                : "units.currency.invalid_icon"
                   }
        # verify invalid warning icon is displayed
        for name, elem in elements.iteritems():
            target = self.baseUnitsFrame.locate(elem)
            result = target.isDisplayed()
            errMessage = "Verify invalid icon is displayed for '%s'"%name
            self.verify_IsTrue(result, errMessage, HaltOnErr=False)
            if result is True:
                # try mouse hover up
                self.baseUnitsFrame.mouseHoverUp(target)
        
        # verify tooltip popup after mouse hover up invalid warning icon
        #for name, elem in elements.iteritems():
        #    driver = self.driver
        #    target = driver.find_element_by_id("ext-quicktips-tip")
        #    baseUnitsFrame.mouseHoverUp(elem.invalidIcon)
             #target = target.
        #    time.sleep(3)
                
            

    #unittest.skip("") 
    def test05_verifyChangeUnits(self):
        
        # go to Administration main frame
        Macros.GoToAdministrationPage()
        # load Base Units Configuration Frame
        Macros.GoToBaseUnitsConfiguration()
   
        # select Default Imperical
        self.baseUnitsFrame.setDefaultMetric.click()
        self.baseUnitsFrame.saveChange()
        result = self.baseUnitsFrame.isLoaded()
        errMessage = "Verify Base Unit Configuration Frame is reloaded"
        self.verify_IsTrue(result, errMessage)
        
        # define the list of datapoint type and the unit need to changed
        unitsToBeChanged = {'Outdoor Temp'            : u'°C',
                            'Electricity Consumption' : u'GWh',
                            'Gas Demand'              : u'm³/h',
                            'Fuel Consumption'        : u'imp gal',
                            'Water Demand'            : u'l/m',
                            'Thermal Consumption'     : u'ton-h',
                            'Steam Demand'            : u'kg/h'}

        # change unit on selected datapoint type
        self.baseUnitsFrame.outdoorTemp = unitsToBeChanged["Outdoor Temp"]
        self.baseUnitsFrame.electricityConsumption = unitsToBeChanged["Electricity Consumption"]
        self.baseUnitsFrame.gasDemand = unitsToBeChanged["Gas Demand"]
        self.baseUnitsFrame.fuelConsumption = unitsToBeChanged["Fuel Consumption"]
        self.baseUnitsFrame.waterDemand = unitsToBeChanged["Water Demand"]
        self.baseUnitsFrame.thermalConsumption = unitsToBeChanged["Thermal Consumption"]
        self.baseUnitsFrame.steamDemand = unitsToBeChanged["Steam Demand"]
        
        # save change
        self.baseUnitsFrame.saveChange()

        # verify units are changed and saved
        current = self.baseUnitsFrame.getContent(UnitsFrameObj.outdoorTemp)
        expected = unitsToBeChanged["Outdoor Temp"]
        errMessage = "Verify unit is changed for '%s'"%"Outdoor Temp"
        self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
        
        current = self.baseUnitsFrame.getContent(UnitsFrameObj.electricityConsumption)
        expected = unitsToBeChanged["Electricity Consumption"]
        errMessage = "Verify unit is changed for '%s'" %"Electricity Consumption"
        self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
        
        current = self.baseUnitsFrame.getContent(UnitsFrameObj.gasDemand)
        expected = unitsToBeChanged["Gas Demand"]
        errMessage = "Verify unit is changed for '%s'" %"Gas Demand"
        self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
        
        current = self.baseUnitsFrame.getContent(UnitsFrameObj.fuelConsumption)
        expected = unitsToBeChanged["Fuel Consumption"]
        errMessage = "Verify unit is changed for '%s'" %"Fuel Consumption"
        self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
        
        current = self.baseUnitsFrame.getContent(UnitsFrameObj.waterDemand)
        expected = unitsToBeChanged["Water Demand"]
        errMessage = "Verify unit is changed for '%s'" %"Water Demand"
        self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
        
        current = self.baseUnitsFrame.getContent(UnitsFrameObj.thermalConsumption)
        expected = unitsToBeChanged["Thermal Consumption"]
        errMessage = "Verify unit is changed for '%s'" %"Thermal Consumption"
        self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
        
        current = self.baseUnitsFrame.getContent(UnitsFrameObj.steamDemand)
        expected = unitsToBeChanged["Steam Demand"]
        errMessage = "Verify unit is changed for '%s'" %"Steam Demand"
        self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
        

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TC0101_Base_Units))
    return suite


if __name__ == "__main__":
    unittest.main()
