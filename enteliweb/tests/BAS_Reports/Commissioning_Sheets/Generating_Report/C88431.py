# coding: utf-8
import settings
from libraries.eweb import Macros
from libraries.PyAutoTestCase import *    # import test case template
from libraries.eweb.PageObjects.Accordion import AccordionPageObj
from libraries.eweb.PageObjects.BAS_Reports.Commissioning_Sheets import CommissioningSheetsPageObj
import os, time
from selenium import webdriver
import json


# Global Settings
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "C88431.json"))


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


class TC88431(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        super(TC88431, cls).setUpClass()
        cls.Browser = settings.BROWSER
        cls.Host = settings.HOST
        cls.Username = settings.USERNAME
        cls.Password = settings.PASSWORD
        
    @classmethod
    def tearDownClass(cls):
        super(TC88431, cls).tearDownClass()
    
    def setUp(self):
        super(TC88431, self).setUp()
        profile = webdriver.FirefoxProfile()
        profile.set_preference('webdriver_enable_native_events', True)
        Macros.LoadEnteliWEB(self.Host, self.Browser, self.Username, self.Password, ff_profile=profile)
        self.accordion = AccordionPageObj()

    def tearDown(self):
        super(TC88431, self).tearDown()
        Macros.CloseEnteliWEB()
        del self.accordion

    #@unittest.skip("")
    def test01(self):
        self._testMethodDoc = ''
        
        Macros.SelectReportInstance("Building Automation\\Commissioning Sheets")
        time.sleep(10)
        
        self.commissioningSheetsReport = CommissioningSheetsPageObj()
        
        self.testData = getTestingData()[0]
        
        reportName = self.testData.reportName
        reportTitle = self.testData.reportTitle
        site = self.testData.site
        deviceRange = self.testData.deviceRange
        objectFilters = self.testData.objectFilters
        
        self.commissioningSheetsReport.reportName = reportName
        self.commissioningSheetsReport.reportTitle = reportTitle
        self.commissioningSheetsReport.site = site
        self.commissioningSheetsReport.deviceRange = deviceRange
        
        for objectFilter in objectFilters:
            self.commissioningSheetsReport.addObjectFilter(objectFilter)
            
        self.commissioningSheetsReport.saveChange()
        
        time.sleep(10)
        
        Macros.SelectReportInstance("Building Automation\\Commissioning Sheets\My Auto testing Report 001")
        
        self.commissioningSheetsReport.deleteInstance()
        
        
        
        
        
        


if __name__ == "__main__":
    unittest.main()
