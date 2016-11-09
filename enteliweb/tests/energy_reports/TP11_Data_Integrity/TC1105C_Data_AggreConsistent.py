'''
Name: TC1105C_Data_AggreConsistent.py
Description: this test case will verify the accuracy of optimized data
             by cross check it with imported data.
             
             test01: examine the data integrity of optimization data by cross check it with imported data
             test02: examine the accuracy of stored optimization data
             
Created on May 11, 2013
@author: hwang
'''
import time, datetime, collections
import settings
from libraries.PyAutoTestCase import *
from libraries.eweb.DataObjects.WebGroup import *
from ddt import ddt, data


# Global settings
#Datapoint_Groups_Under_Test = [44]    # comment this line if you want test all groups
DEBUG = False


def getTestingData(testName=None):
    """
    return a list testing area meter datapoint groups with added testing inforation
    the format of the returned list looks something like
    [ [<group name>, <datapoint energy type>, <group aggregation type>, [tlinstancelist] ], [], [], ... ]
    """
    webgroup = WebGroupDBObj()
    if 'Datapoint_Groups_Under_Test' not in globals():
        global Datapoint_Groups_Under_Test
        Datapoint_Groups_Under_Test = None
    groupList = webgroup.getDatapointGroup(Datapoint_Groups_Under_Test)
    if testName == "test01":
        result = []
        for group in groupList:
            instanceID = webgroup.getDatapointGroupAreaMeterID(group)
            aggreEnergies = webgroup.getAreaMeterEnergyType(instanceID)
            for aggreEnergy in aggreEnergies:
                aggreTypes = webgroup.getAggregationType(instanceID, aggreEnergy)
                for aggreType in aggreTypes:
                    item = [group, aggreEnergy, aggreType]
                    result.append(item)
            
    elif testName == "test02":
        result = []
        for group in groupList:
            energyTypeList = webgroup.getDatapoingGroupEnergyType(group)
            if energyTypeList is not None:
                datapointEnergyTypeList = []
                for energyType in energyTypeList:
                    for key, value in EnergyType.iteritems():
                        if value == energyType:
                            datapointEnergyTypeList.append(key)
                for datapointEnergyType in datapointEnergyTypeList:
                    datapointList = webgroup.getDatapointGroupTLinstanceList(group, datapointEnergyType)
                    if DataPointType[datapointEnergyType] == "CONSUMPTION":
                        item = [group, datapointEnergyType, "Sum", datapointList]
                        result.append(item)
                    if DataPointType[datapointEnergyType] == "DEMAND":
                        item = [group, datapointEnergyType, "Avg", datapointList]
                        result.append(item)
                        item = [group, datapointEnergyType, "Max", datapointList]
                        result.append(item)
                        item = [group, datapointEnergyType, "Min", datapointList]
                        result.append(item)
    else:
        result = groupList
    del webgroup
    return result


