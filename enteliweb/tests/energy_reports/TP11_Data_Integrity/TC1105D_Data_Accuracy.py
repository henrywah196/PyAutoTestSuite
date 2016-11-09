'''
Created on Dec 30, 2015

@author: hwang
'''
import time, datetime
import settings
from libraries.eweb.DataObjects.WebGroup import *
from libraries.eweb.DataObjects.CopperCube import CopperCubeDBObj
from libraries.eweb.DataObjects.Historian import HistorianDBObj
from libraries.PyAutoTestCase import *
from ddt import ddt, data
import pytz    # import timezone to veirfy daylight savings
from pytz import NonExistentTimeError
import random
import calendar, math, decimal
from unittest import result


# Global settings
TimeZone = settings.TimeZone
#TLInstance_Under_Test = ["//LocalSite/1000.PI1.TotalPulses"]
#TLInstance_Under_Test = [["//EWEB16590/1100.AV301.Present_Value", {"year": 2010}], ["//EWEB16590/1100.AV301.Present_Value", {"month": "2014-10"}], ["//EWEB16590/1100.AV301.Present_Value", {"day": "2009-12-26"}], ["//EWEB16590/1100.AV301.Present_Value", {"hour": "2011-11-07 12"}]]

SKIP_RAW_DATA_CHECK = True    # skip all the tests of verifying tlinstance raw data

def getTestingData():
    """
    return a list testing TL reference
    """
    if 'TESTING_DATA_TC1105D_Data_Accuracy' not in globals():
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
    
        global TESTING_DATA_TC1105D_Data_Accuracy
        TESTING_DATA_TC1105D_Data_Accuracy = resultNew
        
    return TESTING_DATA_TC1105D_Data_Accuracy
    


