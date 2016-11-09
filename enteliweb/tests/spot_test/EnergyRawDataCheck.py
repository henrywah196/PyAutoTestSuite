'''
Created on Dec 30, 2015

@author: hwang
'''
import time, datetime
import settings
from libraries.eweb.DataObjects.WebGroup import WebGroupDBObj
from libraries.eweb.DataObjects.CopperCube import CopperCubeDBObj
from libraries.eweb.DataObjects.Historian import HistorianDBObj
from libraries.PyAutoTestCase import *
from ddt import ddt, data
import pytz    # import timezone to veirfy daylight savings
from pytz import NonExistentTimeError
import random
import calendar, math


# Global settings
TimeZone = settings.TimeZone
TLInstance_Under_Test = ["//RV Site/1100.AV102.Value", "//RV Site/1100.AV201.Value"]


def getTestingData():
    """
    return a list testing TL reference
    """
    if 'TESTING_DATA_EnergyRawDataCheck' not in globals():
        webgroup = WebGroupDBObj()
        if 'TLInstance_Under_Test' not in globals():
            global TLInstance_Under_Test
            TLInstance_Under_Test = None
        result = webgroup.getReport_Rate_Tlinstances(TLInstance_Under_Test)
        resultNew = []
        for item in result:
            if "Date Range" in item:
                itemNew = dict(item)
                resultNew.append(itemNew)
            else:
                tlinstanceID = webgroup.getTLInstanceID(item["FullRef"])
        
                # randomly pickup a year
                cursor = webgroup.cursor.execute("select distinct year(timestamp) as year from report_rate_data where tlinstance = ?", tlinstanceID)
                rows = cursor.fetchall()
                i = 0
                while (not len(rows) > 0) and i < 5:
                    time.sleep(15)
                    cursor = webgroup.cursor.execute("select distinct year(timestamp) as year from report_rate_data where tlinstance = ?", tlinstanceID)
                    rows = cursor.fetchall()
                    i = i + 1
                if len(rows) > 0:
                    try:
                        random_index = random.randrange(0, len(rows) - 1)
                        row = rows[random_index]
                    except:
                        row = rows[len(rows) - 1]
                    itemNew = dict(item)
                    itemNew["Date Range"]= {"year": row.year}
                    resultNew.append(itemNew)
            
                # randomly pickup a month
                cursor = webgroup.cursor.execute("select distinct date_format(timestamp, '%Y-%m') as month from report_rate_data where tlinstance = ?", tlinstanceID)
                rows = cursor.fetchall()
                i = 0
                while (not len(rows) > 0) and i < 5:
                    time.sleep(15)
                    cursor = webgroup.cursor.execute("select distinct date_format(timestamp, '%Y-%m') as month from report_rate_data where tlinstance = ?", tlinstanceID)
                    rows = cursor.fetchall()
                    i = i + 1
                if len(rows) > 0:
                    try:
                        random_index = random.randrange(0, len(rows) - 1)
                        row = rows[random_index]
                    except:
                        row = rows[len(rows) - 1]
                    itemNew = dict(item)
                    itemNew["Date Range"]= {"month": row.month}
                    resultNew.append(itemNew)
            
                # randomly pickup a day
                cursor = webgroup.cursor.execute("select distinct date(timestamp) as day from report_rate_data where tlinstance = ?", tlinstanceID)
                rows = cursor.fetchall()
                i = 0
                while (not len(rows) > 0) and i < 5:
                    time.sleep(15)
                    cursor = webgroup.cursor.execute("select distinct date(timestamp) as day from report_rate_data where tlinstance = ?", tlinstanceID)
                    rows = cursor.fetchall()
                    i = i + 1
                if len(rows) > 0:
                    try:
                        random_index = random.randrange(0, len(rows) - 1)
                        row = rows[random_index]
                    except:
                        row = rows[len(rows) - 1]
                    itemNew = dict(item)
                    itemNew["Date Range"]= {"day": row.day}
                    resultNew.append(itemNew)
            
                # randomly pickup an hour
                cursor = webgroup.cursor.execute("select distinct date_format(timestamp, '%Y-%m-%d %H') as hour from report_rate_data where tlinstance = ?", tlinstanceID)
                rows = cursor.fetchall()
                i = 0
                while (not len(rows) > 0) and i < 5:
                    time.sleep(15)
                    cursor = webgroup.cursor.execute("select distinct date_format(timestamp, '%Y-%m-%d %H') as hour from report_rate_data where tlinstance = ?", tlinstanceID)
                    rows = cursor.fetchall()
                    i = i + 1
                if len(rows) > 0:
                    try:
                        random_index = random.randrange(0, len(rows) - 1)
                        row = rows[random_index]
                    except:
                        row = rows[len(rows) - 1]
                    itemNew = dict(item)
                    itemNew["Date Range"]= {"hour": row.hour}
                    resultNew.append(itemNew)
    
        del webgroup
    
        global TESTING_DATA_EnergyRawDataCheck
        TESTING_DATA_EnergyRawDataCheck = resultNew
        
    return TESTING_DATA_EnergyRawDataCheck
    


