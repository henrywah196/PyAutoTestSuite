#-------------------------------------------------------------------------------
# File Name:     TC_Template_LG.py
# Description:   License Generator Test Case Template
#
# Author:        Henry Wang
# Created:       Aug 12, 2014
#-------------------------------------------------------------------------------
import settings
from libraries.PyAutoTestCase import *
from libraries.SLAT.LicenseGenerator import *
from libraries.SLAT.ActivationServer.ActivationServerObj import ActivationServer
from libraries.SLAT.LicenseManager import LicenseManager
from libraries.SLAT.TestData import *
import os, time, datetime
from xml.dom import minidom


class TC_Template_LG(TestCaseTemplate):
    
    def setUp(self):
        super(TC_Template_LG, self).setUp()
        self.currentTest = self.id().split('.')[-1]
        self.lg = LicenseGenerator()    # define license generator
        self.activesvr = ActivationServer()    # define activation server web interface
        self.lm = LicenseManager()
        

    def tearDown(self):
        super(TC_Template_LG, self).tearDown()
        self.lg.Reset()
        self.lg = None
        self.lm.Reset()
        self.lm = None
        self.command_Close_ActivationServer()
        self.activesvr = None
        
        
        
        

    
    def command_Load_License_Generator(self, mode="Testing", logHeader=None):
        #self.lg = LicenseGenerator()    # define license generator
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Load License Generator"
        success = True
        if mode == "Testing":
            self.lg.changeMode("Testing")
        else:
            mode = "RMA"
            self.lg.changeMode("RMA")
        self.lg.Launch(timeout=10)
        success = self.lg.isLaunched()
        self.verify_IsTrue(success, "%s\nVerify License Generator is loaded."%self.messageHeader, HaltOnErr=False)
        if success:
            current = self.lg.getMode()
            expected = mode
            self.verify_IsEqual(expected, current, "%s\nVerify License Generator is in '%s' mode" %(self.messageHeader, mode), HaltOnErr=False)
            if expected != current:
                success = False
                self.command_Close_License_Generator()
        return success
        
    
    def command_Close_License_Generator(self, logHeader=None):
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Close License Generator"
        success = True
        if self.lg:
            if self.lg.ErrorPopup.isLoaded():
                self.lg.ErrorPopup.Close()
                time.sleep(2)
            if self.lg.LGPopup.isLoaded():
                self.lg.LGPopup.Close()
                time.sleep(20)
            if self.lg.AALGPopup.isLoaded():
                self.lg.AALGPopup.Close()
                time.sleep(20)
            if self.lg.EmailPopup.isLoaded():
                self.lg.EmailPopup.Close()
                time.sleep(2)
            if self.lg.ContinuePopup.isLoaded():
                self.lg.ContinuePopup.click("Yes")
                time.sleep(2)
            if self.lg.Log.isLoaded():
                self.lg.Log.Close()
                time.sleep(2)
            self.lg.Close()
            time.sleep(10)
            success = self.lg.isClosed()
            #self.lg = None
        return success
    
    
    def command_Generate_License(self, setting, logHeader=None):
        serial = None
        product = setting["product"] 
        description = setting["description"]
        customer_name = setting["lg"]["customer name"]
        order_number = setting["lg"]["sales order"]
        components = setting["lg"]["components"]
        siteinfo = setting["lg"]["site info"]
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Generate License for %s (%s)"%(product, ', '.join(description))
        success = True
        self.lg.selectProduct(product)
        time.sleep(2)
        
        self.lg.input('Customer Name', customer_name)
        self.lg.input('Sales Order', order_number)
        
        for component in components:
            if type(component) == list:
                self.lg.addComponent(component[0], component[1])
                time.sleep(2)
            else:
                self.lg.addComponent(component)
                time.sleep(2)
              
        if siteinfo:
            self.lg.input("Installation Site Name", siteinfo["Site Name"])
            time.sleep(2)
            self.lg.input("Installation Partner", siteinfo["Partner"])
            time.sleep(2)
            self.lg.input("Installation Site Address", siteinfo["Site Address"])
            time.sleep(2)
                    
        self.lg.click('Generate License')
        time.sleep(30)
        
        if self.lg.AALGPopup.isLoaded():
            self.lg.AALGPopup.Close()
            time.sleep(30)
            
        result = self.lg.ErrorPopup.isLoaded()
        expected = False
        self.verify_IsEqual(expected, result, "%s\nVerify if Error popup after generating license"%self.messageHeader, HaltOnErr=False)
        if result:
            success = False
            self.lg.ErrorPopup.Close()
            time.sleep(3)
            
        if self.lg.EmailPopup.isLoaded():
            self.lg.EmailPopup.Close()
            time.sleep(3)
            
        if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
            self.lg.ContinuePopup.click('Yes')
            time.sleep(10)
                
        if success:
            self.lg.viewLogFile()
            result = self.lg.Log.isLoaded()
            self.verify_IsTrue(result, "%s\nVerify License Generator Log window is loaded"%self.messageHeader, HaltOnErr=False)
            if result:
                lastEntry = self.lg.Log.getLastEntry()
                self.lg.Log.Close()
                if lastEntry:
                    serial = lastEntry[4]
                    
        return serial
    
    
    def command_Query_License(self, product, serial, logHeader=None):
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Query License: %s '%s'"%(product, serial)
        success = True
        self.lg.input("Original Serial", serial)
        self.lg.click("Query")
        time.sleep(50)
            
        # work around for query return error
        if self.lg.ErrorPopup.isLoaded():
            self.lg.ErrorPopup.Close()
            time.sleep(10)
            self.lg.click("Query")    # query again
            time.sleep(50)
            
        expected = False
        current = self.lg.ErrorPopup.isLoaded()
        self.verify_IsEqual(expected, current, "%s\nVerify if ERROR Popup after apply query."%self.messageHeader, HaltOnErr=False)
        if current:
            success = False
            self.lg.ErrorPopup.Close()
        current = self.lg.LGPopup.isLoaded()
        self.verify_IsEqual(expected, current, "%s\nVerify if LicenseGenerator Warning Popup after apply query"%self.messageHeader, HaltOnErr=False)
        if current:
            success = False
            self.lg.LGPopup.Close()
        
        return success
    
    
    def command_Verify_Returned_Components(self, expected, logHeader=None): 
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Verify query returned components"
        success = True
        current = self.lg.getAddedComponents()
        self.verify_IsEqual(expected, current, self.messageHeader, HaltOnErr=False)
        if current != expected:
            success = False
        
        return success    # return True if the current is match with expected
    
            
    def command_Update_Components(self, listOfComponents, logHeader=None):
        """ helper method to modify returned components """
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Update returned components"
        current = self.lg.getAddedComponents()
        for component in current:
            target = component[0]
            found = False
            for item in listOfComponents:
                if item[0] == target:
                    found = True
                    break
            if not found:
                # remove it from the list
                self.lg.removeComponent(target)
                time.sleep(3)
        current = self.lg.getAddedComponents()
        for component in listOfComponents:
            target = component[0]
            found = False
            for item in current:
                if item[0] == target:
                    found = True
                    break
            if found:
                if not (listOfComponents[0][0] == target):
                    # update componet in list
                    self.lg.updateComponent(component[0], component[1])
                    time.sleep(3)
            else:
                # add it to the list
                self.lg.addComponent(component[0], component[1])
                time.sleep(3)
        
        # verify the list of components after modification
        current = self.lg.getAddedComponents()
        expected = listOfComponents
        self.verify_IsEqual(expected, current, "%s\nVerify components have been modified"%self.messageHeader, HaltOnErr=False)
        if current == expected:
            return True
        else:
            return False   
   
   
    def command_Update_License_Details(self, site, partner, address, logHeader=None):
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Update License Details"
        success = True
        try:
            self.lg.input("Installation Site Name", site)
            time.sleep(2)
            self.lg.input("Installation Partner", partner)
            time.sleep(2)
            self.lg.input("Installation Site Address", address)
            time.sleep(2)
        except:
            success = False
        return success
    
    
    def command_Upgrade_License(self, product, serial, logHeader=None): 
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Upgrade License: %s '%s'"%(product, serial)
        success = True
        self.lg.click("Upgrade License")
        time.sleep(50)
        
        # workaround for license expiry warning
        i = 0
        while i < 3:
            if self.lg.AALGPopup.isLoaded():
                break
            if self.lg.LGPopup.isLoaded():
                self.lg.LGPopup.click("Yes")
                time.sleep(50)
            i = i + 1  
        
        if self.lg.AALGPopup.isLoaded():
            self.lg.AALGPopup.Close()
            time.sleep(50)
            
        result = self.lg.ErrorPopup.isLoaded()
        expected = False
        self.verify_IsEqual(expected, result, "%s\nVerify if Error popup after apply upgrade license"%self.messageHeader, HaltOnErr=False)
        if result:
            success = False
            self.lg.ErrorPopup.Close()
            time.sleep(5)
            
        if self.lg.EmailPopup.isLoaded():
            self.lg.EmailPopup.Close()
            time.sleep(5)
            
        if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
            self.lg.ContinuePopup.click('Yes')
            time.sleep(15)
        
        return success    # return True if the current is match with expected  
    
    
    def command_Renew_Subscription(self, product, serial, subModule, ioAddOnList=None, logHeader=None): 
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Renew Subscription (%s): %s '%s'" %(subModule, product, serial)
        success = True 
        self.lg.input("Original Serial", serial)
        time.sleep(2)
        if product == "enteliWEB-Ent":    # workaround to refresh the pane
            self.lg.selectProduct("enteliWEB-Tech-Sub")
            time.sleep(2)
        self.lg.selectProduct(subModule)
        time.sleep(2)
        if product == "enteliWEB-Ent":
            for component in ioAddOnList:
                self.lg.addComponent(component[0], component[1])
                time.sleep(2)
        
        self.lg.click('Generate License')
        time.sleep(50)
        '''
        if self.lg.ErrorPopup.isLoaded():
            self.lg.ErrorPopup.Close()
            time.sleep(10)
            if self.lg.ContinuePopup.isLoaded():
                self.lg.ContinuePopup.click('Yes')
                time.sleep(15)
            self.lg.click('Generate License')
            time.sleep(30)
            '''
        
        expected = False
        current = self.lg.ErrorPopup.isLoaded()
        self.verify_IsEqual(expected, current, "%s\nVerify if ERROR Popup after apply renew subscription."%self.messageHeader, HaltOnErr=False)
        if current:
            success = False
            self.lg.ErrorPopup.Close()
            time.sleep(5)
        
        if self.lg.LGPopup.isLoaded():
            try:
                self.lg.LGPopup.click("Yes")
                time.sleep(50)
            except:    # in case no Yes button in popup
                pass
        
        current = self.lg.LGPopup.isLoaded()
        self.verify_IsEqual(expected, current, "%s\nVerify if LicenseGenerator Warning Popup after apply renew subscription"%self.messageHeader, HaltOnErr=False)
        if current:
            success = False
            self.lg.LGPopup.Close()
            time.sleep(5)
        
        if self.lg.EmailPopup.isLoaded():
            self.lg.EmailPopup.Close()
            time.sleep(15)
            
        if self.lg.ContinuePopup.isLoaded():   # verify if continue popup loaded
            self.lg.ContinuePopup.click('Yes')
            time.sleep(15)
            
        return success
    
    
    def command_Load_ActivationServer(self, logHeader=None):  
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Load Activation Server Web Interface"
        success = True 
        self.activesvr.launch()
        time.sleep(10)
        success = self.activesvr.loginPage.isLoaded()
        self.verify_IsTrue(success, "%s\nVerify login page is loaded"%self.messageHeader, HaltOnErr=False)
        if success:
            self.activesvr.loginPage.username = "Activation"
            self.activesvr.loginPage.password = "delta"
            self.activesvr.loginPage.submit()
            time.sleep(10)
            success = self.activesvr.homePage.isLoaded()
            self.verify_IsTrue(success, "%s\nVerify home page is loaded"%self.messageHeader, HaltOnErr=False)
        return success 
    
    
    def command_Close_ActivationServer(self, logHeader=None):    
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Close Activation Server Web Interface"
        self.activesvr.close()
        
        
    def command_as_Search_Key(self, serialKey, logHeader=None):
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Search License Key: %s" %serialKey
        result = self.activesvr.homePage.search(serialKey)
        self.verify_IsTrue(result, "%s\nVerify if key is found"%self.messageHeader, HaltOnErr=False)
        return result
    

    def command_as_Select_LicenseFile(self, productName, logHeader=None):
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Select License file for %s" %productName
        result = self.activesvr.homePage.selectLicFile(productName)
        self.verify_IsTrue(result, "%s\nVerify license file is selected"%self.messageHeader, HaltOnErr=False)
        result = self.activesvr.licFilePage.isLoaded()
        self.verify_IsTrue(result, "%s\nVerify license file page is opened"%self.messageHeader, HaltOnErr=False)
        return result
        
    
    
    def command_as_Edit_Module(self, moduleName, dicOfFields, logHeader=None):
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Modify module '%s' in License file" %moduleName
        success = True
        success = self.activesvr.licFilePage.selectModule(moduleName)
        if success:
            success = self.activesvr.modulePage.isLoaded()
        if success:
            for key, value in dicOfFields.iteritems():
                if key == "Valid until Day":
                    value = value.strip()
                    if len(value) > 0:
                        self.activesvr.modulePage.validUntilDay = value
                if key == "Valid number of days":
                    self.activesvr.modulePage.validNumberOfDays = value
            self.activesvr.modulePage.saveButton.click()
            time.sleep(5)
            success = self.activesvr.licFilePage.isLoaded()
        return success
    
    
    def command_Load_License_Manager(self, logHeader=None):
        #self.lm = LicenseManager()
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Load License Manager"
        self.lm.Launch(timeout=120)
        result = self.lm.isLaunched()
        self.verify_IsTrue(result, "%s\nVerify License Manager is loaded."%self.messageHeader, HaltOnErr=False)
        return result
        
    
    def command_Close_License_Manager(self, logHeader=None):
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Close License Manager"
        success = True
        if not self.lm.isClosed():
            try:
                self.lm.click('Exit')
                time.sleep(3)
                success = self.lm.isClosed()
                self.verify_IsTrue(success, "%s\nVerify License Manager is closed."%self.messageHeader)
            except:
                success = False
            #self.lm = None
        return success
            
            
    def command_lm_Active_License(self, product, serial, logHeader=None):
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "%s '%s': Active License on License Manager"%(product, serial)
            
        #obtain a list of existiing lic files before start
        self.NewLicFile = None
        licFilesBefore = self.lm.getLicFilesList()
        
        success = True
        success = self.lm.isControlEnabled('Add New')
        self.verify_IsTrue(success, "%s\nVerify 'Add New' button is enabled."%self.messageHeader, HaltOnErr=False)
        if success:
            self.lm.click('Add New')
            time.sleep(3)
            success = self.lm.AddProduct.isLoaded()
            self.verify_IsTrue(success, "%s\nVerify 'Add Product' window is popup."%self.messageHeader, HaltOnErr=False)
        
        if success:
            if "enteliWEB" in product:
                product = "enteliWEB"
                self.lm.AddProduct.select(product)
                time.sleep(2)
                success = self.lm.AddProduct.isSelected(product)
                self.verify_IsTrue(success, "%s\nVerify product '%s' has been selected on 'Add Product' window."%(self.messageHeader, product), HaltOnErr=False)
                
        if success:
            self.lm.AddProduct.click('OK')
            time.sleep(10)
            success = self.lm.AddProduct.isClosed()
            self.verify_IsTrue(success, "%s\nVerify 'Add Product' window is closed."%self.messageHeader, HaltOnErr=False)
            if success:
                success = self.lm.SerialNumberAndActivationType.isLoaded()
                self.verify_IsTrue(success, "%s\nVerify 'Serial Number and Activation type' window is popup."%self.messageHeader, HaltOnErr=False)
        
        if success:
            self.lm.SerialNumberAndActivationType.input('Serial Number', serial)
            time.sleep(2)
            self.lm.SerialNumberAndActivationType.click('Next')
            time.sleep(2)
            success = self.lm.SerialNumberAndActivationType.isClosed()
            self.verify_IsTrue(success, "%s\nVerify 'Serial Number and Activation type' window is closed."%self.messageHeader, HaltOnErr=False)
            if success:
                success = self.lm.DownloadLicense.isLoaded()
                self.verify_IsTrue(success, "%s\nVerify 'Download License' window is popup."%self.messageHeader, HaltOnErr=False)
        
        if success:
            self.lm.DownloadLicense.click('Next')
            time.sleep(50)
            success = self.lm.DownloadLicense.isClosed()
            self.verify_IsTrue(success, "%s\nVerify 'Download License' window is closed."%self.messageHeader, HaltOnErr=False)
            if success:
                success = self.lm.LicenseActivation.isLoaded()
                self.verify_IsTrue(success, "%s\nVerify 'License Activation' window is popup."%self.messageHeader, HaltOnErr=False)
        
        if success:  
            self.lm.LicenseActivation.input('Company', 'Delta Controls')
            time.sleep(2)
            self.lm.LicenseActivation.input('Site Name', 'SL')
            time.sleep(2)
            self.lm.LicenseActivation.input('First Name', 'SQA')
            time.sleep(2)
            self.lm.LicenseActivation.input('Last Name', 'Tester')
            time.sleep(2)
            self.lm.LicenseActivation.select('Country', 'Canada')
            time.sleep(2)
            self.lm.LicenseActivation.input('Email Address', 'sqatester@deltacontrols.com')
            time.sleep(2)
            self.lm.LicenseActivation.click('Next')
            time.sleep(50)
            success = self.lm.LicenseActivation.isClosed()
            self.verify_IsTrue(success, "%s\nVerify 'License Activation' window is closed."%self.messageHeader, HaltOnErr=False)
            if self.lm.VmCallHome.isLoaded():
                self.lm.VmCallHome.click("Close")
                time.sleep(20)
                success = self.lm.VmCallHome.isClosed()
    
        if success:
            success = self.lm.isLicenseListed(serial)
            self.verify_IsTrue(success, "%s\nVerify License serial '%s' is listed in license manager main window."%(self.messageHeader, serial), HaltOnErr=False)
        
        
        #obtain a list of existiing lic files after finish
        if success:
            licFilesAfter = self.lm.getLicFilesList()
            newFiles = list(set(licFilesAfter) - set(licFilesBefore))
            if len(newFiles) > 1:
                for item in newFiles:
                    if ".dcbk" not in item:
                        self.NewLicFile = item
                        break
            else:
                self.NewLicFile = newFiles[0]
                
        return success
    
    
    def command_lm_Delete_LicFile(self, logHeader=None):
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Delete license file: %s"%self.NewLicFile
        
        if self.NewLicFile is not None:
            self.lm.removeLicFile(self.NewLicFile)
            self.NewLicFile = None
    
    
    def command_lm_Transfer_License(self, product, serial, logHeader=None):
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "%s '%s': Transfer License from License Manager"%(product, serial)
        success = True
        success = self.lm.isLicenseListed(serial)
        self.verify_IsTrue(success, "%s\nVerify license serial is listed in license manager."%self.messageHeader, HaltOnErr=False)
        if success:
            self.lm.select(serial)
            time.sleep(2)
            success = self.lm.isControlEnabled('Transfer')
            self.verify_IsTrue(success, "%s\nVerify 'Transfer' button is enabled."%self.messageHeader, HaltOnErr=False)
            
        if success:
            self.lm.click('Transfer')
            time.sleep(50)
            success = self.lm.TransferLicense.isLoaded()
            self.verify_IsTrue(success, "%s\nVerify 'Transfer License' window is popup."%self.messageHeader, HaltOnErr=False)
            
        if success:
            self.lm.TransferLicense.click('Yes')
            time.sleep(30)
            success = self.lm.TransferLicense.isClosed()
            self.verify_IsTrue(success, "%s\nVerify 'Transfer License' window is closed."%self.messageHeader, HaltOnErr=False)
            
        if success:
            result = self.lm.isLicenseListed(serial)
            if result:
                success = False
            else:
                success = True
                
        return success
    
      
    def xmlPPrint(self, xmlString):
        """ pretty print the giving XML string """
        setXML = minidom.parseString(xmlString)
        setXML = setXML.toprettyxml()
        print setXML  
        
            