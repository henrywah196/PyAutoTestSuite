'''
Name: TC1105B_Data_Aggregation.py
Description: this test case will verify the data integrity of imported
             and optimized data.
             
            test01: verify all areas and meters will have datapoint group assigned
                     as long as it contains valid energy datapoint
            test02: examine the state of datapoint_group table, make sure both start and finish have
                    valid timestamp assigned (no NULL)
            test03: verify all datapoint groups should have data in datapoint_group_data table
            test04: verify no duplicated Group in datapoint_group_map table
            test05: verify no duplicated Instance in datapoint_group_map table
            test06: Verify the consistent of Start and Finish between datapoint_group and dataapoint_group_data table
            
             
Created on May 11, 2013
@author: hwang
'''
import time, datetime, collections
import settings
from libraries.PyAutoTestCase import *
from libraries.eweb import OldUtilities
from libraries.eweb.DataObjects.WebGroup import WebGroupDBObj
from ddt import ddt, data
from pytz import timezone


# Global settings
TimeZone = settings.TimeZone
#Datapoint_Groups_Under_Test = [6]    # comment this line if you want test all groups


def getTestingData(testName=None):
    """
    return a list testing area meter datapoint groups
    """
    webgroup = WebGroupDBObj()
    if 'Datapoint_Groups_Under_Test' not in globals():
        global Datapoint_Groups_Under_Test
        Datapoint_Groups_Under_Test = None
    result = webgroup.getDatapointGroup(Datapoint_Groups_Under_Test)
    if testName == "test07":
        result_test07 = []
        for group in result:
            Energy_Types = webgroup.getDatapoingGroupEnergyType(group) 
            Energy_Aggregations = webgroup.getDatapointGroupEnergyAggregation(group)
            if Energy_Types and Energy_Aggregations:
                for etype in Energy_Types:
                    for aggregation in Energy_Aggregations:
                        if etype == "Carbon_Emission" and aggregation in ("Avg", "Max", "Min"):
                            continue
                        item = [group, etype, aggregation]
                        result_test07.append(item)
        result = result_test07
            
    
    del webgroup
    return result