@ddt
class TC1105C_Data_AggreConsistent(TestCaseTemplate):
    
    def setUp(self):
        super(TC1105C_Data_AggreConsistent, self).setUp()
        self.webgroup = WebGroupDBObj()
        
    def tearDown(self):
        super(TC1105C_Data_AggreConsistent, self).tearDown()
        del self.webgroup
    
    
    @data(*getTestingData(testName="test01"))
    def test01(self, testData):
        
        myDBConn = self.webgroup
        group = testData[0]
        areameterInstance = myDBConn.getDatapointGroupAreaMeterID(group)
        groupModel = myDBConn.getInstanceType(areameterInstance)
        aggreEnergy = testData[1]
        aggreType = testData[2]
        
        self._testMethodDoc = "Verify Data Integrity of %s of %s for group-%s"%(aggreType, aggreEnergy, group)
        print self._testMethodDoc
        
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
                        
        step = "Cross check Start Day between Report_Rate_Data and Datapoint_Group_Data"
        expected = None
        if groupModel == 'meter':
            if aggreType == 'Sum': dataPointType = 'CONSUMPTION'
            else: dataPointType = 'DEMAND'
            fullRef = myDBConn.getDataPointFullRef(areameterInstance, aggreEnergy, dataPointType)
            firstTimestamp = myDBConn.getTLInstanceStart(fullRef, from_Data_Table=True)
            expected = []
            firstTimestamp = firstTimestamp.date()
            midnight = datetime.time(0)
            expected.append(datetime.datetime.combine(firstTimestamp, midnight))
            midnight = datetime.time(1)    # change to 01:00 caused by EWEB-17024
            expected.append(datetime.datetime.combine(firstTimestamp, midnight))
        else:
            # verify Area groups
            meterList = myDBConn.getMeterList(areameterInstance, aggreEnergy)
            startList = []
            for meterID in meterList:
                firstTimestamp = None
                if aggreType == 'Sum': dataPointType = 'CONSUMPTION'
                else: dataPointType = 'DEMAND'
                fullRef = myDBConn.getDataPointFullRef(meterID, aggreEnergy, dataPointType)
                firstTimestamp = myDBConn.getTLInstanceStart(fullRef, from_Data_Table=True)
                if firstTimestamp:
                    startList.append(firstTimestamp.date())
            if len(startList) >0:
                startList = sorted(startList)
                expected = []
                firstTime = startList[0]
                midnight = datetime.time(0)
                expected.append(datetime.datetime.combine(firstTime, midnight))
                midnight = datetime.time(1)
                expected.append(datetime.datetime.combine(firstTime, midnight))
        step = step + "\n(startDay: %s in (%s, %s)"%(startDay.strftime("%Y-%m-%d %H:%M:%S"), expected[0].strftime("%Y-%m-%d %H:%M:%S"), expected[1].strftime("%Y-%m-%d %H:%M:%S"))
        self.verify_IsTrue(startDay in expected, step, HaltOnErr=False)
                        
        step = "Cross check Finish Day between Report_Rate_Data and Datapoint_Group_Data"
        expected = None
        if groupModel == 'meter':
            if aggreType == 'Sum': dataPointType = 'CONSUMPTION'
            else: dataPointType = 'DEMAND'
            fullRef = myDBConn.getDataPointFullRef(areameterInstance, aggreEnergy, dataPointType)
            lastTimestamp = myDBConn.getTLInstanceFinish(fullRef, from_Data_Table=True, fullDayCircle=True)
            expected = []
            lastTimestamp = lastTimestamp.date()
            midnight = datetime.time(0)
            expected.append(datetime.datetime.combine(lastTimestamp, midnight))
            midnight = datetime.time(1)
            expected.append(datetime.datetime.combine(lastTimestamp, midnight))
        else:
            # verify Area groups
            meterList = myDBConn.getMeterList(areameterInstance, aggreEnergy)
            finishList = []
            for meterID in meterList:
                lastTimestamp = None
                if aggreType == 'Sum': dataPointType = 'CONSUMPTION'
                else: dataPointType = 'DEMAND'
                fullRef = myDBConn.getDataPointFullRef(meterID, aggreEnergy, dataPointType)
                lastTimestamp = myDBConn.getTLInstanceFinish(fullRef, from_Data_Table=True, fullDayCircle=True)
                if lastTimestamp:
                    finishList.append(lastTimestamp.date())
            if len(finishList) > 0:
                finishList = sorted(finishList)
                finishDate = finishList[len(finishList) - 1]
                expected = []
                midnight = datetime.time(0)
                expected.append(datetime.datetime.combine(finishDate, midnight))
                midnight = datetime.time(1)
                expected.append(datetime.datetime.combine(finishDate, midnight))
        step = step + "\n(finishDay: %s in (%s, %s)"%(finishDay.strftime("%Y-%m-%d %H:%M:%S"), expected[0].strftime("%Y-%m-%d %H:%M:%S"), expected[1].strftime("%Y-%m-%d %H:%M:%S"))
        self.verify_IsTrue(finishDay in expected, step, HaltOnErr=False)    
                        
        step = "Cross check Total Days between Report_Rate_Data and Datapoint_Group_Data"
        expected = None
        if groupModel == 'meter':
            if aggreType == 'Sum': dataPointType = 'CONSUMPTION'
            else: dataPointType = 'DEMAND'
            fullRef = myDBConn.getDataPointFullRef(areameterInstance, aggreEnergy, dataPointType)
            expected = myDBConn.getTLInstanceTotalDays(fullRef, fullDayCircle=True) 
        else:
            # verify Area group
            meterList = myDBConn.getMeterList(areameterInstance, aggreEnergy)
            daysList = []
            for meterID in meterList:
                days = None
                if aggreType == 'Sum': dataPointType = 'CONSUMPTION'
                else: dataPointType = 'DEMAND'
                fullRef = myDBConn.getDataPointFullRef(meterID, aggreEnergy, dataPointType)
                if fullRef is None: continue
                days = myDBConn.getTLInstanceTotalDays(fullRef, fullDayCircle=True)
                if days:
                    daysList.append(days)
            if len(daysList) > 0:
                daysList = sorted(daysList)
                expected = daysList[len(daysList) - 1]    
        self.verify_IsEqual(expected, totalDays, step, HaltOnErr=False)
                    
    
    #@unittest.skip("")
    @data(*getTestingData(testName="test02"))
    def test02(self, testData):
        
        group = testData[0]
        datapointEnergyType = testData[1]
        energyType = EnergyType[datapointEnergyType]
        aggregationType = testData[2]
        datapointList = testData[3]
        
        # update doc string
        self._testMethodDoc = "Verify %s of %s value for group-%s"%(aggregationType, datapointEnergyType, group)
        
        myDBConn = self.webgroup
        
        print self._testMethodDoc
        
        # verify Day
        cursor = myDBConn.cursor.execute("select date(timestamp) as day, value from datapoint_group_data where `Group` = ? and Type = ? and aggregation = ? and period = 'D';", group, energyType, aggregationType)
        rows = cursor.fetchall()
        
        for row in rows:
            rowDay = row.day
            rowValue = row.value
            
            TLInstanceIDList = []
            for item in datapointList:
                tlinstanceID = myDBConn.getTLInstanceID(item)
                TLInstanceIDList.append(tlinstanceID)
            if aggregationType == "Sum":
                Consumption.TLInstanceIDList = TLInstanceIDList
                Consumption.DBConn = myDBConn
                Consumption.DateRange["from"] = rowDay.strftime('%Y-%m-%d')
                Consumption.DateRange["to"] = rowDay.strftime('%Y-%m-%d')
                result = Consumption.getTotalByDay()
                expected = result[0]['total']
                current = rowValue
                step = "verify value(%s) for day: %s"%(aggregationType, rowDay.strftime('%Y-%m-%d'))
                if DEBUG: print step
                self.verify_IsEqual(expected, current, step, HaltOnErr=False)
            elif aggregationType == "Avg":
                Demand.TLInstanceIDList = TLInstanceIDList
                Demand.DBConn = myDBConn
                Demand.DateRange["from"] = rowDay.strftime('%Y-%m-%d 00:00:00')
                Demand.DateRange["to"] = rowDay.strftime('%Y-%m-%d 23:59:59')
                result = Demand.getAverage()
                digits = max(0, -rowValue.as_tuple().exponent)
                expected = round(result, digits)
                current = round(rowValue, digits)
                #print "expected: %s, current: %s"%(expected, current)
                step = "verify value(%s) for day: %s"%(aggregationType, rowDay.strftime('%Y-%m-%d'))
                if DEBUG: print step
                self.verify_IsAlmostEqual(expected, current, digits - 1, step, HaltOnErr=False)
            elif aggregationType == "Max":
                Demand.TLInstanceIDList = TLInstanceIDList
                Demand.DBConn = myDBConn
                Demand.DateRange["from"] = rowDay.strftime('%Y-%m-%d 00:00:00')
                Demand.DateRange["to"] = rowDay.strftime('%Y-%m-%d 23:59:59')
                Demand.Occupancy["from"] = "00:00:00"
                Demand.Occupancy["to"] = "23:59:59"
                Demand.Occupancy["days"] = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
                result = Demand.getOccupiedMax()
                digits = max(0, -rowValue.as_tuple().exponent)
                expected = round(result, digits)
                current = round(rowValue, digits)
                #print "expected: %s, current: %s"%(expected, current)
                step = "verify value(%s) for day: %s"%(aggregationType, rowDay.strftime('%Y-%m-%d'))
                if DEBUG: print step
                self.verify_IsAlmostEqual(expected, current, digits - 1, step, HaltOnErr=False)
            elif aggregationType == "Min":
                Demand.TLInstanceIDList = TLInstanceIDList
                Demand.DBConn = myDBConn
                Demand.DateRange["from"] = rowDay.strftime('%Y-%m-%d 00:00:00')
                Demand.DateRange["to"] = rowDay.strftime('%Y-%m-%d 23:59:59')
                Demand.Occupancy["from"] = "00:00:00"
                Demand.Occupancy["to"] = "23:59:59"
                Demand.Occupancy["days"] = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
                result = Demand.getOccupiedMin()
                digits = max(0, -rowValue.as_tuple().exponent)
                expected = round(result, digits)
                current = round(rowValue, digits)
                #print "expected: %s, current: %s"%(expected, current)
                step = "verify value(%s) for day: %s"%(aggregationType, rowDay.strftime('%Y-%m-%d'))
                if DEBUG: print step
                self.verify_IsAlmostEqual(expected, current, digits - 1, step, HaltOnErr=False)
         

if __name__ == "__main__":
    unittest.main()
