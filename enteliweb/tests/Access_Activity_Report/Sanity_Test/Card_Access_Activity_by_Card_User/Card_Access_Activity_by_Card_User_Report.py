# coding: utf-8
################################################################################################
# Test Case   : AD Hoc report sanity test
#
# Description : Verify the testing report instance generate and return data correctly
#
################################################################################################
import settings
from libraries.eweb import Macros
from libraries.PyAutoTestCase import *    # import test case template
from libraries.eweb.PageObjects.Accordion import AccordionPageObj
from libraries.eweb.PageObjects.Access_Activity_Reports.Access_Activity_Generic import AccessActivityReportPageObj
from libraries.eweb.DataObjects.WebGroup import AccessActivity
import os, time
from selenium import webdriver
import json
import re
from ddt import ddt, data
import chardet
import codecs


# Global Settings
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "Card_Access_Activity_by_Card_User_Report.json"))


def getTestingData():
    """
    return a list of commissioning sheet report settings
    """
    
    class TestData():
        def __init__(self):
            self.reportName  = None
            self.reportTitle = None
            self.site = None
            self.dateRange = None
            self.cardUsers = None
            self.doors = None
            self.events = None
            self.cardNumber = None
            self.siteCode = None
            
    result = None
    current_encoding = (chardet.detect(open(JSON_FILE_LOCATION, "rb").read()))["encoding"]
    json_file = codecs.open(JSON_FILE_LOCATION, "r", encoding=current_encoding)
    json_data = json.load(json_file)
            
    for item in json_data:
        myTestData = TestData()
        myTestData.reportName = item["Report Name"]
        myTestData.reportTitle = item["Report Title"]
        myTestData.site = item["Site"]
        myTestData.dateRange = item["Date Range"]
        myTestData.cardUsers = None
        if "Card Users" in item:
            myTestData.cardUsers = item["Card Users"]
        myTestData.doors = None
        if "Doors" in item:  
            myTestData.doors = item["Doors"]
        myTestData.events = item["Events"]
        myTestData.cardNumber = None
        if "Card Number" in item: 
            myTestData.cardNumber = item["Card Number"]
        myTestData.siteCode = None
        if "Site Code" in item:   
            myTestData.siteCode = item["Site Code"]
        if "Description" in item:
            myTestData.Description = item["Description"]
        if result is None:
            result = []
        result.append(myTestData)
        
    return result


@ddt
class TestCase(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        super(TestCase, cls).setUpClass()
        cls.Browser = settings.BROWSER
        cls.Host = settings.HOST
        cls.Username = settings.USERNAME
        cls.Password = settings.PASSWORD
        
    @classmethod
    def tearDownClass(cls):
        super(TestCase, cls).tearDownClass()
    
    def setUp(self):
        super(TestCase, self).setUp()
        profile = webdriver.FirefoxProfile()
        profile.set_preference('webdriver_enable_native_events', True)
        Macros.LoadEnteliWEB(self.Host, self.Browser, self.Username, self.Password, ff_profile=profile)
        self.accordion = AccordionPageObj()
        
        self.longMessage = True
        self.maxDiff = None

    def tearDown(self):
        super(TestCase, self).tearDown()
        Macros.CloseEnteliWEB()
        del self.accordion

    #@unittest.skip("")
    @data(*getTestingData())
    def testMain(self, testData):
        
        # prepare test data
        self.testData = testData
        reportName = self.testData.reportName
        reportTitle = self.testData.reportTitle
        site = self.testData.site
        testDataDescription = self.testData.Description
        
        # update test doc string
        self._testMethodDoc = "Verify report data returned for filter: %s"%testDataDescription
        
        # setup testing report instance
        self._setupReportInstance()
        
        # select testing report instance
        Macros.SelectReportInstance("Access Control\\Card Access Activity by Card User\\%s"%reportName)
        
        # generating report
        result = self.testingReport.generatingReport(timeout=600)
        self.assertTrue(result, "failed to generate report")
        
        
        # Prepare test helper
        self.resultFromHelper = AccessActivity.get_filtered_events(testData, timestamp_format=True, group_by="Card User")
        
        # verify condition for no data return in report
        if not self.resultFromHelper:
            
            result = self.testingReport.generatedReportHasNoData()
            self.assertTrue(result, "Expecting no data returned in the generated report failed")
            
        else:
            result = not self.testingReport.generatedReportHasNoData()
            self.assertTrue(result, "Expecting data returned in the generated report failed")
            
            self.resultFromReport = self.testingReport.generatedReportGetData()
            
            current = list(self.resultFromReport.keys())
            expected = list(self.resultFromHelper.keys())
            self.perform(self.assertItemsEqual, current, expected, "verify the accuracy of group label failed")
            
            for key, value in self.resultFromReport.iteritems():
                if key in self.resultFromHelper:
                    current = value
                    expected = self.resultFromHelper[key]
                    self.perform(self.assertItemsEqual, current, expected, "verify the accuracy of returned events for Card User '%s' failed"%key)
        
    
    def _setupReportInstance(self):
        
        reportName    = self.testData.reportName
        reportTitle   = self.testData.reportTitle
        site          = self.testData.site
        dateRange     = self.testData.dateRange
        cardUsers     = self.testData.cardUsers
        doors         = self.testData.doors
        events        = self.testData.events
        cardNumber    = self.testData.cardNumber
        siteCode      = self.testData.siteCode
        
        
        if Macros.isReportInstanceExisting("Access Control\\Card Access Activity by Card User\\%s"%reportName):
            Macros.SelectReportInstance("Access Control\\Card Access Activity by Card User\\%s"%reportName)
        else:
            Macros.SelectReportInstance("Access Control\\Card Access Activity by Card User")
        time.sleep(10)
        
        self.testingReport = AccessActivityReportPageObj()
        
        self.testingReport.reportName = reportName
        self.testingReport.reportTitle = reportTitle
        self.testingReport.site = site
        self.testingReport.setupDateRange(dateRange)
        self.testingReport.setupCareUsers(cardUsers)
        self.testingReport.setupDoors(doors)
        self.testingReport.setupEvents(events)
        if cardNumber is not None:
            self.testingReport.cardNumber = cardNumber
        else:
            self.testingReport.cardNumber = ""
        if siteCode is not None:
            self.testingReport.siteCode = siteCode
        else:
            self.testingReport.siteCode = ""
            
        self.testingReport.saveChange()
    
    
if __name__ == "__main__":
    unittest.main()
