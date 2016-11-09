#-------------------------------------------------------------------------------
# Test Case:     TC02.02A - RMA Mode (TC0202A.py)
# Purpose:       The test case verify that user is able to query existing license 
#                using license generator in RMA mode.
#
# Preconditions: 
#
# Author:        Henry Wang
# Created:       Aug 12, 2014
#-------------------------------------------------------------------------------
from libraries.SLAT.TC_Template_LG import *
from ddt import ddt, file_data


@ddt
class TC0202A_RMA_Mode(TC_Template_LG):
    
    def setUp(self):
        super(TC0202A_RMA_Mode, self).setUp()
        success = self.command_Load_License_Generator("RMA")
        if not success:
            self.tearDown()
        
        print "\nTest: %s" %self.currentTest
        
        #if self.currentTest in ('test01', 'test02'):
        #    json_file_location = os.path.abspath(os.path.join(os.path.dirname(__file__), "TC0202.json"))
        #    self.testData = TestData(json_file_location) 
    
    
    def tearDown(self):
        self.command_Close_License_Generator()
        super(TC0202A_RMA_Mode, self).tearDown()    


    #@unittest.skip("")
    @file_data('TC0202.json')
    def test01_Query_License(self, test_data):
        """ Query license in RMA Mode """
        lg = self.lg
        #data = self.testData.getData()
        
        time.sleep(3)
        product = test_data["product"]
        serial = test_data["serial"]
        description = test_data["description"]
        components = test_data["lg"]["query components"]
        siteInfo = test_data["lg"]["site info"]
            
        success = True
        messageHeader = "Query %s '%s':\n"%(product, serial)
        success = self.command_Query_License(product, serial, messageHeader)
            
        if success:
            current = lg.getAddedComponents()
            expected = []
            expected.append([product, ""])
            expected.extend(components)
            self.verify_IsEqual(expected, current, "%sVerify returned components"%messageHeader)
                
            #verify license details for VM module
            if siteInfo:
                name_current = lg.getValue("Installation Site Name")
                partner_current = lg.getValue("Installation Partner")
                address_current = lg.getValue("Installation Site Address")
                name_expected = siteInfo["Site Name"]
                partner_expected = siteInfo["Partner"]
                address_expected = siteInfo["Site Address"]
                self.verify_IsEqual(name_expected, name_current, "%sVerify returned Installation Site Name"%messageHeader)
                self.verify_IsEqual(partner_expected, partner_current, "%sVerify returned Installing Partner"%messageHeader)
                self.verify_IsEqual(address_expected, address_current, "%sVerify returned Installation Site Address"%messageHeader)
                
            # verify eCore binding
            if "eCore Binding" in description:
                expected_hardware_serial = test_data["lg"]["hardware serial"]
                current_hardware_serial = lg.getValue("Hardware Serial")
                self.verify_IsEqual(expected_hardware_serial, current_hardware_serial, "%sVerify returned Hardware Serial"%messageHeader)
                
                
                #reload License Generator
                step = "%sClose License Generator"%messageHeader
                self.command_Close_License_Generator(step)
                # Load License Generator
                step = "%sLoad License Generator"%messageHeader
                success = self.command_Load_License_Generator("RMA", step)
                
                self.sub_test01(test_data)
                            
    
    def sub_test01(self, test_data):
        """ query hardware serial for hardware binding license """
        lg = self.lg
        
        time.sleep(3)
        product = test_data["product"]
        components = test_data["lg"]["query components"]
        hw_serial = test_data["lg"]["hardware serial"]
            
        success = True
        messageHeader = "Hardware Serial Query %s '%s':\n"%(product, hw_serial)
        lg.input("Hardware Serial", hw_serial)
        lg.click("Query")
        time.sleep(35)
            
        # work around for query return error
        if lg.ErrorPopup.isLoaded():
            lg.ErrorPopup.Close()
            time.sleep(3)
            lg.click("Query")    # query again
            time.sleep(35)
            
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
            # verify returned software license serial
            expected_license_serial = test_data["serial"]
            current_license_serial = lg.getValue("Original Serial")
            self.verify_IsEqual(expected_license_serial, current_license_serial, "%sVerify returned license Serial"%messageHeader, HaltOnErr=False)
            # verify returned components
            result = lg.getAddedComponents()
            expected = []
            expected.append([product, ""])
            expected.extend(components)
            current = result
            self.verify_IsEqual(expected, current, "%sVerify returned components"%messageHeader, HaltOnErr=False)
                
   
    @unittest.skip("")
    def test03(self):
        """ Query a license which is upgraded from enteliWEB to enteliWEB_V2 """
        lg = self.lg
        product = self.put["product"]
        serial = self.put["serial"]
        components = self.put["lg"]["query components"]
        siteinfo = self.put["lg"]["site info"]
        
        success = True
        messageHeader = "Query Upgraded License for %s '%s':\n"%(product, serial)
        success = self.command_Query_License(product, serial, messageHeader)
        
        if success:
            # verify returned components
            result = lg.getAddedComponents()
            expected = []
            expected.append([product, ""])
            expected.extend(components)
            current = result
            self.verify_IsEqual(expected, current, "%sVerify returned components"%messageHeader, HaltOnErr=False)
                
            # verify license details info
            if siteinfo:
                name = lg.getValue("Installation Site Name")
                partner = lg.getValue("Installation Partner")
                address = lg.getValue("Installation Site Address")
                current = name
                expected = siteinfo["Site Name"]
                self.verify_IsEqual(expected, current, "%sVerify returned Installation Site Name"%messageHeader, HaltOnErr=False)
                current = partner
                expected = siteinfo["Partner"]
                self.verify_IsEqual(expected, current, "%sVerify returned Installing Partner"%messageHeader, HaltOnErr=False)
                current = address
                expected = siteinfo["Site Address"]
                self.verify_IsEqual(expected, current, "%sVerify returned Installation Site Address"%messageHeader, HaltOnErr=False)
    

if __name__ == "__main__":
    TC0202A_RMA_Mode.execute()