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


# Global Settings
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "sanity_test.json"))


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
        if "Description" in item:
            myTestData.Description = item["Description"]
        if result is None:
            result = []
        result.append(myTestData)
        
    return result


@ddt
class SanityTest(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        super(SanityTest, cls).setUpClass()
        cls.Browser = settings.BROWSER
        cls.Host = settings.HOST
        cls.Username = settings.USERNAME
        cls.Password = settings.PASSWORD
        
    @classmethod
    def tearDownClass(cls):
        super(SanityTest, cls).tearDownClass()
    
    def setUp(self):
        super(SanityTest, self).setUp()
        profile = webdriver.FirefoxProfile()
        profile.set_preference('webdriver_enable_native_events', True)
        Macros.LoadEnteliWEB(self.Host, self.Browser, self.Username, self.Password, ff_profile=profile)
        self.accordion = AccordionPageObj()
        
        self.longMessage = True
        self.maxDiff = None

    def tearDown(self):
        super(SanityTest, self).tearDown()
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
        Macros.SelectReportInstance("Building Automation\\AD HOC\\%s"%reportName)
        
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
            if testDataDescription in ("Sanity Test Active Alarms Report", 
                                       "Sanity Test Calibration Report",
                                       "Sanity Test Decommissioned - Fault Report"):
                self._test01(testData)
            
            elif testDataDescription in ("Sanity Test Controller Firmware Report"):
                self._test02(testData)
                
            elif testDataDescription in ("Sanity Test Data Exchange Settings Report"):
                self._test03(testData)
        
    def _test01(self, testData):
        
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
                
        # verify returned column data for each group
        for key, value in resultFromReport.iteritems():
            for item in value:
                objID = item["ObjectID"]
                deviceNumber = (objID.split("."))[0]
                objReference = (objID.split("."))[1]
                for subKey, subValue in item.iteritems():
                    propertyName = self._getColumnPropertyName(testData.dynamicColumns, subKey)
                    if propertyName is None or propertyName in ("Object_Ref"):
                        continue
                    
                    errMessage = "Verify returned data '%s' for %s under %s failed"%(subKey, objReference, key)
                    current = subValue.strip()
                    expected = None
                    if propertyName == "Device_Number":
                        expected = deviceNumber
                        
                    elif propertyName == "Present_Value":    # dealing with present_value
                        propertyValue = self.testHelper.getPropertyValue(testData.site, deviceNumber, objReference, propertyName)
                        objType = self.testHelper._getObjTypeFromObjRef(objReference)
                        if objType in ("BI", "BO", "BV"):
                            if current.lower() in ("active", "inactive"):    # verify native value
                                expected = propertyValue.value
                            else:
                                expected = (self.testHelper.getPresentValueStateText(testData.site, deviceNumber, objReference))[1]
                        elif objType in ("MI", "MO", "MV"):
                            isNativeValue = True
                            try: int(propertyValue.value)
                            except ValueError: isNativeValue = False
                            if isNativeValue:    # verify native value
                                expected = propertyValue.value
                            else:
                                expected = (self.testHelper.getPresentValueStateText(testData.site, deviceNumber, objReference))[1]
                                
                    elif propertyName == "AD_Value":
                        REGEX = re.compile('^(0|[1-9][0-9]*)$')
                        result = REGEX.match(current)
                        current = result is not None
                        expected = True
                        
                    else:
                        propertyName = self._getColumnPropertyName(testData.dynamicColumns, subKey)
                        propertyValue = self.testHelper.getPropertyValue(testData.site, deviceNumber, objReference, propertyName)
                        expected = propertyValue.value
                        
                        # dealing None returned
                        if expected is None:
                            expected = ""
                
                        # removing white space at the header and tail
                        expected = expected.strip()
                
                        # substitute multiple whitespace with single whitespace
                        expected = ' '.join(expected.split())
                        
                        # dealing with HTML char entities
                        for k, v in ({"&amp;" : "&"}).iteritems():
                            if k in expected:
                                expected = string.replace(expected, k, v)
                        
                        self.perform(self.assertEqual, current, expected, errMessage)
                        
        
    def _test02(self, testData):
        """ Sanity Test Controller Firmware Report """
            
        # verify returned devices (Row)
        resultFromReport = self.testingReport.generatedReportGetData()
        current = []
        for item in resultFromReport:
            deviceNumber = item["Device Number"]
            deviceNumber = re.sub('[,]', '', deviceNumber)    # get rid of comma in string
            current.append(deviceNumber)
                
        expected = list(self.resultFromHelper.keys())
            
        errMessage = "Verify the accuracy of returned devices failed"
        self.perform(self.assertItemsEqual, current, expected, errMessage)
            
            
        # verify returned column data for each devices
        for item in resultFromReport:
            deviceNumber = item["Device Number"]
            deviceNumber = re.sub('[,]', '', deviceNumber)
            objReference = "DEV%s"%deviceNumber
            for key, value in item.iteritems():
                if key in ("Device Number", "Scan Rate"):
                    continue
                errMessage = "Verify returned data '%s' for device %s failed"%(key, deviceNumber)
                current = value.strip()
                propertyName = self._getColumnPropertyName(testData.dynamicColumns, key)
                propertyValue = self.testHelper.getPropertyValue(testData.site, deviceNumber, objReference, propertyName)
                expected = propertyValue.value
                
                # dealing None returned
                if expected is None:
                    expected = ""
                
                # removing white space at the header and tail
                expected = expected.strip()
                
                # substitute multiple whitespace with single whitespace
                expected = ' '.join(expected.split())
                
                # dealing datetime format
                if key == "Last Reset Time":
                    valueFormat = self._getColumnFormat(testData.dynamicColumns, key)
                    expected = self.testHelper.dataFormatHelper(expected, valueFormat[0], valueFormat[1]) 
                
                self.perform(self.assertEqual, current, expected, errMessage)
                
                
    def _test03(self, testData):
        """ Sanity Test Data Exchange Settings Report """
        
        # verify returned devices (Row)
        resultFromReport = self.testingReport.generatedReportGetData()
        current = []
        for item in resultFromReport:
            deviceNumber = item["Device Number"]
            deviceNumber = re.sub('[,]', '', deviceNumber)    # get rid of comma in string
            current.append(deviceNumber)
                
        expected = list(self.resultFromHelper.keys())
            
        errMessage = "Verify the accuracy of returned devices failed"
        self.perform(self.assertItemsEqual, current, expected, errMessage)
        
        # verify returned column data for each devices
        for item in resultFromReport:
            deviceNumber = item["Device Number"]
            deviceNumber = re.sub('[,]', '', deviceNumber)
            objReference = "DES1"
            for key, value in item.iteritems():
                if key in ("Device Number"):
                    continue
                errMessage = "Verify returned data '%s' for device %s failed"%(key, deviceNumber)
                current = value.strip()
                propertyName = self._getColumnPropertyName(testData.dynamicColumns, key)
                propertyValue = self.testHelper.getPropertyValue(testData.site, deviceNumber, objReference, propertyName)
                                
                expected = None
                if key == "Broadcast Destination":
                    groupObj = getattr(propertyValue[0], "address")
                    propertyObj = getattr(groupObj, "network-number")
                    expected = propertyObj.value
                else:
                    expected = propertyValue.value
                
                # dealing None returned
                if expected is None:
                    expected = ""
                
                # removing white space at the header and tail
                expected = expected.strip()
                
                # substitute multiple whitespace with single whitespace
                expected = ' '.join(expected.split())
                
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
        return result
                         
    
    
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
