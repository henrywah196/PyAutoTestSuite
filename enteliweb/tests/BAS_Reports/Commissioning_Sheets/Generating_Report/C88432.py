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


# Global Settings
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "C88432.json"))


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


class TC88432(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        super(TC88432, cls).setUpClass()
        cls.Browser = settings.BROWSER
        cls.Host = settings.HOST
        cls.Username = settings.USERNAME
        cls.Password = settings.PASSWORD
        
    @classmethod
    def tearDownClass(cls):
        super(TC88432, cls).tearDownClass()
    
    def setUp(self):
        super(TC88432, self).setUp()
        profile = webdriver.FirefoxProfile()
        profile.set_preference('webdriver_enable_native_events', True)
        Macros.LoadEnteliWEB(self.Host, self.Browser, self.Username, self.Password, ff_profile=profile)
        self.accordion = AccordionPageObj()

    def tearDown(self):
        super(TC88432, self).tearDown()
        Macros.CloseEnteliWEB()
        del self.accordion

    #@unittest.skip("")
    def test01(self):
        self._testMethodDoc = ''
        
        # setup testing report instance
        self.testData = getTestingData()[1]
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
        
        # verify blank report returned
        result = self.commissioningSheetsReport.generatedReportHasNoData()
        self.assertFalse(result, "expect no data returned in the generated report")
        
        # verify object query returns no data
        testHelper = BasReportTestHelper(self.commissioningSheetsReport.driver)
        deviceNumberList = testHelper.objQueryGetDeviceList(siteName, deviceRange)
        result = testHelper.objQueryGetObjectList(siteName, deviceNumberList, objectFilters)
        result = not bool(result)
        self.assertTrue(result, "expect no data returned from object query helper")
        
        
        
        # Delete testing report instnace
        #Macros.SelectReportInstance("Building Automation\\Commissioning Sheets\\%s"%reportName)
        #self.commissioningSheetsReport.deleteInstance()
        
        
        
        
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
