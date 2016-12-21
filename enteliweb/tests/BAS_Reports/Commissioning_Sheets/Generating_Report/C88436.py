########################################################################################
# Test Case: Devices info are displayed before the set of IP/OP tables from that device
########################################################################################
# coding: utf-8
import settings
from libraries.eweb import Macros
from libraries.PyAutoTestCase import *    # import test case template
from libraries.eweb.PageObjects.Accordion import AccordionPageObj
from libraries.eweb.PageObjects.BAS_Reports.Commissioning_Sheets import CommissioningSheetsPageObj
import os, time
from selenium import webdriver
import json
from libraries.eweb.testhelper.BasReportTestHelper import BasReportTestHelper
import re


# Global Settings
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "C88436.json"))


def getTestingData():
    """
    return a list of commissioning sheet report settings
    """
    
    class TestData():
        def __init__(self):
            self.reportName  = None
            self.reportTitle = None
            self.site = None
            self.deviceRange = None
            self.objectFilters = None
            
    result = None
    json_file = open(JSON_FILE_LOCATION, "r")
    json_data = json.load(json_file)
            
    for item in json_data:
        myTestData = TestData()
        myTestData.reportName = item["Report Name"]
        myTestData.reportTitle = item["Report Title"]
        myTestData.site = item["Site"]
        myTestData.deviceRange = item["Device Range"]
        myTestData.objectFilters = item["Object Filters"]
        if result is None:
            result = []
        result.append(myTestData)
        
    return result


class TC88436(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        super(TC88436, cls).setUpClass()
        cls.Browser = settings.BROWSER
        cls.Host = settings.HOST
        cls.Username = settings.USERNAME
        cls.Password = settings.PASSWORD
        
        profile = webdriver.FirefoxProfile()
        profile.set_preference('webdriver_enable_native_events', True)
        Macros.LoadEnteliWEB(cls.Host, cls.Browser, cls.Username, cls.Password, ff_profile=profile)
        cls.accordion = AccordionPageObj()
        
        cls.testData = getTestingData()[0]
        
        # setup testing report instance
        cls._setupReportInstance()
        
        # select testing report instance
        reportName    = cls.testData.reportName
        Macros.SelectReportInstance("Building Automation\\Commissioning Sheets\\%s"%reportName)
        
        # generating report
        result = cls.commissioningSheetsReport.generatingReport(timeout=600)
        assert result == True, "failed to generate report"
        
        # verify no blank report returned
        result = cls.commissioningSheetsReport.generatedReportHasNoData()
        assert result == False, "No data returned in the generated report"
        
        # get data from generated report
        cls.deviceInfo = cls.commissioningSheetsReport.generatedReportGetData(strKeyWord = "device info only")
               
              
    @classmethod
    def tearDownClass(cls):
        super(TC88436, cls).tearDownClass()
        Macros.CloseEnteliWEB()
    
    def setUp(self):
        super(TC88436, self).setUp()
        
        self.longMessage = True
        self.cls = self.__class__
        

    def tearDown(self):
        super(TC88436, self).tearDown()
        

    #@unittest.skip("")
    def test01(self):
        self._testMethodDoc = 'Verify grouping label'
        
        deviceInfoList = self.cls.deviceInfo
        
        for item in deviceInfoList:
            
            groupingLabel = item["header"]
            # obtain the device number from grouping label
            deviceNumber = self._getDeviceNumberFromHeaderString(groupingLabel)
            siteName = self.cls.testData.site
            objectReference = "DEV" + deviceNumber
            
            testHelper = BasReportTestHelper(self.cls.commissioningSheetsReport.driver)
            result = testHelper.getPropertyValue(siteName, deviceNumber, objectReference, "Object_Name")
            
            expected = "%s (%s)"%(result["value"], deviceNumber)
            current = groupingLabel
            errMessage = "Verify grouping label for device '%s' failed"%deviceNumber
            self.perform(self.assertEqual, current, expected, errMessage)
        
        
    #@unittest.skip("")
    def test02(self):
        self._testMethodDoc = 'Verify devices info'
        
        deviceInfoList = self.cls.deviceInfo
        
        for item in deviceInfoList:
            
            groupingLabel = item["header"]
            # obtain the device number from grouping label
            deviceNumber = self._getDeviceNumberFromHeaderString(groupingLabel)
            siteName = self.cls.testData.site
            objectReference = "DEV" + deviceNumber
            
            testHelper = BasReportTestHelper(self.cls.commissioningSheetsReport.driver)
            
            # verify Model Name
            result = testHelper.getPropertyValue(siteName, deviceNumber, objectReference, "Model_Name")
            current = item["model"]
            expected = (result["value"]).strip()
            errMessage = "Verify device '%s' Model Name failed"%deviceNumber
            self.perform(self.assertEqual, current, expected, errMessage)
         
            # verify Location 
            result = testHelper.getPropertyValue(siteName, deviceNumber, objectReference, "Location")
            current = item["location"]
            expected = (result["value"]).strip()
            errMessage = "Verify device '%s' Location failed"%deviceNumber
            self.perform(self.assertEqual, current, expected, errMessage)
            
            # verify IP Address
            result = testHelper.getPropertyValue(siteName, deviceNumber, objectReference, "IP_Address")
            current = item["ip"]
            expected = (result["value"]).strip()
            errMessage = "Verify device '%s' IP Address failed"%deviceNumber
            self.perform(self.assertEqual, current, expected, errMessage)
        
        
        
        # Delete testing report instnace
        #Macros.SelectReportInstance("Building Automation\\Commissioning Sheets\\%s"%reportName)
        #self.commissioningSheetsReport.deleteInstance()
          
        
    def _getDeviceNumberFromHeaderString(self, headerString):
        """ return the device number part of the device header string """
        result = None
        m = re.search('\(\d+\)$', headerString)
        if m:
            found = m.group(0)
            return found[1:-1]
   
    @classmethod  
    def _setupReportInstance(cls):
        
        reportName    = cls.testData.reportName
        reportTitle   = cls.testData.reportTitle
        site          = cls.testData.site
        deviceRange   = cls.testData.deviceRange
        objectFilters = cls.testData.objectFilters
        
        if Macros.isReportInstanceExisting("Building Automation\\Commissioning Sheets\\%s"%reportName):
            Macros.SelectReportInstance("Building Automation\\Commissioning Sheets\\%s"%reportName)
        else:
            Macros.SelectReportInstance("Building Automation\\Commissioning Sheets")
        time.sleep(10)
        
        cls.commissioningSheetsReport = CommissioningSheetsPageObj()
        
        cls.commissioningSheetsReport.reportName = reportName
        cls.commissioningSheetsReport.reportTitle = reportTitle
        cls.commissioningSheetsReport.site = site
        cls.commissioningSheetsReport.deviceRange = deviceRange
        
        # delete the default object filter
        cls.commissioningSheetsReport.deleteObjectFilter(1)
        
        for objectFilter in objectFilters:
            cls.commissioningSheetsReport.addObjectFilter(objectFilter)
            
        cls.commissioningSheetsReport.saveChange()
        

if __name__ == "__main__":
    unittest.main()
