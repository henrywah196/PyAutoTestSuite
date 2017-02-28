########################################################################################
# Test Case: Validation of objects grouping and ordering in "Inputs" and "Outputs" table
########################################################################################
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
import re


# Global Settings
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "C88439.json"))


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
        if result is None:
            result = []
        result.append(myTestData)
        
    return result


class TC88439(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        super(TC88439, cls).setUpClass()
        cls.Browser = settings.BROWSER
        cls.Host = settings.HOST
        cls.Username = settings.USERNAME
        cls.Password = settings.PASSWORD
        
        profile = webdriver.FirefoxProfile()
        profile.set_preference('webdriver_enable_native_events', True)
        Macros.LoadEnteliWEB(cls.Host, cls.Browser, cls.Username, cls.Password, ff_profile=profile)
        cls.accordion = AccordionPageObj()
        
        cls.testData = getTestingData()[0]
        
        # setup testing report instance
        cls._setupReportInstance()
        
        # select testing report instance
        reportName    = cls.testData.reportName
        Macros.SelectReportInstance("Building Automation\\Commissioning Sheets\\%s"%reportName)
        
        # generating report
        result = cls.commissioningSheetsReport.generatingReport(timeout=600)
        assert result == True, "failed to generate report"
        
        # verify no blank report returned
        result = cls.commissioningSheetsReport.generatedReportHasNoData()
        assert result == False, "No data returned in the generated report"
        
        # get data from generated report
        cls.reportData = cls.commissioningSheetsReport.generatedReportGetData()
               
              
    @classmethod
    def tearDownClass(cls):
        super(TC88439, cls).tearDownClass()
        Macros.CloseEnteliWEB()
    
    def setUp(self):
        super(TC88439, self).setUp()
        
        self.longMessage = True
        self.cls = self.__class__
        

    def tearDown(self):
        super(TC88439, self).tearDown()
        

    #@unittest.skip("")
    def test01(self):
        self._testMethodDoc = 'Verify data grouping ordering in Inputs table'
        
        reportData = self.cls.reportData
        
        for item in reportData:
            
            headerString = item["header"]
            deviceNumber = self._getDeviceNumberFromHeaderString(headerString)
            
            if "inputs" in item:
                current = []
                for inputObj in item["inputs"]:
                    current.append(inputObj["id"])
                expected = self._helperSortingOrdering(current)
                errMessage = "Verify Device '%s' Inputs table sorting and grouping failed."%deviceNumber
                self.perform(self.assertEqual, current, expected, errMessage)
                '''
                print deviceNumber
                print current
                print expected
                self.assertEqual(current, expected, errMessage)
                '''
            
    def test02(self):
        self._testMethodDoc = 'Verify data grouping ordering in Outputs table'
        
        reportData = self.cls.reportData
        
        for item in reportData:
            
            headerString = item["header"]
            deviceNumber = self._getDeviceNumberFromHeaderString(headerString)
            
            if "outputs" in item:
                current = []
                for outputObj in item["outputs"]:
                    current.append(outputObj["id"])
                expected = self._helperSortingOrdering(current)
                errMessage = "Verify Device '%s' Outputs table sorting and grouping failed."%deviceNumber
                self.perform(self.assertEqual, current, expected, errMessage)
                '''
                print deviceNumber
                print current
                print expected
                self.assertEqual(current, expected, errMessage)
                '''
            
        
        
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
          
        
    def _getDeviceNumberFromHeaderString(self, headerString):
        """ return the device number part of the device header string """
        result = None
        m = re.search('\(\d+\)$', headerString)
        if m:
            found = m.group(0)
            result = found[1:-1]
        return result
   
    @classmethod  
    def _setupReportInstance(cls):
        
        reportName    = cls.testData.reportName
        reportTitle   = cls.testData.reportTitle
        site          = cls.testData.site
        deviceRange   = cls.testData.deviceRange
        objectFilters = cls.testData.objectFilters
        
        if Macros.isReportInstanceExisting("Building Automation\\Commissioning Sheets\\%s"%reportName):
            Macros.SelectReportInstance("Building Automation\\Commissioning Sheets\\%s"%reportName)
        else:
            Macros.SelectReportInstance("Building Automation\\Commissioning Sheets")
        time.sleep(10)
        
        cls.commissioningSheetsReport = CommissioningSheetsPageObj()
        
        cls.commissioningSheetsReport.reportName = reportName
        cls.commissioningSheetsReport.reportTitle = reportTitle
        cls.commissioningSheetsReport.site = site
        cls.commissioningSheetsReport.deviceRange = deviceRange
        
        # delete the default object filter
        cls.commissioningSheetsReport.deleteObjectFilter(1)
        
        for objectFilter in objectFilters:
            cls.commissioningSheetsReport.addObjectFilter(objectFilter)
            
        cls.commissioningSheetsReport.saveChange()
        

if __name__ == "__main__":
    unittest.main()
