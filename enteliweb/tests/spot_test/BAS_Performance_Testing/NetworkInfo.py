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


class NetworkInfo(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        super(NetworkInfo, cls).setUpClass()
        cls.Browser = settings.BROWSER
        cls.Host = settings.HOST
        cls.Username = settings.USERNAME
        cls.Password = settings.PASSWORD
        
    @classmethod
    def tearDownClass(cls):
        super(NetworkInfo, cls).tearDownClass()
    
    def setUp(self):
        super(NetworkInfo, self).setUp()
        profile = webdriver.FirefoxProfile()
        profile.set_preference('webdriver_enable_native_events', True)
        Macros.LoadEnteliWEB(self.Host, self.Browser, self.Username, self.Password, ff_profile=profile)
        self.accordion = AccordionPageObj()

    def tearDown(self):
        super(NetworkInfo, self).tearDown()
        Macros.CloseEnteliWEB()
        del self.accordion

    #@unittest.skip("")
    def test01(self):
        self._testMethodDoc = ''
        
        Sites = ["$LocalSite", "RV Site", "Hist DB"]
        
        testHelper = BasReportTestHelper(self.accordion.driver)
        result = []
        for site in Sites:
            info = {}
            info["site"] = site
            deviceList = testHelper.getDevicesList(site)
            totalDevices = len(deviceList)
            info["total devices"] = totalDevices
            info["detail"] = []
            totalObjects = 0
            for device in deviceList:
                objects = []
                objectList = testHelper.getObjectsList(site, device["device number"])
                totalObjects = totalObjects + len(objectList)
                objects.append(device["device number"])
                objects.append(len(objectList))
                info["detail"].append(objects)
            info["total objects"] = totalObjects
            
            result.append(info)
        
        for item in result:    
            print "Network: %s"%item["site"]
            print "total number of devices: %s"%item["total devices"]
            print "total number of objects: %s"%item["total objects"]
            for subitem in item["detail"]:
                print "Device %s, %s objects"%(subitem[0], str(subitem[1]))
            print ""
        

if __name__ == "__main__":
    unittest.main()
