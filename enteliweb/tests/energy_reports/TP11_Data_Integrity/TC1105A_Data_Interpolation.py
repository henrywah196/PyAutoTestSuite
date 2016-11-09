'''
Name: TC1105_Data_Interpolation.py
Description: this test case will verify the data integrity of imported energy data

             test01 will verify the timestamp should interpolated to 5 minutes interval
             test02 will verify the imported start time and compare it with the start time of raw data
             test03 will verify the imported finish time and compare it with the one in report_rate_tlinstance table
             test04 will verify no duplicated timestamp
             test05 will verify no missing timestamp (samples)
             test06 will verify energy sample value should > = 0 (except OAT datapoint).
Created on May 11, 2013
@author: hwang
'''
import time, datetime
import settings
from libraries.eweb.DataObjects.WebGroup import WebGroupDBObj
from libraries.eweb.DataObjects.Historian import HistorianDBObj
from libraries.eweb.DataObjects.CopperCube import CopperCubeDBObj
from libraries.PyAutoTestCase import *
from ddt import ddt, data
from pytz import timezone    # import timezone to veirfy daylight savings
from pytz import NonExistentTimeError
from pytz import AmbiguousTimeError
from test.test_sax import start


# Global settings
TimeZone = settings.TimeZone
#TLInstance_Under_Test = ["//RV Site/1100.AV201.Value",
#                         "//RV Site/1100.AV101.Value"]    # comment it if you want test all datapoint


def getTestingData():
    """
    return a list testing TL reference
    """
    webgroup = WebGroupDBObj()
    if 'TLInstance_Under_Test' not in globals():
        global TLInstance_Under_Test
        TLInstance_Under_Test = None
    result = webgroup.getReport_Rate_Tlinstances(TLInstance_Under_Test)
    del webgroup
    return result


