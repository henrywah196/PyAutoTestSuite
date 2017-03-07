#-------------------------------------------------------------------------------
# Test Case:     eweb14157.py
# Purpose:       request should aborted and return forbidden CSRF verification failed
#
# Author:        Henry Wang
# Created:       Jul 03, 2015
#-------------------------------------------------------------------------------
try:
    import unittest, time, os
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
except ImportError, e:
    raise ImportError(str(e) + ". Install this module before run the script.")
import settings
from libraries.eweb import Macros
from libraries.PyAutoTestCase import *    # import test case template
from libraries.eweb.PageObjects.Accordion import AccordionPageObj
from libraries.eweb.PageObjects.BAS_Reports.Commissioning_Sheets import CommissioningSheetsPageObj

from libraries.eweb.PageObjects import selenium_server_connection

import json


# Global settings
# Global Settings
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "eweb14157.json"))
Base_URL = "http://%s/enteliweb"%settings.HOST
KeyWords = "Forbidden Call: CSRF verification failed"


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
        myTestData.isDefaultFilters = item["Is Default Filters"]
        if "Description" in item:
            myTestData.Description = item["Description"]
        if result is None:
            result = []
        result.append(myTestData)
        
    return result


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
            
        
    def testMain(self):
        # Update doc string based on test data
        self._testMethodDoc = "Verify Request aborted: %s"%"CSRF verification failed"
    
        # prepare test data
        self.testData = getTestingData()[0]
        
        # setup testing report instance but don't submit changes
        self._setupReportInstance()
        
        # Open a new tab and login enteliweb again
        driver = self.testingReport.driver
        target = driver.find_element_by_tag_name("body")
        target.send_keys(Keys.CONTROL + "t")
        driver.switch_to.window(driver.window_handles[-1])    # focus on the new tab
        
        driver.get(Base_URL)
        elemLogout = driver.find_element_by_id("link_logout")
        elemLogout.click()
        time.sleep(2)
        elemUserName = driver.find_element_by_id("username")
        elemPassword = driver.find_element_by_id("password")
        elemSubmit = driver.find_element_by_id("btn_login")
        elemUserName.click()
        elemUserName.clear()
        elemUserName.send_keys(self.Username)
        elemPassword.click()
        elemPassword.clear()
        elemPassword.send_keys(self.Password)
        elemSubmit.click()
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "label_Welcome")))
        driver.switch_to.window(driver.window_handles[0])    # focus back to the original tab
        self.testingReport.save.click()
        driver = self.testingReport.driver
        driver.switch_to.default_content()
        driver.switch_to.frame("mainFrame")
        target = driver.find_element_by_tag_name("body")
        current = target.text.strip()
        expected = KeyWords
        self.assertEqual(current, expected, "Verify forbidden call cannot get through failed")
        
        
    def _setupReportInstance(self):
        
        reportName     = self.testData.reportName
        reportTitle    = self.testData.reportTitle
        site           = self.testData.site
        deviceRange    = self.testData.deviceRange
        objectFilters  = self.testData.objectFilters
        defaultFilters = self.testData.isDefaultFilters
        
        if Macros.isReportInstanceExisting("Building Automation\\Commissioning Sheets\\%s"%reportName):
            Macros.SelectReportInstance("Building Automation\\Commissioning Sheets\\%s"%reportName)
        else:
            Macros.SelectReportInstance("Building Automation\\Commissioning Sheets")
        time.sleep(10)
        
        self.testingReport = CommissioningSheetsPageObj()
        
        self.testingReport.reportName = reportName
        self.testingReport.reportTitle = reportTitle
        self.testingReport.site = site
        self.testingReport.deviceRange = deviceRange
        
        if not defaultFilters:
            # setup object filter
            self.testingReport.deleteObjectFilter(1)    # delete the default object filter
        
            for objectFilter in objectFilters:
                self.testingReport.addObjectFilter(objectFilter)
            
    

if __name__ == "__main__":
    unittest.main()
        
    