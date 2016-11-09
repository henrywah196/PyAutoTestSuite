'''
BTL Specified Test - 5.0
13.X6 Workstation Scheduling Tests
the script is used to create Reference Schedule S1 object
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

gLocalDevice = 910802
gDefaultSite = 'Hist DB'
gDefaultGroup = 'Administrators'

gRemoteDevice = 9901    # address of panel being tested
gDeltaDevice = False

gWriteMode = 'single'    # 'all' (all exceptions written at once)
                         # 'single' (each exception written individually)

gScheduleReal = {'ValueType': 'Real', 'DefaultValue': '0', 'ActiveValue': '5' } # Real
gScheduleUnsigned = {'ValueType': 'UnsignedInteger', 'DefaultValue': '1', 'ActiveValue': '3' } # multi-state
gScheduleEnum = {'ValueType': 'Enum', 'DefaultValue': '0', 'ActiveValue': '1' } # binary

gExceptionDescription = 'Event'    # None (if you don't want add schedule description)

gLongestWriteTime = 0

gSleepFactor = 3    # set > 0 to pause after each write. Each pause will be: gSleepFactor * (largest write time so far + 0.2)
                    # may be helpful when writing large SCH in single mode
                    # for Tetra try = 1; for DSC = 5
### end of script config ###

# global variables
gScheduleType = None
gNumExceptions = 255     # max 255
gServer = None
gUserKey = None

gValueListReal = ['4.29497e+009', '2.22', '3.33', '1.84467e+019', '0.535156', 'NULL', '1', '0.75', '0.8125', '0.75', '0.625', '0.9375', '0.8125', '0.535156', '18']
gValueListsUnsigned = ['1', '2', '3', '4294967201', '5', 'NULL', '2', '3', '2', '3', '4294967201', '3', '4294967201', '5', '4294967201']
gValueListEnum = ['0', '1', '0', '1', '0', 'NULL', '0', '1', '0', '1', '0', '1', '0', '1', '0']

gDateRangeList = [['2014/02/01/6', '2014/02/02/7'],
                  ['2014/02/03/1', '2014/02/06/4'],
                  ['2014/02/08/6', '2014/02/09/7']]    # date ranged used by exception 1 - 3

gSingleDateList = ['2014/02/11/2',
                   '2014/02/12/3',
                   '2014/02/14/5',
                   '2014/02/20/4']    # single date used by exception 4, 13-27, 28, 29, 30(31-255)

gWeekNDayList = [['13', '3', '1'],
                 ['14', '255', '7'],
                 ['255', '6', '2'],
                 ['2', '255', '5'],
                 ['255', '1', '255']]    # Recurring week and day used by exception 5-9
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
    #Port = gServer.getportlist (gUserKey, PORT_TYPE_ETHERNET)[1]
    #Port.bind (gUserKey, gDefaultSite)
    #Port.enable (gUserKey)
    #Port.open (gUserKey)
    
    # connect via existing IP Foreign connection
    PortList = gServer.getportlist(gUserKey, PORT_TYPE_BNIP)
    

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
    if not sDescription:
        sDescription = ''
    if gDeltaDevice:
        ObjRef.setpropertybyname ('Description', LANGUAGE_ID_ENGLISH, 1)
        PropList.modifyitem (ObjRef, sDescription, LANGUAGE_ID_ENGLISH)


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
    if not sDescription:
        sDescription = ''
    if gDeltaDevice:
        ObjRef.setpropertybyname ('Description', LANGUAGE_ID_ENGLISH, 1)
        PropList.modifyitem (ObjRef, sDescription, LANGUAGE_ID_ENGLISH)


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
    if not sDescription:
        sDescription = ''
    if gDeltaDevice:
        ObjRef.setpropertybyname ('Description', LANGUAGE_ID_ENGLISH, 1)
        PropList.modifyitem (ObjRef, sDescription, LANGUAGE_ID_ENGLISH)


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
    if not sDescription:
        sDescription = ''
    if gDeltaDevice:
        ObjRef.setpropertybyname ('Description', LANGUAGE_ID_ENGLISH, 1)
        PropList.modifyitem (ObjRef, sDescription, LANGUAGE_ID_ENGLISH)


def CreateWeeklySchedule(sObjRef, sValueList):
    """ create weekly schedules """
    ObjRef = creference('//' + gDefaultSite + '/' + str(gRemoteDevice) + '.' + sObjRef + '.Schedule', LANGUAGE_ID_ENGLISH, gUserKey)

    # start a property list with the top level element
    PropList = cpropertylist()
    PropList.addreference (ObjRef)

    PropList.setarraycount (None, 7)
    PropList.nextarrayitem ()

    ObjRef.setarrayindex (1, 0)
    ObjRef.setpropertybyname ('DaySchedule', LANGUAGE_ID_ENGLISH, 1)

    PropList.setarraycount (ObjRef, 1)

    # Monday

    ObjRef.setarrayindex (1, 1)
    sValue = sValueList[0]
    addScheduleEntry(ObjRef, PropList, '00:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (2, 1)
    sValue = sValueList[1]
    addScheduleEntry(ObjRef, PropList, '01:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (3, 1)
    sValue = sValueList[2]
    addScheduleEntry(ObjRef, PropList, '01:30:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (4, 1)
    sValue = sValueList[3]
    addScheduleEntry(ObjRef, PropList, '08:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (5, 1)
    sValue = sValueList[4]
    addScheduleEntry(ObjRef, PropList, '17:00:17.17', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (6, 1)
    sValue = sValueList[5]
    addScheduleEntry(ObjRef, PropList, '23:59:59.99', sValue, gScheduleType['ValueType'])


    # Tuesday

    PropList.nextarrayitem()
    ObjRef = PropList.getreference()

    ObjRef.setpropertybyname ('DaySchedule', LANGUAGE_ID_ENGLISH, 1)

    ObjRef.setarrayindex (1, 1)
    sValue = sValueList[0]
    addScheduleEntry(ObjRef, PropList, '00:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (2, 1)
    sValue = sValueList[1]
    addScheduleEntry(ObjRef, PropList, '02:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (3, 1)
    sValue = sValueList[2]
    addScheduleEntry(ObjRef, PropList, '02:30:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (4, 1)
    sValue = sValueList[3]
    addScheduleEntry(ObjRef, PropList, '08:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (5, 1)
    sValue = sValueList[4]
    addScheduleEntry(ObjRef, PropList, '17:00:17.17', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (6, 1)
    sValue = sValueList[5]
    addScheduleEntry(ObjRef, PropList, '23:59:59.99', sValue, gScheduleType['ValueType'])

    # Wednesay

    PropList.nextarrayitem()
    ObjRef = PropList.getreference()

    ObjRef.setpropertybyname ('DaySchedule', LANGUAGE_ID_ENGLISH, 1)

    ObjRef.setarrayindex (1, 1)
    sValue = sValueList[0]
    addScheduleEntry(ObjRef, PropList, '02:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (2, 1)
    sValue = sValueList[1]
    addScheduleEntry(ObjRef, PropList, '03:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (3, 1)
    sValue = sValueList[2]
    addScheduleEntry(ObjRef, PropList, '03:30:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (4, 1)
    sValue = sValueList[3]
    addScheduleEntry(ObjRef, PropList, '08:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (5, 1)
    sValue = sValueList[4]
    addScheduleEntry(ObjRef, PropList, '17:00:17.17', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (6, 1)
    sValue = 'NULL'
    addScheduleEntry(ObjRef, PropList, '21:59:59.99', sValue, gScheduleType['ValueType'])

    # Thursday

    PropList.nextarrayitem()
    ObjRef = PropList.getreference()

    ObjRef.setpropertybyname ('DaySchedule', LANGUAGE_ID_ENGLISH, 1)

    ObjRef.setarrayindex (1, 1)
    sValue = sValueList[0]
    addScheduleEntry(ObjRef, PropList, '02:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (2, 1)
    sValue = sValueList[1]
    addScheduleEntry(ObjRef, PropList, '04:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (3, 1)
    sValue = sValueList[2]
    addScheduleEntry(ObjRef, PropList, '04:30:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (4, 1)
    sValue = sValueList[3]
    addScheduleEntry(ObjRef, PropList, '08:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (5, 1)
    sValue = sValueList[4]
    addScheduleEntry(ObjRef, PropList, '17:00:17.17', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (6, 1)
    sValue = 'NULL'
    addScheduleEntry(ObjRef, PropList, '21:59:59.99', sValue, gScheduleType['ValueType'])



    # Friday

    PropList.nextarrayitem()
    ObjRef = PropList.getreference()

    ObjRef.setpropertybyname ('DaySchedule', LANGUAGE_ID_ENGLISH, 1)

    ObjRef.setarrayindex (1, 1)
    sValue = sValueList[0]
    addScheduleEntry(ObjRef, PropList, '00:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (2, 1)
    sValue = sValueList[1]
    addScheduleEntry(ObjRef, PropList, '05:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (3, 1)
    sValue = sValueList[2]
    addScheduleEntry(ObjRef, PropList, '05:30:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (4, 1)
    sValue = sValueList[3]
    addScheduleEntry(ObjRef, PropList, '08:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (5, 1)
    sValue = sValueList[4]
    addScheduleEntry(ObjRef, PropList, '17:00:17.17', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (6, 1)
    sValue = sValueList[5]
    addScheduleEntry(ObjRef, PropList, '23:59:59.99', sValue, gScheduleType['ValueType'])

    # Saturday

    PropList.nextarrayitem()
    ObjRef = PropList.getreference()

    ObjRef.setpropertybyname ('DaySchedule', LANGUAGE_ID_ENGLISH, 1)

    ObjRef.setarrayindex (1, 1)
    sValue = 'NULL'
    addScheduleEntry(ObjRef, PropList, '00:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (2, 1)
    sValue = sValueList[1]
    addScheduleEntry(ObjRef, PropList, '06:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (3, 1)
    sValue = 'NULL'
    addScheduleEntry(ObjRef, PropList, '06:30:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (4, 1)
    sValue = sValueList[3]
    addScheduleEntry(ObjRef, PropList, '08:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (5, 1)
    sValue = sValueList[4]
    addScheduleEntry(ObjRef, PropList, '12:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (6, 1)
    sValue = 'NULL'
    addScheduleEntry(ObjRef, PropList, '13:00:00.00', sValue, gScheduleType['ValueType'])

    # Sunday

    PropList.nextarrayitem()
    ObjRef = PropList.getreference()

    ObjRef.setpropertybyname ('DaySchedule', LANGUAGE_ID_ENGLISH, 1)

    ObjRef.setarrayindex (1, 1)
    sValue = 'NULL'
    addScheduleEntry(ObjRef, PropList, '00:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (2, 1)
    sValue = sValueList[1]
    addScheduleEntry(ObjRef, PropList, '07:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (3, 1)
    sValue = 'NULL'
    addScheduleEntry(ObjRef, PropList, '07:30:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (4, 1)
    sValue = sValueList[3]
    addScheduleEntry(ObjRef, PropList, '12:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (5, 1)
    sValue = sValueList[4]
    addScheduleEntry(ObjRef, PropList, '17:00:00.00', sValue, gScheduleType['ValueType'])

    ObjRef.setarrayindex (6, 1)
    sValue = 'NULL'
    addScheduleEntry(ObjRef, PropList, '18:00:00.00', sValue, gScheduleType['ValueType'])


    gServer.executeobjectrequest(gUserKey, OBJECT_WRITE, PropList)
    PropList.rewind()
    ItemStatus = PropList.getitemstatus (LANGUAGE_ID_ENGLISH)
    if ItemStatus != 'OK':
        print 'CreateWeeklySchedule() get exceptions: ' + ItemStatus


def CreateExceptionScheduleAll(sObjRef, sValueList):
    """ create exception schedules with WriteMode as All"""
    global gNumExceptions
    gNumExceptions = 255    # set total numbers of exceptions
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
    # Period - Date Range
    listOfTimeValues = {'01:00:00.00':sValueList[0],
                        '06:00:00.00':'NULL',
                        '20:00:00.00':sValueList[2],
                        '21:00:00.00':sValueList[3],
                        '21:05:00.00':sValueList[4],
                        '21:10:00.00':sValueList[5],
                        '21:15:00.00':sValueList[6],
                        '21:20:00.00':sValueList[7],
                        '21:25:00.00':sValueList[8],
                        '21:30:00.00':sValueList[9],
                        '22:00:00.00':sValueList[10],
                        '22:59:59.99':'NULL'}
    addDateRangeEvent(ObjRef, PropList, gDateRangeList[0][0], gDateRangeList[0][1], listOfTimeValues, '16')

    ObjRef.setarrayindex (2, 0)
    PropList.nextarrayitem ()
    # Period - Date Range
    # listOfTimeValues - > same as above
    addDateRangeEvent(ObjRef, PropList, gDateRangeList[1][0], gDateRangeList[1][1], listOfTimeValues, '16')

    ObjRef.setarrayindex (3, 0)
    PropList.nextarrayitem ()
    # Period - Date Range
    # listOfTimeValues - > same as above
    addDateRangeEvent(ObjRef, PropList, gDateRangeList[2][0], gDateRangeList[2][1], listOfTimeValues, '16')

    ObjRef.setarrayindex (4, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    # listOfTimeValues - > same as above
    addDateEvent(ObjRef, PropList, gSingleDateList[0], listOfTimeValues, '16')

    ObjRef.setarrayindex (5, 0)
    PropList.nextarrayitem ()
    # Period - Recurring Week and Day
    # listOfTimeValues - > same as above
    addWeekNDayEvent(ObjRef, PropList, gWeekNDayList[0][0], gWeekNDayList[0][1], gWeekNDayList[0][2], listOfTimeValues, '16')

    ObjRef.setarrayindex (6, 0)
    PropList.nextarrayitem ()
    # Period - Recurring Week and Day
    # listOfTimeValues - > same as above
    addWeekNDayEvent(ObjRef, PropList, gWeekNDayList[1][0], gWeekNDayList[1][1], gWeekNDayList[1][2], listOfTimeValues, '16')

    ObjRef.setarrayindex (7, 0)
    PropList.nextarrayitem ()
    # Period - Recurring Week and Day
    # listOfTimeValues - > same as above
    addWeekNDayEvent(ObjRef, PropList, gWeekNDayList[2][0], gWeekNDayList[2][1], gWeekNDayList[2][2], listOfTimeValues, '16')

    ObjRef.setarrayindex (8, 0)
    PropList.nextarrayitem ()
    # Period - Recurring Week and Day
    # listOfTimeValues - > same as above
    addWeekNDayEvent(ObjRef, PropList, gWeekNDayList[3][0], gWeekNDayList[3][1], gWeekNDayList[3][2], listOfTimeValues, '16')

    ObjRef.setarrayindex (9, 0)
    PropList.nextarrayitem ()
    # Period - Recurring Week and Day
    # listOfTimeValues - > same as above
    addWeekNDayEvent(ObjRef, PropList, gWeekNDayList[4][0], gWeekNDayList[4][1], gWeekNDayList[4][2], listOfTimeValues, '16')

    ObjRef.setarrayindex (10, 0)
    PropList.nextarrayitem ()
    # Period - Calendar Reference
    listOfTimeValues = {'08:15:00.00':sValueList[0], '16:45:00.00':'NULL'}
    addCalendarEvent(ObjRef, PropList, 'CAL1', listOfTimeValues, '15')

    ObjRef.setarrayindex (11, 0)
    PropList.nextarrayitem ()
    # Period - Calendar Reference
    listOfTimeValues = {'12:00:00.00':sValueList[1], '13:00:00.00':'NULL'}
    addCalendarEvent(ObjRef, PropList, 'CAL1', listOfTimeValues, '14')

    ObjRef.setarrayindex (12, 0)
    PropList.nextarrayitem ()
    # Period - Calendar Reference
    listOfTimeValues = {'14:00:00.00':sValueList[0], '15:00:00.00':'NULL'}
    addCalendarEvent(ObjRef, PropList, 'CAL2', listOfTimeValues, '15')

    ObjRef.setarrayindex (13, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'08:15:00.00':sValueList[0], '16:45:00.00':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '15')

    ObjRef.setarrayindex (14, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'08:30:00.00':sValueList[1], '16:30:00.00':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '14')

    ObjRef.setarrayindex (15, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'08:45:00.00':sValueList[2], '16:15:00.00':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '13')

    ObjRef.setarrayindex (16, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'09:00:00.00':sValueList[3], '16:00:00.00':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '12')

    ObjRef.setarrayindex (17, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'09:15:00.00':sValueList[4], '15:45:00.00':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '11')

    ObjRef.setarrayindex (18, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'09:30:00.00':sValueList[5], '15:30:00.00':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '10')

    ObjRef.setarrayindex (19, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'09:45:00.00':sValueList[6], '15:15:00.00':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '9')

    ObjRef.setarrayindex (20, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'10:00:00.00':sValueList[7], '15:00:00.00':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '8')

    ObjRef.setarrayindex (21, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'10:15:00.00':sValueList[8], '14:45:00.00':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '7')

    ObjRef.setarrayindex (22, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'10:30:00.00':sValueList[9], '14:30:00.00':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '6')

    ObjRef.setarrayindex (23, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'10:45:00.00':sValueList[10], '14:15:00.00':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '5')

    ObjRef.setarrayindex (24, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'11:00:00.00':sValueList[11], '14:00:00.00':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '4')

    ObjRef.setarrayindex (25, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'11:15:00.00':sValueList[12], '13:45:00.00':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '3')

    ObjRef.setarrayindex (26, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'11:30:00.00':sValueList[13], '13:30:00.00':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '2')

    ObjRef.setarrayindex (27, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'11:45:00.00':sValueList[14], '13:15:00.00':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '1')

    ObjRef.setarrayindex (28, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    # where the times in the list of time value are not in chronological order
    listOfTimeValues = {'22:00:00.00':sValueList[10],
                        '21:00:00.00':sValueList[3],
                        '06:00:00.00':'NULL',
                        '20:00:00.00':sValueList[2],
                        '01:00:00.00':sValueList[0],
                        '22:59:59.99':'NULL'}
    addDateEvent(ObjRef, PropList, gSingleDateList[2], listOfTimeValues, '16')

    ObjRef.setarrayindex (29, 0)
    PropList.nextarrayitem ()
    # Period - Single Date
    listOfTimeValues = {'00:00:00.00':'NULL',
                        '13:00:00.00':sValueList[0],
                        '15:00:00.00':sValueList[1]}
    addDateEvent(ObjRef, PropList, gSingleDateList[3], listOfTimeValues, '16')


    # the remaining BACnetSpecial Events (30 - 255) are "filler"
    # to create a schedule large encough for testing.
    # you may need to increase Max_Segments_Accepted on simBA.
    # you may need to stop Quattro Service and clean the Quattro
    # database from ProgramData folder.
    singleDateList = getSingleDateList('2008/01/01', 226)

    listOfTimeValues = {'00:00:00.00':'NULL',
                        '11:00:00.00':sValueList[1],
                        '11:30:00.00':'NULL',
                        '21:00:00.00':sValueList[3],
                        '21:05:00.00':sValueList[4],
                        '21:10:00.00':sValueList[5],
                        '21:15:00.00':sValueList[6],
                        '21:20:00.00':sValueList[7],
                        '21:25:00.00':sValueList[8],
                        '21:30:00.00':sValueList[9],
                        '22:00:00.00':sValueList[10],
                        '23:00:00.00':'NULL'}

    i = 30
    while i <= gNumExceptions:
        ObjRef.setarrayindex (i, 0)
        PropList.nextarrayitem ()
        # Period - Single Date
        addDateEvent(ObjRef, PropList, singleDateList[i - 30], listOfTimeValues, '16')
        i = i + 1

    gServer.executeobjectrequest(gUserKey, OBJECT_WRITE, PropList)
    PropList.rewind()
    ItemStatus = PropList.getitemstatus (LANGUAGE_ID_ENGLISH)
    if ItemStatus != 'OK':
        print 'CreateExceptionSchedule() get exceptions: ' + ItemStatus


def CreateExceptionScheduleSingle(sObjRef, sValueList):
    """ create exception schedules using WriteMode as Single"""
    #global gNumExceptions
    #gNumExceptions = 255    # set total numbers of exceptions

    ObjRef = None
    if gDeltaDevice:
        ObjRef = creference('//' + gDefaultSite + '/' + str(gRemoteDevice) + '.' + sObjRef + '.ExceptionsExt', LANGUAGE_ID_ENGLISH, gUserKey)
    else:
        ObjRef = creference('//' + gDefaultSite + '/' + str(gRemoteDevice) + '.' + sObjRef + '.Exceptions', LANGUAGE_ID_ENGLISH, gUserKey)

    # grow the array  1
    ExceptionCount = 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Date Range
    listOfTimeValues = {'01:00:00.00':sValueList[0],
                        '06:00:00.00':'NULL',
                        '20:00:00.00':sValueList[2],
                        '21:00:00.00':sValueList[3],
                        '21:05:00.00':sValueList[4],
                        '21:10:00.00':sValueList[5],
                        '21:15:00.00':sValueList[6],
                        '21:20:00.00':sValueList[7],
                        '21:25:00.00':sValueList[8],
                        '21:30:00.00':sValueList[9],
                        '22:00:00.00':sValueList[10],
                        '22:59:59.99':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateRangeEvent(ObjRef, PropList, gDateRangeList[0][0], gDateRangeList[0][1], listOfTimeValues, '16', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 2
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Date Range
    # listOfTimeValues - > same as above
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateRangeEvent(ObjRef, PropList, gDateRangeList[1][0], gDateRangeList[1][1], listOfTimeValues, '16', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 3
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Date Range
    # listOfTimeValues - > same as above
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateRangeEvent(ObjRef, PropList, gDateRangeList[2][0], gDateRangeList[2][1], listOfTimeValues, '16', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 4
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    # listOfTimeValues - > same as above
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[0], listOfTimeValues, '16', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 5
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Recurring Week and Day
    # listOfTimeValues - > same as above
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addWeekNDayEvent(ObjRef, PropList, gWeekNDayList[0][0], gWeekNDayList[0][1], gWeekNDayList[0][2], listOfTimeValues, '16', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 6
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Recurring Week and Day
    # listOfTimeValues - > same as above
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addWeekNDayEvent(ObjRef, PropList, gWeekNDayList[1][0], gWeekNDayList[1][1], gWeekNDayList[1][2], listOfTimeValues, '16', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 7
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Recurring Week and Day
    # listOfTimeValues - > same as above
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addWeekNDayEvent(ObjRef, PropList, gWeekNDayList[2][0], gWeekNDayList[2][1], gWeekNDayList[2][2], listOfTimeValues, '16', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 8
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Recurring Week and Day
    # listOfTimeValues - > same as above
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addWeekNDayEvent(ObjRef, PropList, gWeekNDayList[3][0], gWeekNDayList[3][1], gWeekNDayList[3][2], listOfTimeValues, '16', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 9
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Recurring Week and Day
    # listOfTimeValues - > same as above
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addWeekNDayEvent(ObjRef, PropList, gWeekNDayList[4][0], gWeekNDayList[4][1], gWeekNDayList[4][2], listOfTimeValues, '16', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 10
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Calendar Reference
    listOfTimeValues = {'08:15:00.00':sValueList[0], '16:45:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addCalendarEvent(ObjRef, PropList, 'CAL1', listOfTimeValues, '15', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 11
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Calendar Reference
    listOfTimeValues = {'12:00:00.00':sValueList[1], '13:00:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addCalendarEvent(ObjRef, PropList, 'CAL1', listOfTimeValues, '14', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 12
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Calendar Reference
    listOfTimeValues = {'14:00:00.00':sValueList[0], '15:00:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addCalendarEvent(ObjRef, PropList, 'CAL2', listOfTimeValues, '15', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 13
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'08:15:00.00':sValueList[0], '16:45:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '15', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 14
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'08:30:00.00':sValueList[1], '16:30:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '14', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 15
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'08:45:00.00':sValueList[2], '16:15:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '13', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 16
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'09:00:00.00':sValueList[3], '16:00:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '12', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 17
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'09:15:00.00':sValueList[4], '15:45:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '11', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 18
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'09:30:00.00':sValueList[5], '15:30:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '10', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 19
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'09:45:00.00':sValueList[6], '15:15:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '9', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 20
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'10:00:00.00':sValueList[7], '15:00:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '8', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 21
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'10:15:00.00':sValueList[8], '14:45:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '7', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 22
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'10:30:00.00':sValueList[9], '14:30:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '6', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 23
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'10:45:00.00':sValueList[10], '14:15:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '5', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 24
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'11:00:00.00':sValueList[11], '14:00:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '4', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 25
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'11:15:00.00':sValueList[12], '13:45:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '3', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 26
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'11:30:00.00':sValueList[13], '13:30:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '2', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 27
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'11:45:00.00':sValueList[14], '13:15:00.00':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[1], listOfTimeValues, '1', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 28
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    # where the times in the list of time value are not in chronological order
    listOfTimeValues = {'22:00:00.00':sValueList[10],
                        '21:00:00.00':sValueList[3],
                        '06:00:00.00':'NULL',
                        '20:00:00.00':sValueList[2],
                        '01:00:00.00':sValueList[0],
                        '22:59:59.99':'NULL'}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[2], listOfTimeValues, '16', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # grow the array 29
    ExceptionCount = ExceptionCount + 1
    if ExceptionCount > gNumExceptions: return
    ObjRef.setdepth(0)
    PropList = cpropertylist()
    ObjRef.setarrayindex(0, 0)
    PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

    ObjRef.setdepth(0)
    ObjRef.setarrayindex (ExceptionCount, 0)
    PropList.addreference(ObjRef)
    # Period - Single Date
    listOfTimeValues = {'00:00:00.00':'NULL',
                        '13:00:00.00':sValueList[0],
                        '15:00:00.00':sValueList[1]}
    # Schedule Description
    Description = None
    if gExceptionDescription:
        Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
    addDateEvent(ObjRef, PropList, gSingleDateList[3], listOfTimeValues, '16', Description)
    ApplySingleChange(PropList, ExceptionCount)

    # the remaining BACnetSpecial Events (30 - 255) are "filler"
    # to create a schedule large encough for testing.
    # you may need to increase Max_Segments_Accepted on simBA.
    # you may need to stop Quattro Service and clean the Quattro
    # database from ProgramData folder.
    singleDateList = getSingleDateList('2014/02/01', 226)

    listOfTimeValues = {'00:00:00.00':'NULL',
                        '11:00:00.00':sValueList[1],
                        '11:30:00.00':'NULL',
                        '21:00:00.00':sValueList[3],
                        '21:05:00.00':sValueList[4],
                        '21:10:00.00':sValueList[5],
                        '21:15:00.00':sValueList[6],
                        '21:20:00.00':sValueList[7],
                        '21:25:00.00':sValueList[8],
                        '21:30:00.00':sValueList[9],
                        '22:00:00.00':sValueList[10],
                        '23:00:00.00':'NULL'}

    while ExceptionCount < gNumExceptions:
        # grow the array 29
        ExceptionCount = ExceptionCount + 1
        ObjRef.setdepth(0)
        PropList = cpropertylist()
        ObjRef.setarrayindex(0, 0)
        PropList.addreferencewithdata(ObjRef, PRIORITY_NONE, str(ExceptionCount), LANGUAGE_ID_ENGLISH)

        ObjRef.setdepth(0)
        ObjRef.setarrayindex (ExceptionCount, 0)
        PropList.addreference(ObjRef)
        # Period - Single Date
        # Schedule Description
        Description = None
        if gExceptionDescription:
            Description = gExceptionDescription + " " + "%03d"%(ExceptionCount,)
        addDateEvent(ObjRef, PropList, singleDateList[ExceptionCount - 30], listOfTimeValues, '16', Description)
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
      time.sleep( gSleepFactor * (gLongestWriteTime + 0.2) )



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
    CreateSchedule('SCH1', 'Test_SCH1', 'Real')
    CreateSchedule('SCH2', 'Test_SCH2', 'UnsignedInteger')
    CreateSchedule('SCH3', 'Test_SCH3', 'Enum')