@ddt
class TC1105D_Data_Accuracy(TestCaseTemplate):
    
    def setUp(self):
        super(TC1105D_Data_Accuracy, self).setUp()
        self.webgroup = WebGroupDBObj()
        self.archiver = None
        
    def tearDown(self):
        super(TC1105D_Data_Accuracy, self).tearDown()
        del self.webgroup
        if self.archiver is not None:
            del self.archiver
        '''    
        if 'TESTING_DATA_EnergyRawDataCheck' in globals():
            global TESTING_DATA_EnergyRawDataCheck
            TESTING_DATA_EnergyRawDataCheck = None
        '''
        
    
    @unittest.skipIf(SKIP_RAW_DATA_CHECK == True, "Raw data check is skipped")    
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
        self._testMethodDoc = "Verify datapoint '%s' consistency of raw data sequence number for %s: %s"%(fullRef, dateRange_Type, dateRange_Value)
        
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
        
        
    @unittest.skipIf(SKIP_RAW_DATA_CHECK == True, "Raw data check is skipped")
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
        self._testMethodDoc = "Verify datapoint '%s' consistency of raw data timestamp for %s: %s"%(fullRef, dateRange_Type, dateRange_Value)
        
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
        
        
    @unittest.skipIf(SKIP_RAW_DATA_CHECK == True, "Raw data check is skipped")
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
        self._testMethodDoc = "Verify datapoint '%s' consistency of raw data value for %s: %s"%(fullRef, dateRange_Type, dateRange_Value)
        
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
    
    
    @unittest.skipIf(SKIP_RAW_DATA_CHECK == True, "Raw data check is skipped")
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
                
                
    @unittest.skipIf(SKIP_RAW_DATA_CHECK == True, "Raw data check is skipped")
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
                
    
    @unittest.skipIf(SKIP_RAW_DATA_CHECK == False, "Running Raw data check")             
    @data(*getTestingData())
    def test06(self, testData):
        
        fullRef = testData["FullRef"]
        self.archiverType = testData["Type"]
        dateRange = testData["Date Range"]
        dateRange_Type = None
        dateRange_Value = None
        for key in dateRange:
            dateRange_Type = key
            dateRange_Value = dateRange[key]
            break
        self.datetimeStart, self.datetimeFinish = self._datetimeStartFinish(testData)
        
        # Update doc string based on test data
        self._testMethodDoc = "Verify datapoint '%s' accuracy of data calculation for %s: %s"%(fullRef, dateRange_Type, dateRange_Value)
        
        tlInstanceType = self.webgroup.getTLInstanceType(fullRef)
        datapointType = self.webgroup.DataPointType[tlInstanceType]    # CONSUMPTION or DEMAND
        
        # confirm the raw DB Data source (Historian or CopperCube) and make a connection
        self.confirmArchiverDB(testData)
        
        # obtain the tlinstance raw ID
        self.rawTLInstance = self.webgroup.getRawTlinstanceID(fullRef)
        
        if datapointType == "CONSUMPTION":
            if self.archiverType == "CopperCube":
                cursor = self.archiver.cursor.execute("select seq, data, ts from %s where ts between '%s' and '%s' and variant in (2,4,5) order by seq asc"%(self.rawTLInstance, self.datetimeStart, self.datetimeFinish))
            else:
                cursor = self.archiver.cursor.execute("select RecordNumber as seq, cast(Data as decimal(38,10)) as data, timestamp as ts from tldata where tlinstance = ? and type = 0 and timestamp between ? and ? order by RecordNumber asc", self.rawTLInstance, self.datetimeStart, self.datetimeFinish)
            rows = cursor.fetchall()
        
            if len(rows) > 0: 
                print self._testMethodDoc
                print "Date Range: %s - %s"%(self.datetimeStart, self.datetimeFinish)
                print "seq: %s, ts: %s, data: %s"%((rows[0]).seq, (rows[0]).ts, (rows[0]).data)
                print "seq: %s, ts: %s, data: %s"%((rows[len(rows) - 1]).seq, (rows[len(rows) - 1]).ts, (rows[len(rows) - 1]).data)
            
                # get consumption from imported energy data
                TLInstanceIDList = [self.webgroup.getTLInstanceID(fullRef)]
                Consumption.TLInstanceIDList = TLInstanceIDList
                Consumption.DBConn = self.webgroup
                Consumption.DateRange["from"] = self.datetimeStart
                Consumption.DateRange["to"] = self.datetimeFinish
                current = Consumption.getTotal()
            
                # get consumption from raw data directly
                expected = self._getConsumpFromRaw(rows)
            
                print "result (expected): %s"%expected
                print "result (current): %s"%current 
        else:
            if self.archiverType == "CopperCube":
                cursor = self.archiver.cursor.execute("select min(data) as min, max(data) as max, avg(data)as avg from %s where ts between '%s' and '%s' and variant in (2,4,5)"%(self.rawTLInstance, self.datetimeStart, self.datetimeFinish))
            else:
                cursor = self.archiver.cursor.execute("select min(cast(Data as decimal(38,10))) as min, max(cast(Data as decimal(38,10))) as max, avg(cast(Data as decimal(38,10))) as avg from tldata where tlinstance = ? and type = 0 and timestamp between ? and ?", self.rawTLInstance, self.datetimeStart, self.datetimeFinish)
            row = cursor.fetchone()
            
            if row is not None:
                print self._testMethodDoc
                print "Date Range: %s - %s"%(self.datetimeStart, self.datetimeFinish)
                
                # get raw value
                expected_Min = row.min
                expected_Max = row.max
                expected_Avg = row.avg
                
                # get demand from imported energy data
                TLInstanceIDList = [self.webgroup.getTLInstanceID(fullRef)]
                Demand.TLInstanceIDList = TLInstanceIDList
                Demand.DBConn = self.webgroup
                Demand.DateRange["from"] = self.datetimeStart
                Demand.DateRange["to"] = self.datetimeFinish
                Demand.Occupancy["from"] = "00:00:00"
                Demand.Occupancy["to"] = "23:59:59"
                Demand.Occupancy["days"] = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
                current_Min = Demand.getOccupiedMin()
                current_Max = Demand.getOccupiedMax()
                current_Avg = Demand.getAverage()
                
                print "Min (expected, current): %s, %s"%(expected_Min, current_Min)
                print "Max (expected, current): %s, %s"%(expected_Max, current_Max)
                print "Avg (expected, current): %s, %s"%(expected_Avg, current_Avg) 
                     
            
        
        
               
     
    ####################
    # Helper methods
    ####################
    def _getConsumpFromRaw(self, rows):
        """
        helper to calcualte the consumption directly form raw data
        """
        meterResets = self._getMeterResetSeq(rows) # see if data contains meter reset
        if meterResets is not None:
            rangeList = []
            rangeList.append([rows[0].seq, meterResets[0] - 1])
            rangeList.append([meterResets[len(meterResets) - 1], rows[len(rows) - 1].seq])
            result = self._startRevise(self.datetimeStart, rows[0]) + self._finishRevise(self.datetimeFinish, rows[len(rows) - 1])
            previousItem = None
            for item in meterResets:
                
                if self.archiverType == "CopperCube":
                    cursor = self.archiver.cursor.execute("select seq, data, ts from %s where seq = %s"%(self.rawTLInstance, item))
                else:
                    cursor = self.archiver.cursor.execute("select RecordNumber as seq, cast(Data as decimal(38,10)) as data, timestamp as ts from tldata where tlinstance = ? and RecordNumber = ?", self.rawTLInstance, item)
                newRow = cursor.fetchone()
                if newRow is not None:
                    result = result + newRow.data
                
                if previousItem is None:
                    previousItem = item
                    continue
                rangeList.append([previousItem, item - 1])
                previousItem = item
            for range in rangeList:
                if self.archiverType == "CopperCube":
                    cursor = self.archiver.cursor.execute("select seq, data, ts from %s where seq between %s and %s and variant in (2,4,5) order by seq asc"%(self.rawTLInstance, range[0], range[1]))
                else:
                    cursor = self.archiver.cursor.execute("select RecordNumber as seq, cast(Data as decimal(38,10)) as data, timestamp as ts from tldata where tlinstance = ? and type = 0 and RecordNumber between ? and ? order by RecordNumber asc", self.rawTLInstance, range[0], range[1])
                newRows = cursor.fetchall()
                if len(newRows) > 0:
                    result = result + (newRows[len(newRows) - 1].data - newRows[0].data)
            return result
        else:
            result = decimal.Decimal(rows[len(rows) - 1].data - rows[0].data) + self._startRevise(self.datetimeStart, rows[0]) + self._finishRevise(self.datetimeFinish, rows[len(rows) - 1])
            return result
    
    def _getMeterResetSeq(self, rows):
        """
        helper to examine the pyodbc returned rows and compose a list with contain 
        all the seq number as meter reset point 
        """
        result = None
        previousRow = None
        for row in rows:
            if previousRow is None:
                previousRow = row
                continue
            if row.data < (previousRow.data / 2):
                if result is None:
                    result = []
                result.append(row.seq)
            previousRow = row
        return result
    
    def _startRevise(self, datetimeStart, firstRowReturned ):
        """
        helper to verify if the timestamp of first Row returned is the same as dateTimeStart.
        if not, need to obtain more rows to calcualte the difference between dateTimeStart and 
        the timestamp of first row returned.
        @dateTimeStart - the expected start datetime string.
        @firstRowReturned - the pyodbc Row object which represent the first row of a returned row batches  
        """
        datetimeStart = datetime.datetime.strptime(datetimeStart, "%Y-%m-%d %H:%M:%S")
        
        if firstRowReturned.ts == datetimeStart:
            return 0
        else:
            if self.archiverType == "CopperCube":
                cursor = self.archiver.cursor.execute("select seq, data, ts from %s where seq < %s and variant in (2,4,5) order by seq desc limit 1"%(self.rawTLInstance, firstRowReturned.seq))
            else:
                cursor = self.archiver.cursor.execute("select RecordNumber as seq, cast(Data as decimal(38,10)) as data, timestamp as ts from tldata where tlinstance = ? and RecordNumber < ? and type = 0 order by RecordNumber desc limit 1", self.rawTLInstance, firstRowReturned.seq)
            row = cursor.fetchone()
            if row:
                if row.data < firstRowReturned.data:
                    diff_ts = (firstRowReturned.ts - row.ts).total_seconds()
                    diff_value = firstRowReturned.data - row.data
                    diff = (firstRowReturned.ts - datetimeStart).total_seconds()
                    return decimal.Decimal(diff_value) / decimal.Decimal(diff_ts) * decimal.Decimal(diff)
                else:
                    return 0
            else:
                return 0
        
        
    def _finishRevise(self, datetimeFinish, lastRowReturned ):
        """
        helper to verify if the timestamp of last Row returned is the same as dateTimeFinish.
        if not, need to obtain more rows to calcualte the difference between dateTimeFinish and 
        the timestamp of last row returned.
        @dateTimeFinish - the expected finish datetime string.
        @lastRowReturned - the pyodbc Row object which represent the last row of a returned row batches  
        """
        datetimeFinish = datetime.datetime.strptime(datetimeFinish, "%Y-%m-%d %H:%M:%S")
        
        if lastRowReturned == datetimeFinish:
            return 0
        else:
            if self.archiverType == "CopperCube":
                cursor = self.archiver.cursor.execute("select seq, data, ts from %s where seq > %s and variant in (2,4,5) order by seq asc limit 1"%(self.rawTLInstance, lastRowReturned.seq))
            else:
                cursor = self.archiver.cursor.execute("select RecordNumber as seq, cast(Data as decimal(38,10)) as data, timestamp as ts from tldata where tlinstance = ? and RecordNumber > ? and type = 0 order by RecordNumber asc limit 1", self.rawTLInstance, lastRowReturned.seq)
            row = cursor.fetchone()
            if row:
                if row.data > lastRowReturned.data:
                    diff_ts = (row.ts - lastRowReturned.ts).total_seconds()
                    diff_value = row.data - lastRowReturned.data
                    diff = (datetimeFinish - lastRowReturned.ts).total_seconds()
                    return decimal.Decimal(diff_value) / decimal.Decimal(diff_ts) * decimal.Decimal(diff)
                else:
                    return 0
            else:
                return 0
        
    
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
            if isinstance(dateRange_Value, str):
                dateRange_Value = (datetime.datetime.strptime(dateRange_Value, "%Y-%m-%d")).date()
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