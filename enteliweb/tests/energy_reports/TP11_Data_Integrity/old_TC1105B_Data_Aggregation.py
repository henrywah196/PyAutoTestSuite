'''
Name: TC1105B_Data_Aggregation.py
Description: this test case will verify the data integrity of imported
             and optimized data.
Created on May 11, 2013
@author: hwang
'''
import time, datetime, collections
import settings
from libraries.PyAutoTestCase import *
from libraries.eweb import Utilities
from libraries.eweb.DataObjects.WebGroup import WebGroupDBObj
from ddt import ddt, data


# Global settings
#Datapoint_Groups_Under_Test = [105, 106]


def getTestingData():
    """
    return a list testing area meter datapoint groups
    """
    webgroup = WebGroupDBObj()
    if 'Datapoint_Groups_Under_Test' not in globals():
        global Datapoint_Groups_Under_Test
        Datapoint_Groups_Under_Test = None
    result = webgroup.getDatapointGroup(Datapoint_Groups_Under_Test)
    del webgroup
    return result


@ddt
class DataAggregation(TestCaseTemplate):
    
    def setUp(self):
        super(DataAggregation, self).setUp()
        self.webgroup = WebGroupDBObj()
        
    def tearDown(self):
        super(DataAggregation, self).tearDown()
        del self.webgroup
        
    
    def test01(self):
        self._testMethodDoc = "Verify the integrity of datapoint_group table generally"
        print "test01 - %s"%self._testMethodDoc
        
        myDBConn = self.webgroup
        
        # verify total number of datapoint groups
        cursor = myDBConn.cursor.execute("select count(*) as total from datapoint_group")
        row = cursor.fetchone()
        expected = self.webgroup.getTotalAreaMeterDatapointGroup()
        errMsg = "Verify no missing group(s) in datapoint_group table (expected, current): Equal or more than %s, %s"%(expected, row.total)
        self.assertTrue(row.total >= expected, errMsg)
            
        # verify no NULL in Start, Finish column
        cursor = myDBConn.cursor.execute("select count(*) as total from datapoint_group where Start is NULL or Finish is NULL")
        row = cursor.fetchone()
        errMsg = "Verify no NULL in Start or Finish column in datapoint_group table (expected, current): %s, %s"%(0, row.total)
        self.assertEqual(0, row.total, errMsg)
        
        # verify all datapoint groups have data in datapoint_group_data table
        cursor = myDBConn.cursor.execute("select count(*) as total from datapoint_group where ID not in (select distinct `Group` from datapoint_group_data)")
        row = cursor.fetchone()
        errMsg = "Verify no group(s) was found having no data in datapoint_group_data table (expected, current): %s, %s"%(0, row.total)
        self.assertEqual(0, row.total, errMsg)
    
    
    #@unittest.skip("")
    @data(*getTestingData())
    def test02(self, testData):
        self._testMethodDoc = "Verify the integrity of Start field in datapoint_group table for group '%s'"%testData
        print "%s - %s"%(self._testMethodName, self._testMethodDoc)
        
        myDBConn = self.webgroup
        group = testData
        
        # get current
        cursor = myDBConn.cursor.execute("select Start from datapoint_group where ID = ?", group)
        row = cursor.fetchone()
        current = row.Start
        
        # get expected
        expected = None
        groupModel = Utilities.getGroupModel(myDBConn, group)
        if groupModel == 'Meter':
            meterInstance = Utilities.getInstanceByGroup(myDBConn, group)
            firstTimestamp = Utilities.getFirstTimestamp(myDBConn, meterInstance)
            if firstTimestamp:
                expected = firstTimestamp.date()
                midnight = datetime.time(0)
                expected = datetime.datetime.combine(expected, midnight)
        else:    # Area group
            areaID = Utilities.getInstanceByGroup(myDBConn, group)
            meterList = Utilities.getMeterList(myDBConn, areaID)
            startList = []
            for meterID in meterList:
                firstTimestamp = Utilities.getFirstTimestamp(myDBConn, meterID)
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
    def test03(self, testData):
        self._testMethodDoc = "Verify the integrity of Finish field in datapoint_group table for group '%s'"%testData
        print "%s - %s"%(self._testMethodName, self._testMethodDoc)
        
        myDBConn = self.webgroup
        group = testData
        
        # get current
        cursor = myDBConn.cursor.execute("select Finish from datapoint_group where ID = ?", group)
        row = cursor.fetchone()
        current = row.Finish
        
        # get expected
        expected = None
        groupModel = Utilities.getGroupModel(myDBConn, group)
        if groupModel == 'Meter':
            meterInstance = Utilities.getInstanceByGroup(myDBConn, group)
            lastTimestamp = Utilities.getLastTimestamp(myDBConn, meterInstance)
            if lastTimestamp:
                expected = lastTimestamp
        else:    # Area group
            areaID = Utilities.getInstanceByGroup(myDBConn, group)
            meterList = Utilities.getMeterList(myDBConn, areaID)
            finishList = []
            for meterID in meterList:
                lastTimestamp = Utilities.getLastTimestamp(myDBConn, meterID)
                if lastTimestamp:
                    finishList.append(lastTimestamp)
            if finishList:
                finishList = sorted(finishList)
                expected = finishList[len(finishList) - 1]
        result = (expected - current).days
                
        errMessage = "Datapoint_Group 'Finish' field is inconsistent for Group: %s" %group
        errMessage = errMessage + "\n" + "Finish Field : %s, is %s days older than the raw data (%s)" %(current, result, expected)
        self.assertTrue(result <= 14, errMessage)
        
    
    #@unittest.skip("") 
    @data(*getTestingData())   
    def test04(self, testData):
        self._testMethodDoc = "Verify the integrity of Type field in datapoint_group_data table for group '%s'"%testData
        print "%s - %s"%(self._testMethodName, self._testMethodDoc)
        
        myDBConn = self.webgroup
        group = testData
        
        # verify aggregation energy type for each group
        cursor = myDBConn.cursor.execute("select Model, instance from datapoint_group_map where `Group` = ?", group)
        row = cursor.fetchone()
        if row:
            expected = Utilities.getAggreEnergyType(myDBConn, row.instance)
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
    def test05(self, testData):
        self._testMethodDoc = "Verify the integrity of Aggregation field in datapoint_group_data table for group '%s'"%testData
        print "%s - %s"%(self._testMethodName, self._testMethodDoc)
        
        myDBConn = self.webgroup
        group = testData
        
        cursor = myDBConn.cursor.execute("select Model, instance from datapoint_group_map where `Group` = ?", group)
        row = cursor.fetchone()
        if row:
            energyTypeList = Utilities.getAggreEnergyType(myDBConn, row.instance)
            for item in energyTypeList:
                cursor = myDBConn.cursor.execute("select distinct Aggregation from datapoint_group_data where type = ? and `Group` = ?", item, group)
                rows = cursor.fetchall()
                current = []
                if rows:
                    for newRow in rows:
                        current.append(newRow.Aggregation)
                expected = Utilities.getAggregationType(myDBConn, row.instance, item)
                result = (set(expected) == set(current))
                errMessage = "Aggregation for energy type '%s' are inconsistent in Group: %s" %(item, group)
                errMessage = errMessage + "\n" + "Expected: %s" %(expected,)
                errMessage = errMessage + "\n" + "Current: %s" %(current,)
                self.assertTrue(result, errMessage)
        else: 
            self.fail("Orphan group was found. Group: %s" %group)
        
    
    #@unittest.skip("")
    @data(*getTestingData())
    def test06(self, testData):
        self._testMethodDoc = "Verify the min(timestamp) in datapoint_group_data is match with the start in datapoint_group table for group '%s'"%testData
        print "%s - %s"%(self._testMethodName, self._testMethodDoc)
        
        myDBConn = self.webgroup
        group = testData
        
        cursor = myDBConn.cursor.execute("select Start from datapoint_group where ID = ?", group)
        row = cursor.fetchone()
        expected = row.Start
        
        cursor = myDBConn.cursor.execute("select min(timestamp) as mint from datapoint_group_data where `Group` = ?", group)
        row = cursor.fetchone()
        current = row.mint
        errMessage = "the start timestamp is inconsistent for Group: %s" %group
        errMessage = errMessage + "\n" + "Datapoint_Group: %s" %(expected,)
        errMessage = errMessage + "\n" + "Datapoint_Group_Data: %s" %(current,)
        self.verify_IsEqual(expected, current, errMessage)
        
    
    #@unittest.skip("")
    @data(*getTestingData())
    def test07(self, testData):
        self._testMethodDoc = "Verify there's no missing day samples in datapoint_group_data table for group '%s'"%testData
        print "%s - %s"%(self._testMethodName, self._testMethodDoc)
        
        myDBConn = self.webgroup
        group = testData
        groupModel = Utilities.getGroupModel(myDBConn, group)
        areameterInstance = Utilities.getInstanceByGroup(myDBConn, group)
        aggreEnergies = Utilities.getAggreEnergyType(myDBConn, areameterInstance)
        
        for aggreEnergy in aggreEnergies:
            aggreTypes = Utilities.getAggregationType(myDBConn, areameterInstance, aggreEnergy)
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
                        tlInstance = Utilities.getTLinstance(myDBConn, areameterInstance, aggreEnergy, 'CONSUMPTION')
                    else:
                        tlInstance = Utilities.getTLinstance(myDBConn, areameterInstance, aggreEnergy, 'DEMAND')
                    cursor = myDBConn.cursor.execute("select min(timestamp) as start from report_rate_data where tlinstance = ?", tlInstance)
                    row = cursor.fetchone()
                    expected = (row.start).date()
                    midnight = datetime.time(0)
                    expected = datetime.datetime.combine(expected, midnight)
                else:
                    # verify Area groups
                    meterList = Utilities.getMeterList(myDBConn, areameterInstance, aggreEnergy)
                    startList = []
                    for meterID in meterList:
                        firstTimestamp = None
                        if aggreType == 'Sum':
                            firstTimestamp = Utilities.getFirstTimestamp(myDBConn, meterID, aggreEnergy, 'CONSUMPTION')
                        else:
                            firstTimestamp = Utilities.getFirstTimestamp(myDBConn, meterID, aggreEnergy, 'DEMAND')
                        if firstTimestamp:
                            startList.append(firstTimestamp.date())
                    if startList:
                        startList = sorted(startList)
                        expected = startList[0]
                        midnight = datetime.time(0)
                        expected = datetime.datetime.combine(expected, midnight)
                errMessage = "Group: %s, Type: %s, Aggregation: %s" %(group, aggreEnergy, aggreType)
                errMessage = errMessage + "\n" + "Start Day (Expected, Current): %s, %s" %(expected, startDay)
                self.verify_IsEqual(expected, startDay, errMessage, HaltOnErr=False)
                        
                # verify finish day
                if finishDay:
                    expected = None
                    if groupModel == 'Meter':
                        if aggreType == 'Sum':
                            expected = Utilities.getLastTimestamp(myDBConn, areameterInstance, aggreEnergy, 'CONSUMPTION')
                        else:
                            expected = Utilities.getLastTimestamp(myDBConn, areameterInstance, aggreEnergy, 'DEMAND')
                    else:
                        # verify Area groups
                        meterList = Utilities.getMeterList(myDBConn, areameterInstance, aggreEnergy)
                        finishList = []
                        for meterID in meterList:
                            lastTimestamp = None
                            if aggreType == 'Sum':
                                lastTimestamp = Utilities.getLastTimestamp(myDBConn, meterID, aggreEnergy, 'CONSUMPTION')
                            else:
                                lastTimestamp = Utilities.getLastTimestamp(myDBConn, meterID, aggreEnergy, 'DEMAND')
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
        

if __name__ == "__main__":
    unittest.main()