@ddt
class TC1105B_DataAggregation(TestCaseTemplate):
    
    def setUp(self):
        super(TC1105B_DataAggregation, self).setUp()
        self.webgroup = WebGroupDBObj()
        
    def tearDown(self):
        super(TC1105B_DataAggregation, self).tearDown()
        del self.webgroup
        
        
    #@unittest.skip("")
    def test01(self):
        self._testMethodDoc = "Verify valid area and meter has datapoint group in datapoint_group_map tables"
        myDBConn = self.webgroup
        
        # verify total number of datapoint groups
        instanceList = self.webgroup.getTotalAreaMeterDatapointGroup()
        for instance in instanceList:
            cursor = myDBConn.cursor.execute("select count(*) as total from datapoint_group_map where instance = ?", instance)
            row = cursor.fetchone()
            current = row.total
            result = (current > 0)
            errMsg = "verify instance '%s' has datapoint group in datapoint_group_map table"%instance
            self.verify_IsTrue(result, errMsg, HaltOnErr=False)
        
    def test02(self):
        self._testMethodDoc = "verify no NULL in Start, Finish column in datapoint_group table"
        myDBConn = self.webgroup
        cursor = myDBConn.cursor.execute("select ID from datapoint_group where Start is NULL or Finish is NULL")
        rows = cursor.fetchall()
        current = []
        expected = []
        if len(rows) > 0:
            for row in rows:
                current.append(row.ID)
        errMsg = "Verify no NULL in Start or Finish column in datapoint_group table"
        self.verify_IsEqual(expected, current, errMsg)
        
    def test03(self):
        self._testMethodDoc = "verify all datapoint groups have data in datapoint_group_data table"
        myDBConn = self.webgroup
        cursor = myDBConn.cursor.execute("select ID from datapoint_group where ID not in (select distinct `Group` from datapoint_group_data)")
        rows = cursor.fetchall()
        expected = []
        current = []
        if len(rows) > 0:
            for row in rows:
                current.append(row.ID)
        errMsg = "Verify no group(s) was found having no data in datapoint_group_data table"
        self.verify_IsEqual(expected, current, errMsg)
        
    def test04(self):
        self._testMethodDoc = "verify no duplicated Group in datapoint_group_map table"
        myDBConn = self.webgroup
        cursor = myDBConn.cursor.execute("select `Group`, count(*) as total from datapoint_group_map group by `Group` having count(*) > 1")
        rows = cursor.fetchall()
        expected = 0
        current = len(rows)
        errMsg = "Verify no duplicated group(s) found in datapoint_group_map table"
        if current > 0:
            for row in rows:
                errMsg = errMsg + "\nDuplicated Group was found: %s"%row.Group
        self.verify_IsEqual(expected, current, errMsg)
        
    def test05(self):
        self._testMethodDoc = "verify no duplicated Instance in datapoint_group_map table"
        myDBConn = self.webgroup
        cursor = myDBConn.cursor.execute("select Instance, count(*) as total from datapoint_group_map group by Instance having count(*) > 1")
        rows = cursor.fetchall()
        expected = 0
        current = len(rows)
        errMsg = "Verify no duplicated Instance(s) found in datapoint_group_map table"
        if current > 0:
            for row in rows:
                errMsg = errMsg + "\nDuplicated Instance was found: %s"%row.Instance
        self.verify_IsEqual(expected, current, errMsg)
    
    
    #@unittest.skip("")
    @data(*getTestingData())
    def test06(self, testData):
        self._testMethodDoc = "Verify the consistent of Start and Finish between datapoint_group and dataapoint_group_data table for group-%s"%testData
        print "%s - %s"%(self._testMethodName, self._testMethodDoc)
        
        myDBConn = self.webgroup
        group = testData
        
        cursor = myDBConn.cursor.execute("select Start, Finish from datapoint_group where ID = ?", group)
        row = cursor.fetchone()
        expectedStart = row.Start
        expectedFinish = row.Finish
        
        cursor = myDBConn.cursor.execute("select min(timestamp) as mint, max(timestamp) as maxt from datapoint_group_data where `Group` = ?", group)
        row = cursor.fetchone()
        currentStart = row.mint
        currentFinish = row.maxt
        
        # need reformat current start for testing
        myDate = currentStart.date()
        myTime = datetime.time(0)
        currentStart = datetime.datetime.combine(myDate, myTime)
        
        # verify Start
        errMessage = "Verify the Start timestamp is consistent for Group: %s" %group
        errMessage = errMessage + "\n(Expected: timestamp in Datapoint_Group, Current: timestamp in Datapoint_Group Data)"
        self.verify_IsEqual(expectedStart, currentStart, errMessage)
        
        # verify Finish
        result = expectedFinish - currentFinish
        errMessage = "Verify the Finish timestamp is inconsistent for Group: %s" %group
        errMessage = errMessage + "\n" + "Datapoint_Group: %s" %(expectedFinish,)
        errMessage = errMessage + "\n" + "Datapoint_Group_Data: %s" %(currentFinish,)
        self.verify_IsTrue(result < datetime.timedelta(minutes=60), errMessage)
    
    
    #@unittest.skip("")
    @data(*getTestingData())
    def test07(self, testData):
        self._testMethodDoc = "Verify the integrity of Start field in datapoint_group table for group-%s"%testData
        print "%s - %s"%(self._testMethodName, self._testMethodDoc)
        
        myDBConn = self.webgroup
        group = testData
        
        # get current
        cursor = myDBConn.cursor.execute("select Start from datapoint_group where ID = ?", group)
        row = cursor.fetchone()
        current = row.Start
        
        # get expected
        expected = None
        groupInstanceID = myDBConn.getDatapointGroupAreaMeterID(group)
        groupModel = myDBConn.getInstanceType(groupInstanceID)
        if groupModel == 'meter':
            meterInstance = groupInstanceID
            datapointInfo = myDBConn.getDataPointInfo(meterInstance)
            firstTimestamp = None
            for datapoint in datapointInfo:
                datapointFullRef = datapoint["FullRef"]
                tlinstanceStart = myDBConn.getTLInstanceStart(datapointFullRef, from_Data_Table=True)
                if firstTimestamp is not None:
                    if firstTimestamp > tlinstanceStart:
                        firstTimestamp = tlinstanceStart
                else:
                    firstTimestamp = tlinstanceStart
            if firstTimestamp:
                expected = firstTimestamp.date()
                midnight = datetime.time(0)
                expected = datetime.datetime.combine(expected, midnight)
        elif groupModel == 'area':    # Area group
            areaID = groupInstanceID
            energyTypes = myDBConn.getAreaMeterEnergyType(areaID)
            meterList = []
            for energyType in energyTypes:
                subList = myDBConn.getMeterList(areaID, energyType)
                meterList.extend(subList)
            startList = []
            for meterID in meterList:
                datapointInfo = myDBConn.getDataPointInfo(meterID)
                firstTimestamp = None
                for datapoint in datapointInfo:
                    datapointFullRef = datapoint["FullRef"]
                    tlinstanceStart = myDBConn.getTLInstanceStart(datapointFullRef, from_Data_Table=True)
                    if firstTimestamp is not None:
                        if firstTimestamp > tlinstanceStart:
                            firstTimestamp = tlinstanceStart
                    else:
                        firstTimestamp = tlinstanceStart
                if firstTimestamp:
                    startList.append(firstTimestamp.date())
            if startList:
                startList = sorted(startList)
                expected = startList[0]
                midnight = datetime.time(0)
                expected = datetime.datetime.combine(expected, midnight)
        errMessage = "Datapoint_Group Start field is inconsistent for Group: %s" %group
        errMessage = errMessage + "\n" + "Start Field (expected, current): %s, %s" %(expected, current)
        self.assertEqual(expected, current, errMessage)
        
    
    #@unittest.skip("")
    @data(*getTestingData())
    def test08(self, testData):
        self._testMethodDoc = "Verify the integrity of Finish field in datapoint_group table for group-%s"%testData
        print "%s - %s"%(self._testMethodName, self._testMethodDoc)
        
        myDBConn = self.webgroup
        group = testData
        
        # get current
        cursor = myDBConn.cursor.execute("select Finish from datapoint_group where ID = ?", group)
        row = cursor.fetchone()
        current = row.Finish
        
        # get expected
        expected = None
        groupInstanceID = myDBConn.getDatapointGroupAreaMeterID(group)
        groupModel = myDBConn.getInstanceType(groupInstanceID)
        if groupModel == 'meter':
            meterInstance = groupInstanceID
            datapointInfo = myDBConn.getDataPointInfo(meterInstance)
            lastTimestamp = None
            for datapoint in datapointInfo:
                datapointFullRef = datapoint["FullRef"]
                tlinstanceFinish = myDBConn.getTLInstanceFinish(datapointFullRef, from_Data_Table=True, fullDayCircle=True)
                if lastTimestamp is not None:
                    if lastTimestamp < tlinstanceFinish:
                        lastTimestamp = tlinstanceFinish
                else:
                    lastTimestamp = tlinstanceFinish
            if lastTimestamp:
                expected = lastTimestamp.date()
                midnight = datetime.time(23, 59, 59)
                expected = datetime.datetime.combine(expected, midnight)
        elif groupModel == 'area':    # Area group
            areaID = groupInstanceID
            meterList = []
            energyTypes = myDBConn.getAreaMeterEnergyType(areaID)
            for energyType in energyTypes:
                subList = myDBConn.getMeterList(areaID, energyType)
                meterList.extend(subList)
            finishList = []
            for meterID in meterList:
                datapointInfo = myDBConn.getDataPointInfo(meterID)
                lastTimestamp = None
                for datapoint in datapointInfo:
                    datapointFullRef = datapoint["FullRef"]
                    tlinstanceFinish = myDBConn.getTLInstanceFinish(datapointFullRef, from_Data_Table=True, fullDayCircle=True)
                    if lastTimestamp is not None:
                        if lastTimestamp < tlinstanceFinish:
                            lastTimestamp = tlinstanceFinish
                    else:
                        lastTimestamp = tlinstanceFinish
                if lastTimestamp:
                    finishList.append(lastTimestamp)
            if finishList:
                finishList = sorted(finishList)
                expected = finishList[len(finishList) - 1]
                midnight = datetime.time(23, 59, 59)
                expected = datetime.datetime.combine(expected, midnight)
                
        errMessage = "Datapoint_Group 'Finish' field is inconsistent for Group: %s" %group
        self.verify_IsEqual(expected, current, errMessage)
        
    
    #@unittest.skip("") 
    @data(*getTestingData())   
    def test09(self, testData):
        self._testMethodDoc = "Verify the integrity of Type field in datapoint_group_data table for group-%s"%testData
        print "%s - %s"%(self._testMethodName, self._testMethodDoc)
        
        myDBConn = self.webgroup
        group = testData
        
        # verify aggregation energy type for each group
        cursor = myDBConn.cursor.execute("select Model, instance from datapoint_group_map where `Group` = ?", group)
        row = cursor.fetchone()
        if row:
            expected = myDBConn.getAreaMeterEnergyType(row.instance)
            cursor = myDBConn.cursor.execute("select distinct Type from datapoint_group_data where `Group` = ?", group)
            rows = cursor.fetchall()
            current = []
            if rows:
                for row in rows:
                    current.append(row.Type)
            #result = (collections.Counter(expected) == collections.Counter(current))    # only suppprt python 2.7x
            result = (set(expected) == set(current))
            errMessage = "Aggregation types are inconsistent in Group: %s" %group
            errMessage = errMessage + "\n" + "Expected: %s" %(expected,)
            errMessage = errMessage + "\n" + "Current: %s" %(current,)
            self.assertTrue(result, errMessage)
        else:
            self.fail("Orphan group was found. Group: %s" %group)
        
    
    #@unittest.skip("")
    @data(*getTestingData())
    def test10(self, testData):
        self._testMethodDoc = "Verify the integrity of Aggregation field in datapoint_group_data table for group-%s"%testData
        print "%s - %s"%(self._testMethodName, self._testMethodDoc)
        
        myDBConn = self.webgroup
        group = testData
        
        cursor = myDBConn.cursor.execute("select Model, instance from datapoint_group_map where `Group` = ?", group)
        row = cursor.fetchone()
        if row:
            energyTypeList = myDBConn.getAreaMeterEnergyType(row.instance)
            for item in energyTypeList:
                cursor = myDBConn.cursor.execute("select distinct Aggregation from datapoint_group_data where type = ? and `Group` = ?", item, group)
                rows = cursor.fetchall()
                current = []
                if rows:
                    for newRow in rows:
                        current.append(newRow.Aggregation)
                expected = myDBConn.getAggregationType(row.instance, item)
                result = (set(expected) == set(current))
                errMessage = "Aggregation for energy type '%s' are inconsistent in Group: %s" %(item, group)
                errMessage = errMessage + "\n" + "Expected: %s" %(expected,)
                errMessage = errMessage + "\n" + "Current: %s" %(current,)
                self.assertTrue(result, errMessage)
        else: 
            self.fail("Orphan group was found. Group: %s" %group)
    
    
    #@unittest.skip("")
    @data(*getTestingData("test07"))
    def test11(self, testData):
        self._testMethodDoc = "Verify the integrity of Period field in datapoint_group_data table for group-%s (Type: %s, Aggregation: %s)"%(testData[0], testData[1], testData[2])
        print "%s - %s"%(self._testMethodName, self._testMethodDoc)
        
        myDBConn = self.webgroup
        group = testData[0]
        energyType = testData[1]
        aggregation = testData[2]
                
        # Verify Day Period
        period = 'D'
        cursor = myDBConn.cursor.execute("select min(timestamp) as mint, max(timestamp) as maxt, count(*) as total from datapoint_group_data where `Group` = ? and Type= ? and Aggregation = ? and Period = ?", group, energyType, aggregation, period)
        row = cursor.fetchone()
        start = row.mint     # start time
        finish = row.maxt    # finish time
        totalDays = row.total    # total of days
        print "energy type: %s, aggregation: %s, period: D"%(energyType, aggregation)
        print "start time %s"%start
        print "finish time %s"%finish
        print "total of days %s"%totalDays
        expected = (finish-start).days + 1 # expected total number of days
        current = totalDays
        errMessage = "Verify integrity for total of days"
        self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
                
        # Verify Hour Period
        period = 'H'
        cursor = myDBConn.cursor.execute("select count(*) as total from (select date(timestamp) as date, count(*) as total from datapoint_group_data where `Group` = ? and Type = ? and Aggregation = ? and Period = ? group by date(timestamp)) as t", group, energyType, aggregation, period)
        row = cursor.fetchone()
        expected = totalDays
        current = row.total
        errMessage = "Verify integrity of total hours by check no missing days"
        self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
                
        cursor = myDBConn.cursor.execute("select * from (select date(timestamp) as date, count(*) as total from datapoint_group_data where `Group` = ? and Type = ? and Aggregation = ? and Period = ? group by date(timestamp)) as t where total <> 24", group, energyType, aggregation, period)
        current = []
        expected = []
        rows = cursor.fetchall()
        if len(rows) > 0:
            for row in rows:
                myDate = row.date
                myTotal = row.total
                if self._isDSTStartDate(myDate):    # verify is DST start
                    if myTotal == 23:
                        continue
                    else:
                        myRecord = {}
                        myRecord["day"] = myDate.strftime("%Y-%m-%d")
                        myRecord["hours_current"] = str(myTotal)
                        myRecord["hours_expected"] = "23"
                        current.append(myRecord)
                elif (myDate == start.date()) or (myDate == finish.date()):    # verify is start or finish date
                    hours_expected = myDBConn.validateDatapointGroupDateTotalHours(group, energyType, aggregation, myDate.strftime("%Y-%m-%d"))
                    if myTotal == hours_expected:
                        continue
                    else:
                        myRecord = {}
                        myRecord["day"] = myDate.strftime("%Y-%m-%d")
                        myRecord["hours_current"] = str(myTotal)
                        myRecord["hours_expected"] = str(hours_expected)
                        current.append(myRecord)
                else:
                    myRecord = {}
                    myRecord["day"] = myDate.strftime("%Y-%m-%d")
                    myRecord["hours_current"] = str(myTotal)
                    myRecord["hours_expected"] = "24"
                    current.append(myRecord)
        errMessage = "Verify integrity of total hours by check no missing hours"
        self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
                
    
    #@unittest.skip("")
    @data(*getTestingData())
    def obsolete_test12(self, testData):
        self._testMethodDoc = "Verify there's no missing day samples in datapoint_group_data table for group-%s"%testData
        print "%s - %s"%(self._testMethodName, self._testMethodDoc)
        
        myDBConn = self.webgroup
        group = testData
        groupModel = OldUtilities.getGroupModel(myDBConn, group)
        areameterInstance = OldUtilities.getInstanceByGroup(myDBConn, group)
        aggreEnergies = OldUtilities.getAggreEnergyType(myDBConn, areameterInstance)
        
        for aggreEnergy in aggreEnergies:
            aggreTypes = OldUtilities.getAggregationType(myDBConn, areameterInstance, aggreEnergy)
            for aggreType in aggreTypes:
                startDay = None
                finishDay = None
                totalDays = None
                tlInstance = None
                cursor = myDBConn.cursor.execute("select min(timestamp) as StartDay, max(timestamp) as FinishDay from datapoint_group_data where `Group` = ? and `Type` = ? and Aggregation = ? and Period = 'D'", group, aggreEnergy, aggreType)    
                row = cursor.fetchone()
                if row:
                    startDay = row.StartDay
                    finishDay = row.FinishDay
                cursor = myDBConn.cursor.execute("select count(*) as total from datapoint_group_data where `Group` = ? and `Type` = ? and Aggregation = ? and Period = 'D'", group, aggreEnergy, aggreType)
                row = cursor.fetchone()
                totalDays = row.total
                        
                # verify starting day
                expected = None
                if groupModel == 'Meter':
                    if aggreType == 'Sum':
                        tlInstance = OldUtilities.getTLinstance(myDBConn, areameterInstance, aggreEnergy, 'CONSUMPTION')
                    else:
                        tlInstance = OldUtilities.getTLinstance(myDBConn, areameterInstance, aggreEnergy, 'DEMAND')
                    cursor = myDBConn.cursor.execute("select min(timestamp) as start from report_rate_data where tlinstance = ?", tlInstance)
                    row = cursor.fetchone()
                    expected = (row.start).date()
                    
                    #midnight = datetime.time(0)    change to 05:00 for EWEB-17024
                    midnight = datetime.time(5)
                    expected = datetime.datetime.combine(expected, midnight)
                else:
                    # verify Area groups
                    meterList = OldUtilities.getMeterList(myDBConn, areameterInstance, aggreEnergy)
                    startList = []
                    for meterID in meterList:
                        firstTimestamp = None
                        if aggreType == 'Sum':
                            firstTimestamp = OldUtilities.getFirstTimestamp(myDBConn, meterID, aggreEnergy, 'CONSUMPTION')
                        else:
                            firstTimestamp = OldUtilities.getFirstTimestamp(myDBConn, meterID, aggreEnergy, 'DEMAND')
                        if firstTimestamp:
                            startList.append(firstTimestamp.date())
                    if startList:
                        startList = sorted(startList)
                        expected = startList[0]
                        #midnight = datetime.time(0)    change to 05:00 for EWEB-17024
                        midnight = datetime.time(5)
                        expected = datetime.datetime.combine(expected, midnight)
                errMessage = "Group: %s, Type: %s, Aggregation: %s" %(group, aggreEnergy, aggreType)
                errMessage = errMessage + "\n" + "Start Day (Expected, Current): %s, %s" %(expected, startDay)
                self.verify_IsEqual(expected, startDay, errMessage, HaltOnErr=False)
                        
                # verify finish day
                if finishDay:
                    expected = None
                    if groupModel == 'Meter':
                        if aggreType == 'Sum':
                            expected = OldUtilities.getLastTimestamp(myDBConn, areameterInstance, aggreEnergy, 'CONSUMPTION')
                        else:
                            expected = OldUtilities.getLastTimestamp(myDBConn, areameterInstance, aggreEnergy, 'DEMAND')
                    else:
                        # verify Area groups
                        meterList = OldUtilities.getMeterList(myDBConn, areameterInstance, aggreEnergy)
                        finishList = []
                        for meterID in meterList:
                            lastTimestamp = None
                            if aggreType == 'Sum':
                                lastTimestamp = OldUtilities.getLastTimestamp(myDBConn, meterID, aggreEnergy, 'CONSUMPTION')
                            else:
                                lastTimestamp = OldUtilities.getLastTimestamp(myDBConn, meterID, aggreEnergy, 'DEMAND')
                            if lastTimestamp:
                                finishList.append(lastTimestamp)
                        if finishList:
                            finishList = sorted(finishList)
                            expected = finishList[len(finishList) - 1]
                    result = (expected - finishDay).days
                    errMessage = "Group: %s, Type: %s, Aggregation: %s" %(group, aggreEnergy, aggreType)
                    errMessage = errMessage + "\n" + "Finish Day: %s, is %s days older than the raw data (%s)" %(finishDay, result, expected)
                    self.verify_IsTrue(result <= 14, errMessage, HaltOnErr=False)
                    
                        
                # verify no day samples missing between start and finish
                errMessage = "Group: %s, Type: %s, Aggregation: %s" %(group, aggreEnergy, aggreType)
                errMessage = errMessage + "\n" + "Start Day ~ Finish Day: %s ~ %s" %(startDay, finishDay)
                if startDay and finishDay:
                    expected = (finishDay.date() - startDay.date()).days + 1
                    errMessage = errMessage + "\n" + "Total days (Expected, Current): %s, %s" %(expected, totalDays)
                    self.verify_IsEqual(expected, totalDays, errMessage, HaltOnErr=False)
                else:
                    try: self.fail(errMessage)
                    except AssertionError, e: self.verificationErrors.append(str(e))        


    ####################
    # Helper methods
    ####################
    def _isDSTStartDate(self, date):
        ''' verify if the given date is a DST start date '''
        myTimeZone = timezone(TimeZone)
        utc_transition_times = myTimeZone._utc_transition_times
        targets = []
        for item in utc_transition_times:
            if item.year == date.year:
                targets.append(item) 
        if len(targets) > 0:
            target = targets[0]    # find start date
            if targets[1].hour > target.hour:
                target = targets[1]
            if target.date() == date:
                return True
            else:
                return False
        else:
            return False 
        

if __name__ == "__main__":
    unittest.main()
