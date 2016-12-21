##############################################################################
# Test Case: Devices in the report are ordered ascending by its device number
##############################################################################
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
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "C88437.json"))


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


class TC88437(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        super(TC88437, cls).setUpClass()
        cls.Browser = settings.BROWSER
        cls.Host = settings.HOST
        cls.Username = settings.USERNAME
        cls.Password = settings.PASSWORD
        
    @classmethod
    def tearDownClass(cls):
        super(TC88437, cls).tearDownClass()
    
    def setUp(self):
        super(TC88437, self).setUp()
        profile = webdriver.FirefoxProfile()
        profile.set_preference('webdriver_enable_native_events', True)
        Macros.LoadEnteliWEB(self.Host, self.Browser, self.Username, self.Password, ff_profile=profile)
        self.accordion = AccordionPageObj()

    def tearDown(self):
        super(TC88437, self).tearDown()
        Macros.CloseEnteliWEB()
        del self.accordion

    #@unittest.skip("")
    def test01(self):
        self._testMethodDoc = 'Verify devices in the report are ordered ascending by its device number'
        
        # setup testing report instance
        self.testData = getTestingData()[0]
        reportName    = self.testData.reportName
        reportTitle   = self.testData.reportTitle
        siteName      = self.testData.site
        deviceRange   = self.testData.deviceRange
        objectFilters = self.testData.objectFilters
        
        self._setupReportInstance()
        
        # select testing report instance
        Macros.SelectReportInstance("Building Automation\\Commissioning Sheets\\%s"%reportName)
        
        # generating report
        result = self.commissioningSheetsReport.generatingReport(timeout=600)
        self.assertTrue(result, "failed to generate report")
        
        # verify no blank report returned
        result = self.commissioningSheetsReport.generatedReportHasNoData()
        self.assertFalse(result, "No data returned in the generated report")
        
        # get data from generated report
        result = self.commissioningSheetsReport.generatedReportGetData(strKeyWord = "device info only")
        resultDeviceNumber = []
        for item in result:
            headerString = item["header"]
            resultDeviceNumber.append(self._getDeviceNumberFromHeaderString(headerString))
        
        # the current order of device numbers you get from generated report
        current = resultDeviceNumber
        # the expected device number ordered numerically
        expected = self._orderDeviceNumber(current)
        
        self.assertListEqual(current, expected, "Device Number are not sorted numerically")
        
        
        
        # Delete testing report instnace
        #Macros.SelectReportInstance("Building Automation\\Commissioning Sheets\\%s"%reportName)
        #self.commissioningSheetsReport.deleteInstance()
    
    def _orderDeviceNumber(self, listDeviceNumber):
        
        listDeviceNumber = [int(x) for x in listDeviceNumber]
        listDeviceNumber.sort()
        listDeviceNumber = [str(x) for x in listDeviceNumber]
        return listDeviceNumber
          
        
    def _getDeviceNumberFromHeaderString(self, headerString):
        """ return the device number part of the device header string """
        result = None
        m = re.search('\(\d+\)$', headerString)
        if m:
            found = m.group(0)
            return found[1:-1]
        
    def _setupReportInstance(self):
        
        reportName    = self.testData.reportName
        reportTitle   = self.testData.reportTitle
        site          = self.testData.site
        deviceRange   = self.testData.deviceRange
        objectFilters = self.testData.objectFilters
        
        if Macros.isReportInstanceExisting("Building Automation\\Commissioning Sheets\\%s"%reportName):
            Macros.SelectReportInstance("Building Automation\\Commissioning Sheets\\%s"%reportName)
        else:
            Macros.SelectReportInstance("Building Automation\\Commissioning Sheets")
        time.sleep(10)
        
        self.commissioningSheetsReport = CommissioningSheetsPageObj()
        
        self.commissioningSheetsReport.reportName = reportName
        self.commissioningSheetsReport.reportTitle = reportTitle
        self.commissioningSheetsReport.site = site
        self.commissioningSheetsReport.deviceRange = deviceRange
        
        # delete the default object filter
        self.commissioningSheetsReport.deleteObjectFilter(1)
        
        for objectFilter in objectFilters:
            self.commissioningSheetsReport.addObjectFilter(objectFilter)
            
        self.commissioningSheetsReport.saveChange()
        

if __name__ == "__main__":
    unittest.main()
