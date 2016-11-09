#-------------------------------------------------------------------------------
# Test Case:     TC02.02C - RMA Mode (TC0202c.py)
# Purpose:       The test case verify that user is able to update / upgrade 
#                existing license using license generator in RMA mode.
#
# Preconditions: 
#
# Author:        Henry Wang
# Created:       Aug 12, 2014
#-------------------------------------------------------------------------------
from libraries.SLAT.TC_Template_LG import *


class TC0202C_RMA_Mode(TC_Template_LG):
    
    def setUp(self):
        super(TC0202C_RMA_Mode, self).setUp()
        print "\nTest: %s" %self.currentTest
        
        if self.currentTest not in ("test04_Regression_SL626"):
            self.command_Load_License_Generator(mode="RMA")
            
        if self.currentTest in ('test01_Upgrade_CopperCube', 
                                'test02_Upgrade_enteliBRIDGE', 
                                'test03_Upgrade_enteliWEB',
                                'test05_Regression_SL659'):
            json_file_location = os.path.abspath(os.path.join(os.path.dirname(__file__), "TC0202C.json"))
            self.testData = TestData(json_file_location)
        
        # setup for test04_Regression_SL626 
        if self.currentTest == 'test04_Regression_SL626':
            self.put = {
                         "type"        : "enteliWEB_V2",
                         "product"     : "enteliWEB-Pro",
                         "serial"      : None,
                         "description" : [],
                         "lg"      : { "components"                : [],
                                       "query components"          : [],
                                       "upgraded query components" : [["enteliWEB-VM", ""]],
                                       "site info"          : None 
                                     }
                       }
            # load license generator in Testing mode
            self.command_Load_License_Generator(mode="Testing")
            
            # generate the testing license
            serial = self.command_Generate_License(self.put)
            
            if serial:
                self.put["serial"] = serial
            else:
                raise Exception("License generating failed")
            
            # reload license generator in RMA mode
            self.command_Close_License_Generator()
            self.command_Load_License_Generator("RMA")
  

    #@unittest.skip("")
    def test01_Upgrade_CopperCube(self):
        """ verify upgrade CopperCube license """
        data = self.testData.getData(value="CopperCube", key="type")
        
        for item in data:
            time.sleep(3)
            product = item["product"]
            upgraded_product = item["upgraded product"]
            serial = item["serial"]
            components = item["lg"]["query components"]
            upgraded_components = item["lg"]["upgraded query components"]
            
            # query license
            step = "%s '%s': Step01 - Query License" %(product, serial)
            success = self.command_Query_License(product, serial, step)
            
            # verify returned components
            if success:
                step = "%s '%s': Step02 - Verify returned components" %(product, serial)
                expected = []
                expected.append([product, ""])
                expected.extend(components)
                success = self.command_Verify_Returned_Components(expected, step)
                    
            # Update License components
            if success:
                step = "%s '%s': Step03 - Update License components" %(product, serial)
                if product != upgraded_product:
                    self.lg.selectProduct(upgraded_product)
                    time.sleep(5)
                listOfComponents = []
                listOfComponents.append([upgraded_product, ""])
                listOfComponents.extend(upgraded_components)
                success = self.command_Update_Components(listOfComponents, step)
                
            # Upgrade License
            if success:
                step = "%s '%s': Step04 - Upgrade License" %(product, serial)
                success = self.command_Upgrade_License(product, serial, step)
            
            # reload license generator
            if success:
                step = "%s '%s': Step05 - Reload License Genertor" %(product, serial)
                self.command_Close_License_Generator(step)
                self.command_Load_License_Generator("RMA", step)
                        
            # query upgraded license
            if success:
                step = "%s '%s': Step06 - Query upgraded license" %(upgraded_product, serial)
                success = self.command_Query_License(upgraded_product, serial, step)
            
            # verify returned components
            if success:
                step = "%s '%s': Step07 - Verify returned components in upgraded license" %(upgraded_product, serial)
                expected = []
                expected.append([upgraded_product, ""])
                expected.extend(upgraded_components)
                success = self.command_Verify_Returned_Components(expected, step)
            
            # reload license generator
            step = "%s '%s': Step08 - Reload License Genertor" %(product, serial)
            self.command_Close_License_Generator(step)
            self.command_Load_License_Generator("RMA", step)
            
            # query license
            step = "%s '%s': Step09 - Query license" %(upgraded_product, serial)
            success = self.command_Query_License(upgraded_product, serial, step)
                
            # restore license components
            if success:
                step = "%s '%s': Step10 - Restore License components to original state" %(product, serial)
                if product != upgraded_product:
                    self.lg.selectProduct(product)
                    time.sleep(5)
                listOfComponents = []
                listOfComponents.append([product, ""])
                listOfComponents.extend(components)
                success = self.command_Update_Components(listOfComponents, step)
                
            # Upgrade License to return to its original state     
            if success:
                step = "%s '%s': Step11 - Upgrade License to return to its original state" %(product, serial)
                success = self.command_Upgrade_License(product, serial, step)
                        
            # reload license generator
            if success:
                step = "%s '%s': Step12 - Reload License Genertor" %(product, serial)
                self.command_Close_License_Generator(step)
                self.command_Load_License_Generator("RMA", step)
                
            # query license to verify if it returns to its original state
            if success:
                step = "%s '%s': Step13 - Query license to verify if it returns to its original state" %(product, serial)
                success = self.command_Query_License(product, serial, step)

                
    @unittest.skip("")
    def test02_Upgrade_enteliBRIDGE(self):
        """ verify upgrade enteliBRIDGE license """
        lg = self.lg
        data = self.testData.getData(value="enteliBRIDGE", key="type")
        
        for item in data:
            time.sleep(3)
            product = item["product"]
            upgraded_product = item["upgraded product"]
            serial = item["serial"]
            components = item["lg"]["query components"]
            upgraded_components = item["lg"]["upgraded query components"]
            
            # query license
            success = True
            self.messageHeader = "Query License: %s '%s'\n"%(product, serial)
            messageHeader = self.messageHeader
            lg.input("Original Serial", serial)
            lg.click("Query")
            time.sleep(50)
            expected = False
            current = lg.ErrorPopup.isLoaded()
            self.verify_IsEqual(expected, current, "%sVerify ERROR Popup"%messageHeader, HaltOnErr=False)
            if current:
                success = False
                lg.ErrorPopup.Close()
            current = lg.LGPopup.isLoaded()
            self.verify_IsEqual(expected, current, "%sVerify LicenseGenerator Warning Popup"%messageHeader, HaltOnErr=False)
            if current:
                success = False
                lg.LGPopup.Close()
            
            if success:
                result = lg.getAddedComponents()
                expected = []
                expected.append([product, ""])
                expected.extend(components)
                current = result
                self.verify_IsEqual(expected, current, "%sVerify returned components"%messageHeader, HaltOnErr=False)
                if current != expected:
                    success = False
                    
            # Upgrade license
            if success:
                self.messageHeader = "Upgrade License %s '%s'\n"%(product, serial)
                messageHeader = self.messageHeader
                if product != upgraded_product:
                    lg.selectProduct(upgraded_product)
                    time.sleep(5)
                listOfComponents = []
                listOfComponents.append([upgraded_product, ""])
                listOfComponents.extend(upgraded_components)
                result = self.command_Upgrade_Components(listOfComponents)
                if result:
                    lg.click("Upgrade License")
                    time.sleep(50)
                    if lg.AALGPopup.isLoaded():
                        lg.AALGPopup.Close()
                        time.sleep(50)
                    result = lg.ErrorPopup.isLoaded()
                    expected = False
                    self.verify_IsEqual(expected, result, "%sVerify if Error popup after generating license"%messageHeader, HaltOnErr=False)
                    if result:
                        success = False
                        lg.ErrorPopup.Close()
                    if lg.EmailPopup.isLoaded():
                        lg.EmailPopup.Close()
                        time.sleep(5)
                    if lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
                        lg.ContinuePopup.click('Yes')
                        time.sleep(15)
            
            # reload license generator
            if success:
                self.messageHeader = "Reload License Generator\n"%(product, serial)
                messageHeader = self.messageHeader
                lg.Close()
                time.sleep(10)
                self.lg = LicenseGenerator()    # define license generator
                self.lg.Launch(timeout=10)
                result = self.lg.isLaunched()
                self.verify_IsTrue(result, "%sVerify License Generator is reloaded."%messageHeader)
                        
            # query upgraded license
            if success:
                lg = self.lg
                self.messageHeader = "Query Upgraded License: %s '%s'\n"%(upgraded_product, serial)
                messageHeader = self.messageHeader
                lg.input("Original Serial", serial)
                lg.click("Query")
                time.sleep(50)
                expected = False
                current = lg.ErrorPopup.isLoaded()
                self.verify_IsEqual(expected, current, "%sVerify ERROR Popup"%messageHeader, HaltOnErr=False)
                if current:
                    success = False
                    lg.ErrorPopup.Close()
                current = lg.LGPopup.isLoaded()
                self.verify_IsEqual(expected, current, "%sVerify LicenseGenerator Warning Popup"%messageHeader, HaltOnErr=False)
                if current:
                    success = False
                    lg.LGPopup.Close()
            
                if success:
                    result = lg.getAddedComponents()
                    expected = []
                    expected.append([upgraded_product, ""])
                    expected.extend(upgraded_components)
                    current = result
                    self.verify_IsEqual(expected, current, "%sVerify returned components"%messageHeader, HaltOnErr=False)
                
            # restore license original state
            if success:
                self.messageHeader = "Restore License Original State: %s '%s'\n"%(product, serial)
                messageHeader = self.messageHeader
                if product != upgraded_product:
                    lg.selectProduct(product)
                    time.sleep(5)
                listOfComponents = []
                listOfComponents.append([product, ""])
                listOfComponents.extend(components)
                result = self.command_Upgrade_Components(listOfComponents)
                if result:
                    lg.click("Upgrade License")
                    time.sleep(50)
                    if lg.AALGPopup.isLoaded():
                        lg.AALGPopup.Close()
                        time.sleep(50)
                    result = lg.ErrorPopup.isLoaded()
                    expected = False
                    self.verify_IsEqual(expected, result, "%sVerify if Error popup "%messageHeader, HaltOnErr=False)
                    if result:
                        success = False
                        lg.ErrorPopup.Close()
                    if lg.EmailPopup.isLoaded():
                        lg.EmailPopup.Close()
                        time.sleep(5)
                    if lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
                        lg.ContinuePopup.click('Yes')
                        time.sleep(15)
                        
            # reload license generator
            if success:
                self.messageHeader = "Reload License Generator\n"%(product, serial)
                messageHeader = self.messageHeader
                lg.Close()
                time.sleep(10)
                self.lg = LicenseGenerator()    # define license generator
                self.lg.Launch(timeout=10)
                result = self.lg.isLaunched()
                self.verify_IsTrue(result, "%sVerify License Generator is reloaded."%messageHeader)
                
            # query license in original state
            if success:
                lg = self.lg
                self.messageHeader = "Query License in Original State: %s '%s'\n"%(upgraded_product, serial)
                messageHeader = self.messageHeader
                lg.input("Original Serial", serial)
                lg.click("Query")
                time.sleep(50)
                expected = False
                current = lg.ErrorPopup.isLoaded()
                self.verify_IsEqual(expected, current, "%sVerify ERROR Popup"%messageHeader, HaltOnErr=False)
                if current:
                    success = False
                    lg.ErrorPopup.Close()
                current = lg.LGPopup.isLoaded()
                self.verify_IsEqual(expected, current, "%sVerify LicenseGenerator Warning Popup"%messageHeader, HaltOnErr=False)
                if current:
                    success = False
                    lg.LGPopup.Close()
            
                if success:
                    result = lg.getAddedComponents()
                    expected = []
                    expected.append([product, ""])
                    expected.extend(components)
                    current = result
                    self.verify_IsEqual(expected, current, "%sVerify returned components"%messageHeader, HaltOnErr=False)
                
    
    #@unittest.skip("")    
    def test03_Upgrade_enteliWEB(self):
        """ verify upgrade enteliWEB license """
        data = self.testData.getData(value="enteliWEB_V2", key="type")
        
        for item in data:
            time.sleep(3)
            product = item["product"]
            upgraded_product = item["upgraded product"]
            serial = item["serial"]
            description = item["description"]
            components = item["lg"]["query components"]
            upgraded_components = item["lg"]["upgraded components"]
            upgraded_query_components = item["lg"]["upgraded query components"]
            site_info = item["lg"]["site info"]
            
            # query license
            step = "%s '%s': Step01 - Query License" %(product, serial)
            success = self.command_Query_License(product, serial, step)
            
            # verify returned components
            if success:
                step = "%s '%s': Step02 - Verify returned components" %(product, serial)
                expected = []
                expected.append([product, ""])
                expected.extend(components)
                success = self.command_Verify_Returned_Components(expected, step)
            
            # Update License components
            if success:
                step = "%s '%s': Step03 - Update License components" %(product, serial)
                if product != upgraded_product:
                    self.lg.selectProduct(upgraded_product)
                    time.sleep(5)
                listOfComponents = []
                listOfComponents.append([upgraded_product, ""])
                listOfComponents.extend(upgraded_components)
                success = self.command_Update_Components(listOfComponents, step)
            
            # update license details information if required
            if success:
                if site_info:
                    step = "%s '%s': Step04 - Update License Details" %(product, serial)
                    site = site_info["Site Name"]
                    partner = site_info["Partner"]
                    address = site_info["Site Address"]
                    self.command_Update_License_Details(site, partner, address, step)
                    
            # Upgrade License
            if success:
                step = "%s '%s': Step05 - Upgrade License" %(product, serial)
                success = self.command_Upgrade_License(product, serial, step)
            
            # reload license generator
            if success:
                step = "%s '%s': Step06 - Reload License Genertor" %(product, serial)
                self.command_Close_License_Generator(step)
                self.command_Load_License_Generator("RMA", step)
                
            # query upgraded license
            if success:
                step = "%s '%s': Step07 - Query upgraded license" %(upgraded_product, serial)
                success = self.command_Query_License(upgraded_product, serial, step)
            
            # verify returned components
            if success:
                step = "%s '%s': Step08 - Verify returned components in upgraded license" %(upgraded_product, serial)
                expected = []
                expected.append([upgraded_product, ""])
                expected.extend(upgraded_query_components)
                success = self.command_Verify_Returned_Components(expected, step)
            
            # reload license generator
            step = "%s '%s': Step09 - Reload License Genertor" %(product, serial)
            success = self.command_Close_License_Generator(step)
            if success:
                success = self.command_Load_License_Generator("RMA", step)
            
            # query license
            if success:
                step = "%s '%s': Step10 - Query License" %(product, serial)
                success = self.command_Query_License(product, serial, step)
                
            # restore license components
            if success:
                step = "%s '%s': Step11 - Restore License components to original state" %(product, serial)
                if product != upgraded_product:
                    self.lg.selectProduct(product)
                    time.sleep(5)
                listOfComponents = []
                listOfComponents.append([product, ""])
                listOfComponents.extend(components)
                success = self.command_Update_Components(listOfComponents, step)
                
            # Upgrade License to return to its original state     
            if success:
                step = "%s '%s': Step12 - Upgrade License to return to its original state" %(product, serial)
                success = self.command_Upgrade_License(product, serial, step)
                        
            # reload license generator
            if success:
                step = "%s '%s': Step13 - Reload License Generator" %(product, serial)
                self.command_Close_License_Generator(step)
                self.command_Load_License_Generator("RMA", step)
                
            # query license to verify if it returns to its original state
            if success:
                step = "%s '%s': Step14 - Query license to verify if it returns to its original state" %(product, serial)
                success = self.command_Query_License(product, serial, step)
                
            # verify returned components
            if success:
                step = "%s '%s': Step15 - Verify returned components" %(product, serial)
                expected = []
                expected.append([product, ""])
                expected.extend(components)
                success = self.command_Verify_Returned_Components(expected, step)


    #@unittest.skip("")
    def test04_Regression_SL626(self):
        ''' Adding VM module to a license does not add License details info '''
        lg = self.lg
        product = self.put["product"]
        serial = self.put["serial"]
        components = self.put["lg"]["query components"]
        siteinfo = { "Site Name" : "aaa", "Partner" : "bbb", "Site Address" : "ccc" }
        
        # query license
        success = self.command_Query_License(product, serial)
        
        # add VM module without license details
        if success:
            lg.addComponent("enteliWEB-VM")    # add VM module
            time.sleep(2)
            lg.click("Upgrade License")
            time.sleep(50)
            result = lg.LGPopup.isLoaded()    # verify error popup
            self.verify_IsTrue(result, "Verify License Generator popup is loaded.")
            if result:
                lg.LGPopup.click("OK")
                time.sleep(2)
            if lg.ContinuePopup.isLoaded():
                lg.ContinuePopup.click("Yes")
                time.sleep(2)
                
        # query license
        success = self.command_Query_License(product, serial)
            
        # verify returned component 
        if success:
            expected = []
            expected.append([product, ""])
            expected.extend(components)
            success = self.command_Verify_Returned_Components(expected, "Verify vm module is not being added.") 
            
        
        # add VM module with license details
        components = self.put["lg"]["upgraded query components"]
        site = siteinfo["Site Name"]
        partner = siteinfo["Partner"]
        address = siteinfo["Site Address"]
        
        lg.addComponent("enteliWEB-VM")    # add VM module
        time.sleep(2)
        self.command_Update_License_Details(site, partner, address)
        success = self.command_Upgrade_License(product, serial)
        
        # reload license generator
        if success:
            self.command_Close_License_Generator()
            self.command_Load_License_Generator("RMA")
        
        # query license    
        success = self.command_Query_License(product, serial)
        
        # verify returned component
        if success:
            expected = []
            expected.append([product, ""])
            expected.extend(components)
            success = self.command_Verify_Returned_Components(expected, "Verify vm module is being added.")
        
        # verify returned license details     
        if success:
            lg = self.lg
            site_current = lg.getValue("Installation Site Name")
            partner_current = lg.getValue("Installation Partner")
            address_current = lg.getValue("Installation Site Address")
            self.verify_IsEqual(site, site_current, "Verify Installation site name is retained.")
            self.verify_IsEqual(partner, partner_current, "Verify Installing partner is retained.")
            self.verify_IsEqual(address, address_current, "Verify Installation site address is retained.")


    #@unittest.skip("")
    def test05_Regression_SL659(self): 
        """ 
        Upgrade a eWEB license by select a different edition will refresh 
        and wipe out all the added components from UI
        """       
        lg = self.lg
        data = self.testData.getData("SL-659")
        
        product = data[0]["product"]
        upgraded_product = data[0]["upgraded product"]
        serial = data[0]["serial"]
        components = data[0]["lg"]["query components"]
        
        # query license
        success = True
        self.messageHeader = "Query License: %s '%s'\n"%(product, serial)
        messageHeader = self.messageHeader
        lg.input("Original Serial", serial)
        lg.click("Query")
        time.sleep(50)
        
        # work around for query return error
        if lg.ErrorPopup.isLoaded():
            lg.ErrorPopup.Close()
            time.sleep(5)
            lg.click("Query")    # query again
            time.sleep(50)
            
        expected = False
        current = lg.ErrorPopup.isLoaded()
        self.verify_IsEqual(expected, current, "%sVerify ERROR Popup"%messageHeader, HaltOnErr=False)
        if current:
            success = False
            lg.ErrorPopup.Close()
        current = lg.LGPopup.isLoaded()
        self.verify_IsEqual(expected, current, "%sVerify LicenseGenerator Warning Popup"%messageHeader, HaltOnErr=False)
        if current:
            success = False
            lg.LGPopup.Close()
            
        if success:
            result = lg.getAddedComponents()
            expected = []
            expected.append([product, ""])
            expected.extend(components)
            current = result
            self.verify_IsEqual(expected, current, "%sVerify returned components"%messageHeader, HaltOnErr=False)
            if current != expected:
                success = False
                
        # change product
        if success:
            self.messageHeader = "Change Product from '%s' to '%s'\n"%(product, upgraded_product)
            messageHeader = self.messageHeader
            if product != upgraded_product:
                lg.selectProduct(upgraded_product)
                time.sleep(5)
            
            current = lg.getAddedComponents()
            expected = []
            expected.append([upgraded_product, ""])
            expected.extend(components)
            self.verify_IsEqual(expected, current, "%sVerify returned components doesn't wipe out"%messageHeader)
        
        
if __name__ == "__main__":
    TC0202C_RMA_Mode.execute()