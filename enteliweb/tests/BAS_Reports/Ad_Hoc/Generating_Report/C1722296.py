# coding: utf-8
################################################################################################
# Test Case   : Property value comparison should support NULL
#
# Description : Verify property value comparison like Manual_Override = NULL and 
#               Manual_Override <> NULL return expected data.
#
#               Verify property value comparison like Priority_Array[x] = NULL and 
#               Priority_Array[x] <> NULL return expected data.
#
#               Verify NULL string is case insensitive, as long as the exactly 4 
#               characters are used in property value comparison.
#
#               Verify operator other than = and <> is not functional for NULL, blank report 
#               should returned if invalid operator is used for NULL.
#
#               Verify applied to other property as well as long as its attribute isNULL="TRUE" 
#               existing. for example Profile_Name of object in V3 device is NULL.
#
# Note for limitation:
#               In object filter, NULL is treated as a special marker, search for string NULL 
#               will not work. for example property value comparison Description = NULL will 
#               not return any objects, which have string NULL in its description.
################################################################################################
import settings
from libraries.eweb import Macros
from libraries.PyAutoTestCase import *    # import test case template
from libraries.eweb.PageObjects.Accordion import AccordionPageObj
from libraries.eweb.PageObjects.BAS_Reports.Ad_Hoc import AdHocPageObj
import os, time
from selenium import webdriver
import json
import re
from libraries.eweb.testhelper.BasReportTestHelper import BasReportTestHelper
from ddt import ddt, data


# Global Settings
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "C1722296.json"))


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
        if "Description" in item:
            myTestData.Description = item["Description"]
        if result is None:
            result = []
        result.append(myTestData)
        
    return result


@ddt
class TC1722296(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        super(TC1722296, cls).setUpClass()
        cls.Browser = settings.BROWSER
        cls.Host = settings.HOST
        cls.Username = settings.USERNAME
        cls.Password = settings.PASSWORD
        
    @classmethod
    def tearDownClass(cls):
        super(TC1722296, cls).tearDownClass()
    
    def setUp(self):
        super(TC1722296, self).setUp()
        profile = webdriver.FirefoxProfile()
        profile.set_preference('webdriver_enable_native_events', True)
        Macros.LoadEnteliWEB(self.Host, self.Browser, self.Username, self.Password, ff_profile=profile)
        self.accordion = AccordionPageObj()
        
        self.longMessage = True
        self.maxDiff = None

    def tearDown(self):
        super(TC1722296, self).tearDown()
        Macros.CloseEnteliWEB()
        del self.accordion

    #@unittest.skip("")
    @data(*getTestingData())
    def test01(self, testData):
        
        # prepare test data
        self.testData = testData
        reportName = self.testData.reportName
        reportTitle = self.testData.reportTitle
        site = self.testData.site
        deviceRange = self.testData.deviceRange
        objectFilters = self.testData.objectFilters
        testDataDescription = self.testData.Description
        
        # update test doc string
        self._testMethodDoc = "Verify report data returned for filter: %s"%testDataDescription
        
        # setup testing report instance
        self._setupReportInstance()
        
        # select testing report instance
        Macros.SelectReportInstance("Building Automation\\AD HOC\\%s"%reportName)
        
        # generating report
        result = self.testingReport.generatingReport(timeout=600)
        self.assertTrue(result, "failed to generate report")
        
        # Prepare test helper
        testHelper = BasReportTestHelper(self.testingReport.driver)
        deviceList = testHelper.objQueryGetDeviceList(site, deviceRange)
        resultFromHelper = testHelper.objQueryGetObjectList(site, deviceList, objectFilters)
        
        # verify condition for no data return in report
        if not resultFromHelper:
            
            result = self.testingReport.generatedReportHasNoData()
            self.assertTrue(result, "Expecting no data returned in the generated report failed")
            
        else:
            result = not self.testingReport.generatedReportHasNoData()
            self.assertTrue(result, "Expecting data returned in the generated report failed")
        
            # verify grouping label
            current = self.testingReport.generatedReportGetData("grouping label")
            resultDeviceList = list(resultFromHelper.keys())
            resultDeviceList.sort()
            expected = []
            for deviceNumber in resultDeviceList:
                propertyValue = testHelper.getPropertyValue(site, deviceNumber, "DEV%s"%deviceNumber, "Object_Name")
                deviceName = propertyValue["value"]
                expected.append("%s (%s)"%(deviceName, deviceNumber))
            
            self.perform(self.assertItemsEqual, current, expected, "Verify the accuracy of grouping label failed")
        
            # verify returned object references in each group
            resultFromReport = self.testingReport.generatedReportGetData()
            for key, value in resultFromReport.iteritems():
                deviceNumber = self._getDeviceNumberFromHeaderString(key)
                if deviceNumber in resultFromHelper:
                    current = []
                    for item in value:
                        current.append(item["ObjectID"])
                    expected = []
                    for item in resultFromHelper[deviceNumber]:
                        objReference = "%s.%s%s"%(deviceNumber, item["object type"], item["object number"])
                        expected.append(objReference)
                    errMessage = "Verify the accuracy of returned object references for group '%s' failed"%key
                    self.perform(self.assertItemsEqual, current, expected, errMessage)
    
    
    def _setupReportInstance(self):
        
        reportName    = self.testData.reportName
        reportTitle   = self.testData.reportTitle
        site          = self.testData.site
        deviceRange   = self.testData.deviceRange
        objectFilters = self.testData.objectFilters
        
        if Macros.isReportInstanceExisting("Building Automation\\AD HOC\\%s"%reportName):
            Macros.SelectReportInstance("Building Automation\\AD HOC\\%s"%reportName)
        else:
            Macros.SelectReportInstance("Building Automation\\AD HOC")
        time.sleep(10)
        
        self.testingReport = AdHocPageObj()
        
        self.testingReport.reportName = reportName
        self.testingReport.reportTitle = reportTitle
        self.testingReport.site = site
        self.testingReport.deviceRange = deviceRange
        
        # delete the default object filter
        self.testingReport.deleteObjectFilter(1)
        
        for objectFilter in objectFilters:
            self.testingReport.addObjectFilter(objectFilter)
            
        self.testingReport.saveChange()
    
    
    def _getDeviceNumberFromHeaderString(self, headerString):
        """ return the device number part of the device header string """
        result = None
        m = re.search('\(\d+\)$', headerString)
        if m:
            found = m.group(0)
            return found[1:-1]
        

if __name__ == "__main__":
    unittest.main()
