#-------------------------------------------------------------------------------
# Test Case:     TC02.01B - Test Mode_License Subscription (TC0201B.py)
# Purpose:       The test case verify renew / extend license subscription using 
#                license generator in test mode.
#
# Author:        Henry Wang
# Created:       Sep 19, 2014
#-------------------------------------------------------------------------------
from libraries.SLAT.TC_Template_LG import *
import datetime
from datetime import timedelta


class TC0201B_Test_Mode(TC_Template_LG):
    
    def setUp(self):
        super(TC0201B_Test_Mode, self).setUp()
        print "\nTest: %s" %self.currentTest
        
        if self.currentTest in ("test01", "test02", "test03", "test04", "test05", 
                                "test06", "test07", "test08", "test09", "test10"):
            json_file_location = os.path.abspath(os.path.join(os.path.dirname(__file__), "TC0201B.json"))
            self.testData = TestData(json_file_location)  
        
        
    #@unittest.skip("")
    def test01(self):
        ''' Able to extend license subscription when generating a new license '''
        data = self.testData.getData("test01")
        
        for item in data:
            type =             item["type"]
            product =          item["product"]
            serial =           None
            description =      item["description"]
            components =       item["lg"]["components"]
            query_components = item["lg"]["query components"]
            siteInfo =         item["lg"]["site info"]
            modules =          item["as"]["Modules"]
            success = True
            
            # Load License Generator
            step = "Step01 - Load License Generator"
            success = self.command_Load_License_Generator("Testing", step)
            
            # Generate license
            if success:
                step = "Step02 - Generate license for '%s'"%product
                serial = self.command_Generate_License(item, step)
            
            # query generated license
            if serial:
                step = "Step03 - %s '%s': Query Generated License" %(product, serial)
                success = self.command_Query_License(product, serial, step)
            else:
                success = False
                
            # examine returned components
            if success:
                step = "Step04 - %s '%s': Verify returned components" %(product, serial)
                expected = []
                expected.append([product, ""])
                expected.extend(query_components)
                success = self.command_Verify_Returned_Components(expected, step)
                
            # Close License Generator
            step = "Step05 - Close License Generator"
            self.command_Close_License_Generator(step)
                
            # examine license file in activation server
            if success:
                step = "Step06 - Load Activation Server Web Interface"
                success = self.command_Load_ActivationServer(step)
            
            # search license key
            if success:
                step = "Step07 - %s '%s': Search license key in Activation Server"%(product, serial)
                success = self.command_as_Search_Key(serial, step)
                
            # open license file
            if success:
                step = "Step08 - %s '%s': Select license file in Activation Server" %(product, serial)
                success = self.command_as_Select_LicenseFile(type, step)
            
            # examine modules in license file
            if success:
                for key, value in modules.iteritems():
                    step = "Step09 - %s '%s': examine module '%s' in license file in Activation Server"%(product, serial, key)
                    result = self.activesvr.licFilePage.getModuleInfo(key)
                    current = []
                    if result:
                        current.append(result[3])
                        if key in ("IOPTS", "ACTIVE", "PAS002"):
                            current.append(result[2])
                        if key in ("ACTIVE", "SUB"):
                            current.append(result[4])
                            current.append(result[5])
                        if key in ("CCKEL", "PAS003"):
                            if result[3] == "Yes":
                                current.append(result[4])
                                current.append(result[5])
                    expected = value
                    self.verify_IsEqual(expected, current, step, HaltOnErr=False)
                
            # close activation server web interface
            step = "Step10 - Close Activation Server Web Interface"
            self.command_Close_ActivationServer(step)
            
            
    #@unittest.skip("")    
    def test02(self):
        ''' Able to renew license subscription on an inactivated license '''
        data = self.testData.getData("test02")
        
        for item in data:
            type =             item["type"]
            product =          item["product"]
            serial =           None
            description =      item["description"]
            components =       item["lg"]["components"]
            query_components = item["lg"]["query components"]
            siteInfo =         item["lg"]["site info"]
            modules =          item["as"]["Modules"]
            sub_renew = item["sub renew"]
            success = True
            
            # Load License Generator
            step = "Step01 - Load License Generator"
            success = self.command_Load_License_Generator("Testing", step)
            
            # Generate license
            if success:
                step = "Step02 - Generate license for '%s'"%product
                serial = self.command_Generate_License(item, step)
            
            # query generated license
            if serial:
                step = "Step03 - %s '%s': Query Generated License" %(product, serial)
                success = self.command_Query_License(product, serial, step)
            else:
                success = False
                
            # examine returned components
            if success:
                step = "Step04 - %s '%s': Verify returned components" %(product, serial)
                expected = []
                expected.append([product, ""])
                expected.extend(query_components)
                success = self.command_Verify_Returned_Components(expected, step)
            
            # Verify warning popup when renew sub using ExpSub module
            if success:
                step = "Step05 - %s '%s': Verify warning popup when renew using wrong ExpSub" %(product, serial)
                subModule = product + "-ExpSub"
                self.lg.input("Original Serial", serial)
                time.sleep(2)
                self.lg.selectProduct(subModule)
                time.sleep(2)
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["expsub"]
                    for component in ioAddOnList:
                        self.lg.addComponent(component[0], component[1])
                        time.sleep(2)
                                
                self.lg.click('Generate License')
                time.sleep(30)
        
                result = self.lg.LGPopup.isLoaded()
                self.verify_IsTrue(result, "%s\nVerify if LicenseGenerator Warning Popup after apply renew subscription"%self.messageHeader, HaltOnErr=False)
                if result:
                    self.lg.LGPopup.Close()
                    time.sleep(5)
        
                if self.lg.EmailPopup.isLoaded():
                    self.lg.EmailPopup.Close()
                    time.sleep(5)
            
                if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
                    self.lg.ContinuePopup.click('Yes')
                    time.sleep(15)
                    
            # Verify warning popup when renew sub using module of wrong edition
            if success:
                step = "Step06 - %s '%s': Verify warning popup when renew sub using Sub module of wrong edition" %(product, serial)
                subModule = "enteliWEB-Exp-Sub"
                if product in ("enteliWEB-Tech", "enteliWEB-Lite", "enteliWEB-Exp", "enteliWEB-Ent"):
                    subModule = "enteliWEB-Pro-Sub"
                self.lg.input("Original Serial", serial)
                time.sleep(2)
                self.lg.selectProduct(subModule)
                time.sleep(2)
                                
                self.lg.click('Generate License')
                time.sleep(30)
        
                result = self.lg.LGPopup.isLoaded()
                self.verify_IsTrue(result, "%s\nVerify if LicenseGenerator Warning Popup after apply renew subscription"%self.messageHeader, HaltOnErr=False)
                if result:
                    self.lg.LGPopup.Close()
                    time.sleep(5)
        
                if self.lg.EmailPopup.isLoaded():
                    self.lg.EmailPopup.Close()
                    time.sleep(5)
            
                if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
                    self.lg.ContinuePopup.click('Yes')
                    time.sleep(15) 
            
            # renew subscription
            if success:
                step = step = "Step07 - %s '%s': Renew License Subscription" %(product, serial)
                subModule = product + "-Sub"
                ioAddOnList = None
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["sub"]
                i = 0
                while i < sub_renew["times"]:    # how many times to apply sub renew
                    success = self.command_Renew_Subscription(product, serial, subModule, ioAddOnList, step)
                    if success:
                        i = i + 1
                        time.sleep(3)
                    else:
                        break
            
            # Close License Generator
            step = "Step08 - Close License Generator"
            self.command_Close_License_Generator(step)
                
            # examine license file in activation server
            if success:
                step = "Step09 - Load Activation Server Web Interface"
                success = self.command_Load_ActivationServer(step)
            
            # search license key
            if success:
                step = "Step10 - %s '%s': Search license key in Activation Server"%(product, serial)
                success = self.command_as_Search_Key(serial, step)
                
            # open license file
            if success:
                step = "Step11 - %s '%s': Select license file in Activation Server" %(product, serial)
                success = self.command_as_Select_LicenseFile(type, step)
            
            # examine modules in license file
            if success:
                for key, value in modules.iteritems():
                    step = "Step12 - %s '%s': examine module '%s' in license file in Activation Server"%(product, serial, key)
                    result = self.activesvr.licFilePage.getModuleInfo(key)
                    current = []
                    if result:
                        current.append(result[3])
                        if key in ("IOPTS", "ACTIVE", "PAS002"):
                            current.append(result[2])
                        if key in ("ACTIVE", "SUB"):
                            current.append(result[4])
                            current.append(result[5])
                        if key in ("CCKEL", "PAS003"):
                            if result[3] == "Yes":
                                current.append(result[4])
                                current.append(result[5])
                    expected = value
                    if key == "SUB":
                        expected = sub_renew["SUB"]
                    if key == "ACTIVE":
                        expected = sub_renew["ACTIVE"]
                    self.verify_IsEqual(expected, current, step, HaltOnErr=False)
                
            # close activation server web interface
            step = "Step13 - Close Activation Server Web Interface"
            self.command_Close_ActivationServer(step)


    #@unittest.skip("")
    def test03(self):
        """ Able to renew license subscription on an activated, subscription not expired license """
        data = self.testData.getData("test03")
        
        for item in data:
            type =             item["type"]
            product =          item["product"]
            serial =           None
            description =      item["description"]
            components =       item["lg"]["components"]
            query_components = item["lg"]["query components"]
            siteInfo =         item["lg"]["site info"]
            modules =          item["as"]["Modules"]
            sub_renew = item["sub renew"]
            success = True
            
            # Load License Generator
            step = "Step01 - Load License Generator"
            success = self.command_Load_License_Generator("Testing", step)
            
            # Generate license
            if success:
                step = "Step02 - Generate license for '%s'"%product
                serial = self.command_Generate_License(item, step)
            
            # query generated license
            if serial:
                step = "Step03 - %s '%s': Query Generated License" %(product, serial)
                success = self.command_Query_License(product, serial, step)
            else:
                success = False
                
            # examine returned components
            if success:
                step = "Step04 - %s '%s': Verify returned components" %(product, serial)
                expected = []
                expected.append([product, ""])
                expected.extend(query_components)
                success = self.command_Verify_Returned_Components(expected, step)
                
            # Close License Generator
            step = "Step05 - Close License Generator"
            self.command_Close_License_Generator(step)
            
            # load license manager
            if success:
                step = "Step06 - %s '%s': Load License Manager" %(product, serial)
                success = self.command_Load_License_Manager(step)
                
            # active license
            if success:
                step = "Step07 - %s '%s': Active license on License Manager" %(product, serial)
                success = self.command_lm_Active_License(product, serial, step)
                
            # transfer license
            if success:
                step = "Step08 - %s '%s': Transfer license on License Manager" %(product, serial)   
                success = self.command_lm_Transfer_License(product, serial, step)
                
            # close license manager
            step = "Step09 - %s '%s': close License Manager" %(product, serial)
            success = self.command_Close_License_Manager(step)
            
            # Load License Generator
            if success:
                step = "Step10 - Load License Generator"
                self.command_Load_License_Generator("Testing", step)
                
            # Verify warning popup when renew sub using ExpSub module
            if success:
                step = "Step13 - %s '%s': Verify warning popup when renew sub using ExpSub" %(product, serial)
                subModule = product + "-ExpSub"
                self.lg.input("Original Serial", serial)
                time.sleep(2)
                self.lg.selectProduct(subModule)
                time.sleep(2)
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["expsub"]
                    for component in ioAddOnList:
                        self.lg.addComponent(component[0], component[1])
                        time.sleep(2)
                                
                self.lg.click('Generate License')
                time.sleep(30)
        
                result = self.lg.LGPopup.isLoaded()
                self.verify_IsTrue(result, "%s\nVerify if LicenseGenerator Warning Popup after apply renew subscription"%self.messageHeader, HaltOnErr=False)
                if result:
                    self.lg.LGPopup.Close()
        
                if self.lg.EmailPopup.isLoaded():
                    self.lg.EmailPopup.Close()
                    time.sleep(5)
            
                if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
                    self.lg.ContinuePopup.click('Yes')
                    time.sleep(15)
            
            # renew subscription
            if success:
                step = step = "Step14 - %s '%s': Renew License Subscription" %(product, serial)
                subModule = product + "-Sub"
                ioAddOnList = None
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["sub"]
                i = 0
                while i < sub_renew["times"]:    # how many times to apply sub renew
                    success = self.command_Renew_Subscription(product, serial, subModule, ioAddOnList, step)
                    if success:
                        i = i + 1
                        time.sleep(3)
                    else:
                        break  
                    
            # Close License Generator
            step = "Step15 - Close License Generator"
            self.command_Close_License_Generator(step)
            
            # examine license file in activation server
            if success:
                step = "Step16 - Load Activation Server Web Interface"
                success = self.command_Load_ActivationServer(step)
            
            # search license key
            if success:
                step = "Step17 - %s '%s': Search license key in Activation Server"%(product, serial)
                success = self.command_as_Search_Key(serial, step)
                
            # open license file
            if success:
                step = "Step18 - %s '%s': Select license file in Activation Server" %(product, serial)
                success = self.command_as_Select_LicenseFile(type, step)
            
            # examine modules in license file
            if success:
                for key, value in modules.iteritems():
                    step = "Step19 - %s '%s': examine module '%s' in license file in Activation Server"%(product, serial, key)
                    result = self.activesvr.licFilePage.getModuleInfo(key)
                    current = []
                    if result:
                        current.append(result[3])
                        if key in ("IOPTS", "ACTIVE", "PAS002"):
                            current.append(result[2])
                        if key in ("ACTIVE", "SUB"):
                            current.append(result[4])
                            current.append(result[5])
                        if key in ("CCKEL", "PAS003"):
                            if result[3] == "Yes":
                                current.append(result[4])
                                current.append(result[5])
                    expected = value
                    if key == "SUB":
                        expected = sub_renew["SUB"]
                        # convert from valid number of days to valid until day
                        numOfDays = int(expected[2]) - 1
                        today = datetime.date.today()
                        untilDate = today + timedelta(days=numOfDays)
                        expected[1] = untilDate.strftime('%m/%d/%Y')
                        expected[2] = "0"
                    if key == "ACTIVE":
                        expected = sub_renew["ACTIVE"]
                        # convert from valid number of days to valid until day
                        numOfDays = int(expected[3])
                        if numOfDays != 0:
                            today = datetime.date.today()
                            untilDate = today + timedelta(days=numOfDays - 1)
                            expected[2] = untilDate.strftime('%m/%d/%Y')
                            expected[3] = "0"
                    if key in ("CCKEL", "PAS003"):
                        if expected[0] == "Yes":
                            numOfDays = int(expected[2]) - 1
                            today = datetime.date.today()
                            untilDate = today + timedelta(days=numOfDays)
                            expected[1] = untilDate.strftime('%m/%d/%Y')
                            expected[2] = "0"
                        
                    self.verify_IsEqual(expected, current, step, HaltOnErr=False)
                
            # close activation server web interface
            step = "Step20 - Close Activation Server Web Interface"
            self.command_Close_ActivationServer(step)  


    #@unittest.skip("")
    def test04(self):
        """ Able to renew license subscription on an subscription expired less than one year license """
        data = self.testData.getData("test04")
        
        for item in data:
            type =             item["type"]
            product =          item["product"]
            serial =           None
            description =      item["description"]
            components =       item["lg"]["components"]
            query_components = item["lg"]["query components"]
            siteInfo =         item["lg"]["site info"]
            modules =          item["as"]["Modules"]
            sub_renew = item["sub renew"]
            
            passing_days = sub_renew["passing days"]
            today = datetime.date.today()
            passingDate = today - timedelta(days=passing_days)
            passingDateStr = passingDate.strftime('%m/%d/%Y')
            success = True
            
            # Load License Generator
            step = "Step01 - Load License Generator"
            self.command_Load_License_Generator("Testing", step)
            
            # Generate license
            step = "Step02 - Generate license for '%s'"%product
            serial = self.command_Generate_License(item, step)
            
            # query generated license
            if serial:
                step = "Step03 - %s '%s': Query Generated License" %(product, serial)
                success = self.command_Query_License(product, serial, step)
            else:
                success = False
                
            # examine returned components
            if success:
                step = "Step04 - %s '%s': Verify returned components" %(product, serial)
                expected = []
                expected.append([product, ""])
                expected.extend(query_components)
                success = self.command_Verify_Returned_Components(expected, step)
                
            # Close License Generator
            step = "Step05 - Close License Generator"
            self.command_Close_License_Generator(step)
            
            # load license manager
            if success:
                step = "Step06 - %s '%s': Load License Manager" %(product, serial)
                self.command_Load_License_Manager(step)
                time.sleep(5)
                success = self.lm.isLaunched()
                
            # active license
            if success:
                step = "Step07 - %s '%s': Active license on License Manager" %(product, serial)
                success = self.command_lm_Active_License(product, serial, step)
                
            # transfer license
            if success:
                step = "Step08 - %s '%s': Transfer license on License Manager" %(product, serial)   
                success = self.command_lm_Transfer_License(product, serial, step)
                
            # close license manager
            step = "Step09 - %s '%s': close License Manager" %(product, serial)
            success = self.command_Close_License_Manager(step)
            
            # examine and modify license file in activation server
            if success:
                step = "Step10 - Load Activation Server Web Interface"
                success = self.command_Load_ActivationServer(step)
            
            # search license key
            if success:
                step = "Step11 - %s '%s': Search license key in Activation Server"%(product, serial)
                success = self.command_as_Search_Key(serial, step)
                
            # open license file
            if success:
                step = "Step12 - %s '%s': Select license file in Activation Server" %(product, serial)
                success = self.command_as_Select_LicenseFile(type, step)
            
                
            # modify modules by give an expiry date which is less than one year
            if success:
                for key, value in modules.iteritems():
                    step = "Step13 - %s '%s': modify module '%s' in license file in Activation Server"%(product, serial, key)
                    if key == "SUB":
                        dicOfFields = {}
                        dicOfFields["Valid until Day"] = passingDateStr
                        dicOfFields["Valid number of days"] = "0"
                        success = self.command_as_Edit_Module(key, dicOfFields, step) 
                    if (key == "ACTIVE" and int(value[3]) != 0):
                        dicOfFields = {}
                        dicOfFields["Valid until Day"] = passingDateStr
                        dicOfFields["Valid number of days"] = "0"
                        success = self.command_as_Edit_Module(key, dicOfFields, step)
                    if key in ("CCKEL", "PAS003"):
                        if value[0] == "Yes":
                            dicOfFields = {}
                            dicOfFields["Valid until Day"] = passingDateStr
                            dicOfFields["Valid number of days"] = "0"
                            success = self.command_as_Edit_Module(key, dicOfFields, step)
                            
            # close activation server web interface
            step = "Step14 - Close Activation Server Web Interface"
            self.command_Close_ActivationServer(step)
            
            # Load License Generator
            if success:
                step = "Step15 - Load License Generator"
                success = self.command_Load_License_Generator("Testing", step)
                
            # Verify warning popup when renew sub using ExpSub module
            if success:
                step = "Step18 - %s '%s': Verify warning popup when renew sub using ExpSub" %(product, serial)
                subModule = product + "-ExpSub"
                self.lg.input("Original Serial", serial)
                time.sleep(2)
                self.lg.selectProduct(subModule)
                time.sleep(2)
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["expsub"]
                    for component in ioAddOnList:
                        self.lg.addComponent(component[0], component[1])
                        time.sleep(2)
                                
                self.lg.click('Generate License')
                time.sleep(30)
        
                result = self.lg.LGPopup.isLoaded()
                self.verify_IsTrue(result, "%s\nVerify if LicenseGenerator Warning Popup after apply renew subscription"%self.messageHeader, HaltOnErr=False)
                if result:
                    self.lg.LGPopup.Close()
        
                if self.lg.EmailPopup.isLoaded():
                    self.lg.EmailPopup.Close()
                    time.sleep(5)
            
                if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
                    self.lg.ContinuePopup.click('Yes')
                    time.sleep(15)
                    
            # renew subscription
            if success:
                step = step = "Step19 - %s '%s': Renew License Subscription" %(product, serial)
                subModule = product + "-Sub"
                ioAddOnList = None
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["sub"]
                i = 0
                while i < sub_renew["times"]:    # how many times to apply sub renew
                    success = self.command_Renew_Subscription(product, serial, subModule, ioAddOnList, step)
                    if success:
                        i = i + 1
                        time.sleep(3)
                    else:
                        break  
                    
            # Close License Generator
            step = "Step20 - Close License Generator"
            self.command_Close_License_Generator(step)
            
            # examine license file in activation server
            if success:
                step = "Step21 - Load Activation Server Web Interface"
                success = self.command_Load_ActivationServer(step)
            
            # search license key
            if success:
                step = "Step22 - %s '%s': Search license key in Activation Server"%(product, serial)
                success = self.command_as_Search_Key(serial, step)
                
            # open license file
            if success:
                step = "Step23 - %s '%s': Select license file in Activation Server" %(product, serial)
                success = self.command_as_Select_LicenseFile(type, step)
            
            # examine modules in license file
            if success:
                for key, value in modules.iteritems():
                    step = "Step24 - %s '%s': examine module '%s' in license file in Activation Server"%(product, serial, key)
                    result = self.activesvr.licFilePage.getModuleInfo(key)
                    current = []
                    if result:
                        current.append(result[3])
                        if key in ("IOPTS", "ACTIVE", "PAS002"):
                            current.append(result[2])
                        if key in ("ACTIVE", "SUB"):
                            current.append(result[4])
                            current.append(result[5])
                        if key in ("CCKEL", "PAS003"):
                            if result[3] == "Yes":
                                current.append(result[4])
                                current.append(result[5])
                    expected = value
                    numOfDays = sub_renew["times"] * 365
                    if key == "SUB":
                        # convert from valid number of days to valid until day
                        untilDate = passingDate + timedelta(days=numOfDays)
                        expected[1] = untilDate.strftime('%m/%d/%Y')
                        expected[2] = "0"
                    if key == "ACTIVE":
                        # convert from valid number of days to valid until day
                        if int(expected[3]) != 0:
                            untilDate = passingDate + timedelta(days=numOfDays)
                            expected[2] = untilDate.strftime('%m/%d/%Y')
                            expected[3] = "0"
                    if key in ("CCKEL", "PAS003"):
                        if expected[0] == "Yes":
                            expected[1] = passingDateStr
                            expected[2] = "0"
                        
                    self.verify_IsEqual(expected, current, step, HaltOnErr=False)
                
            # close activation server web interface
            step = "Step25 - Close Activation Server Web Interface"
            self.command_Close_ActivationServer(step) 


    #@unittest.skip("")
    def test05(self):
        """ Able to renew license subscription on an subscription expired more than one year license """
        data = self.testData.getData("test05")
        
        for item in data:
            type =             item["type"]
            product =          item["product"]
            serial =           None
            description =      item["description"]
            components =       item["lg"]["components"]
            query_components = item["lg"]["query components"]
            siteInfo =         item["lg"]["site info"]
            modules =          item["as"]["Modules"]
            sub_renew = item["sub renew"]
            
            passing_days = sub_renew["passing days"]
            today = datetime.date.today()
            passingDate = today - timedelta(days=passing_days)
            passingDateStr = passingDate.strftime('%m/%d/%Y')
            success = True
            
            # Load License Generator
            step = "Step01 - Load License Generator"
            self.command_Load_License_Generator("Testing", step)
            
            # Generate license
            step = "Step02 - Generate license for '%s'"%product
            serial = self.command_Generate_License(item, step)
            
            # query generated license
            if serial:
                step = "Step03 - %s '%s': Query Generated License" %(product, serial)
                success = self.command_Query_License(product, serial, step)
            else:
                success = False
                
            # examine returned components
            if success:
                step = "Step04 - %s '%s': Verify returned components" %(product, serial)
                expected = []
                expected.append([product, ""])
                expected.extend(query_components)
                success = self.command_Verify_Returned_Components(expected, step)
                
            # Close License Generator
            step = "Step05 - Close License Generator"
            self.command_Close_License_Generator(step)
            
            # load license manager
            if success:
                step = "Step06 - %s '%s': Load License Manager" %(product, serial)
                success = self.command_Load_License_Manager(step)
                
            # active license
            if success:
                step = "Step07 - %s '%s': Active license on License Manager" %(product, serial)
                success = self.command_lm_Active_License(product, serial, step)
                
            # transfer license
            if success:
                step = "Step08 - %s '%s': Transfer license on License Manager" %(product, serial)   
                success = self.command_lm_Transfer_License(product, serial, step)
                
            # close license manager
            step = "Step09 - %s '%s': close License Manager" %(product, serial)
            success = self.command_Close_License_Manager(step)
            
            # examine and modify license file in activation server
            if success:
                step = "Step10 - Load Activation Server Web Interface"
                success = self.command_Load_ActivationServer(step)
            
            # search license key
            if success:
                step = "Step11 - %s '%s': Search license key in Activation Server"%(product, serial)
                success = self.command_as_Search_Key(serial, step)
                
            # open license file
            if success:
                step = "Step12 - %s '%s': Select license file in Activation Server" %(product, serial)
                success = self.command_as_Select_LicenseFile(type, step)
            
                
            # modify modules by give an expiry date which is less than one year
            if success:
                for key, value in modules.iteritems():
                    step = "Step13 - %s '%s': modify module '%s' in license file in Activation Server"%(product, serial, key)
                    if key == "SUB":
                        dicOfFields = {}
                        dicOfFields["Valid until Day"] = passingDateStr
                        dicOfFields["Valid number of days"] = "0"
                        success = self.command_as_Edit_Module(key, dicOfFields, step) 
                    if (key == "ACTIVE" and int(value[3]) != 0):
                        dicOfFields = {}
                        dicOfFields["Valid until Day"] = passingDateStr
                        dicOfFields["Valid number of days"] = "0"
                        success = self.command_as_Edit_Module(key, dicOfFields, step)
                    if key in ("CCKEL", "PAS003"):
                        if value[0] == "Yes":
                            dicOfFields = {}
                            dicOfFields["Valid until Day"] = passingDateStr
                            dicOfFields["Valid number of days"] = "0"
                            success = self.command_as_Edit_Module(key, dicOfFields, step)
                            
            # close activation server web interface
            step = "Step14 - Close Activation Server Web Interface"
            self.command_Close_ActivationServer(step)
            
            # Load License Generator
            if success:
                step = "Step15 - Load License Generator"
                self.command_Load_License_Generator("Testing", step)
                
            # Verify warning popup when renew sub using Sub module
            if success:
                step = "Step18 - %s '%s': Verify warning popup when renew sub using ExpSub" %(product, serial)
                subModule = product + "-Sub"
                self.lg.input("Original Serial", serial)
                time.sleep(2)
                self.lg.selectProduct(subModule)
                time.sleep(2)
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["sub"]
                    for component in ioAddOnList:
                        self.lg.addComponent(component[0], component[1])
                        time.sleep(2)
                                
                self.lg.click('Generate License')
                time.sleep(30)
        
                result = self.lg.LGPopup.isLoaded()
                self.verify_IsTrue(result, "%s\nVerify if LicenseGenerator Warning Popup after apply renew subscription"%self.messageHeader, HaltOnErr=False)
                if result:
                    self.lg.LGPopup.Close()
        
                if self.lg.EmailPopup.isLoaded():
                    self.lg.EmailPopup.Close()
                    time.sleep(5)
            
                if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
                    self.lg.ContinuePopup.click('Yes')
                    time.sleep(15)
                    
            # renew subscription
            if success:
                step = "Step19 - %s '%s': Renew License Subscription" %(product, serial)
                subModule = product + "-ExpSub"
                ioAddOnList = None
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["expsub"]
                i = 0
                while i < sub_renew["times"]:    # how many times to apply sub renew
                    success = self.command_Renew_Subscription(product, serial, subModule, ioAddOnList, step)
                    if success:
                        i = i + 1
                        time.sleep(3)
                    else:
                        break  
                    
            # Close License Generator
            step = "Step20 - Close License Generator"
            self.command_Close_License_Generator(step)
            
            # examine license file in activation server
            if success:
                step = "Step21 - Load Activation Server Web Interface"
                success = self.command_Load_ActivationServer(step)
            
            # search license key
            if success:
                step = "Step22 - %s '%s': Search license key in Activation Server"%(product, serial)
                success = self.command_as_Search_Key(serial, step)
                
            # open license file
            if success:
                step = "Step23 - %s '%s': Select license file in Activation Server" %(product, serial)
                success = self.command_as_Select_LicenseFile(type, step)
            
            # examine modules in license file
            if success:
                for key, value in modules.iteritems():
                    step = "Step24 - %s '%s': examine module '%s' in license file in Activation Server"%(product, serial, key)
                    result = self.activesvr.licFilePage.getModuleInfo(key)
                    current = []
                    if result:
                        current.append(result[3])
                        if key in ("IOPTS", "ACTIVE", "PAS002"):
                            current.append(result[2])
                        if key in ("ACTIVE", "SUB"):
                            current.append(result[4])
                            current.append(result[5])
                        if key in ("CCKEL", "PAS003"):
                            if result[3] == "Yes":
                                current.append(result[4])
                                current.append(result[5])
                    expected = value
                    currentDate = datetime.date.today()
                    numOfDays = sub_renew["times"] * 365
                    if key == "SUB":
                        # convert from valid number of days to valid until day
                        untilDate = currentDate + timedelta(days=numOfDays)
                        expected[1] = untilDate.strftime('%m/%d/%Y')
                        expected[2] = "0"
                    if key == "ACTIVE":
                        # convert from valid number of days to valid until day
                        if int(expected[3]) != 0:
                            untilDate = currentDate + timedelta(days=numOfDays)
                            expected[2] = untilDate.strftime('%m/%d/%Y')
                            expected[3] = "0"
                    if key in ("CCKEL", "PAS003"):
                        if expected[0] == "Yes":
                            expected[1] = passingDateStr
                            expected[2] = "0"
                        
                    self.verify_IsEqual(expected, current, step, HaltOnErr=False)
                
            # close activation server web interface
            step = "Step25 - Close Activation Server Web Interface"
            self.command_Close_ActivationServer(step)


    #@unittest.skip("")
    def test06(self):
        ''' Able to extend enteliWEB-KEL module subscription when generating a new license '''
        data = self.testData.getData("test06")
        
        for item in data:
            type =             item["type"]
            product =          item["product"]
            serial =           None
            description =      item["description"]
            components =       item["lg"]["components"]
            query_components = item["lg"]["query components"]
            siteInfo =         item["lg"]["site info"]
            modules =          item["as"]["Modules"]
            success = True
            
            # Load License Generator
            step = "Step01 - Load License Generator"
            self.command_Load_License_Generator("Testing", step)
            
            # Generate license
            step = "Step02 - Generate license for '%s'"%product
            serial = self.command_Generate_License(item, step)
            
            # query generated license
            if serial:
                step = "Step03 - %s '%s': Query Generated License" %(product, serial)
                success = self.command_Query_License(product, serial, step)
            else:
                success = False
                
            # examine returned components
            if success:
                step = "Step04 - %s '%s': Verify returned components" %(product, serial)
                expected = []
                expected.append([product, ""])
                expected.extend(query_components)
                success = self.command_Verify_Returned_Components(expected, step)
                
            # Close License Generator
            step = "Step05 - Close License Generator"
            self.command_Close_License_Generator(step)
                
            # examine license file in activation server
            if success:
                step = "Step06 - Load Activation Server Web Interface"
                success = self.command_Load_ActivationServer(step)
            
            # search license key
            if success:
                step = "Step07 - %s '%s': Search license key in Activation Server"%(product, serial)
                success = self.command_as_Search_Key(serial, step)
                
            # open license file
            if success:
                step = "Step08 - %s '%s': Select license file in Activation Server" %(product, serial)
                success = self.command_as_Select_LicenseFile(type, step)
            
            # examine modules in license file
            if success:
                for key, value in modules.iteritems():
                    step = "Step09 - %s '%s': examine module '%s' in license file in Activation Server"%(product, serial, key)
                    result = self.activesvr.licFilePage.getModuleInfo(key)
                    current = []
                    if result:
                        current.append(result[3])
                        if key in ("IOPTS", "ACTIVE", "PAS002"):
                            current.append(result[2])
                        if key in ("ACTIVE", "SUB"):
                            current.append(result[4])
                            current.append(result[5])
                        if key in ("CCKEL", "PAS003"):
                            if result[3] == "Yes":
                                current.append(result[4])
                                current.append(result[5])
                    expected = value
                    self.verify_IsEqual(expected, current, step, HaltOnErr=False)
                
            # close activation server web interface
            step = "Step10 - Close Activation Server Web Interface"
            self.command_Close_ActivationServer(step)
    
    
    #@unittest.skip("")    
    def test07(self):
        ''' Able to renew enteliWEB-KEL module subscription on an inactivated license '''
        data = self.testData.getData("test07")
        
        for item in data:
            type =             item["type"]
            product =          item["product"]
            serial =           None
            description =      item["description"]
            components =       item["lg"]["components"]
            query_components = item["lg"]["query components"]
            siteInfo =         item["lg"]["site info"]
            modules =          item["as"]["Modules"]
            sub_renew = item["sub renew"]
            success = True
            
            # Load License Generator
            step = "Step01 - Load License Generator"
            self.command_Load_License_Generator("Testing", step)
            
            # Generate license
            step = "Step02 - Generate license for '%s'"%product
            serial = self.command_Generate_License(item, step)
            
            # query generated license
            if serial:
                step = "Step03 - %s '%s': Query Generated License" %(product, serial)
                success = self.command_Query_License(product, serial, step)
            else:
                success = False
                
            # examine returned components
            if success:
                step = "Step04 - %s '%s': Verify returned components" %(product, serial)
                expected = []
                expected.append([product, ""])
                expected.extend(query_components)
                success = self.command_Verify_Returned_Components(expected, step)
            
            # Verify warning popup when renew sub using ExpSub module
            if success:
                step = "Step05 - %s '%s': Verify warning popup when renew sub using ExpSub" %(product, serial)
                subModule = product + "-KEL-ExpSub"
                self.lg.input("Original Serial", serial)
                time.sleep(2)
                self.lg.selectProduct(subModule)
                time.sleep(2)
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["expsub"]
                    for component in ioAddOnList:
                        self.lg.addComponent(component[0], component[1])
                        time.sleep(2)
                                
                self.lg.click('Generate License')
                time.sleep(30)
        
                result = self.lg.LGPopup.isLoaded()
                self.verify_IsTrue(result, "%s\nVerify if LicenseGenerator Warning Popup after apply renew subscription"%self.messageHeader, HaltOnErr=False)
                if result:
                    self.lg.LGPopup.Close()
        
                if self.lg.EmailPopup.isLoaded():
                    self.lg.EmailPopup.Close()
                    time.sleep(5)
            
                if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
                    self.lg.ContinuePopup.click('Yes')
                    time.sleep(15)
                    
            # Verify warning popup when renew sub using module of wrong edition
            if success:
                step = "Step06 - %s '%s': Verify warning popup when renew sub using Sub module of wrong edition" %(product, serial)
                subModule = "enteliWEB-Exp-KEL-Sub"
                if product in ("enteliWEB-Tech", "enteliWEB-Lite", "enteliWEB-Exp", "enteliWEB-Ent"):
                    subModule = "enteliWEB-Pro-KEL-Sub"
                self.lg.input("Original Serial", serial)
                time.sleep(2)
                self.lg.selectProduct(subModule)
                time.sleep(2)
                                
                self.lg.click('Generate License')
                time.sleep(30)
        
                result = self.lg.LGPopup.isLoaded()
                self.verify_IsTrue(result, "%s\nVerify if LicenseGenerator Warning Popup after apply renew subscription"%self.messageHeader, HaltOnErr=False)
                if result:
                    self.lg.LGPopup.Close()
        
                if self.lg.EmailPopup.isLoaded():
                    self.lg.EmailPopup.Close()
                    time.sleep(5)
            
                if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
                    self.lg.ContinuePopup.click('Yes')
                    time.sleep(15) 
            
            # renew subscription
            if success:
                step = step = "Step07 - %s '%s': Renew License Subscription" %(product, serial)
                subModule = product + "-KEL-Sub"
                ioAddOnList = None
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["sub"]
                i = 0
                while i < sub_renew["times"]:    # how many times to apply sub renew
                    success = self.command_Renew_Subscription(product, serial, subModule, ioAddOnList, step)
                    if success:
                        i = i + 1
                        time.sleep(3)
                    else:
                        break
            
            # Close License Generator
            step = "Step08 - Close License Generator"
            self.command_Close_License_Generator(step)
                
            # examine license file in activation server
            if success:
                step = "Step09 - Load Activation Server Web Interface"
                success = self.command_Load_ActivationServer(step)
            
            # search license key
            if success:
                step = "Step10 - %s '%s': Search license key in Activation Server"%(product, serial)
                success = self.command_as_Search_Key(serial, step)
                
            # open license file
            if success:
                step = "Step11 - %s '%s': Select license file in Activation Server" %(product, serial)
                success = self.command_as_Select_LicenseFile(type, step)
            
            # examine modules in license file
            if success:
                for key, value in modules.iteritems():
                    step = "Step12 - %s '%s': examine module '%s' in license file in Activation Server"%(product, serial, key)
                    result = self.activesvr.licFilePage.getModuleInfo(key)
                    current = []
                    if result:
                        current.append(result[3])
                        if key in ("IOPTS", "ACTIVE", "PAS002"):
                            current.append(result[2])
                        if key in ("ACTIVE", "SUB"):
                            current.append(result[4])
                            current.append(result[5])
                        if key in ("CCKEL", "PAS003"):
                            if result[3] == "Yes":
                                current.append(result[4])
                                current.append(result[5])
                    expected = value
                    if key == "CCKEL":
                        expected = sub_renew["CCKEL"]
                    self.verify_IsEqual(expected, current, step, HaltOnErr=False)
                
            # close activation server web interface
            step = "Step13 - Close Activation Server Web Interface"
            self.command_Close_ActivationServer(step)        
    
    
    #@unittest.skip("")
    def test08(self):
        """ Able to renew enteliWEB-KEL module subscription on an Activated license, which KEL module is not expired """
        data = self.testData.getData("test08")
        
        for item in data:
            type =             item["type"]
            product =          item["product"]
            serial =           None
            description =      item["description"]
            components =       item["lg"]["components"]
            query_components = item["lg"]["query components"]
            siteInfo =         item["lg"]["site info"]
            modules =          item["as"]["Modules"]
            sub_renew = item["sub renew"]
            success = True
            
            # Load License Generator
            step = "Step01 - Load License Generator"
            self.command_Load_License_Generator("Testing", step)
            
            # Generate license
            step = "Step02 - Generate license for '%s'"%product
            serial = self.command_Generate_License(item, step)
            
            # query generated license
            if serial:
                step = "Step03 - %s '%s': Query Generated License" %(product, serial)
                success = self.command_Query_License(product, serial, step)
            else:
                success = False
                
            # examine returned components
            if success:
                step = "Step04 - %s '%s': Verify returned components" %(product, serial)
                expected = []
                expected.append([product, ""])
                expected.extend(query_components)
                success = self.command_Verify_Returned_Components(expected, step)
                
            # Close License Generator
            step = "Step05 - Close License Generator"
            self.command_Close_License_Generator(step)
            
            # load license manager
            if success:
                step = "Step06 - %s '%s': Load License Manager" %(product, serial)
                success = self.command_Load_License_Manager(step)
                
            # active license
            if success:
                step = "Step07 - %s '%s': Active license on License Manager" %(product, serial)
                success = self.command_lm_Active_License(product, serial, step)
                
            # transfer license
            if success:
                step = "Step08 - %s '%s': Transfer license on License Manager" %(product, serial)   
                success = self.command_lm_Transfer_License(product, serial, step)
                
            # close license manager
            step = "Step09 - %s '%s': close License Manager" %(product, serial)
            success = self.command_Close_License_Manager(step)
            
            # Load License Generator
            if success:
                step = "Step10 - Load License Generator"
                self.command_Load_License_Generator("Testing", step)
                
            # Verify warning popup when renew sub using ExpSub module
            if success:
                step = "Step13 - %s '%s': Verify warning popup when renew sub using ExpSub" %(product, serial)
                subModule = product + "-KEL-ExpSub"
                self.lg.input("Original Serial", serial)
                time.sleep(2)
                self.lg.selectProduct(subModule)
                time.sleep(2)
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["expsub"]
                    for component in ioAddOnList:
                        self.lg.addComponent(component[0], component[1])
                        time.sleep(2)
                                
                self.lg.click('Generate License')
                time.sleep(30)
        
                result = self.lg.LGPopup.isLoaded()
                self.verify_IsTrue(result, "%s\nVerify if LicenseGenerator Warning Popup after apply renew subscription"%self.messageHeader, HaltOnErr=False)
                if result:
                    self.lg.LGPopup.Close()
        
                if self.lg.EmailPopup.isLoaded():
                    self.lg.EmailPopup.Close()
                    time.sleep(5)
            
                if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
                    self.lg.ContinuePopup.click('Yes')
                    time.sleep(15)
            
            # renew subscription
            if success:
                step = step = "Step14 - %s '%s': Renew License Subscription" %(product, serial)
                subModule = product + "-KEL-Sub"
                ioAddOnList = None
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["sub"]
                i = 0
                while i < sub_renew["times"]:    # how many times to apply sub renew
                    success = self.command_Renew_Subscription(product, serial, subModule, ioAddOnList, step)
                    if success:
                        i = i + 1
                        time.sleep(3)
                    else:
                        break  
                    
            # Close License Generator
            step = "Step15 - Close License Generator"
            self.command_Close_License_Generator(step)
            
            # examine license file in activation server
            if success:
                step = "Step16 - Load Activation Server Web Interface"
                success = self.command_Load_ActivationServer(step)
            
            # search license key
            if success:
                step = "Step17 - %s '%s': Search license key in Activation Server"%(product, serial)
                success = self.command_as_Search_Key(serial, step)
                
            # open license file
            if success:
                step = "Step18 - %s '%s': Select license file in Activation Server" %(product, serial)
                success = self.command_as_Select_LicenseFile(type, step)
            
            # examine modules in license file
            if success:
                for key, value in modules.iteritems():
                    step = "Step19 - %s '%s': examine module '%s' in license file in Activation Server"%(product, serial, key)
                    result = self.activesvr.licFilePage.getModuleInfo(key)
                    current = []
                    if result:
                        current.append(result[3])
                        if key in ("IOPTS", "ACTIVE", "PAS002"):
                            current.append(result[2])
                        if key in ("ACTIVE", "SUB"):
                            current.append(result[4])
                            current.append(result[5])
                        if key in ("CCKEL", "PAS003"):
                            if result[3] == "Yes":
                                current.append(result[4])
                                current.append(result[5])
                    expected = value
                    if key == "SUB":
                        # convert from valid number of days to valid until day
                        numOfDays = int(expected[2]) - 1
                        today = datetime.date.today()
                        untilDate = today + timedelta(days=numOfDays)
                        expected[1] = untilDate.strftime('%m/%d/%Y')
                        expected[2] = "0"
                    if key == "ACTIVE":
                        # convert from valid number of days to valid until day
                        numOfDays = int(expected[3])
                        if numOfDays != 0:
                            today = datetime.date.today()
                            untilDate = today + timedelta(days=numOfDays - 1)
                            expected[2] = untilDate.strftime('%m/%d/%Y')
                            expected[3] = "0"
                    if key == "CCKEL":
                        expected = sub_renew["CCKEL"]
                    if key in ("CCKEL", "PAS003"):
                        if expected[0] == "Yes":
                            numOfDays = int(expected[2]) - 1
                            today = datetime.date.today()
                            untilDate = today + timedelta(days=numOfDays)
                            expected[1] = untilDate.strftime('%m/%d/%Y')
                            expected[2] = "0"
                        
                    self.verify_IsEqual(expected, current, step, HaltOnErr=False)
                
            # close activation server web interface
            step = "Step20 - Close Activation Server Web Interface"
            self.command_Close_ActivationServer(step)
    
    
    #@unittest.skip("")
    def test09(self):
        """ Able to renew enteliWEB-KEL module subscription on an Activated license, which KEL module is expired less than one year """
        data = self.testData.getData("test09")
        
        for item in data:
            type =             item["type"]
            product =          item["product"]
            serial =           None
            description =      item["description"]
            components =       item["lg"]["components"]
            query_components = item["lg"]["query components"]
            siteInfo =         item["lg"]["site info"]
            modules =          item["as"]["Modules"]
            sub_renew = item["sub renew"]
            
            passing_days = sub_renew["passing days"]
            today = datetime.date.today()
            passingDate = today - timedelta(days=passing_days)
            passingDateStr = passingDate.strftime('%m/%d/%Y')
            success = True
            
            # Load License Generator
            step = "Step01 - Load License Generator"
            self.command_Load_License_Generator("Testing", step)
            
            # Generate license
            step = "Step02 - Generate license for '%s'"%product
            serial = self.command_Generate_License(item, step)
            
            # query generated license
            if serial:
                step = "Step03 - %s '%s': Query Generated License" %(product, serial)
                success = self.command_Query_License(product, serial, step)
            else:
                success = False
                
            # examine returned components
            if success:
                step = "Step04 - %s '%s': Verify returned components" %(product, serial)
                expected = []
                expected.append([product, ""])
                expected.extend(query_components)
                success = self.command_Verify_Returned_Components(expected, step)
                
            # Close License Generator
            step = "Step05 - Close License Generator"
            self.command_Close_License_Generator(step)
            
            # load license manager
            if success:
                step = "Step06 - %s '%s': Load License Manager" %(product, serial)
                success = self.command_Load_License_Manager(step)
                
            # active license
            if success:
                step = "Step07 - %s '%s': Active license on License Manager" %(product, serial)
                success = self.command_lm_Active_License(product, serial, step)
                
            # transfer license
            if success:
                step = "Step08 - %s '%s': Transfer license on License Manager" %(product, serial)   
                success = self.command_lm_Transfer_License(product, serial, step)
                
            # close license manager
            step = "Step09 - %s '%s': close License Manager" %(product, serial)
            success = self.command_Close_License_Manager(step)
            
            # examine and modify license file in activation server
            if success:
                step = "Step10 - Load Activation Server Web Interface"
                success = self.command_Load_ActivationServer(step)
            
            # search license key
            if success:
                step = "Step11 - %s '%s': Search license key in Activation Server"%(product, serial)
                success = self.command_as_Search_Key(serial, step)
                
            # open license file
            if success:
                step = "Step12 - %s '%s': Select license file in Activation Server" %(product, serial)
                success = self.command_as_Select_LicenseFile(type, step)
            
                
            # modify modules by give an expiry date which is less than one year
            if success:
                for key, value in modules.iteritems():
                    step = "Step13 - %s '%s': modify module '%s' in license file in Activation Server"%(product, serial, key)
                    if key == "SUB":
                        dicOfFields = {}
                        dicOfFields["Valid until Day"] = passingDateStr
                        dicOfFields["Valid number of days"] = "0"
                        success = self.command_as_Edit_Module(key, dicOfFields, step) 
                    if (key == "ACTIVE" and int(value[3]) != 0):
                        dicOfFields = {}
                        dicOfFields["Valid until Day"] = passingDateStr
                        dicOfFields["Valid number of days"] = "0"
                        success = self.command_as_Edit_Module(key, dicOfFields, step)
                    if key in ("CCKEL", "PAS003"):
                        if value[0] == "Yes":
                            dicOfFields = {}
                            dicOfFields["Valid until Day"] = passingDateStr
                            dicOfFields["Valid number of days"] = "0"
                            success = self.command_as_Edit_Module(key, dicOfFields, step)
                            
            # close activation server web interface
            step = "Step14 - Close Activation Server Web Interface"
            self.command_Close_ActivationServer(step)
            
            # Load License Generator
            if success:
                step = "Step15 - Load License Generator"
                self.command_Load_License_Generator("Testing", step)
                
            # Verify warning popup when renew sub using ExpSub module
            if success:
                step = "Step18 - %s '%s': Verify warning popup when renew sub using ExpSub" %(product, serial)
                subModule = product + "-KEL-ExpSub"
                self.lg.input("Original Serial", serial)
                time.sleep(2)
                self.lg.selectProduct(subModule)
                time.sleep(2)
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["expsub"]
                    for component in ioAddOnList:
                        self.lg.addComponent(component[0], component[1])
                        time.sleep(2)
                                
                self.lg.click('Generate License')
                time.sleep(30)
        
                result = self.lg.LGPopup.isLoaded()
                self.verify_IsTrue(result, "%s\nVerify if LicenseGenerator Warning Popup after apply renew subscription"%self.messageHeader, HaltOnErr=False)
                if result:
                    self.lg.LGPopup.Close()
        
                if self.lg.EmailPopup.isLoaded():
                    self.lg.EmailPopup.Close()
                    time.sleep(5)
            
                if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
                    self.lg.ContinuePopup.click('Yes')
                    time.sleep(15)
                    
            # renew subscription
            if success:
                step = step = "Step19 - %s '%s': Renew License Subscription" %(product, serial)
                subModule = product + "-KEL-Sub"
                ioAddOnList = None
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["sub"]
                i = 0
                while i < sub_renew["times"]:    # how many times to apply sub renew
                    success = self.command_Renew_Subscription(product, serial, subModule, ioAddOnList, step)
                    if success:
                        i = i + 1
                        time.sleep(3)
                    else:
                        break  
                    
            # Close License Generator
            step = "Step20 - Close License Generator"
            self.command_Close_License_Generator(step)
            
            # examine license file in activation server
            if success:
                step = "Step21 - Load Activation Server Web Interface"
                success = self.command_Load_ActivationServer(step)
            
            # search license key
            if success:
                step = "Step22 - %s '%s': Search license key in Activation Server"%(product, serial)
                success = self.command_as_Search_Key(serial, step)
                
            # open license file
            if success:
                step = "Step23 - %s '%s': Select license file in Activation Server" %(product, serial)
                success = self.command_as_Select_LicenseFile(type, step)
            
            # examine modules in license file
            if success:
                for key, value in modules.iteritems():
                    step = "Step24 - %s '%s': examine module '%s' in license file in Activation Server"%(product, serial, key)
                    result = self.activesvr.licFilePage.getModuleInfo(key)
                    current = []
                    if result:
                        current.append(result[3])
                        if key in ("IOPTS", "ACTIVE", "PAS002"):
                            current.append(result[2])
                        if key in ("ACTIVE", "SUB"):
                            current.append(result[4])
                            current.append(result[5])
                        if key in ("CCKEL", "PAS003"):
                            if result[3] == "Yes":
                                current.append(result[4])
                                current.append(result[5])
                    expected = value
                    numOfDays = sub_renew["times"] * 365
                    if key == "SUB":
                        expected[1] = passingDateStr
                        expected[2] = "0"
                    if key == "ACTIVE":
                        if int(expected[3]) != 0:
                            expected[2] = passingDateStr
                            expected[3] = "0"
                    if key == "PAS003":
                        if expected[0] == "Yes":
                            expected[1] = passingDateStr
                            expected[2] = "0"
                    if key == "CCKEL":
                        if expected[0] == "Yes":
                            untilDate = passingDate + timedelta(days=numOfDays)
                            expected[1] = untilDate.strftime('%m/%d/%Y')
                            expected[2] = "0"
                        
                    self.verify_IsEqual(expected, current, step, HaltOnErr=False)
                
            # close activation server web interface
            step = "Step25 - Close Activation Server Web Interface"
            self.command_Close_ActivationServer(step) 
    
    
    #@unittest.skip("")
    def test10(self):
        """ Able to renew enteliWEB-KEL module subscription on an Activated license, which KEL module is expired more than one year """
        data = self.testData.getData("test10")
        
        for item in data:
            type =             item["type"]
            product =          item["product"]
            serial =           None
            description =      item["description"]
            components =       item["lg"]["components"]
            query_components = item["lg"]["query components"]
            siteInfo =         item["lg"]["site info"]
            modules =          item["as"]["Modules"]
            sub_renew = item["sub renew"]
            
            passing_days = sub_renew["passing days"]
            today = datetime.date.today()
            passingDate = today - timedelta(days=passing_days)
            passingDateStr = passingDate.strftime('%m/%d/%Y')
            success = True
            
            # Load License Generator
            step = "Step01 - Load License Generator"
            self.command_Load_License_Generator("Testing", step)
            
            # Generate license
            step = "Step02 - Generate license for '%s'"%product
            serial = self.command_Generate_License(item, step)
            
            # query generated license
            if serial:
                step = "Step03 - %s '%s': Query Generated License" %(product, serial)
                success = self.command_Query_License(product, serial, step)
            else:
                success = False
                
            # examine returned components
            if success:
                step = "Step04 - %s '%s': Verify returned components" %(product, serial)
                expected = []
                expected.append([product, ""])
                expected.extend(query_components)
                success = self.command_Verify_Returned_Components(expected, step)
                
            # Close License Generator
            step = "Step05 - Close License Generator"
            self.command_Close_License_Generator(step)
            
            # load license manager
            if success:
                step = "Step06 - %s '%s': Load License Manager" %(product, serial)
                success = self.command_Load_License_Manager(step)
                
            # active license
            if success:
                step = "Step07 - %s '%s': Active license on License Manager" %(product, serial)
                success = self.command_lm_Active_License(product, serial, step)
                
            # transfer license
            if success:
                step = "Step08 - %s '%s': Transfer license on License Manager" %(product, serial)   
                success = self.command_lm_Transfer_License(product, serial, step)
                
            # close license manager
            step = "Step09 - %s '%s': close License Manager" %(product, serial)
            success = self.command_Close_License_Manager(step)
            
            # examine and modify license file in activation server
            if success:
                step = "Step10 - Load Activation Server Web Interface"
                success = self.command_Load_ActivationServer(step)
            
            # search license key
            if success:
                step = "Step11 - %s '%s': Search license key in Activation Server"%(product, serial)
                success = self.command_as_Search_Key(serial, step)
                
            # open license file
            if success:
                step = "Step12 - %s '%s': Select license file in Activation Server" %(product, serial)
                success = self.command_as_Select_LicenseFile(type, step)
            
                
            # modify modules by give an expiry date which is more than one year
            if success:
                for key, value in modules.iteritems():
                    step = "Step13 - %s '%s': modify module '%s' in license file in Activation Server"%(product, serial, key)
                    if key == "SUB":
                        dicOfFields = {}
                        dicOfFields["Valid until Day"] = passingDateStr
                        dicOfFields["Valid number of days"] = "0"
                        success = self.command_as_Edit_Module(key, dicOfFields, step) 
                    if (key == "ACTIVE" and int(value[3]) != 0):
                        dicOfFields = {}
                        dicOfFields["Valid until Day"] = passingDateStr
                        dicOfFields["Valid number of days"] = "0"
                        success = self.command_as_Edit_Module(key, dicOfFields, step)
                    if key in ("CCKEL", "PAS003"):
                        if value[0] == "Yes":
                            dicOfFields = {}
                            dicOfFields["Valid until Day"] = passingDateStr
                            dicOfFields["Valid number of days"] = "0"
                            success = self.command_as_Edit_Module(key, dicOfFields, step)
                            if success and key == "CCKEL":
                                success = self.command_as_Edit_Module("KEWEB", dicOfFields, step)
                                 
                            
            # close activation server web interface
            step = "Step14 - Close Activation Server Web Interface"
            self.command_Close_ActivationServer(step)
            
            # Load License Generator
            if success:
                step = "Step15 - Load License Generator"
                self.command_Load_License_Generator("Testing", step)
                
            # Verify warning popup when renew sub using Sub module
            if success:
                step = "Step18 - %s '%s': Try renew KEL Module subscription using the wrong KEL-Sub module" %(product, serial)
                subModule = product + "-KEL-Sub"
                self.lg.input("Original Serial", serial)
                time.sleep(2)
                self.lg.selectProduct(subModule)
                time.sleep(2)
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["sub"]
                    for component in ioAddOnList:
                        self.lg.addComponent(component[0], component[1])
                        time.sleep(2)
                                
                self.lg.click('Generate License')
                time.sleep(30)
        
                result = self.lg.LGPopup.isLoaded()
                self.verify_IsTrue(result, "%s\nVerify if LicenseGenerator Warning Popup after apply renew subscription"%self.messageHeader, HaltOnErr=False)
                if result:
                    self.lg.LGPopup.Close()
        
                if self.lg.EmailPopup.isLoaded():
                    self.lg.EmailPopup.Close()
                    time.sleep(5)
            
                if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
                    self.lg.ContinuePopup.click('Yes')
                    time.sleep(15)
                    
            # renew subscription
            if success:
                step = "Step19 - %s '%s': Renew KEL moduel Subscription" %(product, serial)
                subModule = product + "-KEL-ExpSub"
                ioAddOnList = None
                if product == "enteliWEB-Ent":
                    ioAddOnList = item["lg"]["expsub"]
                i = 0
                while i < sub_renew["times"]:    # how many times to apply sub renew
                    success = self.command_Renew_Subscription(product, serial, subModule, ioAddOnList, step)
                    if success:
                        i = i + 1
                        time.sleep(3)
                    else:
                        break  
                    
            # Close License Generator
            step = "Step20 - Close License Generator"
            self.command_Close_License_Generator(step)
            
            # examine license file in activation server
            if success:
                step = "Step21 - Load Activation Server Web Interface"
                success = self.command_Load_ActivationServer(step)
            
            # search license key
            if success:
                step = "Step22 - %s '%s': Search license key in Activation Server"%(product, serial)
                success = self.command_as_Search_Key(serial, step)
                
            # open license file
            if success:
                step = "Step23 - %s '%s': Select license file in Activation Server" %(product, serial)
                success = self.command_as_Select_LicenseFile(type, step)
            
            # examine modules in license file
            if success:
                for key, value in modules.iteritems():
                    step = "Step24 - %s '%s': examine module '%s' in license file in Activation Server"%(product, serial, key)
                    result = self.activesvr.licFilePage.getModuleInfo(key)
                    current = []
                    if result:
                        current.append(result[3])
                        if key in ("IOPTS", "ACTIVE", "PAS002"):
                            current.append(result[2])
                        if key in ("ACTIVE", "SUB"):
                            current.append(result[4])
                            current.append(result[5])
                        if key in ("CCKEL", "PAS003"):
                            if result[3] == "Yes":
                                current.append(result[4])
                                current.append(result[5])
                    expected = value
                    currentDate = datetime.date.today()
                    numOfDays = sub_renew["times"] * 365
                    if key == "SUB":
                        expected[1] = passingDateStr
                        expected[2] = "0"
                    if key == "ACTIVE":
                        # convert from valid number of days to valid until day
                        if int(expected[3]) != 0:
                            expected[2] = passingDateStr
                            expected[3] = "0"
                    if key == "PAS003":
                        if expected[0] == "Yes":
                            expected[1] = passingDateStr
                            expected[2] = "0"
                    if key == "CCKEL":
                        if expected[0] == "Yes":
                            untilDate = currentDate + timedelta(days=numOfDays)
                            expected[1] = untilDate.strftime('%m/%d/%Y')
                            expected[2] = "0"
                        
                    self.verify_IsEqual(expected, current, step, HaltOnErr=False)
                
            # close activation server web interface
            step = "Step25 - Close Activation Server Web Interface"
            self.command_Close_ActivationServer(step)
    
            
if __name__ == "__main__":
    TC0201B_Test_Mode.execute()