'''
BTL Specified Test - 5.0
13.X6 Workstation Scheduling Tests
the script is used to create Reference Schedule S3, which
is in a self-inconsistent state
'''

import os
import sys
import string
import ctypes
import random
import time
import datetime
import csv

from bntest import *

### script Config info ###
# NO_SPACE error - write request larger than panel's max packet segment size (21 for DAC, 33 for Tetra)
#                - try smaller write request, or switch to writing one exception at a time (gMode = 'single')
# INTERNAL error - Usually caused by Quattro timing out waiting for panel to ACK
#
# Ethernet connection may need to be set (look for line after '# connect via ethernet')
# index can be [0] for first ethernet card, [1] for second card
###

gLocalDevice = 6660
gDefaultSite = 'BTL Test Site'
gDefaultGroup = 'Administrators'

gRemoteDevice = 871    # address of panel being tested
gDeltaDevice = False

gWriteMode = 'single'    # 'all' (all exceptions written at once)
                         # 'single' (each exception written individually)

gScheduleReal = {'ValueType': 'Real', 'DefaultValue': '70.0', 'ActiveValue': '5' } # Real
gScheduleUnsigned = {'ValueType': 'UnsignedInteger', 'DefaultValue': '3', 'ActiveValue': '3' } # multi-state
gScheduleEnum = {'ValueType': 'Enum', 'DefaultValue': '1', 'ActiveValue': '1' } # binary

gExceptionDescription = 'This is exactly 30 characters.'

gLongestWriteTime = 0

gSleepFactor = 0    # set > 0 to pause after each write. Each pause will be: gSleepFactor * (largest write time so far + 0.2)
                    # may be helpful when writing large SCH in single mode
                    # for Tetra try = 1; for DSC = 5
### end of script config ###

# global variables
gScheduleType = None
gNumExceptions = None
gServer = None
gUserKey = None

gValueListReal = ['60.0', '61.0', '62.0', '63.0', '64.0', '65.0', '66.0', '67.0', '68.0', '69.0', '70.0', '71.0', '72.0', '73.0', '74.0', '75.0']
gValueListsUnsigned = ['4294967200', '4294967201', '4294967202', '4294967203', '4294967204', '4294967205', '4294967206', '4294967207', '4294967208', '4294967209', '4294967210', '4294967211', '4294967212', '4294967213', '4294967214']
gValueListEnum = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']

gDateRangeList = [['2013/09/01/7', '2013/09/02/1'],
                  ['2013/09/03/2', '2013/09/06/5'],
                  ['2013/09/08/7', '2013/09/09/1']]    # date ranged used by Date Range Event

gSingleDateList = ['2013/01/11/5',
                   '2013/01/12/6',
                   '2013/01/13/7',
                   '2013/01/20/7']    # single date used by Single Date Event

gWeekNDayList = [['13', '3', '1'],
                 ['14', '255', '7'],
                 ['255', '6', '2'],
                 ['2', '255', '5'],
                 ['255', '1', '255']]    # Recurring week and day used by Recurring Week and day event
                                         # 3rd Monday of each odd month
                                         # every Sunday in every even month
                                         # last Tuesday of each month
                                         # every Friday in February
                                         # first 7 Days of every month


