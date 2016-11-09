#-------------------------------------------------------------------------------
# Test Case:     TC02.02B - RMA Mode (TC0202B.py)
# Purpose:       The test case verify that user is able to clone an existing license 
#                using license generator in RMA mode.
#                The test for now only cover clone hardware binded license, such as eCore.
#
# Preconditions: 
#
# Author:        Henry Wang
# Created:       Aug 12, 2014
#-------------------------------------------------------------------------------
import settings
from libraries.PyAutoTestCase import *
from libraries.SLAT.LicenseGenerator import *
from libraries.SLAT.TestData import *
import os, time, datetime


class TC0202B_RMA_Mode(TestCaseTemplate):
    
    def setUp(self):
        super(TC0202B_RMA_Mode, self).setUp()
        LicenseGenerator.changeMode('RMA')
        self.lg = LicenseGenerator()    # define license generator
        self.lg.Launch(timeout=10)
        result = self.lg.isLaunched()
        self.verify_IsTrue(result, "Verify License Generator is loaded.")
        current = self.lg.getMode()
        expected = "RMA"
        if expected != current:
            self.tearDown()
        self.verify_IsEqual(expected, current, "Verify License Generator is in RMA mode")
        
        currentTest = self.id().split('.')[-1]
        print "\nTest: %s" %currentTest
        
        if currentTest in ('test01_Clone_License', 'test02_Unassign_Hardware'):
            json_file_location = os.path.abspath(os.path.join(os.path.dirname(__file__), "TC0202.json"))
            self.testData = TestData(json_file_location)
        
        # setup for test03_Regression_SL612 
        if currentTest == 'test03_Regression_SL612':
            self.put = {
                         "type"          : "enteliWEB_V2",
                         "product"       : "enteliWEB-Exp",
                         "serial"        : "u08VL-65dF6-QzGaw-4WEEa-5b5MO-0L5zf",
                         "serial cloned" : None,
                         "lg"      : { 
                                       "components" : [["enteliWEB-KEE", ""],
                                                       ["enteliWEB-VM", ""],
                                                       ["enteliWEB-API", ""], 
                                                       ["enteliWEB-PAS-FS", "123"],
                                                       ["enteliWEB-PAS-CM", ""]],
                                       "Site Info"  : { "Site Name" : "aaa", "Partner" : "bbb", "Site Address" : "ccc" }
                                     }
                       }
  

    def tearDown(self):
        super(TC0202B_RMA_Mode, self).tearDown()
        if self.lg.ErrorPopup.isLoaded():
            self.lg.ErrorPopup.Close()
        if self.lg.LGPopup.isLoaded():
            self.lg.LGPopup.Close()
        self.lg.Close()
        time.sleep(10)
        
    #@unittest.skip("")
    def test01_Clone_License(self):
        """ clone a hardware binding software license """
        lg = self.lg
        data = self.testData.getData("eCore Binding")
        
        for item in data:
            time.sleep(3)
            product = item["product"]
            components = item["lg"]["query components"]
            serial = item["serial"]
            hw_serial = item["lg"]["hardware serial"]
            cloned_serial = None
            
            success = True
            messageHeader = "Hardware Serial Query %s '%s':\n"%(product, hw_serial)
            lg.input("Hardware Serial", hw_serial)
            lg.click("Query")
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
                # clone the queried license
                lg.click("Clone License")
                time.sleep(20)
                if lg.AALGPopup.isLoaded():
                    lg.AALGPopup.Close()
                    time.sleep(30)
                if lg.EmailPopup.isLoaded():
                    lg.EmailPopup.Close()
                    time.sleep(2)
                if lg.ContinuePopup.isLoaded():
                    lg.ContinuePopup.click("Yes")
                    time.sleep(10)
                lg.viewLogFile()
                result = lg.Log.isLoaded()
                self.verify_IsTrue(result, "Verify License Generator Log window is loaded")
                lastEntry = lg.Log.getLastEntry()
                lg.Log.Close()
                if lastEntry:
                    cloned_serial = lastEntry[4]
                    print "The cloned license serial: %s"%cloned_serial
                    
            # reload license generator
            if cloned_serial:
                lg.Close()
                time.sleep(10)
                self.lg = LicenseGenerator()    # define license generator
                self.lg.Launch(timeout=10)
                result = self.lg.isLaunched()
                self.verify_IsTrue(result, "Verify License Generator is reloaded.")
                lg = self.lg
             
            # query the cloned license     
            if cloned_serial:   
                messageHeader = "Cloned license Query %s '%s':\n"%(product, cloned_serial)
                lg.input("Original Serial", cloned_serial)
                lg.click("Query")
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
                    # verify no hardware serial returned
                    hw_serial_current = lg.getValue("Hardware Serial")
                    hw_serial_expected = ""
                    self.verify_IsEqual(hw_serial_expected, hw_serial_current, "%sVerify returned hardware serial"%messageHeader, HaltOnErr=False)
                    
                    # verify returned optional components
                    result = lg.getAddedComponents()
                    expected = []
                    expected.append([product, ""])
                    expected.extend(components)
                    current = result
                    self.verify_IsEqual(expected, current, "%sVerify returned components"%messageHeader, HaltOnErr=False)
                    
                
    #@unittest.skip("")
    def test02_Unassign_Hardware(self):
        """ unassign hardware id from a hardware binding license """
        lg = self.lg
        data = self.testData.getData("eCore Binding")
        
        # select eCore B as testing object
        put = None
        for item in data:
            if "eCore B" in item["description"]:
                put = item
                break
        if not put:
            raise Exception("testing data for eCore B was not found")
        
        product = put["product"]
        components = put["lg"]["query components"]
        serial = put["serial"]
        hw_serial = put["lg"]["hardware serial"]
        
        # query license
        success = True
        messageHeader = "Hardware Serial Query %s '%s':\n"%(product, hw_serial)
        lg.input("Hardware Serial", hw_serial)
        lg.click("Query")
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
            # unassign hardware
            messageHeader = "Unassign Hardware %s '%s':\n"%(product, serial)
            lg.click("Unassign Hardware")
            time.sleep(35)
            expected = False
            current = lg.ErrorPopup.isLoaded()
            self.verify_IsEqual(expected, current, "%sVerify ERROR Popup"%messageHeader, HaltOnErr=False)
            if current:
                success = False
                lg.ErrorPopup.Close()
            expected = True
            current = lg.LGPopup.isLoaded()
            self.verify_IsEqual(expected, current, "%sVerify LicenseGenerator success Popup"%messageHeader, HaltOnErr=False)
            if current:
                lg.LGPopup.Close()
                
        if success:
            # verify query hardware serial
            messageHeader = "Hardware Serial Query %s '%s':\n"%(product, hw_serial)
            lg.input("Hardware Serial", hw_serial)
            lg.click("Query")
            time.sleep(35)
            expected = True
            current = lg.LGPopup.isLoaded()
            self.verify_IsEqual(expected, current, "%sVerify LicenseGenerator warning Popup"%messageHeader, HaltOnErr=False)
            if current:
                lg.LGPopup.Close()
                
            # verify query license serial
            messageHeader = "license Query %s '%s':\n"%(product, serial)
            lg.input("Original Serial", serial)
            lg.click("Query")
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
                # verify no returned hardware serial
                hw_serial_current = lg.getValue("Hardware Serial")
                hw_serial_expected = ""
                self.verify_IsEqual(hw_serial_expected, hw_serial_current, "%sVerify returned hardware serial"%messageHeader, HaltOnErr=False)
                
                # verify returned components
                result = lg.getAddedComponents()
                expected = []
                expected.append([product, ""])
                expected.extend(components)
                current = result
                self.verify_IsEqual(expected, current, "%sVerify returned components"%messageHeader, HaltOnErr=False)    
            

    #@unittest.skip("")
    def test03_Regression_SL612(self):
        ''' a cloned license does not retain license details info '''
        lg = self.lg
        product = self.put["product"]
        serial = self.put["serial"]
        components = self.put["lg"]["components"]
        
        # query existing license
        lg.input("Original Serial", serial)
        lg.click("Query")
        time.sleep(35)
        current = lg.ErrorPopup.isLoaded()
        expected = False
        self.verify_IsEqual(expected, current, "Query '%s': Verify ERROR Popup"%serial)
        current = lg.LGPopup.isLoaded()
        self.verify_IsEqual(expected, current, "Query '%s': Verify LicenseGenerator Popup"%serial)
        
        # verify returned components
        result = lg.getAddedComponents()
        expected = []
        expected.append([product, ""])
        expected.extend(components)
        current = result
        self.verify_IsEqual(expected, current, "Query '%s': Verify returned components"%serial)
        
        # verify returned license details
        name_current = lg.getValue("Installation Site Name")
        partner_current = lg.getValue("Installation Partner")
        address_current = lg.getValue("Installation Site Address")
        name_expected = self.put["lg"]["Site Info"]["Site Name"]
        partner_expected = self.put["lg"]["Site Info"]["Partner"]
        address_expected = self.put["lg"]["Site Info"]["Site Address"]
        self.verify_IsEqual(name_expected, name_current, "Query '%s': Verify Installation site name is retained."%serial)
        self.verify_IsEqual(partner_expected, partner_current, "Query '%s': Verify Installing partner is retained."%serial)
        self.verify_IsEqual(address_expected, address_current, "Query '%s': Verify Installation site address is retained."%serial)
        
        # clone the existing license
        lg.click("Clone License")
        time.sleep(15)
        if lg.AALGPopup.isLoaded():
            lg.AALGPopup.Close()
            time.sleep(30)
        if lg.EmailPopup.isLoaded():
            lg.EmailPopup.Close()
            time.sleep(2)
        if lg.ContinuePopup.isLoaded():
            lg.ContinuePopup.click("Yes")
        time.sleep(10)
        lg.viewLogFile()
        result = lg.Log.isLoaded()
        self.verify_IsTrue(result, "Verify License Generator Log window is loaded")
        lastEntry = lg.Log.getLastEntry()
        lg.Log.Close()
        if lastEntry:
            self.put["serial cloned"] = lastEntry[4]
            print "The cloned license serial: %s"%lastEntry[4]
            
        # reload license generator
        lg.Close()
        time.sleep(10)
        self.lg = LicenseGenerator()    # define license generator
        self.lg.Launch(timeout=10)
        result = self.lg.isLaunched()
        self.verify_IsTrue(result, "Verify License Generator is reloaded.")
        lg = self.lg
        
        # query the cloned license
        serial = self.put["serial cloned"]
        lg.input("Original Serial", serial)
        lg.click("Query")
        time.sleep(35)
        current = lg.ErrorPopup.isLoaded()
        expected = False
        self.verify_IsEqual(expected, current, "Query cloned '%s': Verify ERROR Popup"%serial)
        current = lg.LGPopup.isLoaded()
        self.verify_IsEqual(expected, current, "Query cloned '%s': Verify LicenseGenerator Popup"%serial)
        
        # verify returned components
        result = lg.getAddedComponents()
        expected = []
        expected.append([product, ""])
        expected.extend(components)
        current = result
        self.verify_IsEqual(expected, current, "Query cloned '%s': Verify returned components"%serial)
        
        # verify returned license details
        name_current = lg.getValue("Installation Site Name")
        partner_current = lg.getValue("Installation Partner")
        address_current = lg.getValue("Installation Site Address")
        name_expected = self.put["lg"]["Site Info"]["Site Name"]
        partner_expected = self.put["lg"]["Site Info"]["Partner"]
        address_expected = self.put["lg"]["Site Info"]["Site Address"]
        self.verify_IsEqual(name_expected, name_current, "Query cloned '%s': Verify Installation site name is retained."%serial)
        self.verify_IsEqual(partner_expected, partner_current, "Query cloned '%s': Verify Installing partner is retained."%serial)
        self.verify_IsEqual(address_expected, address_current, "Query cloned '%s': Verify Installation site address is retained."%serial)
        
    
        
        
    

if __name__ == "__main__":
    TC0202B_RMA_Mode.execute()