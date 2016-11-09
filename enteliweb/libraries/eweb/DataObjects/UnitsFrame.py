'''
Created on Jun 11, 2013

@author: hwang
'''
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Enteliweb.libenteliwebReporting.PageObjects.BasePageObject import BaseFrameObject
from Enteliweb.libenteliwebReporting.PageObjects.BaseWebElement import TextBoxWebElement, ButtonWebElement, DropDownBoxWebElement
import time


class UnitsFrameObj(BaseFrameObject):
    
    headerTitle = TextBoxWebElement("units.title")
    alertMessage = TextBoxWebElement("units.alert_message")
    setDefaultMetric = ButtonWebElement("units.setdefaultmetric")
    setDefaultImperial = ButtonWebElement("units.setdefaultimperial")
    outdoorTemp = DropDownBoxWebElement("units.outdoor_temp")
    electricityConsumption = DropDownBoxWebElement("units.electricity_consumption")
    electricityDemand = DropDownBoxWebElement("units.electricity_demand")
    apparentConsumption = DropDownBoxWebElement("units.apparent_consumption")
    apparentDemand = DropDownBoxWebElement("units.apparent_demand")
    gasConsumption = DropDownBoxWebElement("units.gas_consumption")
    gasDemand = DropDownBoxWebElement("units.gas_demand")
    energyConsumption = DropDownBoxWebElement("units.energy_consumption")
    energyDemand = DropDownBoxWebElement("units.energy_demand")
    fuelConsumption = DropDownBoxWebElement("units.fuel_consumption")
    fuelDemand = DropDownBoxWebElement("units.fuel_demand")
    waterConsumption = DropDownBoxWebElement("units.water_consumption")
    waterDemand = DropDownBoxWebElement("units.water_demand")
    thermalConsumption = DropDownBoxWebElement("units.thermal_consumption")
    thermalDemand = DropDownBoxWebElement("units.thermal_demand")
    steamConsumption = DropDownBoxWebElement("units.steam_consumption")
    steamDemand = DropDownBoxWebElement("units.steam_demand")
    carbonEmission = DropDownBoxWebElement("units.carbon_emission")
    currency = DropDownBoxWebElement("units.currency")
    save = ButtonWebElement("units.save")
    
    
    def __init__(self):
        super(UnitsFrameObj, self).__init__()
        self.titleExpected = "Base Units Configuration"
        self.focus()
        
    def __repr__(self):
        super(UnitsFrameObj, self).__repr__()
        
    def __str__(self):
        return "Base Units Configuration Page"
        
    def saveChange(self):
        """ click the save button and wait page refreshed"""
        timeout = 10
        self.click(UnitsFrameObj.save)
        """
        limit = 60
        finish = False
        last = 0
        while not finish:
            elem = UnitsFrameObj.setDefaultMetric
            if elem.isDisplayed() or last > 60:
                finish = True
                print "Save Base Units last %s seconds" %last
            time.sleep(1)
            last = last + 1
        """
        locator = self.setDefaultMetric.locator
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.ID, locator["value"])))
        except TimeoutException:
            time.sleep(3)
            if self.isLoaded() and self.setDefaultMetric.isDisplayed():
                pass
            else:
                raise Exception("%s is not finish loading within %s seconds"%(self, timeout))
            
        

    