@ddt
class EnergyRawDataCheck(TestCaseTemplate):
    
    def setUp(self):
        super(EnergyRawDataCheck, self).setUp()
        self.webgroup = WebGroupDBObj()
        self.archiver = None
        
    def tearDown(self):
        super(EnergyRawDataCheck, self).tearDown()
        del self.webgroup
        if self.archiver is not None:
            del self.archiver
        '''    
        if 'TESTING_DATA_EnergyRawDataCheck' in globals():
            global TESTING_DATA_EnergyRawDataCheck
            TESTING_DATA_EnergyRawDataCheck = None
        '''
        
    
    #@unittest.skip("")    
    @data(*getTestingData())
    def test01(self, testData):
        
        fullRef = testData["FullRef"]
        archiverType = testData["Type"]
        dateRange = testData["Date Range"]
        dateRange_Type = None
        dateRange_Value = None
        for key in dateRange:
            dateRange_Type = key
            dateRange_Value = dateRange[key]
            break
        datetimeStart, datetimeFinish = self._datetimeStartFinish(testData)
        
        # Update doc string based on test data
        self._testMethodDoc = "Verify datapoint '%s' consistency of sequence number for %s: %s"%(fullRef, dateRange_Type, dateRange_Value)
        
        # confirm the raw DB Data source (Historian or CopperCube) and make a connection
        self.confirmArchiverDB(testData)
        
        # obtain the first timestamp from raw DB source (Historian or CopperCube)
        rawTLInstanceTable = self.webgroup.getRawTlinstanceID(fullRef)
        
        if archiverType == "CopperCube":
            cursor = self.archiver.cursor.execute("select seq from %s where ts between '%s' and '%s' and variant in (2,4,5) order by seq asc"%(rawTLInstanceTable, datetimeStart, datetimeFinish))
        else:
            cursor = self.archiver.cursor.execute("select RecordNumber as seq from tldata where tlinstance = ? and type = 0 and timestamp between ? and ? order by RecordNumber asc", rawTLInstanceTable, datetimeStart, datetimeFinish)
        rows = cursor.fetchall()
            
        # verify consistency of sequence number
        current = None
        for row in rows:
            if current is None:
                current = row.seq
            else:
                if not (row.seq > current):
                    errMessage =  "current seq: %s is large than previous one: %s"%(row.seq, current)
                    self.verify_IsTrue(False, errMessage, HaltOnErr=False)
                    current = row.seq
                else:
                    current = row.seq
        
        
    #@unittest.skip("")    
    @data(*getTestingData())
    def test02(self, testData):
        
        fullRef = testData["FullRef"]
        archiverType = testData["Type"]
        dateRange = testData["Date Range"]
        dateRange_Type = None
        dateRange_Value = None
        for key in dateRange:
            dateRange_Type = key
            dateRange_Value = dateRange[key]
            break
        datetimeStart, datetimeFinish = self._datetimeStartFinish(testData)
        
        # Update doc string based on test data
        self._testMethodDoc = "Verify datapoint '%s' consistency of timestamp for %s: %s"%(fullRef, dateRange_Type, dateRange_Value)
        
        # confirm the raw DB Data source (Historian or CopperCube) and make a connection
        self.confirmArchiverDB(testData)
        
        # obtain the first timestamp from raw DB source (Historian or CopperCube)
        rawTLInstanceTable = self.webgroup.getRawTlinstanceID(fullRef)
        
        if archiverType == "CopperCube":
            cursor = self.archiver.cursor.execute("select seq, ts from %s where ts between '%s' and '%s' and variant in (2,4,5) order by seq asc"%(rawTLInstanceTable, datetimeStart, datetimeFinish))
        else:
            cursor = self.archiver.cursor.execute("select RecordNumber as seq, timestamp as ts from tldata where tlinstance = ? and type = 0 and timestamp between ? and ? order by RecordNumber asc", rawTLInstanceTable, datetimeStart, datetimeFinish)
        rows = cursor.fetchall()
        
        # verify consistency of timestamp
        current = None
        for row in rows:
            if not current:
                current = row.ts
            else:
                if not (row.ts > current):
                    
                    # verify if it is DST boundary
                    culprit = row.ts
                    year = culprit.year
                    dstTransitions = self._getDSTTransitionTimes(TimeZone, year)
                    culprit = datetime.datetime.strftime(culprit, "%Y-%m-%d %H:%M:%S")
                    if culprit != dstTransitions[1]:
                        errMessage = "current timestamp (seq: %s): %s is large than previous one: %s"%(row.seq, row.ts, current)
                        self.verify_IsTrue(False, errMessage, HaltOnErr=False)
                    current = row.ts
                else:
                    current = row.ts
        
        
    #@unittest.skip("")    
    @data(*getTestingData())
    def test03(self, testData):
        
        fullRef = testData["FullRef"]
        archiverType = testData["Type"]
        dateRange = testData["Date Range"]
        dateRange_Type = None
        dateRange_Value = None
        for key in dateRange:
            dateRange_Type = key
            dateRange_Value = dateRange[key]
            break
        datetimeStart, datetimeFinish = self._datetimeStartFinish(testData)
        
        # Update doc string based on test data
        self._testMethodDoc = "Verify datapoint '%s' consistency of raw data for %s: %s"%(fullRef, dateRange_Type, dateRange_Value)
        
        # verify the datapoint type (Consumption or Demand or OAT) and skip test if it is not Consumption 
        tlInstanceType = self.webgroup.getTLInstanceType(fullRef)
        datapointType = self.webgroup.DataPointType[tlInstanceType]
        if datapointType != "CONSUMPTION":
            self.skipTest("skip non-CONSUMPTION datapoint")
        
        # confirm the raw DB Data source (Historian or CopperCube) and make a connection
        self.confirmArchiverDB(testData)
        
        # obtain the first timestamp from raw DB source (Historian or CopperCube)
        rawTLInstanceTable = self.webgroup.getRawTlinstanceID(fullRef)
        
        if archiverType == "CopperCube":
            cursor = self.archiver.cursor.execute("select seq, data, ts from %s where ts between '%s' and '%s' and variant in (2,4,5) order by seq asc"%(rawTLInstanceTable, datetimeStart, datetimeFinish))
        else:
            cursor = self.archiver.cursor.execute("select RecordNumber as seq, cast(Data as decimal(38,10)) as data, timestamp as ts from tldata where tlinstance = ? and type = 0 and timestamp between ? and ? order by RecordNumber asc", rawTLInstanceTable, datetimeStart, datetimeFinish)    
        rows = cursor.fetchall()
        
        # verify consistency of data
        current = None
        for row in rows:
            if not current:
                current = row.data
            else:
                if not (row.data >= current):
                    errMessage = "current data (seq: %s): %s is large than previous one: %s"%(row.seq, row.data, current)
                    self.verify_IsTrue(False, errMessage, HaltOnErr=False)
                    current = row.data
                else:
                    current = row.data
    
    
    #@unittest.skip("")    
    @data(*getTestingData())
    def test04(self, testData):
        
        fullRef = testData["FullRef"]
        archiverType = testData["Type"]
        dateRange = testData["Date Range"]
        dateRange_Type = None
        dateRange_Value = None
        for key in dateRange:
            dateRange_Type = key
            dateRange_Value = dateRange[key]
            break
        datetimeStart, datetimeFinish = self._datetimeStartFinish(testData)
        
        # Update doc string based on test data
        self._testMethodDoc = "Verify datapoint '%s' raw data missing samples for %s: %s"%(fullRef, dateRange_Type, dateRange_Value)
        
        # verify the datapoint type (Consumption or Demand or OAT) and skip test if it is not Consumption 
        tlInstanceType = self.webgroup.getTLInstanceType(fullRef)
        datapointType = self.webgroup.DataPointType[tlInstanceType]
        if datapointType != "CONSUMPTION":
            self.skipTest("skip non-CONSUMPTION datapoint")
        
        # confirm the raw DB Data source (Historian or CopperCube) and make a connection
        self.confirmArchiverDB(testData)
        
        # obtain the first timestamp from raw DB source (Historian or CopperCube)
        rawTLInstanceTable = self.webgroup.getRawTlinstanceID(fullRef)
        
        # get the sampling interval of the raw tlinstance
        tlReference = self.webgroup.getRawTlinstanceID(fullRef, ReturnTableName=False)
        sampleInterval = self.archiver.getSampleInterval(tlReference)
        
        if archiverType == "CopperCube":
            cursor = self.archiver.cursor.execute("select seq, data, ts from %s where ts between '%s' and '%s' and variant in (2,4,5) order by seq asc"%(rawTLInstanceTable, datetimeStart, datetimeFinish))
        else:
            cursor = self.archiver.cursor.execute("select RecordNumber as seq, cast(Data as decimal(38,10)) as data, timestamp as ts from tldata where tlinstance = ? and type = 0 and timestamp between ? and ? order by RecordNumber asc", rawTLInstanceTable, datetimeStart, datetimeFinish)
        rows = cursor.fetchall()

        previousRow = None        
        for row in rows:
            if previousRow is None:
                previousRow = row
                continue
            else:
                diff = (row.ts - previousRow.ts).total_seconds()
                diff = int(math.ceil(diff))
                if diff - sampleInterval > 60:
                    
                    # verify if it is DST boundary
                    culprit = row.ts - datetime.timedelta(hours=1)
                    culprit = datetime.datetime.strftime(culprit, "%Y-%m-%d %H:%M:%S")
                    if not self._isDayLightSavings(culprit):
                        errMessage = "missing samples found between %s and %s"%(previousRow.seq, row.seq)
                        self.verify_IsTrue(False, errMessage, HaltOnErr=False)
                previousRow = row
                
                
    #@unittest.skip("")    
    @data(*getTestingData())
    def test05(self, testData):
        
        fullRef = testData["FullRef"]
        archiverType = testData["Type"]
        dateRange = testData["Date Range"]
        dateRange_Type = None
        dateRange_Value = None
        for key in dateRange:
            dateRange_Type = key
            dateRange_Value = dateRange[key]
            break
        datetimeStart, datetimeFinish = self._datetimeStartFinish(testData)
        
        # Update doc string based on test data
        self._testMethodDoc = "Verify datapoint '%s' raw data meter reset for %s: %s"%(fullRef, dateRange_Type, dateRange_Value)
        
        # verify the datapoint type (Consumption or Demand or OAT) and skip test if it is not Consumption 
        tlInstanceType = self.webgroup.getTLInstanceType(fullRef)
        datapointType = self.webgroup.DataPointType[tlInstanceType]
        if datapointType != "CONSUMPTION":
            self.skipTest("skip non-CONSUMPTION datapoint")
        
        # confirm the raw DB Data source (Historian or CopperCube) and make a connection
        self.confirmArchiverDB(testData)
        
        # obtain the first timestamp from raw DB source (Historian or CopperCube)
        rawTLInstanceTable = self.webgroup.getRawTlinstanceID(fullRef)
        
        if archiverType == "CopperCube":
            cursor = self.archiver.cursor.execute("select seq, data, ts from %s where ts between '%s' and '%s' and variant in (2,4,5) order by seq asc"%(rawTLInstanceTable, datetimeStart, datetimeFinish))
        else:
            cursor = self.archiver.cursor.execute("select RecordNumber as seq, cast(Data as decimal(38,10)) as data, timestamp as ts from tldata where tlinstance = ? and type = 0 and timestamp between ? and ? order by RecordNumber asc", rawTLInstanceTable, datetimeStart, datetimeFinish)
        rows = cursor.fetchall()
        previousRow = None
        for row in rows:
            if not previousRow:
                previousRow = row
            else:
                current = row.data
                expected = previousRow.data / 2
                if current <= expected:
                    errMessage =  "meter reset found between %s and %s"%(previousRow.seq, row.seq)
                    self.verify_IsTrue(False, errMessage, HaltOnErr=False)
                previousRow = row
               
     
    ####################
    # Helper methods
    ####################
    def _datetimeStartFinish(self, testData):
        """ 
        helper function to return the start and finsih 
        date time from Date Range of test data in the format of
        yyyy-mm-dd hh:mm:ss
        """
        dateRange = testData["Date Range"]
        dateRange_Type = None
        dateRange_Value = None
        datetimeStart = None
        datetimeFinish = None
        for key in dateRange:
            dateRange_Type = key
            dateRange_Value = dateRange[key]
            break
        if dateRange_Type == "year":
            datetimeStart = "%s-01-01 00:00:00"%dateRange_Value
            datetimeFinish = "%s-12-31 23:59:59"%dateRange_Value
        elif dateRange_Type == "month":
            year = int((dateRange_Value.split("-"))[0])
            month = int((dateRange_Value.split("-"))[1])
            days = (calendar.monthrange(year, month))[1]
            datetimeStart = "%s-01 00:00:00"%dateRange_Value
            datetimeFinish = "%s-%s 23:59:59"%(dateRange_Value, days)
        elif dateRange_Type == "day":
            datetimeStart = dateRange_Value.strftime("%Y-%m-%d 00:00:00")
            datetimeFinish = dateRange_Value.strftime("%Y-%m-%d 23:59:59")
        elif dateRange_Type == "hour":
            datetimeStart = "%s:00:00"%dateRange_Value
            datetimeFinish = "%s:59:59"%dateRange_Value
        
        return datetimeStart, datetimeFinish
        
    
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
    
    
    def _isDayLightSavings(self, timeStamp):
        ''' verify if the given timestamp is in the day light savings boundary '''
        myTimeZone = pytz.timezone(TimeZone)
        try:
            myTimeZone.localize(datetime.datetime.strptime(timeStamp, "%Y-%m-%d %H:%M:%S"), is_dst=None)
            return False
        except NonExistentTimeError:
            return True  
        
    
    def _getDSTTransitionTimes(self, timezoneString, year):
        ''' 
        with the give year, return a list of datetime string
        to represent the DST start and finish of the given timezone
        the first item in the list is DST start, the second is DST end
        '''
        myTimeZone = pytz.timezone(timezoneString)
        utc_transition_times = myTimeZone._utc_transition_times
        targets = []
        for item in utc_transition_times:
            if item.year == year:
                targets.append(item) 
        if len(targets) > 0:
            utc_dt01 = targets[0]
            utc_dt02 = targets[1]
            local_dt01 = utc_dt01.replace(tzinfo=pytz.utc).astimezone(myTimeZone)
            local_dt01 = myTimeZone.normalize(local_dt01)
            local_dt02 = utc_dt02.replace(tzinfo=pytz.utc).astimezone(myTimeZone)
            local_dt02 = myTimeZone.normalize(local_dt02)
            
            targets = []
            if (local_dt01.dst()).seconds > (local_dt02.dst()).seconds:
                targets.append(local_dt01.strftime("%Y-%m-%d %H:%M:%S"))
                targets.append(local_dt02.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                targets.append(local_dt02.strftime("%Y-%m-%d %H:%M:%S"))
                targets.append(local_dt01.strftime("%Y-%m-%d %H:%M:%S"))
        
        return targets
        
        

if __name__ == "__main__":
    unittest.main(verbosity=2)