#-------------------------------------------------------------------------------
# Test Case:     TC02.01A - Test Mode_License Generating (TC0201A.py)
# Purpose:       The test case verify multi-SKUs product license can be generated 
#                and uploaded in license activate server.
#
# Test coverage:
#                 
#
# Author:        Henry Wang
# Created:       Aug 12, 2014
#-------------------------------------------------------------------------------
from libraries.SLAT.TC_Template_LG import *
from ddt import ddt, file_data


Products = {u'CuCube-S'         : u'301130',
            u'CuCube-M'         : u'301131',
            u'CuCube-L'         : u'301132',
            u'CuCube-XL'        : u'301133',
            u'CuCube-S-SQL'     : u'301134',
            u'CuCube-M-SQL'     : u'301135',
            u'CuCube-L-SQL'     : u'301136',
            u'CuCube-XL-SQL'    : u'301137',
            u'CuCube-S-L'       : u'301138',
            u'CuCube-M-L'       : u'301139',
            u'CuCube-L-L'       : u'301140',
            u'CuCube-XL-L'      : u'301141',
            u'CuCube-S-SQL-L'   : u'301142',
            u'CuCube-M-SQL-L'   : u'301143',
            u'CuCube-L-SQL-L'   : u'301144',
            u'CuCube-XL-SQL-L'  : u'301145',
            u'enteliBRIDGE-SDK' : u'SPECIAL',
            u'enteliBRIDGE'     : u'301051',
            u'enteliWEB-Trial'  : u'345738',
            u'enteliWEB-Tech'   : u'345715',
            u'enteliWEB-Lite'   : u'345709',
            u'enteliWEB-Exp'    : u'345710',
            u'enteliWEB-Pro'    : u'345711',
            u'enteliWEB-Ent'    : u'345713',
            u'enteliWEB-Tech-Sub'    : u'345725',
            u'enteliWEB-Lite-Sub'    : u'345836',
            u'enteliWEB-Exp-Sub'     : u'345720',
            u'enteliWEB-Pro-Sub'     : u'345719',
            u'enteliWEB-Ent-Sub'     : u'345723',
            u'enteliWEB-Tech-ExpSub' : u'345735',
            u'enteliWEB-Lite-ExpSub' : u'345841',
            u'enteliWEB-Exp-ExpSub'  : u'345730',
            u'enteliWEB-Pro-ExpSub'  : u'345731',
            u'enteliWEB-Ent-ExpSub'  : u'345733',
            u'enteliWEB-Lite-KEL-Sub' : u'345846',
            u'enteliWEB-Exp-KEL-Sub'  : u'345847',
            u'enteliWEB-Pro-KEL-Sub'  : u'345848',
            u'enteliWEB-Ent-KEL-Sub'  : u'345849',
            u'enteliWEB-Lite-KEL-ExpSub' : u'345854',
            u'enteliWEB-Exp-KEL-ExpSub'  : u'345855',
            u'enteliWEB-Pro-KEL-ExpSub'  : u'345856',
            u'enteliWEB-Ent-KEL-ExpSub'  : u'345857'}

