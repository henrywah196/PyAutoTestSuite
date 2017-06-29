# coding: utf-8
################################################################################################
# Test Case   : 
#
# Description : 
#
################################################################################################
import settings
from libraries.PyAutoTestCase import *    # import test case template
from libraries.eweb.DataObjects.WebGroup import WebGroupDBObj
import os, time
import json
import re
from ddt import ddt, data
import string


# Global Settings
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "DB_Test.json"))


ACCESS_EVENT_TYPES = {"None"              : "",
                      "Valid Access"      : "CU",
                      "Unrecognized Card" : "CU",
                      "Invalid PIN"       : "CU",
                      "Disabled Card"     : "CU",
                      "Expired User"      : "CU",
                      "Inactive User"     : "CU",
                      "User Disabled"     : "CU",
                      "APB Violation"     : "CU",
                      "Time Zone Violation" : "CU",
                      "Invalid Zone Access" : "CU",
                      "Lost Card"           : "CU",
                      "PIN Timeout"         : "CU",
                      "Access Inhibit"      : "",
                      "Forced Open"         : "DC",
                      "Forced Open Restored" : "DC",
                      "Trouble"              : "DC",
                      "Trouble Ended"        : "DC",
                      "Life Safety On"       : "DC",
                      "Life Safety Off"      : "DC",
                      "Manual Control"       : "DC",
                      "Manual Locked"        : "DC",
                      "Manual Unlocked"      : "DC",
                      "Manual Life Safety"   : "DC",
                      "Manual Lock Down"     : "DC",
                      "Manual Emergency"     : "DC",
                      "Manual Relinquish"    : "DC",
                      "Lock Schedule Active" : "DC",
                      "Lock Schedule Relinquished"   : "DC",
                      "Unlock Schedule"              : "DC",
                      "Unlock Schedule Pending"      : "DC",
                      "Unlock Schedule Relinquished" : "DC",
                      "Relock Mode Timeout"          : "DC",
                      "Relock Mode Locked"           : "DC",
                      "Relock Mode Unlocked"         : "DC",
                      "Relock Mode Schedule Locked"  : "DC",
                      "Relock Mode Enabled"          : "DC",
                      "Motion Unlocked Door"         : "DC",
                      "Motion Locked Door"           : "DC",
                      "GCL+ Control"                 : "DC",
                      "GCL+ Relinquished"            : "DC",
                      "Door Group Manual Unlocked"   : "DC",
                      "Door Group Manual Locked"     : "DC",
                      "Door Group Manual Life Safety"   : "DC",
                      "Door Group Manual Lock Down"      : "DC",
                      "Door Group Manual Lockdown"       : "DC",
                      "Door Group Control Relinquished" : "DC",
                      "Door Ajar"                       : "DC",
                      "Door Ajar Ended"                 : "DC",
                      "Trace User"                      : "CU",
                      "Elevator Hatch Open"             : "",
                      "Elevator Hatch Closed"           : "",
                      "Public Mode"                     : "",
                      "Secure Mode"                     : "",
                      "Floor Override"                  : "",
                      "Elevator Bypass On"              : "",
                      "Elevator Bypass Off"             : "",
                      "Elevator Emergency On"           : "",
                      "Elevator Emergency Off"          : "",
                      "Time Change"                     : "",
                      "Device Online"                   : "",
                      "Device Offline"                  : "",
                      "Device Reset"                    : "",
                      "Request To Exit"                 : "DC",
                      "Approval Denied"                 : "CU",
                      "Relock Mode Relinquished"        : "DC",
                      "Muster"                          : "CU",
                      "Database Load"                   : "",
                      "Database Save"                   : "",
                      "Database Cleared"                : "",
                      "Two Man Fail Timeout"            : "",
                      "Two Man Fail Authentication"     : "",
                      "Two Man Valid Access"            : "",
                      "Two Man Initiated"               : "",
                      "Manual Bypass"                   : "DC",
                      "Dead Battery"                    : "",
                      "Single Phase Fault"              : "",
                      "Command Failure"                 : "",
                      "Status On"                       : "",
                      "Status Off"                      : "",
                      "Under Voltage"                   : "",
                      "Over Voltage"                    : "",
                      "Alarm Output Activated"          : "",
                      "Alarm Output Acknowledged"       : "",
                      "Invalid Status"                  : "",
                      "Invalid Status Restored"         : "",
                      "Single Phase Fault Restored"     : "",  
                      "Over Voltage Restored"           : "",
                      "Under Voltage Restored"          : "",
                      "Dead Battery Restored"           : "",
                      "Command Failure Restored"        : "",
                      "Breaker Shorted"                 : "",
                      "Breaker Short Restored"          : "",
                      "Alarm Input Active"              : "",
                      "Alarm Input Restored"            : "",
                      "Reserved"                        : "" 
                               }