def CreateSchedule(sObjRef, sObjName, sObjType):

    # define Schedule type: gScheduleReal, gScheduleUnsigned or gScheduleEnum
    global gScheduleType
    sValueList = None

    if sObjType == 'Real':
        gScheduleType = gScheduleReal
        sValueList = gValueListReal
    elif sObjType == 'UnsignedInteger':
        gScheduleType = gScheduleUnsigned
        sValueList = gValueListsUnsigned
    else:
        gScheduleType = gScheduleEnum
        sValueList = gValueListEnum

    # connect to the server and log in
    global gServer, gUserKey

    gServer = cserver()
    gServer.connect()
    gUserKey = gServer.login('Delta', 'Login')

    if not gDefaultSite in gServer.sitegetlist(gUserKey):
        gServer.sitecreate(gUserKey, gDefaultSite)

    # open the site
    gServer.siteopen (gUserKey, gDefaultSite)
    # set the local device number
    gServer.setupsetparameter (gUserKey, gDefaultSite, 'CFG_SITE_DEVICENUMBER', 0, gLocalDevice)

    # connect via ethernet
    Port = gServer.getportlist (gUserKey, PORT_TYPE_ETHERNET)[1]
    Port.bind (gUserKey, gDefaultSite)
    Port.enable (gUserKey)
    Port.open (gUserKey)

    # wait for the network to calm down
    time.sleep(5)

    # set device local date and time
    if not gDeltaDevice:
        setDeviceTime()

    DeleteObject(gDefaultSite, gRemoteDevice, sObjRef, False)
    time.sleep(5)
    CreateObject(gDefaultSite, gRemoteDevice, sObjRef, sObjName)
    time.sleep(5)

    WriteProperty(gDefaultSite, gRemoteDevice, sObjRef, 'DefaultValue.' + gScheduleType['ValueType'], gScheduleType['DefaultValue'])


    # add weekly schedule entries
    CreateWeeklySchedule(sObjRef, sValueList)

    if gWriteMode == "all":
        # add exception schedule entries using WriteMode as All
        CreateExceptionScheduleAll(sObjRef, sValueList)
    else:
        # add exception schedule entries using WriteMode as Single
        CreateExceptionScheduleSingle(sObjRef, sValueList)

    gServer.logout(gUserKey)
    gServer.disconnect()
    gServer = None


def CreateObject(Site, Device, ObjectID, ObjectName, bIgnoreErrors = False):

    global gServer, gUserKey

    ref = creference()
    ref.parsereference ('//' + Site + '/' + str(Device) + '.' + ObjectID + '.Name', LANGUAGE_ID_ENGLISH, gUserKey)
    PropList = cpropertylist()
    PropList.addreferencewithdata (ref, PRIORITY_NONE, ObjectName, LANGUAGE_ID_ENGLISH)

    gServer.executeobjectrequest (gUserKey, OBJECT_CREATE, PropList)
    PropList.rewind()
    ItemStatus = PropList.getitemstatus (LANGUAGE_ID_ENGLISH)
    if ItemStatus != 'OK' and not bIgnoreErrors:
        print 'Could not create: ' + ObjectID


def DeleteObject(Site, Device, ObjectID, PrintError = True):

    global gServer, gUserKey

    # Delete the object
    ref = creference()
    ref.parsereference ('//' + Site + '/' + str(Device) + '.' + ObjectID, LANGUAGE_ID_ENGLISH, gUserKey)
    PropList = cpropertylist()
    PropList.addreference (ref)

    gServer.executeobjectrequest (gUserKey, OBJECT_DELETE, PropList)
    PropList.rewind()
    ItemStatus = PropList.getitemstatus (LANGUAGE_ID_ENGLISH)
    if ItemStatus != 'OK' and PrintError:
        print 'Exception attempting to delete ' + ref.formatreference(LANGUAGE_ID_ENGLISH, FORMAT_FULL, gUserKey) + ': ' + ItemStatus


def WriteProperty(Site, Device, ObjectID, Property, WriteVal):

    global gServer, gUserKey
    ref = creference()
    ref.parsereference ('//' + Site + '/' + str(Device) + '.' + ObjectID + '.' + Property, LANGUAGE_ID_ENGLISH, gUserKey)
    PropList = cpropertylist()
    PropList.addreferencewithdata(ref, 5, WriteVal, LANGUAGE_ID_ENGLISH)

    gServer.executeobjectrequest(gUserKey, OBJECT_WRITE, PropList)

    PropList.rewind()
    ItemStatus = PropList.getitemstatus(LANGUAGE_ID_ENGLISH)
    if ItemStatus != 'OK':
        print 'Error Writing to ' + ObjectID + ': ' + ItemStatus
        return


def addScheduleEntry(ObjRef, PropList, sTime, sValue, sValueType):
    """ add the time value pair of the schedule entry"""
    ObjRef.setpropertybyname ('Time', LANGUAGE_ID_ENGLISH, 2)
    PropList.modifyitem (ObjRef, sTime, LANGUAGE_ID_ENGLISH)
    ObjRef.setpropertybyname ('Value', LANGUAGE_ID_ENGLISH, 2)
    if sValue == 'NULL':
        ObjRef.setpropertybyname ('Null', LANGUAGE_ID_ENGLISH, 3)
        PropList.modifyitem (ObjRef, ' ', LANGUAGE_ID_ENGLISH)
    else:
        ObjRef.setpropertybyname (sValueType, LANGUAGE_ID_ENGLISH, 3)
        PropList.modifyitem (ObjRef, sValue, LANGUAGE_ID_ENGLISH)


