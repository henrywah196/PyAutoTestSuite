#-------------------------------------------------------------------------------
# Test Case:     TC01.04 - LicGen Webservice for  renew Subscription (TC0104.py)
# Purpose:       The test case verify renew / extend license subscription using 
#                licGen Web Services.
#
# Author:        Henry Wang
# Created:       July 29, 2015
#-------------------------------------------------------------------------------
from libraries.SLAT.TC_Template_LG import *
import datetime
from datetime import timedelta
from ddt import ddt, data
import requests
from xml.etree import ElementTree


json_file_location = os.path.abspath(os.path.join(os.path.dirname(__file__), "TC0104.json"))
TestData = TestData(json_file_location)

@ddt
class TC0104_Renew_License(TC_Template_LG):
    
    def setUp(self):
        super(TC0104_Renew_License, self).setUp()
        print "\nTest: %s" %self.currentTest
        self.test_data = None
        
        self.Base_URL = "http://192.168.50.99/cgi-bin/WSLicGen.exe/license"
        self.payload = {'Serial' : None}
        self.setHeaders = {'Accept' : 'text/xml',
                           'Content-length' : None}
        self.r = None
        
        
    @unittest.skip("")
    @data(*TestData.getData("test01"))
    def test01_Extend_Sub(self, testData):
        #Extend subscription when generating a license
        self.test_data = testData
        self.setSalesOrder()
        self._testMethodDoc = "Extend subscription when generating a license for %s(%s)"%(self.test_data["product"][1], self.test_data["lg"]["sales order"])
        
        ##################
        # Generate license
        ##################
        setXML = self.setXML()    # format XML string using test_data
        
        # debugging: print setXML
        print "XML for generate new license request:"
        self.xmlPPrint(setXML)
        
        # send web service request
        self.setHeaders["Content-length"] = len(setXML)
        self.r = requests.post(self.Base_URL, data=setXML, headers=self.setHeaders)
        
        step="Verify web service call success"
        expected = 200
        current = self.r.status_code
        print "HTTP code returned: %s"%current
        self.verify_IsEqual(expected, current, step)
        
        step = "Verify returned XML string is well formed"
        result = self.r.text
        print "XML for generate new license respond:"
        print result
        self.verify_XML_IsWellFormed(result, step)
        
        step = "Obtain license serial from returned xml string"
        #print(self.r.url)
        #print (self.r.text)
        element = ElementTree.fromstring(self.r.text)
        element = element.find("LicenseSerial")
        element = element.find("SerialNumber")
        #print ("Licenser Serial: %s"%element.text)
        self.test_data["serial"] = element.text
        
        ###############
        # query license
        ###############
        step = "query license serial"
        self.payload["Serial"] = self.test_data["serial"]
        self.r = requests.get(self.Base_URL, params=self.payload)
        
        step="Verify service query call success"
        expected = 200
        current = self.r.status_code
        self.verify_IsEqual(expected, current, step)
        
        #############################
        # verify Active / Sub modules
        #############################
        step = "Verify license subscription from returned XML string"       
        self.helper_VerifyExpiry(step, self.test_data, flag="test01")
            
            
    @unittest.skip("")
    @data(*TestData.getData("test02"))
    def test02_Renew_Sub_Inactivated(self, testData):
        #Renew subscription on inactivated license
        self.test_data = testData
        self.setSalesOrder()
        self._testMethodDoc = "Renew subscription on inactivated license for %s(%s)"%(self.test_data["product"][1], self.test_data["lg"]["sales order"])
        
        ##################
        # Generate license
        ##################
        setXML = self.setXML()    # format XML string using test_data
        
        # debugging: print setXML
        print "XML for generate new license request:"
        self.xmlPPrint(setXML)
        
        # send web service request
        self.setHeaders["Content-length"] = len(setXML)
        self.r = requests.post(self.Base_URL, data=setXML, headers=self.setHeaders)
        
        step="Generate License: Verify web service call success"
        expected = 200
        current = self.r.status_code
        print "HTTP code returned: %s"%current
        self.verify_IsEqual(expected, current, step)
        
        step = "Generate License: Verify returned XML string is well formed"
        result = self.r.text
        print "XML for generate new license respond:"
        print result
        self.verify_XML_IsWellFormed(result, step)
        
        step = "Generate License: Obtain license serial from returned xml string"
        #print(self.r.url)
        #print (self.r.text)
        element = ElementTree.fromstring(self.r.text)
        element = element.find("LicenseSerial")
        element = element.find("SerialNumber")
        #print ("Licenser Serial: %s"%element.text)
        self.test_data["serial"] = element.text
        
        #########################################################
        # Verify warning popup when renew sub using ExpSub module
        #########################################################
        #self.subTest_IncorrectSubModule("ExpRenew License")
        
        ################################################################### 
        # Verify warning popup when renew sub using module of wrong edition
        ###################################################################
        
        ####################
        # renew subscription
        ####################
        setXML = self.setXML(flag="Renew License")
        
        print "XML for renew license request:"
        self.xmlPPrint(setXML)
        
        # send web service request
        self.setHeaders["Content-length"] = len(setXML)
        i = 0
        while i < self.test_data["sub renew"]["times"]: 
            self.r = requests.put(self.Base_URL, data=setXML, headers=self.setHeaders)
        
            step="Verify web service call success"
            expected = 200
            current = self.r.status_code
            print "HTTP code returned: %s"%current
            self.verify_IsEqual(expected, current, step)
            i = i + 1
        
        ###############
        # query license
        ###############
        step = "query license serial"
        self.payload["Serial"] = self.test_data["serial"]
        self.r = requests.get(self.Base_URL, params=self.payload)
        
        step="Verify service query call success"
        expected = 200
        current = self.r.status_code
        self.verify_IsEqual(expected, current, step)
        
        #############################
        # verify Active / Sub modules
        #############################
        step = "Verify license subscription from returned XML string"       
        self.helper_VerifyExpiry(step, self.test_data, flag="test02")          


    @unittest.skip("")
    @data(*TestData.getData("test03"))
    def test03_Renew_Sub_Activated(self, testData):
        # Renew subscription on activated (not expired) license
        self.test_data = testData
        self.setSalesOrder()
        self._testMethodDoc = "Renew subscription on activated not expired license for %s(%s)"%(self.test_data["product"][1], self.test_data["lg"]["sales order"])
            
        ##################
        # Generate license
        ##################
        setXML = self.setXML()    # format XML string using test_data
        
        # debugging: print setXML
        print "XML for generate new license request:"
        self.xmlPPrint(setXML)
        
        # send web service request
        self.setHeaders["Content-length"] = len(setXML)
        self.r = requests.post(self.Base_URL, data=setXML, headers=self.setHeaders)
        
        step="Generate License: Verify web service call success"
        expected = 200
        current = self.r.status_code
        print "HTTP code returned: %s"%current
        self.verify_IsEqual(expected, current, step)
        
        step = "Generate License: Verify returned XML string is well formed"
        result = self.r.text
        print "XML for generate new license respond:"
        print result
        self.verify_XML_IsWellFormed(result, step)
        
        # Obtain license serial from returned xml string"
        element = ElementTree.fromstring(self.r.text)
        element = element.find("LicenseSerial")
        element = element.find("SerialNumber")
        self.test_data["serial"] = element.text
        
        ###################################
        # active license on license manager
        ###################################
        step = "Load License Manager"
        success = self.command_Load_License_Manager(step)
        
        if success:    # active license
            step = "Active license: %s %s" %(self.test_data["product"][1], self.test_data["serial"])
            success = self.command_lm_Active_License(self.test_data["product"][1], self.test_data["serial"], step)
            
        step = "Close License Manager"
        self.command_Close_License_Manager(step)
        
        if success:    # delete new lic file
            step = "Delete Lic File for %s %s"%(self.test_data["product"][1], self.test_data["serial"])
            self.command_lm_Delete_LicFile(step)
        
        ####################
        # renew subscription
        ####################
        setXML = self.setXML(flag="Renew License")
        
        print "XML for renew license request:"
        self.xmlPPrint(setXML)
        
        # send web service request
        self.setHeaders["Content-length"] = len(setXML)
        i = 0
        while i < self.test_data["sub renew"]["times"]: 
            self.r = requests.put(self.Base_URL, data=setXML, headers=self.setHeaders)
        
            step="Renew subscription: Verify web service call success"
            expected = 200
            current = self.r.status_code
            print "Renew subscription: HTTP %s returned"%current
            self.verify_IsEqual(expected, current, step)
            i = i + 1
        
        ###############
        # query license
        ###############
        self.payload["Serial"] = self.test_data["serial"]
        self.r = requests.get(self.Base_URL, params=self.payload)
        
        step="Verify service query call success"
        expected = 200
        current = self.r.status_code
        self.verify_IsEqual(expected, current, step)
        
        #############################
        # verify Active / Sub modules
        #############################
        step = "Verify license subscription from returned XML string"       
        self.helper_VerifyExpiry(step, self.test_data, flag="test03")     


    @unittest.skip("")
    @data(*TestData.getData("test04"))
    def test04_Renew_Sub_OneYearLess(self, testData):
        # Renew subscription on expired less than one year license
        self.test_data = testData
        self.setSalesOrder()
        self._testMethodDoc = "Renew subscription on expired less than one year license for %s(%s)"%(self.test_data["product"][1], self.test_data["lg"]["sales order"])
        
        ##################
        # Generate license
        ##################
        setXML = self.setXML()    # format XML string using test_data
        
        # debugging: print setXML
        print "XML for generate new license request:"
        self.xmlPPrint(setXML)
        
        # send web service request
        self.setHeaders["Content-length"] = len(setXML)
        self.r = requests.post(self.Base_URL, data=setXML, headers=self.setHeaders)
        
        step="Generate License: Verify web service call success"
        expected = 200
        current = self.r.status_code
        print "HTTP code returned: %s"%current
        self.verify_IsEqual(expected, current, step)
        
        step = "Generate License: Verify returned XML string is well formed"
        result = self.r.text
        print "XML for generate new license respond:"
        print result
        self.verify_XML_IsWellFormed(result, step)
        
        # Obtain license serial from returned xml string"
        element = ElementTree.fromstring(self.r.text)
        element = element.find("LicenseSerial")
        element = element.find("SerialNumber")
        self.test_data["serial"] = element.text
        
        ###################################
        # active license on license manager
        ###################################
        step = "Load License Manager"
        success = self.command_Load_License_Manager(step)
        
        if success:    # active license
            step = "Active license: %s %s" %(self.test_data["product"][1], self.test_data["serial"])
            success = self.command_lm_Active_License(self.test_data["product"][1], self.test_data["serial"], step)
            
        step = "Close License Manager"
        self.command_Close_License_Manager(step)
        
        if success:    # delete new lic file
            step = "Delete Lic File for %s %s"%(self.test_data["product"][1], self.test_data["serial"])
            self.command_lm_Delete_LicFile(step)
            
        ###################################################################
        # modify license by give an expire date which is less than one year
        ###################################################################
        productType = self.test_data["type"]
        serial = self.test_data["serial"]
        modules = self.test_data["as"]["Modules"]
        
        passing_days = self.test_data["sub renew"]["passing days"]
        today = datetime.date.today()
        self.passingDate = today - timedelta(days=passing_days)
        passingDateStr = self.passingDate.strftime('%m/%d/%Y')
        
        if success:
            step = "Load Activation Server Web Interface"
            success = self.command_Load_ActivationServer(step)
            
        # search license key
        if success:
            step = "Search license key %s in Activation Server"%serial
            success = self.command_as_Search_Key(serial, step)
            
        # open license file
        if success:
            step = "Select license file in Activation Server"
            success = self.command_as_Select_LicenseFile(productType, step)
                
        if success:
            for key, value in modules.iteritems():
                step = "Modify license module in Activation Server"
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
                            
        # close activation server web interface
        step = "Close Activation Server Web Interface"
        self.command_Close_ActivationServer(step)  
        
        #########################################################
        # Verify warning popup when renew sub using ExpSub module
        #########################################################
        #self.subTest_IncorrectSubModule("ExpRenew License")
        
        ####################
        # renew subscription
        ####################
        setXML = self.setXML(flag="Renew License")
        
        print "XML for renew license request:"
        self.xmlPPrint(setXML)
        
        # send web service request
        self.setHeaders["Content-length"] = len(setXML)
        i = 0
        while i < self.test_data["sub renew"]["times"]: 
            self.r = requests.put(self.Base_URL, data=setXML, headers=self.setHeaders)
        
            step="Renew subscription: Verify web service call success"
            expected = 200
            current = self.r.status_code
            print "Renew subscription: HTTP %s returned"%current
            self.verify_IsEqual(expected, current, step)
            i = i + 1
            
        ###############
        # query license
        ###############
        self.payload["Serial"] = self.test_data["serial"]
        self.r = requests.get(self.Base_URL, params=self.payload)
        
        step="Verify service query call success"
        expected = 200
        current = self.r.status_code
        self.verify_IsEqual(expected, current, step)
        
        #############################
        # verify Active / Sub modules
        #############################
        step = "Verify license subscription from returned XML string"       
        self.helper_VerifyExpiry(step, self.test_data, flag="test04") 


    #@unittest.skip("")
    @data(*TestData.getData("test05"))
    def test05_Renew_Sub_OneYearMore(self, testData):
        # Renew subscription on expired more than one year license
        self.test_data = testData
        self.setSalesOrder()
        self._testMethodDoc = "Renew subscription on expired less than one year license for %s(%s)"%(self.test_data["product"][1], self.test_data["lg"]["sales order"])
        
        ##################
        # Generate license
        ##################
        setXML = self.setXML()    # format XML string using test_data
        
        # debugging: print setXML
        print "XML for generate new license request:"
        self.xmlPPrint(setXML)
        
        # send web service request
        self.setHeaders["Content-length"] = len(setXML)
        self.r = requests.post(self.Base_URL, data=setXML, headers=self.setHeaders)
        
        step="Generate License: Verify web service call success"
        expected = 200
        current = self.r.status_code
        print "HTTP code returned: %s"%current
        self.verify_IsEqual(expected, current, step)
        
        step = "Generate License: Verify returned XML string is well formed"
        result = self.r.text
        print "XML for generate new license respond:"
        print result
        self.verify_XML_IsWellFormed(result, step)
        
        # Obtain license serial from returned xml string"
        element = ElementTree.fromstring(self.r.text)
        element = element.find("LicenseSerial")
        element = element.find("SerialNumber")
        self.test_data["serial"] = element.text
        
        ###################################
        # active license on license manager
        ###################################
        step = "Load License Manager"
        success = self.command_Load_License_Manager(step)
        
        if success:    # active license
            step = "Active license: %s %s" %(self.test_data["product"][1], self.test_data["serial"])
            success = self.command_lm_Active_License(self.test_data["product"][1], self.test_data["serial"], step)
            
        step = "Close License Manager"
        self.command_Close_License_Manager(step)
        
        if success:    # delete new lic file
            step = "Delete Lic File for %s %s"%(self.test_data["product"][1], self.test_data["serial"])
            self.command_lm_Delete_LicFile(step)
            
        ###################################################################
        # modify license by give an expire date which is less than one year
        ###################################################################
        productType = self.test_data["type"]
        serial = self.test_data["serial"]
        modules = self.test_data["as"]["Modules"]
        
        passing_days = self.test_data["sub renew"]["passing days"]
        today = datetime.date.today()
        self.passingDate = today - timedelta(days=passing_days)
        passingDateStr = self.passingDate.strftime('%m/%d/%Y')
        
        if success:
            step = "Load Activation Server Web Interface"
            success = self.command_Load_ActivationServer(step)
            
        # search license key
        if success:
            step = "Search license key %s in Activation Server"%serial
            success = self.command_as_Search_Key(serial, step)
            
        # open license file
        if success:
            step = "Select license file in Activation Server"
            success = self.command_as_Select_LicenseFile(productType, step)
                
        if success:
            for key, value in modules.iteritems():
                step = "Modify license module in Activation Server"
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
                            
        # close activation server web interface
        step = "Close Activation Server Web Interface"
        self.command_Close_ActivationServer(step)  
        
        #########################################################
        # Verify warning popup when renew sub using Sub module
        #########################################################
        #self.subTest_IncorrectSubModule("Renew License")
        
        ####################
        # renew subscription
        ####################
        setXML = self.setXML(flag="ExpRenew License")
        
        print "XML for renew license request:"
        self.xmlPPrint(setXML)
        
        # send web service request
        self.setHeaders["Content-length"] = len(setXML)
        i = 0
        while i < self.test_data["sub renew"]["times"]: 
            self.r = requests.put(self.Base_URL, data=setXML, headers=self.setHeaders)
        
            step="Renew subscription: Verify web service call success"
            expected = 200
            current = self.r.status_code
            print "Renew subscription: HTTP %s returned"%current
            self.verify_IsEqual(expected, current, step)
            i = i + 1
            
        ###############
        # query license
        ###############
        self.payload["Serial"] = self.test_data["serial"]
        self.r = requests.get(self.Base_URL, params=self.payload)
        
        step="Verify service query call success"
        expected = 200
        current = self.r.status_code
        self.verify_IsEqual(expected, current, step)
        
        #############################
        # verify Active / Sub modules
        #############################
        step = "Verify license subscription from returned XML string"       
        self.helper_VerifyExpiry(step, self.test_data, flag="test05") 
    
    
    def subTest_IncorrectSubModule(self, renewFlag):
        """ Verify warning returned when renew sub using ExpSub module 
            renewFlag could be "ExpRenew License" or "Renew License"
        """
        
        setXML = self.setXML(flag=renewFlag)
        
        print "XML for %s request:"%renewFlag
        self.xmlPPrint(setXML)
        
        # send web service request
        self.setHeaders["Content-length"] = len(setXML)
        self.r = requests.put(self.Base_URL, data=setXML, headers=self.setHeaders)
        
        step="Verify web service call success"
        expected = 200
        current = self.r.status_code
        print "HTTP code returned: %s"%current
        self.verify_IsEqual(expected, current, step)  
    
        
    #############################
    #
    # Helper Method for testing
    #
    #############################  
    def setSalesOrder(self):
        self.test_data["lg"]["sales order"] = time.strftime("%Y%m%d%H%M") + "_" + self.test_data["lg"]["sales order"]
    
            
    def setXML(self, flag="Generate License"):
        setXML = "<License>"
        
        if flag == "Renew License":
            setXML += "<PO>%s</PO>"%self.test_data["lg"]["sales order"]
            setXML += "<Partner>%s</Partner>"%self.test_data["lg"]["customer name"]
            setXML += "<Product>%s</Product>"%self.test_data["type"]
            setXML += "<BaseSKU>"
            setXML += "<ID>%s</ID>"%self.test_data["sub renew"]["sub"][0]
            setXML += "<Name>%s</Name><!-- Optional -->"%self.test_data["sub renew"]["sub"][1]
            setXML += "</BaseSKU>"
            if self.test_data["product"][1] == "enteliWEB-Ent":
                ioAddOnList = self.test_data["sub renew"]["subIO"]
                setXML += "<SKUList>"
                for item in ioAddOnList:
                    setXML += "<SKU>"
                    setXML += "<ID>%s</ID>"%item[0]
                    setXML += "<Name>%s</Name><!-- Optional -->"%item[1]
                    setXML += "<Qty>%s</Qty>"%item[2]
                    setXML += "</SKU>"
                setXML += "</SKUList>"
            setXML += "<LicenseSerial>"
            setXML += "<SerialNumber>%s</SerialNumber>"%self.test_data["serial"]
            setXML += "</LicenseSerial>"
        elif flag == "ExpRenew License":
            setXML += "<PO>%s</PO>"%self.test_data["lg"]["sales order"]
            setXML += "<Partner>%s</Partner>"%self.test_data["lg"]["customer name"]
            setXML += "<Product>%s</Product>"%self.test_data["type"]
            setXML += "<BaseSKU>"
            setXML += "<ID>%s</ID>"%self.test_data["sub renew"]["expsub"][0]
            setXML += "<Name>%s</Name><!-- Optional -->"%self.test_data["sub renew"]["expsub"][1]
            setXML += "</BaseSKU>"
            if self.test_data["product"][1] == "enteliWEB-Ent":
                ioAddOnList = self.test_data["sub renew"]["expsubIO"]
                setXML += "<SKUList>"
                for item in ioAddOnList:
                    setXML += "<SKU>"
                    setXML += "<ID>%s</ID>"%item[0]
                    setXML += "<Name>%s</Name><!-- Optional -->"%item[1]
                    setXML += "<Qty>%s</Qty>"%item[2]
                    setXML += "</SKU>"
                setXML += "</SKUList>"
            setXML += "<LicenseSerial>"
            setXML += "<SerialNumber>%s</SerialNumber>"%self.test_data["serial"]
            setXML += "</LicenseSerial>"
        else:
            setXML += "<PO>%s</PO>"%self.test_data["lg"]["sales order"]
            setXML += "<Partner>%s</Partner>"%self.test_data["lg"]["customer name"]
            setXML += "<Product>%s</Product>"%self.test_data["type"]
        
            setXML += "<BaseSKU>"
            setXML += "<ID>%s</ID>"%self.test_data["product"][0]
            setXML += "<Name>%s</Name><!-- Optional -->"%self.test_data["product"][1]
            setXML += "</BaseSKU>"
        
            if self.test_data["lg"]["components"]:
                setXML += "<SKUList>"
                components = self.test_data["lg"]["components"]
                for item in components:
                    setXML += "<SKU>"
                    setXML += "<ID>%s</ID>"%item[0]
                    setXML += "<Name>%s</Name><!-- Optional -->"%item[1]
                    setXML += "<Qty>%s</Qty>"%item[2]
                    setXML += "</SKU>"
                setXML += "</SKUList>"
            
            if self.test_data["lg"]["site info"]:
                setXML += "<VMInfo>"
                setXML += "<SiteName>%s</SiteName>"%self.test_data["lg"]["site info"]["Site Name"]
                setXML += "<SiteAddress>%s</SiteAddress>"%self.test_data["lg"]["site info"]["Site Address"]
                setXML += "</VMInfo>"
        
        setXML += "</License>"
        
        return setXML
    
    
    def helper_VerifyExpiry(self, errMessage, test_data, flag):
        """ test helper to verify the Active and Sub module expire date in XML string """

        xmlString = self.r.text
        print "XML for query license respond:"
        print xmlString
        element = ElementTree.fromstring(xmlString)
        step = errMessage + "\n...Verify LicenseSerial node"
        expected = ["SerialNumber"]
        subElement = element.find("LicenseSerial")
        result = subElement.getchildren()
        current = []
        if result:
            for item in result:
                current.append(item.tag)
        self.verify_IsEqual(expected, current, step)
        expected = test_data["serial"]
        subElement = subElement.find("SerialNumber")
        current = subElement.text
        self.verify_IsEqual(expected, current, step)
        
        if flag == "test01":
            step = errMessage + "\n...Verify Active / Sub Modules"
            subElement = element.find("ModuleList")
            result = subElement.getchildren()
            current = {}
            if result:
                for item in result:
                    id = item.find("ID")
                    if id is not None and (id.text in ("ACTIVE", "SUB")):
                        valueList = []
                        value = item.find("Value")
                        if value is not None:
                            valueList.append(value.text)
                        expiry = item.find("Expiry")
                        if expiry is not None:
                            valueList.append(expiry.text)
                        current[id.text] = valueList
            expected = {}
            components = test_data["lg"]["components"]
            for item in components:
                if "Sub-AddOn" in item[1]:
                    days = (int(item[2]) + 1) * 365
                    daysString = "%s Days"%days
                    expected["SUB"] = ["yes", daysString]
                    if "enteliWEB-Tech" in test_data["product"][1]:
                        expected["ACTIVE"] = ["1", daysString]
            self.verify_IsEqual(expected, current, step)
            
        if flag == "test02":
            step = errMessage + "\n...Verify Active / Sub Modules"
            subElement = element.find("ModuleList")
            result = subElement.getchildren()
            current = {}
            if result:
                for item in result:
                    id = item.find("ID")
                    if id is not None and (id.text in ("ACTIVE", "SUB")):
                        valueList = []
                        value = item.find("Value")
                        if value is not None:
                            valueList.append(value.text)
                        expiry = item.find("Expiry")
                        if expiry is not None:
                            valueList.append(expiry.text)
                        current[id.text] = valueList
            expected = {}
            expected["SUB"] = self.test_data["sub renew"]["SUB"]
            if "enteliWEB-Tech" in test_data["product"][1]:
                expected["ACTIVE"] = self.test_data["sub renew"]["ACTIVE"]
            self.verify_IsEqual(expected, current, step)
            
        if flag == "test03":
            step = errMessage + "\n...Verify Active / Sub Modules"
            subElement = element.find("ModuleList")
            result = subElement.getchildren()
            current = {}
            if result:
                for item in result:
                    id = item.find("ID")
                    if id is not None and (id.text in ("ACTIVE", "SUB")):
                        valueList = []
                        value = item.find("Value")
                        if value is not None:
                            valueList.append(value.text)
                        expiry = item.find("Expiry")
                        if expiry is not None:
                            valueList.append(expiry.text)
                        current[id.text] = valueList
            expected = {}
            expected["SUB"] = []
            expected["SUB"].append("yes")
            # convert from valid number of days to valid until day
            numOfDays = int((self.test_data["sub renew"]["SUB"][1]).split()[0]) - 1
            today = datetime.date.today()
            untilDate = today + timedelta(days=numOfDays)
            expected["SUB"].append(untilDate.strftime('%Y-%m-%d'))
            if "enteliWEB-Tech" in test_data["product"][1]:
                expected["ACTIVE"] = []
                expected["ACTIVE"].append("1")
                expected["ACTIVE"].append(untilDate.strftime('%Y-%m-%d'))
            self.verify_IsEqual(expected, current, step)
            
        if flag == "test04":
            step = errMessage + "\n...Verify Active / Sub Modules"
            subElement = element.find("ModuleList")
            result = subElement.getchildren()
            current = {}
            if result:
                for item in result:
                    id = item.find("ID")
                    if id is not None and (id.text in ("ACTIVE", "SUB")):
                        valueList = []
                        value = item.find("Value")
                        if value is not None:
                            valueList.append(value.text)
                        expiry = item.find("Expiry")
                        if expiry is not None:
                            valueList.append(expiry.text)
                        current[id.text] = valueList
            expected = {}
            expected["SUB"] = []
            expected["SUB"].append("yes")
            # convert from valid number of days to valid until day
            numOfDays = test_data["sub renew"]["times"] * 365
            untilDate = self.passingDate + timedelta(days=numOfDays)
            untilDateStr = untilDate.strftime('%Y-%m-%d')
            expected["SUB"].append(untilDateStr)
            
            if "enteliWEB-Tech" in test_data["product"][1]:
                expected["ACTIVE"] = []
                expected["ACTIVE"].append("1")
                expected["ACTIVE"].append(untilDateStr)
            self.verify_IsEqual(expected, current, step)
            
        if flag == "test05":
            step = errMessage + "\n...Verify Active / Sub Modules"
            subElement = element.find("ModuleList")
            result = subElement.getchildren()
            current = {}
            if result:
                for item in result:
                    id = item.find("ID")
                    if id is not None and (id.text in ("ACTIVE", "SUB")):
                        valueList = []
                        value = item.find("Value")
                        if value is not None:
                            valueList.append(value.text)
                        expiry = item.find("Expiry")
                        if expiry is not None:
                            valueList.append(expiry.text)
                        current[id.text] = valueList
            expected = {}
            expected["SUB"] = []
            expected["SUB"].append("yes")
            # convert from valid number of days to valid until day
            currentDate = datetime.date.today()
            numOfDays = test_data["sub renew"]["times"] * 365 
            untilDate = currentDate + timedelta(days=numOfDays)
            untilDateStr = untilDate.strftime('%Y-%m-%d')
            expected["SUB"].append(untilDateStr)
            
            if "enteliWEB-Tech" in test_data["product"][1]:
                expected["ACTIVE"] = []
                expected["ACTIVE"].append("1")
                expected["ACTIVE"].append(untilDateStr)
            self.verify_IsEqual(expected, current, step)
    
            
if __name__ == "__main__":
    TC0104_Renew_License.execute()