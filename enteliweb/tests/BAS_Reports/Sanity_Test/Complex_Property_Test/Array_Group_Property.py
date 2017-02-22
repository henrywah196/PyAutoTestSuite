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
from libraries.eweb.PageObjects.BAS_Reports.Ad_Hoc import AdHocPageObj
import os, time
from selenium import webdriver
import json
import re
from libraries.eweb.testhelper.BasReportTestHelper import BasReportTestHelper
from ddt import ddt, data
import string
from dateutil.parser import parse


# Global Settings
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "Array_Group_Property.json"))


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
        myTestData.dynamicColumns = item["Dynamic Columns"]
        myTestData.sortAndGroup = item["Sort and Group"]
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
        deviceRange = self.testData.deviceRange
        objectFilters = self.testData.objectFilters
        testDataDescription = self.testData.Description
        
        # update test doc string
        self._testMethodDoc = "Verify report data returned for filter: %s"%testDataDescription
        
        # setup testing report instance
        self._setupReportInstance()
        
        # select testing report instance
        Macros.SelectReportInstance("Building Automation\\Object Query\\%s"%reportName)
        
        # generating report
        result = self.testingReport.generatingReport(timeout=600)
        self.assertTrue(result, "failed to generate report")
        
        # Prepare test helper
        self.testHelper = BasReportTestHelper(self.testingReport.driver)
        deviceList = self.testHelper.objQueryGetDeviceList(site, deviceRange)
        self.resultFromHelper = self.testHelper.objQueryGetObjectList(site, deviceList, objectFilters)
        
        # verify condition for no data return in report
        if not self.resultFromHelper:
            
            result = self.testingReport.generatedReportHasNoData()
            self.assertTrue(result, "Expecting no data returned in the generated report failed")
            
        else:
            result = not self.testingReport.generatedReportHasNoData()
            self.assertTrue(result, "Expecting data returned in the generated report failed")
        
            # verify returned data
            self._test03(testData)
            
        
    def _test03(self, testData):
        """ Sanity Test Data Exchange Settings Report """
        
        # verify grouping label
        current = self.testingReport.generatedReportGetData("grouping label")
        resultDeviceList = list(self.resultFromHelper.keys())
        resultDeviceList.sort()
        expected = []
        for deviceNumber in resultDeviceList:
            propertyValue = self.testHelper.getPropertyValue(testData.site, deviceNumber, "DEV%s"%deviceNumber, "Object_Name")
            deviceName = propertyValue.value
            expected.append("%s (%s)"%(deviceName, deviceNumber))
            
        self.perform(self.assertItemsEqual, current, expected, "Verify the accuracy of grouping label failed")
        
        # verify returned object references in each group
        resultFromReport = self.testingReport.generatedReportGetData()
        for key, value in resultFromReport.iteritems():
            deviceNumber = self._getDeviceNumberFromHeaderString(key)
            if deviceNumber in self.resultFromHelper:
                current = []
                for item in value:
                    current.append(item["ObjectID"])
                expected = []
                for item in self.resultFromHelper[deviceNumber]:
                    objReference = "%s.%s%s"%(deviceNumber, item["object type"], item["object number"])
                    expected.append(objReference)
                errMessage = "Verify the accuracy of returned object references for group '%s' failed"%key
                self.perform(self.assertItemsEqual, current, expected, errMessage)
        
        # verify returned column data for Property Value column
        for key, value in resultFromReport.iteritems():
            for item in value:
                objID = item["ObjectID"]
                deviceNumber = (objID.split("."))[0]
                objReference = (objID.split("."))[1]
                propertyName = self._getColumnPropertyName(testData.dynamicColumns, "Property Value")
                
                errMessage = "Verify returned data '%s' for %s under %s failed"%(propertyName, objReference, key)
                current = item["Property Value"].strip()
                propertyValue = self.testHelper.getPropertyValue(testData.site, deviceNumber, objReference, propertyName)
                
                propertyName = propertyName.split('.')    # propertyName is a list now
                i = 1
                while i < len(propertyName):
                    attrName = propertyName[i]
                    propertyValue = getattr(propertyValue, attrName)
                    i = i + 1
                expected = (propertyValue.value).strip()
                
                if "dateTime" in propertyName:
                    expected = self.testHelper.dataFormatHelper(expected, "DateTime")
                self.perform(self.assertEqual, current, expected, errMessage)  
                
                
    def _getColumnFormat(self, listDynamicColumns, columnLabel):  
        """ helper to find the value format assigned in dynamic column 
            based on the given column label name
        """ 
        result = None
        for item in listDynamicColumns:
            if item["Heading"] == columnLabel:
                result = item["Format"]
                break
        return result
                
                    
    def _getColumnPropertyName(self, listDynamicColumns, columnLabel):
    
        """ helper to find the property name assigned in dynamic column 
            based on the given column label name
        """ 
        result = None
        for item in listDynamicColumns:
            if item["Heading"] == columnLabel:
                result = item["Property"]
                break
        return result.strip()
                         
    
    def _setupReportInstance(self):
        
        reportName     = self.testData.reportName
        reportTitle    = self.testData.reportTitle
        site           = self.testData.site
        deviceRange    = self.testData.deviceRange
        objectFilters  = self.testData.objectFilters
        dynamicColumns = self.testData.dynamicColumns
        sortAndGroup   = self.testData.sortAndGroup
        
        if Macros.isReportInstanceExisting("Building Automation\\Object Query\\%s"%reportName):
            Macros.SelectReportInstance("Building Automation\\Object Query\\%s"%reportName)
        else:
            Macros.SelectReportInstance("Building Automation\\Object Query")
        time.sleep(10)
        
        self.testingReport = AdHocPageObj()
        
        self.testingReport.reportName = reportName
        self.testingReport.reportTitle = reportTitle
        self.testingReport.site = site
        self.testingReport.deviceRange = deviceRange
        
        # setup object filter
        self.testingReport.deleteObjectFilter(1)    # delete the default object filter
        
        for objectFilter in objectFilters:
            self.testingReport.addObjectFilter(objectFilter)
            
        # setup dynamic columns
        self.testingReport.editReportFormat(dynamicColumns, sortAndGroup)
            
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