Components = {'enteliBRIDGE'   : ['345950 - enteliBRIDGE-ModBUS-TCP',
                                  '345952 - enteliBRIDGE-N2',
                                  'INTERNAL - enteliBRIDGE-TestProto1'],
              'enteliWEB-Tech' : ['345725 - enteliWEB-Tech-Sub-AddOn',
                                  '345797 - enteliWEB-EV',
                                  'PAS-ONLY - enteliWEB-PAS-EED',
                                  'PAS-ONLY - enteliWEB-PAS-FS',
                                  'PAS-ONLY - enteliWEB-PAS-CM',
                                  'PAS-ONLY - enteliWEB-PAS-DT',
                                  'PAS-ONLY - enteliWEB-PAS-MAPI',
                                  'OBSOLETE - enteliWEB-UpgdFromExp',
                                  'OBSOLETE - enteliWEB-UpgdFromPro',
                                  'OBSOLETE - enteliWEB-UpgdFromEnt',
                                  'OBSOLETE - enteliWEB-UpgdFromTech',
                                  'OBSOLETE - enteliWEB-OldBE',
                                  'OBSOLETE - enteliWEB-OldPE'],
              'enteliWEB-Lite' : ['345836 - enteliWEB-Sub-AddOn',
                                  '345798 - enteliWEB-EV',
                                  '345806 - enteliWEB-KEE',
                                  '345811 - enteliWEB-KEL',
                                  '345846 - enteliWEB-KEL-Sub-AddOn',
                                  '345816 - enteliWEB-VM',
                                  '345820 - enteliWEB-API',
                                  'PAS-ONLY - enteliWEB-PAS-EED',
                                  'PAS-ONLY - enteliWEB-PAS-FS',
                                  'PAS-ONLY - enteliWEB-PAS-CM',
                                  'PAS-ONLY - enteliWEB-PAS-DT',
                                  'PAS-ONLY - enteliWEB-PAS-MAPI',
                                  'OBSOLETE - enteliWEB-UpgdFromExp',
                                  'OBSOLETE - enteliWEB-UpgdFromPro',
                                  'OBSOLETE - enteliWEB-UpgdFromEnt',
                                  'OBSOLETE - enteliWEB-UpgdFromTech',
                                  'OBSOLETE - enteliWEB-OldBE',
                                  'OBSOLETE - enteliWEB-OldPE'],
              'enteliWEB-Exp'  : ['345720 - enteliWEB-Sub-AddOn',
                                  '345799 - enteliWEB-EV',
                                  '345807 - enteliWEB-KEE',
                                  '345812 - enteliWEB-KEL',
                                  '345847 - enteliWEB-KEL-Sub-AddOn',
                                  '345817 - enteliWEB-VM',
                                  '345821 - enteliWEB-API',
                                  'PAS-ONLY - enteliWEB-PAS-EED',
                                  'PAS-ONLY - enteliWEB-PAS-FS',
                                  'PAS-ONLY - enteliWEB-PAS-CM',
                                  'PAS-ONLY - enteliWEB-PAS-DT',
                                  'PAS-ONLY - enteliWEB-PAS-MAPI',
                                  'OBSOLETE - enteliWEB-UpgdFromExp',
                                  'OBSOLETE - enteliWEB-UpgdFromPro',
                                  'OBSOLETE - enteliWEB-UpgdFromEnt',
                                  'OBSOLETE - enteliWEB-UpgdFromTech',
                                  'OBSOLETE - enteliWEB-OldBE',
                                  'OBSOLETE - enteliWEB-OldPE'],
              'enteliWEB-Pro'  : ['345719 - enteliWEB-Sub-AddOn',
                                  '345800 - enteliWEB-EV',
                                  '345808 - enteliWEB-KEE',
                                  '345813 - enteliWEB-KEL',
                                  '345848 - enteliWEB-KEL-Sub-AddOn',
                                  '345818 - enteliWEB-VM',
                                  '345822 - enteliWEB-API',
                                  'PAS-ONLY - enteliWEB-PAS-EED',
                                  'PAS-ONLY - enteliWEB-PAS-FS',
                                  'PAS-ONLY - enteliWEB-PAS-CM',
                                  'PAS-ONLY - enteliWEB-PAS-DT',
                                  'PAS-ONLY - enteliWEB-PAS-MAPI',
                                  'OBSOLETE - enteliWEB-UpgdFromExp',
                                  'OBSOLETE - enteliWEB-UpgdFromPro',
                                  'OBSOLETE - enteliWEB-UpgdFromEnt',
                                  'OBSOLETE - enteliWEB-UpgdFromTech',
                                  'OBSOLETE - enteliWEB-OldBE',
                                  'OBSOLETE - enteliWEB-OldPE'],
              'enteliWEB-Ent'  : ['345827 - enteliWEB-Ent-100000IO-AddOn',
                                  '345826 - enteliWEB-Ent-50000IO-AddOn',
                                  '345825 - enteliWEB-Ent-25000IO-AddOn',
                                  '345796 - enteliWEB-Ent-2500IO-AddOn',
                                  '345723 - enteliWEB-Sub-AddOn',
                                  '345801 - enteliWEB-EV',
                                  '345809 - enteliWEB-KEE',
                                  '345814 - enteliWEB-KEL',
                                  '345849 - enteliWEB-KEL-Sub-AddOn',
                                  '345819 - enteliWEB-VM',
                                  '345823 - enteliWEB-API',
                                  'PAS-ONLY - enteliWEB-PAS-EED',
                                  'PAS-ONLY - enteliWEB-PAS-FS',
                                  'PAS-ONLY - enteliWEB-PAS-CM',
                                  'PAS-ONLY - enteliWEB-PAS-DT',
                                  'PAS-ONLY - enteliWEB-PAS-MAPI',
                                  'OBSOLETE - enteliWEB-UpgdFromExp',
                                  'OBSOLETE - enteliWEB-UpgdFromPro',
                                  'OBSOLETE - enteliWEB-UpgdFromEnt',
                                  'OBSOLETE - enteliWEB-UpgdFromTech',
                                  'OBSOLETE - enteliWEB-OldBE',
                                  'OBSOLETE - enteliWEB-OldPE']}