def addDateEvent(ObjRef, PropList, sDate, listOfTimeValues, sPriority, sDescription=None):
    """ add a single date exception event """
    # Period - Single Date
    ObjRef.setpropertybyname ('Period', LANGUAGE_ID_ENGLISH, 1)
    ObjRef.setpropertybyname ('CalendarEntry', LANGUAGE_ID_ENGLISH, 2)
    ObjRef.setpropertybyname ('Date', LANGUAGE_ID_ENGLISH, 3)
    PropList.modifyitem (ObjRef, sDate, LANGUAGE_ID_ENGLISH)
    # Schedules
    ObjRef.setpropertybyname ('Schedule', LANGUAGE_ID_ENGLISH, 1)

    listOfTimeValues = sorted(listOfTimeValues.items())
    i = 0
    for item in listOfTimeValues:
        i = i + 1
        ObjRef.setarrayindex (i, 1)
        sTime = item[0]
        sValue = item[1]
        addScheduleEntry(ObjRef, PropList, sTime, sValue, gScheduleType['ValueType'])

    # Event Priority
    ObjRef.setpropertybyname ('EventPriority', LANGUAGE_ID_ENGLISH, 1)
    PropList.modifyitem (ObjRef, sPriority, LANGUAGE_ID_ENGLISH)
    # Description
    if gDeltaDevice:
        ObjRef.setpropertybyname ('Description', LANGUAGE_ID_ENGLISH, 1)
        PropList.modifyitem (ObjRef, '', LANGUAGE_ID_ENGLISH)


def addDateRangeEvent(ObjRef, PropList, sDateStart, sDateEnd, listOfTimeValues, sPriority, sDescription=None):
    """ add a date range exception event"""
    # Period - Date Range
    ObjRef.setpropertybyname ('Period', LANGUAGE_ID_ENGLISH, 1)
    ObjRef.setpropertybyname ('CalendarEntry', LANGUAGE_ID_ENGLISH, 2)
    ObjRef.setpropertybyname ('DateRange', LANGUAGE_ID_ENGLISH, 3)
    ObjRef.setpropertybyname ('StartDate', LANGUAGE_ID_ENGLISH, 4)
    PropList.modifyitem (ObjRef, sDateStart, LANGUAGE_ID_ENGLISH)
    ObjRef.setpropertybyname ('EndDate', LANGUAGE_ID_ENGLISH, 4)
    PropList.modifyitem (ObjRef, sDateEnd, LANGUAGE_ID_ENGLISH)
    # Schedules
    ObjRef.setpropertybyname ('Schedule', LANGUAGE_ID_ENGLISH, 1)

    listOfTimeValues = sorted(listOfTimeValues.items())
    i = 0
    for item in listOfTimeValues:
        i = i + 1
        ObjRef.setarrayindex (i, 1)
        sTime = item[0]
        sValue = item[1]
        addScheduleEntry(ObjRef, PropList, sTime, sValue, gScheduleType['ValueType'])

    # Event Priority
    ObjRef.setpropertybyname ('EventPriority', LANGUAGE_ID_ENGLISH, 1)
    PropList.modifyitem (ObjRef, sPriority, LANGUAGE_ID_ENGLISH)
    # Description
    if gDeltaDevice:
        ObjRef.setpropertybyname ('Description', LANGUAGE_ID_ENGLISH, 1)
        PropList.modifyitem (ObjRef, '', LANGUAGE_ID_ENGLISH)