@ddt
class TC1105A_DataInterpolation(TestCaseTemplate):
    
    
    def setUp(self):
        super(TC1105A_DataInterpolation, self).setUp()
        self.webgroup = WebGroupDBObj()
        self.archiver = None
        
        
    def tearDown(self):
        super(TC1105A_DataInterpolation, self).tearDown()
        del self.webgroup
        if self.archiver is not None:
            del self.archiver
    
    
    #@unittest.skip("") 
    @data(*getTestingData())
    def test01(self, testData):
        # Update doc string based on test data
        self._testMethodDoc = "Verify Timestamp interpolation for [%s]"%testData["FullRef"]
        
        FullRef = testData["FullRef"]
        
        # get timestamps which is not interpolated in 5 minutes interval
        result = self.webgroup.validateTimeStampInterpolation(FullRef)
        
        errMessage = "Verify timestamps should interpolated to 5 minutes interval"
        self.verify_IsEqual(None, result, errMessage)
      
        
    #@unittest.skip("")    
    @data(*getTestingData())
    def test02(self, testData):
        # Update doc string based on test data
        self._testMethodDoc = "Verify Start (timestamp) for [%s]"%testData["FullRef"]
        
        FullRef = testData["FullRef"]
        
        # obtain the tl instance first timestamp from report_rate_data table
        current = self.webgroup.getTLInstanceStart(FullRef, from_Data_Table=True)
        
        # confirm the raw DB Data source (Historian or CopperCube) and make a connection
        self.confirmArchiverDB(testData)
        
        # obtain the first timestamp from raw DB source (Historian or CopperCube)
        tlinstanceID_Raw = self.webgroup.getRawTlinstanceID(FullRef)
        expected = self.archiver.getTLInstanceStart(tlinstanceID_Raw)
            
        # check and using baseline start if tl reference has baseline data assigned
        containsBaselineData = self.webgroup.containsBaselineData(FullRef)
        if containsBaselineData:
            expected = self.webgroup.getTLInstanceBaseLineStart(FullRef)
            
        print "Local: %s"%current
        if containsBaselineData:
            print "Raw(Baseline): %s\n"%expected
        else:
            print "Raw: %s\n"%expected
            
        difference = current - expected
        if difference < datetime.timedelta(0):
            difference = expected - current
            
        errMessage = "The difference between local and raw Start (timestamp) should less than 5 minutes"
        self.verify_IsTrue(difference < datetime.timedelta(minutes=5), errMessage)
        
        
    @data(*getTestingData())
    def test03(self, testData):
        # Update doc string based on test data
        self._testMethodDoc = "Verify Finish (timestamp) for [%s]"%testData["FullRef"]
        
        # obtain the Finish (timestamp) from report_rate_data table
        FullRef = testData["FullRef"]
        current = self.webgroup.getTLInstanceFinish(FullRef, from_Data_Table=True)
        
        # obtain the Finish (timestamp) from report_rate_tlinstance table
        expected = self.webgroup.getTLInstanceFinish(FullRef)
        
        print "Local: %s"%current
        print "Raw: %s"%expected
        difference = expected - current
        print "difference: %s\n"%difference
        
        errMessage = "The difference between local and raw Finish (timestamp) should not more than 10 minutes"
        result = (difference >= datetime.timedelta(0)) and (difference <= datetime.timedelta(minutes=10))
        self.verify_IsTrue(result, errMessage, HaltOnErr=False)
        
        # verify Baseline finish
        containsBaselineData = self.webgroup.containsBaselineData(FullRef)
        if containsBaselineData:
            current = self.webgroup.getTLInstanceBaseLineFinish(FullRef, from_Tlinstance_Table=True)    # baseline finish from report_rate_tlinstance table
            expected = self.webgroup.getTLInstanceBaseLineFinish(FullRef)    # from baseline table
            print "Local(BaselineFinish): %s"%current
            print "Raw: %s"%expected
            difference = current - expected
            print "difference: %s\n"%difference
            errMessage = "The difference between local and raw BaselineFinish (timestamp) should not more than 5 minutes"
            result = (difference > datetime.timedelta(0)) and (difference <= datetime.timedelta(minutes=5))
            self.verify_IsTrue(result, errMessage, HaltOnErr=False)
        
        
    #@unittest.skip("") 
    @data(*getTestingData())
    def test04(self, testData):
        # Update doc string based on test data
        self._testMethodDoc = "Verify no duplicated Timestamp for [%s]"%testData["FullRef"]
        
        FullRef = testData["FullRef"]
        
        # get timestamps which found duplicated
        result = self.webgroup.validateTimeStampDuplication(FullRef)
        
        errMessage = "Verify timestamps should unique (no duplication)"
        self.verify_IsEqual(None, result, errMessage)
   
    #@unittest.skip("")     
    @data(*getTestingData())
    def test05(self, testData):
        # Update doc string based on test data
        self._testMethodDoc = "Verify no missing samples for [%s]"%testData["FullRef"]
        
        self.testData = testData
        FullRef = self.testData["FullRef"]
        
        #define interval 5 minutes
        interval = datetime.timedelta(minutes = 5)
        
        #obtain Start, Finish (timestamp) from Report_Rate_data table
        startTime = self.webgroup.getTLInstanceStart(FullRef, from_Data_Table=True)
        finishTime = self.webgroup.getTLInstanceFinish(FullRef, from_Data_Table=True)
        containsBaselineData = self.webgroup.containsBaselineData(FullRef)
        
        current_set = set(self.webgroup.getTLInstanceTimeStamps(FullRef))
        expected_set = self._getTimestampSuperSet(startTime, finishTime, interval)
        result = sorted(expected_set - current_set)
        if len(result) > 0:
            for item in result:
                if containsBaselineData and self._isBaselineGap(item):
                    continue
                elif self._isDayLightSavings(item.strftime("%Y-%m-%d %H:%M:%S")):
                    continue
                else:
                    errMessage = "Verify Timestamp is found: %s"%item.strftime("%Y-%m-%d %H:%M:%S")
                    self.verify_IsTrue(False, errMessage, HaltOnErr=False)
                    
                
    @data(*getTestingData())
    def test06(self, testData):
        # Update doc string based on test data
        self._testMethodDoc = "Verify sample energy value for [%s]"%testData["FullRef"]
        
        FullRef = testData["FullRef"]
        
        # skip OAT datapoint
        cursor = self.webgroup.cursor.execute("select Type from datapoint_detail where fullref = ?", FullRef)
        row = cursor.fetchone()
        if row.Type == "Temperature":
            self.skipTest("skip out door temperature datapoint")
            
        # verify energy data value should large than or equal to zero
        result = None
        cursor = self.webgroup.cursor.execute("select * from report_rate_data where tlinstance = ? and value < 0", self.webgroup.getTLInstanceID(FullRef))
        rows = cursor.fetchall()
        if len(rows) > 0:
            result = []
            for row in rows:
                item = []
                item.append(row.Timestamp.strftime("%Y-%m-%d %H:%M:%S"))
                item.append(row.Value)
                result.append(item)
        errMessage = "Verify energy sample value should Large than or equal to 0"
        self.verify_IsEqual(None, result, errMessage)
            
                
                    
    #@unittest.skip("")     
    @data(*getTestingData())
    def oldtest05(self, testData):
        # Update doc string based on test data
        self._testMethodDoc = "Verify no missing samples for [%s]"%testData["FullRef"]
        
        FullRef = testData["FullRef"]
        tlinstanceID = self.webgroup.getTLInstanceID(FullRef)
        
        #define interval 5 minutes
        interval = datetime.timedelta(minutes = 5)
        
        #obtain Start, Finish (timestamp) from Report_Rate_data table
        startTime = self.webgroup.getTLInstanceStart(FullRef, from_Data_Table=True)
        finishTime = self.webgroup.getTLInstanceFinish(FullRef, from_Data_Table=True)
        
        recordNumber = 0
        while startTime <= finishTime:
            recordNumber = recordNumber + 1
            found = self.webgroup.isTimestampExisting(FullRef, startTime)
            if not found:
                # verify if it is daylight saving
                if self._isDayLightSavings(startTime.strftime("%Y-%m-%d %H:%M:%S")):
                    recordNumber = recordNumber - 1
                else:
                    errMessage = "Verify Timestamp is found: %s"%startTime.strftime("%Y-%m-%d %H:%M:%S")
                    self.verify_IsTrue(False, errMessage, HaltOnErr=False)
            startTime = startTime + interval
     
     
    ####################
    # Helper methods
    ####################
    def _isDayLightSavings(self, timeStamp):
        ''' verify if the given timestamp is in the day light savings boundary '''
        myTimeZone = timezone(TimeZone)
        try:
            myTimeZone.localize(datetime.datetime.strptime(timeStamp, "%Y-%m-%d %H:%M:%S"), is_dst=None)
            return False
        except AmbiguousTimeError:
            return False
        except NonExistentTimeError:
            return True
        
        
    def _isBaselineGap(self, timeStamp):
        """
        verify if the given timestamp is in between the baseline finish and raw (historian) start
        """
        if not hasattr(self, 'beginTime'):
            self.beginTime = self.webgroup.getTLInstanceBaseLineFinish(self.testData["FullRef"], from_Tlinstance_Table=True)
        
        if not hasattr(self, 'endTime'):
            self.confirmArchiverDB(self.testData)
            # obtain the first timestamp from raw DB source (Historian or CopperCube)
            tlinstanceID_Raw = self.webgroup.getRawTlinstanceID(self.testData["FullRef"])
            self.endTime = self.archiver.getTLInstanceStart(tlinstanceID_Raw)
        if timeStamp >= self.beginTime and timeStamp < self.endTime:
            return True
        else:
            return False
        
       
        
    def confirmArchiverDB(self, testData):
        """
        based one the tl instnace information,confirm the raw DB 
        Data source (Historian or CopperCube) and make a connection
        """ 
        # confirm the raw DB Data source (Historian or CopperCube) and make a connection
        for key, value in (settings.ArchiverDB).iteritems():
            if (testData["Host"]).lower() == (value["SERVER"]).lower():
                if value["TYPE"] == "Historian":
                    self.archiver = HistorianDBObj(value)
                elif value["TYPE"] == "CopperCube":
                    self.archiver = CopperCubeDBObj(value)
                break
            
            
    def _getTimestampSuperSet(self, start, end, delta):
        """
        helper to return the expected timestamp list when epxected interval
        """
        result = []
        curr = start
        while curr < end:
            result.append(curr)
            curr +=delta
        return set(result)
        

if __name__ == "__main__":
    unittest.main()