@ddt
class TC0201A_Test_Mode(TC_Template_LG):
    
    def setUp(self):
        super(TC0201A_Test_Mode, self).setUp()
        print "\nTest: %s" %self.currentTest
        
        # setup for test03_Verify_Eng_Component 
        if self.currentTest == 'test03':
            self.put = "enteliWEB-Ent"    # product under test
            self.components_kee = [ ['enteliWEB-Ent', ''], ['enteliWEB-KEE', ''] ]
            self.components_kel = [ ['enteliWEB-Ent', ''], ['enteliWEB-KEL', ''] ]
        
        # setup for test04_Verify_VM_Component    
        if self.currentTest == 'test04':
            self.put = "enteliWEB-Pro"
            self.components_vm =  [ ['enteliWEB-Pro', ''], ['enteliWEB-VM', ''] ]
            self.customer_name = "SQA Test"
            self.order_number = "123456789"  
            
        if self.currentTest == 'test05':
            self.put = "enteliWEB-Tech"
            self.customer_name = "SQA Test"
            self.order_number = "123456789"
            
        if self.currentTest == 'test06':
            self.put = {
                         "type"        : "enteliWEB_V2",
                         "product"     : "enteliWEB-Ent",
                         "description" : None,
                         "lg"          : { 
                                           "customer name"    : "SQA Test",
                                           "sales order"      : "123456789",
                                           "components"       : [ 
                                                                  ["enteliWEB-Ent-100000IO-AddOn", "2"], 
                                                                  ["enteliWEB-Ent-50000IO-AddOn", "1"], 
                                                                  ["enteliWEB-Ent-25000IO-AddOn", "1"], 
                                                                  ["enteliWEB-Ent-2500IO-AddOn", "8"], 
                                                                  "enteliWEB-EV", "enteliWEB-KEE", 
                                                                  "enteliWEB-VM", "enteliWEB-API", 
                                                                  ["enteliWEB-PAS-FS", "500"], 
                                                                  "enteliWEB-PAS-CM", 
                                                                  "enteliWEB-PAS-DT", 
                                                                  "enteliWEB-PAS-MAPI" 
                                                                ],
                                           "site info"        : { 
                                                                  "Site Name" : "Good Site", 
                                                                  "Partner" : "Smart Partner", 
                                                                  "Site Address" : "Super Address" 
                                                                }
                                         }
                       }
            
        #if self.currentTest == 'test07':
        #    json_file_location = os.path.abspath(os.path.join(os.path.dirname(__file__), "TC0201A.json"))
        #    self.testData = TestData(json_file_location) 
     
    
    def tearDown(self):
        super(TC0201A_Test_Mode, self).tearDown()
        #if self.currentTest == 'test05':
        #    self.testData.saveData()

        
    #@unittest.skip("")
    def test01(self):
        ''' Examine product list'''
        
        # Load License Generator
        step = "Step01 - Load License Generator"
        success = self.command_Load_License_Generator("Testing", step)
        
        if success:
            step = "Step02 - Verify product list in license generator"
            current = self.lg.getProductList()
            expected = Products
            self.verify_IsEqual(expected, current, step)
        
        
    #@unittest.skip("")    
    def test02(self):
        ''' Examine available components for multi-SKU license '''
        
        # Load License Generator
        step = "Step01 - Load License Generator"
        success = self.command_Load_License_Generator("Testing", step)
        
        if success:
            step = "Step02 - Verify available components"
            for key, value in Components.iteritems():
                self.lg.selectProduct(key)    # select product item
                expected = value
                current = self.lg.getDropdownList('Components DropDown')
                self.verify_IsEqual(expected, current, "%s for '%s'" %(step, key), HaltOnErr=False)
       
        
    #@unittest.skip("")    
    def test03(self):
        ''' Examine add KEE and KEL modules together is not allowed '''
        
        # Load License Generator
        step = "Step01 - Load License Generator"
        success = self.command_Load_License_Generator("Testing", step)
        
        if success:
            self.lg.selectProduct(self.put)    # select product under test
            component1 = 'enteliWEB-KEE'
            component2 = 'enteliWEB-KEL'
            self.lg.addComponent(component1)
            current = self.lg.getAddedComponents()
            expected = self.components_kee
            self.verify_IsEqual(expected, current, "Step02 - verify added components after add '%s'" %component1, HaltOnErr=False)
        
            self.lg.addComponent(component2)
            result = self.lg.LGPopup.isLoaded()    # verify if the alert is popup
            self.verify_IsTrue(result, "Step03 - Verify warning popup when try to add '%s' if '%s' already existing." %(component2, component1))
            self.lg.LGPopup.click('Yes')
            result = self.lg.LGPopup.isClosed()    # verify if the alert popup closed
            self.verify_IsTrue(result, "Step04 - Verify warning popup closed after click Yes button")
            current = self.lg.getAddedComponents()
            expected = self.components_kel
            self.verify_IsEqual(expected, current, "Step05 - verify added components after change from '%s' to '%s'" %(component1, component2), HaltOnErr=False)
        
            self.lg.addComponent(component1)
            result = self.lg.LGPopup.isLoaded()    # verify if the alert is popup
            self.verify_IsTrue(result, "Step06 - Verify warning popup when try to add '%s' if '%s' already existing." %(component1, component2))
            self.lg.LGPopup.click('Yes')
            result = self.lg.LGPopup.isClosed()    # verify if the alert popup closed
            self.verify_IsTrue(result, "Step07 - Verify warning popup closed after click Yes button")
            current = self.lg.getAddedComponents()
            expected = self.components_kee
            self.verify_IsEqual(expected, current, "Step08 - verify added components after change from '%s' to '%s'" %(component2, component1), HaltOnErr=False)
        
        
    #@unittest.skip("")    
    def test04(self):
        ''' Examine License Details are required if VM is enabled '''
        
        # Load License Generator
        step = "Step01 - Load License Generator"
        success = self.command_Load_License_Generator("Testing", step)
        
        if success:
            step = "Step02 - Obtain the latest license serial from log file"
            self.lg.viewLogFile()
            result = self.lg.Log.isLoaded()
            self.verify_IsTrue(result, "%s\nVerify License Generator Log window is loaded"%step)
            lastEntry_Before_Test = self.lg.Log.getLastEntry()
            self.lg.Log.Close()
        
            step = "Step03 - try generate license with VM enabled but without license details info"
            self.lg.selectProduct(self.put)    # select product under test
            self.lg.addComponent('enteliWEB-VM')
            current = self.lg.getAddedComponents()
            expected = self.components_vm
            self.verify_IsEqual(expected, current, "%s\nVerify added components after add '%s'" %(step, 'enteliWEB-VM'))
            self.lg.input('Customer Name', self.customer_name)
            self.lg.input('Sales Order', self.order_number)
            self.lg.click('Generate License')    # try generate license
            time.sleep(3)
            result = self.lg.LGPopup.isLoaded()    # verify if the alert is popup
            self.verify_IsTrue(result, "%s\nVerify warning popup when add VM module without license details information"%step)
            if result:
                self.lg.LGPopup.click('OK')
            result = self.lg.LGPopup.isClosed()
            self.verify_IsTrue(result, "%s\nVerify warning popup closed after click OK button"%step)
            if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
                self.lg.ContinuePopup.click('Yes')
                time.sleep(3)
        
            step = "Step04 - verify no new license serial generated"
            self.lg.viewLogFile()
            result = self.lg.Log.isLoaded()
            self.verify_IsTrue(result, "%s\nVerify License Generator Log window is loaded"%step)
            lastEntry_After_Test = self.lg.Log.getLastEntry()
            self.verify_IsEqual(lastEntry_Before_Test, lastEntry_After_Test, "%s\nVerify no new license serial is generated"%step)
            self.lg.Log.Close()
        
            step = "Step05 - verify new license is generated after license details is provided"
            self.lg.input('Installation Site Name', "Testing site")
            self.lg.input('Installation Partner', "Name of Partner")
            self.lg.input('Installation Site Address', "Site Address")
            self.lg.click('Generate License')
            time.sleep(15)
            if self.lg.AALGPopup.isLoaded():
                self.lg.AALGPopup.Close()
                time.sleep(30)
            if self.lg.EmailPopup.isLoaded():
                self.lg.EmailPopup.Close()
                time.sleep(5)
            if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
                self.lg.ContinuePopup.click('Yes')
        
            self.lg.viewLogFile()
            result = self.lg.Log.isLoaded()
            self.verify_IsTrue(result, "%s\nVerify License Generator Log window is loaded"%step)
            lastEntry_After_Test = self.lg.Log.getLastEntry()
            self.lg.Log.Close()
            result = (lastEntry_Before_Test != lastEntry_After_Test)
            self.verify_IsTrue(result, "%s\nVerify new entry is added to License Generator Log"%step)
    
    
    #@unittest.skip("")
    def test05(self):
        ''' Examine Customer Name and Sales Order fields are required fields'''
        # Load License Generator
        step = "Step01 - Load License Generator"
        success = self.command_Load_License_Generator("Testing", step)
        
        if success:
            step = "Step02 - Obtain the latest license serial from log file"
            self.lg.viewLogFile()
            result = self.lg.Log.isLoaded()
            self.verify_IsTrue(result, "%s\nVerify License Generator Log window is loaded"%step)
            lastEntry_Before_Test = self.lg.Log.getLastEntry()
            self.lg.Log.Close()
            
            step = "Step03 - Verify error pop up if no input for General Info"
            self.lg.selectProduct(self.put)    # select product under test
            self.lg.click('Generate License')    # try generate license
            time.sleep(3)
            result = self.lg.LGPopup.isLoaded()    # verify if the alert is popup
            self.verify_IsTrue(result, "%s\nVerify warning popup when generate license with no input for Customer name"%step)
            if result:
                self.lg.LGPopup.click('OK')
            
            self.lg.input('Customer Name', self.customer_name)
            self.lg.click('Generate License')    # try generate license
            time.sleep(3)
            result = self.lg.LGPopup.isLoaded()    # verify if the alert is popup
            self.verify_IsTrue(result, "%s\nVerify warning popup when generate license with no input for sales order"%step)
            if result:
                self.lg.LGPopup.click('OK')
                
            step = "Step04 - verify no new license serial generated"
            self.lg.viewLogFile()
            result = self.lg.Log.isLoaded()
            self.verify_IsTrue(result, "%s\nVerify License Generator Log window is loaded"%step)
            lastEntry_After_Test = self.lg.Log.getLastEntry()
            self.verify_IsEqual(lastEntry_Before_Test, lastEntry_After_Test, "%s\nVerify no new license serial is generated"%step)
            self.lg.Log.Close()
            
            step = "Step05 - verify new license is generated after  General Info is provided"
            self.lg.input('Customer Name', self.customer_name)
            self.lg.input('Sales Order', self.order_number)
            self.lg.click('Generate License')
            time.sleep(15)
            if self.lg.AALGPopup.isLoaded():
                self.lg.AALGPopup.Close()
                time.sleep(30)
            if self.lg.EmailPopup.isLoaded():
                self.lg.EmailPopup.Close()
                time.sleep(5)
            if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
                self.lg.ContinuePopup.click('Yes')
        
            self.lg.viewLogFile()
            result = self.lg.Log.isLoaded()
            self.verify_IsTrue(result, "%s\nVerify License Generator Log window is loaded"%step)
            lastEntry_After_Test = self.lg.Log.getLastEntry()
            self.lg.Log.Close()
            result = (lastEntry_Before_Test != lastEntry_After_Test)
            self.verify_IsTrue(result, "%s\nVerify new entry is added to License Generator Log"%step)
            
    
    #@unittest.skip("")
    def test06(self):
        ''' Examine the functionality of Clear All button'''
        
        test_data = self.put
        
        # Load License Generator
        step = "Step01 - Load License Generator"
        success = self.command_Load_License_Generator("Testing", step)
        
        if success:
            step = "Step02 - Generate License"
            serial = self.command_Generate_License(test_data, step) 
            
        if serial:
            step = "Step03 - Verify the functionality of Clear All button"
            self.lg.click('Clear All')
            time.sleep(3)
            
            expected = ""
            current = self.lg.getValue('Customer Name')
            self.verify_IsEqual(expected, current, "%s\nVerify configuration field '%s' is clear after click Clear All button"%(step, 'Customer Name'))
            current = self.lg.getValue('Sales Order')
            self.verify_IsEqual(expected, current, "%s\nVerify configuration field '%s' is clear after click Clear All button"%(step, 'Sales Order'))
            current = self.lg.getValue('Installation Site Name')
            self.verify_IsEqual(expected, current, "%s\nVerify configuration field '%s' is clear after click Clear All button"%(step, 'Installation Site Name'))
            current = self.lg.getValue('Installation Partner')
            self.verify_IsEqual(expected, current, "%s\nVerify configuration field '%s' is clear after click Clear All button"%(step, 'Installation Partner'))
            current = self.lg.getValue('Installation Site Address')
            self.verify_IsEqual(expected, current, "%s\nVerify configuration field '%s' is clear after click Clear All button"%(step, 'Installation Site Address'))
            
            expected = test_data["product"] 
            current = (self.lg.getAddedComponents())[0][0]
            self.verify_IsEqual(expected, current, "%s\nVerify AddOn components are clear after click Clear All button"%step)
            
    
    #@unittest.skip("") 
    @file_data('TC0201A.json')   
    def test07_Generate_License(self, test_data):
        ''' Examine generate client software license '''
        
        # generate license
        product = test_data["product"] 
        description = test_data["description"]
        serial = None
        components = test_data["lg"]["components"]
        query_components = test_data["lg"]["query components"]
        siteinfo = test_data["lg"]["site info"]
        success = True
            
        # Load License Generator
        step = "Step01 - Load License Generator"
        success = self.command_Load_License_Generator("Testing", step)
            
        if success:
            
            self.lg.selectProduct("enteliWEB-Tech-Sub")    # this is a work around to refresh selection
            time.sleep(3)
            
            logHeader = "Step02 - Generate License for %s (%s)\n"%(product, ', '.join(description))
            serial = self.command_Generate_License(test_data, logHeader)
                
        if serial:
            test_data["serial"] = serial
            
        step =  "Step03 - Examine the new generated license by query its serial"
        if serial:
            self.lg.selectProduct("enteliWEB-Tech-Sub")    # this is a work around to refresh selection
            time.sleep(3)
                    
            success = self.command_Query_License(product, serial, step)
                   
        if success:
            step = "step04 - Examine query returned components"
            result = self.lg.getAddedComponents()
            expected = []
            expected.append([product, ""])
            expected.extend(query_components)
            current = result
            self.verify_IsEqual(expected, current, "%s\nQuery '%s'" %(step, test_data["serial"]), HaltOnErr=False)
                    
                
        step = "Step05 - Close license generator"
        self.command_Close_License_Generator(step)
                

if __name__ == "__main__":
    TC0201A_Test_Mode.execute()