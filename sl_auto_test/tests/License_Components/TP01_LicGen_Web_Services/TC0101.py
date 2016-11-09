#--------------------------------------------------------------------------------------
# Test Case:     TC01.01 - Web Service for create a new license (TC0101.py)
# Purpose:       The basic functionality of the webservice call to generate new 
#                licenses via a POST command (SL-722)
#
# Preconditions: 1. Modify TC0101.json to update testing data if required before 
#                   start to run the script.
#
# Author:        Henry Wang
# Created:       Mar 18, 2015
#--------------------------------------------------------------------------------------
import requests, pprint
from ddt import ddt, file_data
from xml.etree import ElementTree
from xml.dom import minidom
from libraries.SLAT.TC_Template_LG import *


@ddt
class TC0101_Generate_License(TC_Template_LG):
    
    def setUp(self):
        
        super(TC0101_Generate_License, self).setUp()
        self.Base_URL = "http://192.168.50.99/cgi-bin/WSLicGen.exe/license"
        self.payload = {'Serial' : None}
        self.setHeaders = {'Accept' : 'text/xml',
                           'Content-length' : None}
        self.r = None
        print "\nTest: %s" %self.currentTest
    
    def tearDown(self):
        super(TC0101_Generate_License, self).tearDown() 
        
    #@unittest.skip("")
    @file_data('TC0101.json')
    def test01_GenerateLicense(self, test_data):
        # Generate license web service call
        self.test_data = test_data
        self.setSalesOrder()    # update sales order in test_data based on testing date and time
        test_method = self.__getattribute__(self.currentTest)    # update doc string based on test data
        self._testMethodDoc = "%s for %s(SO# %s)"%(test_method.__doc__, self.test_data["product"][1], self.test_data["lg"]["sales order"])
        
        # format XML string using test_data
        setXML = self.setXML()
        self.setHeaders["Content-length"] = len(setXML)
        
        # debugging: print setXML
        print "XML for generate new license request:"
        self.xmlPPrint(setXML)
        
        # send web service request
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
        
        step = "query license serial"
        self.payload["Serial"] = self.test_data["serial"]
        self.r = requests.get(self.Base_URL, params=self.payload)
        
        step="Verify service query call success"
        expected = 200
        current = self.r.status_code
        self.verify_IsEqual(expected, current, step)
        
        step = "Verify the content of returned XML string"       
        self.subTest_VerifyXMLContent(step, test_data)
    
    
    def setSalesOrder(self):
        self.test_data["lg"]["sales order"] = time.strftime("%Y%m%d%H") + "_" + self.test_data["lg"]["sales order"]
    
    
    def setXML(self):
        
        setXML = "<License>"
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
    
    def subTest_VerifyXMLContent(self, errMessage, test_data):
        """ test helper to verify the content of returned XML string """
        xmlString = self.r.text
        print "XML for query new license respond:"
        print xmlString
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
        components = test_data["lg"]["components"]
        if components:
            expected = len(components) + 1
        else:
            expected = 1
        subElement = element.find("SKUList")
        result = subElement.getchildren()
        current = None
        if result:
            current = len(result)
        self.verify_IsEqual(expected, current, step)
        
        step = errMessage + "\n...Verify returned SKUs under SKUList node"
        expected = []
        expected.append(test_data["product"])
        expected[0].append("1")
        components = test_data["lg"]["components"]
        if components:
            expected.extend(components)
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


if __name__ == "__main__":
    TC0101_Generate_License.execute()


