#--------------------------------------------------------------------------------------
# Test Case:     TC01.03 - Web Service for fetching a license configuration (TC0103.py)
# Purpose:       The basic functionality of the webservice call to query a license and 
#                return the license configuration information (SL-724)
#
# Preconditions: 1. Modify TC0103.json if required before start to run the script.
#
# Author:        Henry Wang
# Created:       Feb 27, 2015
#--------------------------------------------------------------------------------------
import requests, threading
from ddt import ddt, file_data
from xml.etree import ElementTree
from libraries.SLAT.TC_Template_LG import *


@ddt
class TC0103_Query_License(TC_Template_LG):
    
    def setUp(self):
        
        super(TC0103_Query_License, self).setUp()
        self.Base_URL = "http://192.168.50.99/cgi-bin/WSLicGen.exe/license"
        self.payload = {'Serial' : None}
        self.r = None
        print "\nTest: %s" %self.currentTest
    
    def tearDown(self):
        super(TC0103_Query_License, self).tearDown() 
        
    
    #@unittest.skip("")
    @file_data('TC0103.json')
    def test01_QueryLicense(self, test_data):
        # update doc string based on test data
        #test_method = self.__getattribute__(self.currentTest)
        self._testMethodDoc = "Web Service call for %s(%s)"%(test_data["product"], test_data["serial"])
        
        licenseSerial = test_data["serial"]
            
        self.payload["Serial"] = licenseSerial
        
        self.r = requests.get(self.Base_URL, params=self.payload)
        
        step="Verify web service call success"
        expected = 200
        current = self.r.status_code
        print "Query license %s returns HTTP code: %s"%(licenseSerial, current)
        self.verify_IsEqual(expected, current, step)
        
        step = "Verify returned XML string is well formed"
        result = self.r.text
        print "XML for query license respond:"
        print result
        self.verify_XML_IsWellFormed(result, step)
        
        step = "Verify the content of returned XML string"
        self.subTest_VerifyXMLContent(step, test_data)
        
    
    #@unittest.skip("")
    def test02_Multiple_Query(self):
        #Verify multiple query can be handled
        self._testMethodDoc = "Verify multiple query can be handled"
        
        licenseSerial = "ar8VE-65dF6-QzGaH-4WEEa-db5MO-0i5zz"
        
        # setup new thread
        thread1 = myThread(1, "Thread-1")
        thread1.Base_URL = self.Base_URL
        thread1.payload["Serial"] = licenseSerial
        thread2 = myThread(2, "Thread-2")
        thread2.Base_URL = self.Base_URL
        thread2.payload["Serial"] = licenseSerial
        # start new thread and wait it finish
        thread1.start()
        time.sleep(3)
        thread2.start()
        
        thread1.waitting()
        thread2.waitting()
        
        for thread in (thread1, thread2):
            step="Verify web service call success for %s"%thread.threadName
            expected = 200
            current = thread.r.status_code
            self.verify_IsEqual(expected, current, step)
        
            step = "Verify returned XML string is well formed for %s"%thread.threadName
            result = thread.r.text
            self.verify_XML_IsWellFormed(result, step)
        
            step = "Verify the content of returned XML string for %s"%thread.threadName
            self.myThread_VerifyXMLContent(step, thread)
        
        
    def subTest_VerifyXMLContent(self, errMessage, test_data):
        """ test helper to verify the content of returned XML string """
        xmlString = self.r.text
        element = ElementTree.fromstring(xmlString)
        
        step = errMessage + "\n...Verify root node"
        expected = "License"
        current = element.tag
        self.verify_IsEqual(expected, current, step)
        
        step = errMessage + "\n...Verify sub nodes"
        expected = ["SKUList", "ModuleList", "FreeDataList", "LicenseSerial", "VMInfo"]
        result = element.getchildren()
        current = []
        if result:
            for item in result:
                current.append(item.tag)
        self.verify_IsEqual(expected, current, step)
        
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
        
        step = errMessage + "\n...Verify VMInfo node"
        expected = ["SiteName", "SiteAddress"]
        subElement = element.find("VMInfo")
        result = subElement.getchildren()
        current = []
        if result:
            for item in result:
                current.append(item.tag)
        self.verify_IsEqual(expected, current, step)
        
        step = errMessage + "\n...Verify VMInfo.SiteName node"
        expected = None
        if test_data["lg"]["site info"]:
            expected = test_data["lg"]["site info"]["Site Name"]
        siteNameNode = subElement.find("SiteName")
        current = siteNameNode.text
        self.verify_IsEqual(expected, current, step)
        
        step = errMessage + "\n...Verify VMInfo.SiteAddress node"
        expected = None
        if test_data["lg"]["site info"]:
            expected = test_data["lg"]["site info"]["Site Address"]
        siteAddressNode = subElement.find("SiteAddress")
        current = siteAddressNode.text
        self.verify_IsEqual(expected, current, step)
        
        step = errMessage + "\n...Verify total SKUs returned under SKUList node"
        components = test_data["lg"]["query components"]
        expected = len(components)
        subElement = element.find("SKUList")
        result = subElement.getchildren()
        current = None
        if result:
            current = len(result)
        self.verify_IsEqual(expected, current, step)
        
        step = errMessage + "\n...Verify returned SKUs under SKUList node"
        expected = test_data["lg"]["query components"]
        subElement = element.find("SKUList")
        result = subElement.getchildren()
        current = []
        if result:
            for item in result:
                sku = []
                skuID = item.find("ID")
                if skuID is not None:
                    sku.append(skuID.text)
                name = item.find("Name")
                if name is not None:
                    sku.append(name.text)
                qty = item.find("Qty")
                if qty is not None:
                    sku.append(qty.text)
                current.append(sku)
        self.verify_IsEqual(expected, current, step)
        
        step = errMessage + "\n...Verify Modules"
        expected = test_data["ModuleList"]
        subElement = element.find("ModuleList")
        result = subElement.getchildren()
        current = {}
        if result:
            for item in result:
                id = item.find("ID")
                if id is not None:
                    valueList = []
                    value = item.find("Value")
                    if value is not None:
                        valueList.append(value.text)
                    expiry = item.find("Expiry")
                    if expiry is not None:
                        valueList.append(expiry.text)
                    current[id.text] = valueList
        self.verify_IsEqual(expected, current, step)
                    

    def myThread_VerifyXMLContent(self, errMessage, thread):
        """ test helper for multiple query to verify the content of returned XML string"""
        xmlString = thread.r.text
        element = ElementTree.fromstring(xmlString)
        
        step = errMessage + "\n...Verify root node"
        expected = "License"
        current = element.tag
        self.verify_IsEqual(expected, current, step)
        
        step = errMessage + "\n...Verify sub nodes"
        expected = ["SKUList", "ModuleList", "FreeDataList", "LicenseSerial", "VMInfo"]
        result = element.getchildren()
        current = []
        if result:
            for item in result:
                current.append(item.tag)
        self.verify_IsEqual(expected, current, step)
        
        step = errMessage + "\n...Verify LicenseSerial node"
        expected = ["SerialNumber"]
        subElement = element.find("LicenseSerial")
        result = subElement.getchildren()
        current = []
        if result:
            for item in result:
                current.append(item.tag)
        self.verify_IsEqual(expected, current, step)
        expected = thread.payload["Serial"]
        subElement = subElement.find("SerialNumber")
        current = subElement.text
        self.verify_IsEqual(expected, current, step)
        
        step = errMessage + "\n...Verify VMInfo node"
        expected = ["SiteName", "SiteAddress"]
        subElement = element.find("VMInfo")
        result = subElement.getchildren()
        current = []
        if result:
            for item in result:
                current.append(item.tag)
        self.verify_IsEqual(expected, current, step)
        

class myThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = name
        self.Base_URL = None
        self.payload = {'Serial' : None}
        self.r = None
        self.isFinished = False
    def run(self):
        print "Starting " + self.threadName
        self.licQuery()
        
    def licQuery(self):
        self.r = requests.get(self.Base_URL, params=self.payload)
        self.isFinished = True
        
    def waitting(self):
        i = 0
        while not self.isFinished:
            time.sleep(5)
            i = i + 1
            if i > 11:
                raise Exception("Testing Thread doesn't finish within 60 seconds")
            
        
if __name__ == "__main__":
    TC0103_Query_License.execute()
            
        
            