def addWeekNDayEvent(ObjRef, PropList, sMonth, sWeek, sDay, listOfTimeValues, sPriority, sDescription=None):
    """ add a week and day exception event """
    # Period - Recurring Week & Day
    ObjRef.setpropertybyname ('Period', LANGUAGE_ID_ENGLISH, 1)
    ObjRef.setpropertybyname ('CalendarEntry', LANGUAGE_ID_ENGLISH, 2)
    ObjRef.setpropertybyname ('WeekNDay', LANGUAGE_ID_ENGLISH, 3)
    ObjRef.setpropertybyname ('WDay', LANGUAGE_ID_ENGLISH, 4)
    PropList.modifyitem (ObjRef, sDay, LANGUAGE_ID_ENGLISH)
    ObjRef.setpropertybyname ('Month', LANGUAGE_ID_ENGLISH, 4)
    PropList.modifyitem (ObjRef, sMonth, LANGUAGE_ID_ENGLISH)
    ObjRef.setpropertybyname ('Week', LANGUAGE_ID_ENGLISH, 4)
    PropList.modifyitem (ObjRef, sWeek, LANGUAGE_ID_ENGLISH)
    # Schedule
    ObjRef.setpropertybyname ('Schedule', LANGUAGE_ID_ENGLISH, 1)

    listOfTimeValues = sorted(listOfTimeValues.items())
    i = 0
    for item in listOfTimeValues:
        i = i + 1
        ObjRef.setarrayindex (i, 1)
        sTime = item[0]
        sValue = item[1]
        addScheduleEntry(ObjRef, PropList, sTime, sValue, gScheduleType['ValueType'])

    # Event Priority
    ObjRef.setpropertybyname ('EventPriority', LANGUAGE_ID_ENGLISH, 1)
    PropList.modifyitem (ObjRef, sPriority, LANGUAGE_ID_ENGLISH)
    # Description
    if gDeltaDevice:
        ObjRef.setpropertybyname ('Description', LANGUAGE_ID_ENGLISH, 1)
        PropList.modifyitem (ObjRef, '', LANGUAGE_ID_ENGLISH)


def addCalendarEvent(ObjRef, PropList, sCALObjRef, listOfTimeValues, sPriority, sDescription=None):
    """ add a Calender exception event """
    # Period - Calendar Instance
    ObjRef.setpropertybyname ('Period', LANGUAGE_ID_ENGLISH, 1)
    ObjRef.setpropertybyname ('CalendarReference', LANGUAGE_ID_ENGLISH, 2)
    PropList.modifyitem (ObjRef, sCALObjRef, LANGUAGE_ID_ENGLISH)
    # Schedule
    ObjRef.setpropertybyname ('Schedule', LANGUAGE_ID_ENGLISH, 1)

    listOfTimeValues = sorted(listOfTimeValues.items())
    i = 0
    for item in listOfTimeValues:
        i = i + 1
        ObjRef.setarrayindex (i, 1)
        sTime = item[0]
        sValue = item[1]
        addScheduleEntry(ObjRef, PropList, sTime, sValue, gScheduleType['ValueType'])

    # Event Priority
    ObjRef.setpropertybyname ('EventPriority', LANGUAGE_ID_ENGLISH, 1)
    PropList.modifyitem (ObjRef, sPriority, LANGUAGE_ID_ENGLISH)
    # Description
    if gDeltaDevice:
        ObjRef.setpropertybyname ('Description', LANGUAGE_ID_ENGLISH, 1)
        PropList.modifyitem (ObjRef, '', LANGUAGE_ID_ENGLISH)


