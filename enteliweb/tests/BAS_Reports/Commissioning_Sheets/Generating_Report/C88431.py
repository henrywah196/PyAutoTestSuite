# coding: utf-8
import settings
from libraries.eweb import Macros
from libraries.PyAutoTestCase import *    # import test case template
from libraries.eweb.PageObjects.Accordion import AccordionPageObj
from libraries.eweb.PageObjects.BAS_Reports.Commissioning_Sheets import CommissioningSheetsPageObj
import os, time
from selenium import webdriver


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
        
        reportName = "My Auto testing Report 001"
        reportTitle = reportName
        site = "$LocalSite"
        deviceRange = "1200"
        
        self.commissioningSheetsReport.reportName = reportName
        self.commissioningSheetsReport.reportTitle = reportTitle
        self.commissioningSheetsReport.site = site
        self.commissioningSheetsReport.deviceRange = deviceRange
        
        self.commissioningSheetsReport.addFilter.click()
        time.sleep(10)
        result = self.commissioningSheetsReport.objectFilterWindow.isDisplayed()
        self.commissioningSheetsReport.objectFilterWindow.addProperty(["Present_Value", ">=", "20.5"])
        propertyValueComparisonRule = {"logic" : "OR",
                                       "list of propertyValueComparison": [ ["Present_Value", ">=", "20.5"],
                                                                            ["Description", "=", "testing"]
                                                                          ]}
        self.commissioningSheetsReport.objectFilterWindow.addRule(propertyValueComparisonRule)
        
        
        
        
        
        


if __name__ == "__main__":
    unittest.main()