def getTestingData():
    """
    return a list of commissioning sheet report settings
    """
    
    class TestData():
        def __init__(self):
            self.siteName  = None
            self.changedValue = None
            self.numberOfEvents = None
            
    result = None
    json_file = open(JSON_FILE_LOCATION, "r")
    json_data = json.load(json_file)
            
    for item in json_data:
        myTestData = TestData()
        myTestData.siteName = item["SiteName"]
        myTestData.changedValue = item["ChangedValue"]
        myTestData.numberOfEvents = item["NumberOfEvents"]
        
        if result is None:
            result = []
        result.append(myTestData)
        
    return result


@ddt
class TestCase(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        super(TestCase, cls).setUpClass()
        cls.webgroup = WebGroupDBObj()
       
        
    @classmethod
    def tearDownClass(cls):
        super(TestCase, cls).tearDownClass()
        del cls.webgroup
    
    def setUp(self):
        super(TestCase, self).setUp()
       
        
        self.longMessage = True
        self.maxDiff = None

    def tearDown(self):
        super(TestCase, self).tearDown()
            
            
    @data(*getTestingData())        
    def test01(self, testData):
        
        # prepare test data
        self.testData = testData
        siteName = self.testData.siteName
        changedValue = self.testData.changedValue
        numberOfEvents = self.testData.numberOfEvents
        
        # update test doc string
        self._testMethodDoc = "Verify all generated testing events are collected in event table" 
        
        if numberOfEvents is None:
            self.skipTest("Test skipped on purpose.")
        
        expected = numberOfEvents
        cursor = self.webgroup.cursor.execute("select id from alarm_category where category = 7")
        row = cursor.fetchone()
        category_id = row.id
        
        sqlString = None
        if len(changedValue) > 1:
            sqlString = "select count(*) as total from event where category = {0} and NotifyTypeText = 'event' and (pParameterText like '%changed-value={1}%' or pParameterText like '%changed-value={2}%')".format(category_id,changedValue[0],changedValue[1])
        else:
            sqlString = "select count(*) as total from event where category = {0} and NotifyTypeText = 'event' and pParameterText like '%changed-value={1}%'".format(category_id,changedValue[0])
        cursor = self.webgroup.cursor.execute(sqlString)
        row = cursor.fetchone()
        current = row.total
        self.assertEqual(current, expected, "Verify all testing events are collected in event table failed")
        
    
    @data(*getTestingData())    
    def test02(self, testData):
        
        # prepare test data
        self.testData = testData
        siteName = self.testData.siteName
        changedValue = self.testData.changedValue
        numberOfEvents = self.testData.numberOfEvents
        
        # update test doc string
        self._testMethodDoc = "Verify one-to-one mapping between event and access_event table"
        
        cursor = self.webgroup.cursor.execute("select id from alarm_category where category = 7")
        row = cursor.fetchone()
        category_id = row.id
        
        sqlString = "select count(*) as total from event where category = {0} and NotifyTypeText = 'event' and EventType = 2 and pAlarmText is not NULL".format(category_id)
        cursor = self.webgroup.cursor.execute(sqlString)
        row = cursor.fetchone()
        expected = row.total
        
        sqlString = "select count(*) as total from access_event"
        cursor = self.webgroup.cursor.execute(sqlString)
        row = cursor.fetchone()
        current = row.total
        errMessage = "Verify one-to-one mapping between event and access_event table by 'examine total number of records' failed"
        self.perform(self.assertEqual, current, expected, errMessage)
        
        sqlString = "Select Recno from Event where category ={0} and NotifyTypeText = 'event' and EventType = 2 and pAlarmText is not NULL and not Exists(Select 1 from access_event where access_event.ID =  event.RecNo)".format(category_id)
        cursor = self.webgroup.cursor.execute(sqlString)
        rows = cursor.fetchall()
        
        self.assertItemsEqual(rows, [], "Verify one-to-one mapping between event and access_event table by 'examine record numbers' failed")
        
    
    def test03(self):
        
        # update test doc string
        self._testMethodDoc = "Verify content in access_event table"
        
        sqlString = """select t.ID, t.SiteName, t.EventType, t.DeviceDoorRef, t.DeviceDoorObjectName, t.DeviceDoorDeviceNumber, t.DeviceDoorObjectAbbr,
                       t.DeviceDoorObjectInstance, t.CardUserName, t.CardUserObjectAbbr, t.CardUserInstance, t.CardUserNumber, t.CardUserSiteCode,
                       t.EventArg, t.FloorName, t.pAlarmText, alarm_detail.EventId
                       from (select access_event.ID, access_event.SiteName, access_event.EventType, access_event.DeviceDoorRef, access_event.DeviceDoorObjectName, 
                       access_event.DeviceDoorDeviceNumber, access_event.DeviceDoorObjectAbbr, access_event.DeviceDoorObjectInstance,
                       access_event.CardUserName, access_event.CardUserObjectAbbr, access_event.CardUserInstance, access_event.CardUserNumber,
                       access_event.CardUserSiteCode, access_event.EventArg, access_event.FloorName, event.InputRef, event.pAlarmText from access_event
                       left join event on access_event.ID = event.recno) as t
                       left join alarm_detail on t.InputRef = alarm_detail.ID;"""
                       
        cursor = self.webgroup.cursor.execute(sqlString)
        rows = cursor.fetchall()
        for row in rows:
            dicEventExpected = self._getEventInfo(row)
            
            recordNumber = row.ID
            eventName = dicEventExpected["EventName"]
            for key, value in dicEventExpected.iteritems():
                if key in ("ID", "EventName"):
                    continue
                errMessage = "Verify content '%s' of event type '%s' in access_event table for id '%s' failed"%(key, eventName, recordNumber)
                current = row.__getattribute__(key)
                expected = value
                if key in ("EventType", "EventArg") and value is not None and value != "":
                    expected = int(value)
                if key == "CardUserObjectAbbr" and value == "":    # special case dealing
                    expected = "CU" 
                if key == "CardUserName" and current is not None:  # special case dealing
                    current = current.rstrip()
                if key == "DeviceDoorObjectName" and current is not None: # special case dealing
                    current = current.rstrip()
                if key == "SiteName":
                    self.perform(self.assertTrue, current in expected, errMessage)
                else:
                    self.perform(self.assertEqual, current, expected, errMessage)
                
        
    def _getEventInfo(self, row):
        """ convert and return dict by alarmText """
        dicEvent = {"ID"                       : None,
                     "SiteName"                 : row.EventId,
                     "EventType"                : None, 
                     "EventName"                : None,
                     "DeviceDoorRef"            : None,
                     "DeviceDoorObjectName"     : None,
                     "DeviceDoorDeviceNumber"   : None,
                     "DeviceDoorObjectAbbr"     : None,
                     "DeviceDoorObjectInstance" : None,
                     "CardUserName"             : None,
                     "CardUserObjectAbbr"       : None,
                     "CardUserInstance"         : None,
                     "CardUserNumber"           : None,
                     "CardUserSiteCode"         : None,
                     "EventArg"                 : None,
                     "FloorName"                : None }
        #dicEvent["ID"] = row.RecNo
        
        alarmText = row.pAlarmText
        dicAlarmText = self._getAlarmTextInfo(alarmText)
        result = dicAlarmText["Event"].split(" (")
        dicEvent["EventName"] = (result[0]).strip()
        if dicEvent["EventName"] in ACCESS_EVENT_TYPES:
            dicEvent["EventType"] = (result[1][:-1]).strip()
            dicEvent["DeviceDoorRef"] = dicAlarmText["DCRef"].strip()
            if dicAlarmText["DCName"] is not None:
                dicEvent["DeviceDoorObjectName"] = dicAlarmText["DCName"].strip()
            else:
                dicEvent["DeviceDoorObjectName"] = dicAlarmText["DCName"]
            result = dicEvent["DeviceDoorRef"].split(".")
            dicEvent["DeviceDoorDeviceNumber"] = result[0].strip()
            result = self._splitObjectRef(result[1].strip())
            dicEvent["DeviceDoorObjectAbbr"] = result[0]
            dicEvent["DeviceDoorObjectInstance"] = result[1] 
            dicEvent["EventArg"] = dicAlarmText["Arg"].strip()
        
            if ACCESS_EVENT_TYPES[dicEvent["EventName"]] == "CU":
                if dicAlarmText["CUName"] is not None:
                    dicEvent["CardUserName"] = dicAlarmText["CUName"].strip()
                else:
                    dicEvent["CardUserName"] = dicAlarmText["CUName"]
                result = dicAlarmText["CURef"].strip()
                result = result.split(".")
                if len(result) > 1:
                    result = result[1]
                else:
                    result = result[0]
                result = self._splitObjectRef(result)
                dicEvent["CardUserObjectAbbr"] = result[0]
                dicEvent["CardUserInstance"] = result[1]
                result = dicAlarmText["Card"].strip()
                result = result.split("(")
                dicEvent["CardUserNumber"] = result[0].strip()
                dicEvent["CardUserSiteCode"] = (result[1][:-1]).strip()
            
        return dicEvent
            
        
        
    def _getAlarmTextInfo(self, alarmText):
        """ helper used by _getEventInfo()
            it chop the text message to several different part
        """
        result = {"Event"  : None,
                  "DCRef"  : None,
                  "CURef"  : None,
                  "Card"   : None,
                  "Arg"    : None,
                  "DCName" : None,
                  "CUName" : None}
        arrAlarmText = alarmText.split("): ")
        result["Event"] = arrAlarmText[0] + ")"
        start = len(result["Event"]) + 2
        alarmText = alarmText[start:]
        arrAlarmText = alarmText.split(",")
        result["DCRef"] = arrAlarmText[0]
        start = len(result["DCRef"]) + 1
        alarmText = alarmText[start:]
        eventName = ((result["Event"].split(" ("))[0]).strip()
        if (eventName in ACCESS_EVENT_TYPES) and (ACCESS_EVENT_TYPES[eventName] == "CU"):
            arrAlarmText = alarmText.split(",")
            result["CURef"] = arrAlarmText[0]
            start = len(result["CURef"]) + 1
            alarmText = alarmText[start:]
            arrAlarmText =alarmText.split(",")
            result["Card"] = arrAlarmText[0]
            start = len(result["Card"]) + 1
            alarmText = alarmText[start:]
            arrAlarmText = alarmText.split(",")
            result["Arg"] = arrAlarmText[0]
            start = len(result["Arg"]) + 1
            alarmText = alarmText[start:]
            alarmText = alarmText.rstrip()    # removing new line char from the end
            arrAlarmText = alarmText.split("\n")
            try:
                result["DCName"] = arrAlarmText[1]
            except:
                result["DCName"] = None
            try:
                result["CUName"] = arrAlarmText[2]
            except:
                result["CUName"] = None
        elif (eventName in ACCESS_EVENT_TYPES) and (ACCESS_EVENT_TYPES[eventName] == "DC"):
            arrAlarmText = alarmText.split(",")
            result["Arg"] = arrAlarmText[0]
            start = len(result["Arg"]) + 1
            alarmText = alarmText[start:]
            arrAlarmText = alarmText.split("\n")
            result["DCName"] = arrAlarmText[1]
        else:
            arrAlarmText = alarmText.split("\n")
            result["Arg"] = arrAlarmText[0]
            start = len(result["Arg"])
            alarmText = alarmText[start:]
            arrAlarmText = alarmText.split("\n")
            try: result["DCName"] = arrAlarmText[1]
            except: pass
            
        return result
    
    
    def _splitObjectRef(self, objRefString):
        """ split object reference and return its type and number in a list format
            for example, AV12 returns [AV, 12]
        """
        result = []
        try: number = re.search(r'\d+', objRefString).group()
        except AttributeError: number = None
        if number is not None:
            type = objRefString[:-len(number)]
            result.append(type)
            result.append(number)
        else:
            result.append(objRefString)
            result.append(number)
        return result
    

if __name__ == "__main__":
    unittest.main()
