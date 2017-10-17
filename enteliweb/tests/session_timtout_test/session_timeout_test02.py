# coding: utf-8
################################################################################################
# Test Case   : Implement Back end for ESignature and block command request (EWEB-22475)
#
# Description : 
#
################################################################################################
import settings
from selenium import webdriver
from libraries.eweb import Macros
from libraries.PyAutoTestCase import *    # import test case template
from libraries.eweb.DataObjects.WebGroup import WebGroupDBObj
from libraries.eweb.PageObjects.LoginPage import LoginPageObj
import os, time
import json
import re
from ddt import ddt, data
import requests
from requests.exceptions import ConnectionError
from requests.auth import HTTPBasicAuth
import base64
from enum import Enum
try:
    from lxml import etree
except ImportError:
    raise Exception("this package needs lxml module, please install it first.")


# Global Settings
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "session_timeout_test02.json"))


def getTestingData():
    """
    return a list of testing data
    """
    
    class TestData():
        
        def __init__(self):
            self.description = None 
            self.url = None 
            self.page_flag = None
            self.action = None
            
    json_file = open(JSON_FILE_LOCATION, "r")
    json_data = json.load(json_file)
            
    result = []        
    for item in json_data:
        myTestData = TestData()
        myTestData.description = item["description"]
        myTestData.url = item["url"]
        myTestData.page_flag = item["page flag"] 
        myTestData.action = item["action"]
        
        result.append(myTestData)
        
    return result


@ddt
class TestCase(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        super(TestCase, cls).setUpClass()
        cls.browser = settings.BROWSER
        cls.host = settings.HOST
        cls.username = "tester"
        cls.password = "demo"
        cls.base_url = "http://%s/enteliweb"%cls.host
        
        
    @classmethod
    def tearDownClass(cls):
        super(TestCase, cls).tearDownClass()
    
    
    def setUp(self):
        super(TestCase, self).setUp()
        self.longMessage = True
        self.maxDiff = None
        
        profile = webdriver.FirefoxProfile()
        profile.set_preference('webdriver_enable_native_events', True)
        Macros.LoadEnteliWEB(self.host, self.browser, self.username, self.password, ff_profile=profile)
        self.login_page = LoginPageObj()
            

    def tearDown(self):
        super(TestCase, self).tearDown()
        
        Macros.CloseEnteliWEB()
        del self.login_page


    @data(*getTestingData())
    def test01(self, test_data):
        
        self.test_data = test_data
        self._testMethodDoc = test_data.description
        url = self.base_url + test_data.url
        driver = self.login_page.driver
        driver.get(url)
        time.sleep(12)
        result = self._is_test_page_loaded()
        self.assertTrue(result, "Verify test page is loaded failed.")
        time.sleep(80)
        result = self.login_page.isLoaded()
        self.assertFalse(result, "Verify no auto log off after session time out failed.")
        if test_data.action == "reload":
            driver.get(url)
            time.sleep(12)
            result = self.login_page.isLoaded()
            self.assertTrue(result, "Verify login page is loaded failed.")
            self._login()
            result = self._is_test_page_loaded()
            self.assertTrue(result, "Verify test page is loaded after relogin failed.")
        
        
    def _is_test_page_loaded(self):
        
        page_flag = self.test_data.page_flag
        driver = self.login_page.driver
        
        if page_flag[0] == "title":
            print "title of test page: %s"%driver.title
            return page_flag[1] == driver.title
        elif page_flag[0] == "string":
            return page_flag[1] in driver.page_source
        
        
    def _login(self):
        
        # login to enteliWEB
        self.login_page.username = self.username
        self.login_page.password = self.password
        self.login_page.click(LoginPageObj.submit)
        time.sleep(12)
            
        
        
        
    
        

if __name__ == "__main__":
    unittest.main()
