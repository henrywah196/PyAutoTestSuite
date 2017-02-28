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
from libraries.eweb.PageObjects.BAS_Reports.Commissioning_Sheets import CommissioningSheetsPageObj
import os, time
from selenium import webdriver
import json
import re
from libraries.eweb.testhelper.BasReportTestHelper import BasReportTestHelper
from ddt import ddt, data
import string


# Global Settings
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "Commissioning_Sheets_Report.json"))


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
        Macros.SelectReportInstance("Building Automation\\Commissioning Sheets\\%s"%reportName)
        
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
            
            self.resultFromReport = self.testingReport.generatedReportGetData()
        
            # verify grouping label
            self._test01(testData)
            
            # verify device info
            self._test02(testData)
            
            # verify returned object in each group
            self._test03(testData)
            
            # verify grouping & sorting under inputs outputs table
            self._test04(testData)
    
    def _test01(self, testData):
        
        # verify grouping label
        result = self.testingReport.generatedReportGetData("device info only")
        current = []
        for item in result:
            current.append(item["header"])
            
        resultDeviceList = list(self.resultFromHelper.keys())
        resultDeviceList.sort()
        expected = []
        for deviceNumber in resultDeviceList:
            propertyValue = self.testHelper.getPropertyValue(testData.site, deviceNumber, "DEV%s"%deviceNumber, "Object_Name")
            deviceName = propertyValue.value
            expected.append("%s (%s)"%(deviceName, deviceNumber))
            
        self.perform(self.assertItemsEqual, current, expected, "Verify the accuracy of grouping label failed")
        
    
    def _test02(self, testData):
        # Verify devices info
        
        deviceInfoList = self.testingReport.generatedReportGetData(strKeyWord = "device info only")
        
        for item in deviceInfoList:
            
            groupingLabel = item["header"]
            # obtain the device number from grouping label
            deviceNumber = self._getDeviceNumberFromHeaderString(groupingLabel)
            siteName = testData.site
            objectReference = "DEV" + deviceNumber
            
            testHelper = self.testHelper
            
            # verify Model Name
            result = testHelper.getPropertyValue(siteName, deviceNumber, objectReference, "Model_Name")
            current = item["model"]
            expected = (result.value).strip()
            errMessage = "Verify device '%s' Model Name failed"%deviceNumber
            self.perform(self.assertEqual, current, expected, errMessage)
         
            # verify Location 
            result = testHelper.getPropertyValue(siteName, deviceNumber, objectReference, "Location")
            current = item["location"]
            expected = (result.value).strip()
            errMessage = "Verify device '%s' Location failed"%deviceNumber
            self.perform(self.assertEqual, current, expected, errMessage)
            
            # verify IP Address
            result = testHelper.getPropertyValue(siteName, deviceNumber, objectReference, "IP_Address")
            current = item["ip"]
            expected = None
            if result.value:
                expected = (result.value).strip()
            else:
                expected = ""
            errMessage = "Verify device '%s' IP Address failed"%deviceNumber
            self.perform(self.assertEqual, current, expected, errMessage)
            
            
    def _test03(self, testData):
        # verify returned object reference in each group
        resultFromReport = self.resultFromReport
        for item in resultFromReport:
            groupingLabel = item["header"]
            # obtain the device number from grouping label
            deviceNumber = self._getDeviceNumberFromHeaderString(groupingLabel)
            if not deviceNumber in self.resultFromHelper:
                continue
            objExpected = (self.resultFromHelper)[deviceNumber]
            
            if "inputs" in item:
                # verify returned inputs objects
                inputs = item["inputs"]
                inputsCurrent = []
                for input in inputs:
                    inputsCurrent.append(input["id"])
                
                inputsExpected = []
                for obj in objExpected:
                    if obj["object type"] in ("AI", "BI", "MI"):
                        inputsExpected.append(obj["object type"] + obj["object number"])
                        
                errMessage = "Verify the accuracy of returned Inputs object references for device '%s' failed"%deviceNumber
                self.perform(self.assertItemsEqual, inputsCurrent, inputsExpected, errMessage)
        
                
            if "outputs" in item:
                # verify returned outputs objects
                outputs = item["outputs"]
                outputsCurrent = []
                for output in outputs:
                    outputsCurrent.append(output["id"])
                
                outputsExpected = []
                for obj in objExpected:
                    if obj["object type"] in ("AO", "BO", "MO", "LO"):
                        outputsExpected.append(obj["object type"] + obj["object number"])
                
                errMessage = "Verify the accuracy of returned Outputs object references for device '%s' failed"%deviceNumber        
                self.perform(self.assertItemsEqual, outputsCurrent, outputsExpected, errMessage)
                
    def _test04(self, testData):
        # verify grouping & sorting under inputs outputs table
        resultFromReport = self.resultFromReport
        
        for item in resultFromReport:
            
            headerString = item["header"]
            deviceNumber = self._getDeviceNumberFromHeaderString(headerString)
            
            if "inputs" in item:
                current = []
                for inputObj in item["inputs"]:
                    current.append(inputObj["id"])
                expected = self._helperSortingOrdering(current)
                errMessage = "Verify Device '%s' Inputs table sorting and grouping failed."%deviceNumber
                self.perform(self.assertEqual, current, expected, errMessage)
            
            if "outputs" in item:
                current = []
                for outputObj in item["outputs"]:
                    current.append(outputObj["id"])
                expected = self._helperSortingOrdering(current)
                errMessage = "Verify Device '%s' Outputs table sorting and grouping failed."%deviceNumber
                self.perform(self.assertEqual, current, expected, errMessage)
                         
    
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
            
        self.testingReport.saveChange()
    
    
    def _getDeviceNumberFromHeaderString(self, headerString):
        """ return the device number part of the device header string """
        result = None
        m = re.search('\(\d+\)$', headerString)
        if m:
            found = m.group(0)
            return found[1:-1]
        
        
    def _getObjTypeFromObjRef(self, objectReference):
        """ helper to return adn object type part string from the object reference string
            for example, return AV from AV100
        """
        return re.sub(r'\d+', '', objectReference) 
    
    
    def _getObjNumberFromObjRef(self, objRefString):
        """ return the number part of an object reference string"""
        result = None
        m = re.search('\d+$', objRefString)
        if m:
            result = m.group(0)
        return result
        
        
    def _helperSortingOrdering(self, objList):
        """ helper to regenerate a list of grouped and ordered objet list """
        groupList = []
        for objRef in objList:
            objNumber = self._getObjNumberFromObjRef(objRef)
            if int(objNumber) < 100:
                if 99 not in groupList:
                    groupList.append(99)
            else:
                patNumber = objNumber[:-2] + "00"
                if int(patNumber) not in groupList:
                    groupList.append(int(patNumber))
        groupList.sort(key=int)
        
        groupDic = {}
        for item in groupList:
            groupDic[item] = []
            
        for objRef in objList:
            objNumber = self._getObjNumberFromObjRef(objRef)
            if int(objNumber) < 100:
                groupDic[99].append(objRef)
            else:
                patNumber = objNumber[:-2] + "00"
                if int(patNumber) in groupDic:
                    groupDic[int(patNumber)].append(objRef)
                    
        for key, value in groupDic.iteritems():
            objTypeGroup = {"AI": [], "AO": [], "BI": [], "BO": [], "MI": [], "MO": [], "LO": [], "PI": []}
            for objRef in value:
                objType = self._getObjTypeFromObjRef(objRef)
                objNumber = self._getObjNumberFromObjRef(objRef)
                if objType in objTypeGroup:
                    objTypeGroup[objType].append(int(objNumber))
            for k, v in objTypeGroup.iteritems():
                if len(v) > 0:
                    v.sort(key=int)
            groupDic[key] = objTypeGroup
                    
        result = []
        typeList = ["AI", "BI", "MI", "PI", "AO", "BO", "LO", "MO"]
        for item in groupList:
            objTypeGroup = groupDic[item]
            for objType in typeList:
                if len(objTypeGroup[objType]) > 0:
                    for objNumber in objTypeGroup[objType]:
                        result.append(objType + str(objNumber))
        return result
    

if __name__ == "__main__":
    unittest.main()
