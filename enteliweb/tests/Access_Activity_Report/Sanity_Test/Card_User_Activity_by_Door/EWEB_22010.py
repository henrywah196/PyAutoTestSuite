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
from libraries.eweb.DataObjects.WebGroup import AccessActivity, DateTimeFormat
import os, time
from selenium import webdriver
import json
import re
from ddt import ddt, data
import chardet
import codecs
from datetime import datetime


# Global Settings
class ReportParameter:
    reportName    = "Card User Activity by Door EWEB_22010"
    reportTitle   = "Card User Activity by Door EWEB_22010"
    site          = "$LocalSite"
    dateRange     = ["This Week"]
    cardUsers     = {"Find Option" : "Find by Keyword", "Filter By"   : "*"}
    doors         = {"Find Option" : "Find by Keyword", "Filter By"   : "*"}
    events        = [2, 3]
    cardNumber    = None
    siteCode      = None
      
FormatString = [
                 "MMMM d,y HH:mm",
                 "MMMM d,y hh:mm a",
                 "MM d,y HH:mm",
                 "MM d,y hh:mm a",
                 "y/MM/dd HH:mm",
                 "y/MM/dd hh:mm a",
                 "dd MMMM y HH:mm",
                 "dd MM y HH:mm",
                 "dd.MM.y HH:mm",
                 "y-MM-dd HH:mm"
               ]





@ddt
class TestCase(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        super(TestCase, cls).setUpClass()
        cls.Browser = settings.BROWSER
        cls.Host = settings.HOST
        cls.Username = settings.USERNAME
        cls.Password = settings.PASSWORD
        cls.profile = webdriver.FirefoxProfile()
        cls.profile.set_preference('webdriver_enable_native_events', True)
        Macros.LoadEnteliWEB(cls.Host, cls.Browser, cls.Username, cls.Password, ff_profile=cls.profile)
        cls.accordion = AccordionPageObj()
        
        # setup testing report instance
        cls._setupReportInstance()
        
    @classmethod
    def tearDownClass(cls):
        super(TestCase, cls).tearDownClass()
        Macros.CloseEnteliWEB()
        del cls.accordion
    
    def setUp(self):
        super(TestCase, self).setUp()
        #profile = webdriver.FirefoxProfile()
        #profile.set_preference('webdriver_enable_native_events', True)
        #Macros.LoadEnteliWEB(self.Host, self.Browser, self.Username, self.Password, ff_profile=profile)
        #self.accordion = AccordionPageObj()
        
        self.longMessage = True
        self.maxDiff = None

    def tearDown(self):
        super(TestCase, self).tearDown()
        #Macros.CloseEnteliWEB()
        #del self.accordion

    #@unittest.skip("")
    @data(*FormatString)
    def testMain(self, testData):
        
        # update test doc string
        self._testMethodDoc = "Verify Timestamp sorting in format '%s'"%testData
        print self._testMethodDoc
        
        # select testing report instance
        Macros.SelectReportInstance("Access Control\\Card User Activity by Door\\%s"%ReportParameter.reportName)
        
        # update timestamp format
        self._updateFormat(testData)
        
        # generating report
        result = self.testingReport.generatingReport(timeout=600)
        self.assertTrue(result, "failed to generate report")
        
        
        # Prepare test helper
        self.resultFromHelper = AccessActivity.get_filtered_events(ReportParameter, timestamp_format=True, group_by="Door")
        
        # verify condition for no data return in report
        if not self.resultFromHelper:
            
            result = self.testingReport.generatedReportHasNoData()
            self.assertTrue(result, "Expecting no data returned in the generated report failed")
            
        else:
            result = not self.testingReport.generatedReportHasNoData()
            self.assertTrue(result, "Expecting data returned in the generated report failed")
            
            self.resultFromReport = self.testingReport.generatedReportGetData()
            
            
            for key, value in self.resultFromReport.iteritems():
                if len(value) > 1:
                    current = []
                    for item in value:
                        current.append(item["Timestamp"])
                    expected = sorted(current, reverse=True,  key=lambda x: datetime.strptime(x, DateTimeFormat[testData]))
                    errMessage = "%s under group '%s' failed"%(self._testMethodDoc, key)
                    self.perform(self.assertEqual, current, expected, errMessage)
    
    
    def _updateFormat(self, formatString):
        self.testingReport.focus()
        self.testingReport.editFormat.click()
        time.sleep(1)
        result = self.testingReport.reportFormatWindow.isDisplayed()
        if not result:
            raise Exception("Edit Format Window is not displayed after click Edit Format button")
        
        dicColumnSetting = {"Heading": None,
                            "Property": "Timestamp",
                            "Alignment": None,
                            "Format": formatString,
                            "Visible": None}
            
        self.testingReport.reportFormatWindow.editColumn(dicColumnSetting)
            
        self.testingReport.reportFormatWindow.ok.click()
        
        
    @classmethod
    def _setupReportInstance(cls):
        
        reportName    = ReportParameter.reportName
        reportTitle   = ReportParameter.reportTitle
        site          = ReportParameter.site
        dateRange     = ReportParameter.dateRange
        cardUsers     = ReportParameter.cardUsers
        doors         = ReportParameter.doors
        events        = ReportParameter.events
        cardNumber    = ReportParameter.cardNumber
        siteCode      = ReportParameter.siteCode
        
        
        if Macros.isReportInstanceExisting("Access Control\\Card User Activity by Door\\%s"%reportName):
            Macros.SelectReportInstance("Access Control\\Card User Activity by Door\\%s"%reportName)
        else:
            Macros.SelectReportInstance("Access Control\\Card User Activity by Door")
        time.sleep(10)
        
        cls.testingReport = AccessActivityReportPageObj()
        
        cls.testingReport.reportName = reportName
        cls.testingReport.reportTitle = reportTitle
        cls.testingReport.site = site
        cls.testingReport.setupDateRange(dateRange)
        cls.testingReport.setupCareUsers(cardUsers)
        cls.testingReport.setupDoors(doors)
        cls.testingReport.setupEvents(events)
        if cardNumber is not None:
            cls.testingReport.cardNumber = cardNumber
        else:
            cls.testingReport.cardNumber = ""
        if siteCode is not None:
            cls.testingReport.siteCode = siteCode
        else:
            cls.testingReport.siteCode = ""
            
        cls.testingReport.saveChange()
    
    
if __name__ == "__main__":
    unittest.main()