def CreateWeeklySchedule(sObjRef, sValueList):
    """ create weekly schedules """
    global gScheduleType
    ObjRef = creference('//' + gDefaultSite + '/' + str(gRemoteDevice) + '.' + sObjRef + '.Schedule', LANGUAGE_ID_ENGLISH, gUserKey)

    # start a property list with the top level element
    PropList = cpropertylist()
    PropList.addreference (ObjRef)

    PropList.setarraycount (None, 7)
    PropList.nextarrayitem ()

    ObjRef.setarrayindex (1, 0)
    ObjRef.setpropertybyname ('DaySchedule', LANGUAGE_ID_ENGLISH, 1)

    PropList.setarraycount (ObjRef, 1)

    # Monday (contains REAL values and NULL)
    gScheduleType = gScheduleReal

    ObjRef.setarrayindex (1, 1)
    sValue = gValueListReal[11]
    addScheduleEntry(ObjRef, PropList, '00:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (2, 1)
    sValue = gValueListReal[12]
    addScheduleEntry(ObjRef, PropList, '01:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (3, 1)
    sValue = gValueListReal[13]
    addScheduleEntry(ObjRef, PropList, '01:30:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (4, 1)
    sValue = gValueListReal[14]
    addScheduleEntry(ObjRef, PropList, '08:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (5, 1)
    sValue = gValueListReal[15]
    addScheduleEntry(ObjRef, PropList, '17:00:17.17', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (6, 1)
    sValue = 'NULL'
    addScheduleEntry(ObjRef, PropList, '23:59:59.99', sValue, gScheduleType['ValueType'])


    # Tuesday (contains ENUMERATED values and NULL)
    gScheduleType = gScheduleEnum

    PropList.nextarrayitem()
    ObjRef = PropList.getreference()

    ObjRef.setpropertybyname ('DaySchedule', LANGUAGE_ID_ENGLISH, 1)

    ObjRef.setarrayindex (1, 1)
    sValue = gValueListEnum[1]
    addScheduleEntry(ObjRef, PropList, '00:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (2, 1)
    sValue = gValueListEnum[2]
    addScheduleEntry(ObjRef, PropList, '02:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (3, 1)
    sValue = gValueListEnum[3]
    addScheduleEntry(ObjRef, PropList, '02:30:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (4, 1)
    sValue = gValueListEnum[4]
    addScheduleEntry(ObjRef, PropList, '08:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (5, 1)
    sValue = gValueListEnum[5]
    addScheduleEntry(ObjRef, PropList, '17:00:17.17', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (6, 1)
    sValue = 'NULL'
    addScheduleEntry(ObjRef, PropList, '23:59:59.99', sValue, gScheduleType['ValueType'])

    # Wednesay (contains Unsigned32 values and NULL)
    gScheduleType = gScheduleUnsigned

    PropList.nextarrayitem()
    ObjRef = PropList.getreference()

    ObjRef.setpropertybyname ('DaySchedule', LANGUAGE_ID_ENGLISH, 1)

    ObjRef.setarrayindex (1, 1)
    sValue = gValueListsUnsigned[1]
    addScheduleEntry(ObjRef, PropList, '02:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (2, 1)
    sValue = gValueListsUnsigned[2]
    addScheduleEntry(ObjRef, PropList, '03:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (3, 1)
    sValue = gValueListsUnsigned[3]
    addScheduleEntry(ObjRef, PropList, '03:30:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (4, 1)
    sValue = gValueListsUnsigned[4]
    addScheduleEntry(ObjRef, PropList, '08:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (5, 1)
    sValue = gValueListsUnsigned[5]
    addScheduleEntry(ObjRef, PropList, '17:00:17.17', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (6, 1)
    sValue = 'NULL'
    addScheduleEntry(ObjRef, PropList, '21:59:59.99', sValue, gScheduleType['ValueType'])


    gServer.executeobjectrequest(gUserKey, OBJECT_WRITE, PropList)
    PropList.rewind()
    ItemStatus = PropList.getitemstatus (LANGUAGE_ID_ENGLISH)
    if ItemStatus != 'OK':
        print 'CreateWeeklySchedule() get exceptions: ' + ItemStatus


def CreateExceptionScheduleAll(sObjRef, sValueList):
    """ create exception schedules """
    global gNumExceptions
    global gScheduleType
    gNumExceptions = 3    # set total numbers of exceptions
    ObjRef = None
    if gDeltaDevice:
        ObjRef = creference('//' + gDefaultSite + '/' + str(gRemoteDevice) + '.' + sObjRef + '.ExceptionsExt', LANGUAGE_ID_ENGLISH, gUserKey)
    else:
        ObjRef = creference('//' + gDefaultSite + '/' + str(gRemoteDevice) + '.' + sObjRef + '.Exceptions', LANGUAGE_ID_ENGLISH, gUserKey)

    # start a property list with the top level element
    PropList = cpropertylist()
    PropList.addreference (ObjRef)

    # create ExceptionScheduleSize items in the array
    PropList.setarraycount (None, gNumExceptions)
    PropList.nextarrayitem ()

    ObjRef.setarrayindex (1, 0)
    # Period - Single Date (contains REAL value)
    listOfTimeValues = {'01:00:00.00':gValueListReal[1],
                        '06:00:00.00':'NULL',
                        '20:00:00.00':gValueListReal[2],
                        '21:00:00.00':gValueListReal[3],
                        '21:05:00.00':gValueListReal[4],
                        '21:10:00.00':gValueListReal[5],
                        '21:15:00.00':gValueListReal[6],
                        '21:20:00.00':gValueListReal[7],
                        '21:25:00.00':gValueListReal[8],
                        '21:30:00.00':gValueListReal[9],
                        '22:00:00.00':gValueListReal[10],
                        '22:59:59.99':'NULL'}
    gScheduleType = gScheduleReal
    addDateEvent(ObjRef, PropList, gSingleDateList[0], listOfTimeValues, '16')

    ObjRef.setarrayindex (2, 0)
    PropList.nextarrayitem ()
    # Period - Single Date (contains ENUMERATED value)
    listOfTimeValues = {'01:00:00.00':gValueListEnum[1],
                        '06:00:00.00':'NULL',
                        '20:00:00.00':gValueListEnum[2],
                        '21:00:00.00':gValueListEnum[3],
                        '21:05:00.00':gValueListEnum[4],
                        '21:10:00.00':gValueListEnum[5],
                        '21:15:00.00':gValueListEnum[6],
                        '21:20:00.00':gValueListEnum[7],
                        '21:25:00.00':gValueListEnum[8],
                        '21:30:00.00':gValueListEnum[9],
                        '22:00:00.00':gValueListEnum[10],
                        '22:59:59.99':'NULL'}
    gScheduleType = gScheduleEnum
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '16')

    ObjRef.setarrayindex (3, 0)
    PropList.nextarrayitem ()
    # Period - Single Date (contains Unsigned32 value)
    listOfTimeValues = {'01:00:00.00':gValueListsUnsigned[1],
                        '06:00:00.00':'NULL',
                        '20:00:00.00':gValueListsUnsigned[2],
                        '21:00:00.00':gValueListsUnsigned[3],
                        '21:05:00.00':gValueListsUnsigned[4],
                        '21:10:00.00':gValueListsUnsigned[5],
                        '21:15:00.00':gValueListsUnsigned[6],
                        '21:20:00.00':gValueListsUnsigned[7],
                        '21:25:00.00':gValueListsUnsigned[8],
                        '21:30:00.00':gValueListsUnsigned[9],
                        '22:00:00.00':gValueListsUnsigned[10],
                        '22:59:59.99':'NULL'}
    gScheduleType = gScheduleUnsigned
    addDateEvent(ObjRef, PropList, gSingleDateList[2], listOfTimeValues, '16')


    gServer.executeobjectrequest(gUserKey, OBJECT_WRITE, PropList)
    PropList.rewind()
    ItemStatus = PropList.getitemstatus (LANGUAGE_ID_ENGLISH)
    if ItemStatus != 'OK':
        print 'CreateExceptionSchedule() get exceptions: ' + ItemStatus

def CreateExceptionScheduleSingle(sObjRef, sValueList):
    """ create exception schedules """
    global gNumExceptions
    global gScheduleType
    gNumExceptions = 3    # set total numbers of exceptions
    ObjRef = None
    if gDeltaDevice:
        ObjRef = creference('//' + gDefaultSite + '/' + str(gRemoteDevice) + '.' + sObjRef + '.ExceptionsExt', LANGUAGE_ID_ENGLISH, gUserKey)
    else:
        ObjRef = creference('//' + gDefaultSite + '/' + str(gRemoteDevice) + '.' + sObjRef + '.Exceptions', LANGUAGE_ID_ENGLISH, gUserKey)

    # grow the array  1
    ExceptionCount = 1
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date (contains REAL value)
    listOfTimeValues = {'01:00:00.00':gValueListReal[1],
                        '06:00:00.00':'NULL',
                        '20:00:00.00':gValueListReal[2],
                        '21:00:00.00':gValueListReal[3],
                        '21:05:00.00':gValueListReal[4],
                        '21:10:00.00':gValueListReal[5],
                        '21:15:00.00':gValueListReal[6],
                        '21:20:00.00':gValueListReal[7],
                        '21:25:00.00':gValueListReal[8],
                        '21:30:00.00':gValueListReal[9],
                        '22:00:00.00':gValueListReal[10],
                        '22:59:59.99':'NULL'}
    gScheduleType = gScheduleReal
    addDateEvent(ObjRef, PropList, gSingleDateList[0], listOfTimeValues, '16')
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 2
    ExceptionCount = ExceptionCount + 1
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date (contains ENUMERATED value)
    listOfTimeValues = {'01:00:00.00':gValueListEnum[1],
                        '06:00:00.00':'NULL',
                        '20:00:00.00':gValueListEnum[2],
                        '21:00:00.00':gValueListEnum[3],
                        '21:05:00.00':gValueListEnum[4],
                        '21:10:00.00':gValueListEnum[5],
                        '21:15:00.00':gValueListEnum[6],
                        '21:20:00.00':gValueListEnum[7],
                        '21:25:00.00':gValueListEnum[8],
                        '21:30:00.00':gValueListEnum[9],
                        '22:00:00.00':gValueListEnum[10],
                        '22:59:59.99':'NULL'}
    gScheduleType = gScheduleEnum
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '16')
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 3
    ExceptionCount = ExceptionCount + 1
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date (contains Unsigned32 value)
    listOfTimeValues = {'01:00:00.00':gValueListsUnsigned[1],
                        '06:00:00.00':'NULL',
                        '20:00:00.00':gValueListsUnsigned[2],
                        '21:00:00.00':gValueListsUnsigned[3],
                        '21:05:00.00':gValueListsUnsigned[4],
                        '21:10:00.00':gValueListsUnsigned[5],
                        '21:15:00.00':gValueListsUnsigned[6],
                        '21:20:00.00':gValueListsUnsigned[7],
                        '21:25:00.00':gValueListsUnsigned[8],
                        '21:30:00.00':gValueListsUnsigned[9],
                        '22:00:00.00':gValueListsUnsigned[10],
                        '22:59:59.99':'NULL'}
    gScheduleType = gScheduleUnsigned
    addDateEvent(ObjRef, PropList, gSingleDateList[2], listOfTimeValues, '16')
    ApplySingleChange(PropList, ExceptionCount)

def ApplySingleChange(PropList, ExceptionCount):
    """helper function used by CreateExceptionScheduleSingle() """
    global gLongestWriteTime
    StartTime = time.time()
    gServer.executeobjectrequest(gUserKey, OBJECT_WRITE, PropList)
    EndTime = time.time()
    TotalTime = EndTime - StartTime

    gLongestWriteTime = max(gLongestWriteTime, TotalTime)
    print ("%d   Write Time: %s" % (ExceptionCount, str(TotalTime)))
    #print 'DEBUG: LongestWriteTime: ' + str(LongestWriteTime)

    PropList.rewind()
    ItemStatus = PropList.getitemstatus (LANGUAGE_ID_ENGLISH)
    if ItemStatus != 'OK':
      print 'Error when writing exceptions: ' + ItemStatus

    if gSleepFactor > 0:
      time.sleep( gSleepFactor * (LongestWriteTime + 0.2) )

def getSingleDateList(startingDate, NumberOfEntry):
    """ generate a list of single date string in the format of
        'yyyy/mm/dd/wd'
    """
    result = []
    wdConverter = {0:1, 1:2, 2:3, 3:4, 4:5, 5:6, 6:7}
    dateObj = datetime.datetime.strptime(startingDate, '%Y/%m/%d').date()
    i = 0
    while i < NumberOfEntry:
        if i <> 0:
            dateObj = dateObj + datetime.timedelta(1)
        dayOfWeek = wdConverter[dateObj.weekday()]
        dateString = dateObj.strftime('%Y/%m/%d') + '/' + str(dayOfWeek)
        result.append(dateString)
        i = i + 1
    return result


def setDeviceTime(dateString=None, timeString=None):
    """ set device time
        dateString format: yyyy/mm/dd/w
        timestring format: xx:xx:xx.xx
    """
    wdConverter = {0:1, 1:2, 2:3, 3:4, 4:5, 5:6, 6:7}
    sDate = dateString
    sTime = timeString
    if sDate == None:
        today = datetime.datetime.today()
        myDate = today.date()
        dayOfWeek = wdConverter[myDate.weekday()]
        sDate = myDate.strftime('%Y/%m/%d') + '/' + str(dayOfWeek)
    if sTime == None:
        today = datetime.datetime.today()
        myTime = today.time()
        sTime = myTime.strftime('%H:%M:%S.00')
    WriteProperty(gDefaultSite, gRemoteDevice, 'DEV'+ str(gRemoteDevice), 'Date', sDate)
    WriteProperty(gDefaultSite, gRemoteDevice, 'DEV'+ str(gRemoteDevice), 'Time', sTime)


if __name__ == '__main__':
    CreateSchedule('SCH4', 'Test_SCH4', 'Real')
    CreateSchedule('SCH5', 'Test_SCH5', 'UnsignedInteger')
    CreateSchedule('SCH6', 'Test_SCH6', 'Enum')
