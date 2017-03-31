#!/usr/bin/env python

"""
This application presents a 'console' prompt to the user asking for Who-Is and I-Am
commands which create the related APDUs, then lines up the corresponding I-Am
for incoming traffic and prints out the contents.
"""

import sys, datetime, random, time

from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.consolelogging import ConfigArgumentParser
from bacpypes.consolecmd import ConsoleCmd

from bacpypes.core import run, enable_sleeping

from bacpypes.pdu import Address, GlobalBroadcast, LocalStation
from bacpypes.apdu import WhoIsRequest, IAmRequest, UnconfirmedEventNotificationRequest
from bacpypes.basetypes import ServicesSupported, EventType, NotifyType, EventState, TimeStamp, DateTime, \
                               NotificationParameters, NotificationParametersChangeOfValue, \
                               NotificationParametersChangeOfValueNewValue, StatusFlags
from bacpypes.errors import DecodingError

from bacpypes.app import BIPSimpleApplication
from bacpypes.service.device import LocalDeviceObject
from bacpypes.primitivedata import ObjectIdentifier, Date, Time

from EventParameters import EventTypes, EventParam, cmdParamGenerator

# some debugging
_debug = 1
_log = ModuleLogger(globals())

# globals
this_device = None
this_application = None


#
#   WhoIsIAmApplication
#

@bacpypes_debugging
class WhoIsIAmApplication(BIPSimpleApplication):

    def __init__(self, *args):
        if _debug: WhoIsIAmApplication._debug("__init__ %r", args)
        BIPSimpleApplication.__init__(self, *args)

        # keep track of requests to line up responses
        self._request = None

    def request(self, apdu):
        if _debug: WhoIsIAmApplication._debug("request %r", apdu)

        # save a copy of the request
        self._request = apdu

        # forward it along
        BIPSimpleApplication.request(self, apdu)

    def confirmation(self, apdu):
        if _debug: WhoIsIAmApplication._debug("confirmation %r", apdu)

        # forward it along
        BIPSimpleApplication.confirmation(self, apdu)

    def indication(self, apdu):
        if _debug: WhoIsIAmApplication._debug("indication %r", apdu)

        if (isinstance(self._request, WhoIsRequest)) and (isinstance(apdu, IAmRequest)):
            device_type, device_instance = apdu.iAmDeviceIdentifier
            if device_type != 'device':
                raise DecodingError("invalid object type")

            if (self._request.deviceInstanceRangeLowLimit is not None) and \
                (device_instance < self._request.deviceInstanceRangeLowLimit):
                pass
            elif (self._request.deviceInstanceRangeHighLimit is not None) and \
                (device_instance > self._request.deviceInstanceRangeHighLimit):
                pass
            else:
                # print out the contents
                sys.stdout.write('pduSource = ' + repr(apdu.pduSource) + '\n')
                sys.stdout.write('iAmDeviceIdentifier = ' + str(apdu.iAmDeviceIdentifier) + '\n')
                sys.stdout.write('maxAPDULengthAccepted = ' + str(apdu.maxAPDULengthAccepted) + '\n')
                sys.stdout.write('segmentationSupported = ' + str(apdu.segmentationSupported) + '\n')
                sys.stdout.write('vendorID = ' + str(apdu.vendorID) + '\n')
                sys.stdout.flush()

        # forward it along
        BIPSimpleApplication.indication(self, apdu)


    def doorEvent(self, deviceID=None, messageText=None):

        request = UnconfirmedEventNotificationRequest()

        # set Event Notification Parameters #
        request.processIdentifier = 0
        if not deviceID: deviceID = 1200
        request.initiatingDeviceIdentifier = ObjectIdentifier('device', deviceID)
        request.eventObjectIdentifier = ObjectIdentifier(297, 1)

        dateTime = DateTime()
        #dateTime.date = Date("2017-03-16")
        #dateTime.time = Time("16:33:25.255")
        currentTime = datetime.datetime.now()
        dateTime.date = Date(currentTime.strftime("%Y-%m-%d"))
        dateTime.time = Time(currentTime.strftime("%H:%M:%S") + ".%s"%(random.randint(0, 255)))
        timeStamp = TimeStamp()
        timeStamp.dateTime = dateTime
        request.timeStamp = timeStamp

        request.notificationClass = 7
        request.priority = 120
        request.eventType = EventType('changeOfValue')
        if not messageText: messageText = 'Valid Access (1): 1200.DC2,CU15,1234567(1),0,Henry_Test_DC02 abcHenry_Test_CU15'
        request.messageText = messageText
        request.notifyType = NotifyType('event')
        request.ackRequired = False
        request.fromState = EventState('normal')
        request.toState = EventState('normal')

        statusFlags = StatusFlags()
        newValue = NotificationParametersChangeOfValueNewValue()
        newValue.changedValue = 969.0
        changeOfValue = NotificationParametersChangeOfValue()
        changeOfValue.newValue = newValue
        changeOfValue.statusFlags = statusFlags
        eventValues = NotificationParameters()
        eventValues.changeOfValue = changeOfValue
        request.eventValues = eventValues

        # set the destination
        address = GlobalBroadcast()
        #address = LocalStation("168.152.32.99/24")   # cannot make it work
        request.pduDestination = address

        self.request(request)


#
#   WhoIsIAmConsoleCmd
#

@bacpypes_debugging
class WhoIsIAmConsoleCmd(ConsoleCmd):

    def do_whois(self, args):
        """whois [ <addr> ] [ <lolimit> <hilimit> ]"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_whois %r", args)

        try:
            # gather the parameters
            request = WhoIsRequest()
            if (len(args) == 1) or (len(args) == 3):
                addr = Address(args[0])
                del args[0]
            else:
                addr = GlobalBroadcast()

            if len(args) == 2:
                lolimit = int(args[0])
                hilimit = int(args[1])
            else:
                lolimit = hilimit = None

            # code lives in the device service
            this_application.who_is(lolimit, hilimit, addr)

        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)

    def do_iam(self, args):
        """iam"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_iam %r", args)

        # code lives in the device service
        this_application.i_am()

    def do_rtn(self, args):
        """rtn <addr> <net> ... """
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_rtn %r", args)

        # safe to assume only one adapter
        adapter = this_application.nsap.adapters[0]
        if _debug: WhoIsIAmConsoleCmd._debug("    - adapter: %r", adapter)

        # provide the address and a list of network numbers
        router_address = Address(args[0])
        network_list = [int(arg) for arg in args[1:]]

        # pass along to the service access point
        this_application.nsap.add_router_references(adapter, router_address, network_list)

    # my added testing command
    def do_hi(self, args):
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_hi %r", args)

        print "hellow world"

    def do_test_whois(self, args=None):

        lolimit = 9830
        hilimit = 9830
        addr    = GlobalBroadcast()
        this_application.who_is(lolimit, hilimit, addr)


    def do_doorEvents(self, args):
        """doorEvents [ <number of hours> H | <number of days> D ] """
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_doorEvents %r", args)

        try:
            timeCount = 1
            timeUnit  = "HOUR"

            if len(args) == 0:      # default 1 Hour
                pass
            elif len(args) >= 2:    # x Hours or x Days
                timeCount = int(args[0])
                if args[1] == "D":
                    timeUnit = "DAY"
            else:                   # x Hours
                timeCount = int(args[0])

            currentTime = datetime.datetime.now()
            finishTime = None
            if timeUnit == "DAY":
                finishTime = currentTime + datetime.timedelta(days=timeCount)
            else:
                finishTime = currentTime + datetime.timedelta(hours=timeCount)

            totalEventsGenerated = 0
            print "... Start doorEvents (%s)"%currentTime
            while currentTime < finishTime:

                interval = random.randint(1, 10)    # random x minutes
                eventCount = random.randint(1, 10)  # random X events

                i = 1
                while i <=eventCount:
                    eventType = EventTypes[random.randint(0, len(EventTypes) - 1)]
                    if eventType == "validAccess":
                        self.do_validAccess(cmdParamGenerator(eventType))
                        totalEventsGenerated = totalEventsGenerated + 1
                    elif eventType == "invalidZone":
                        self.do_invalidZone(cmdParamGenerator(eventType))
                        totalEventsGenerated = totalEventsGenerated + 1
                    elif eventType == "lostCard":
                        self.do_lostCard(cmdParamGenerator(eventType))
                        totalEventsGenerated = totalEventsGenerated + 1
                    elif eventType == "unrecognizedCard":
                        self.do_unrecognizedCard(cmdParamGenerator(eventType))
                        totalEventsGenerated = totalEventsGenerated + 1
                    elif eventType == "invalidPin":
                        self.do_invalidPin(cmdParamGenerator(eventType))
                        totalEventsGenerated = totalEventsGenerated + 1
                    elif eventType == "disabledCard":
                        self.do_disabledCard(cmdParamGenerator(eventType))
                        totalEventsGenerated = totalEventsGenerated + 1
                    elif eventType == "expiredUser":
                        self.do_expiredUser(cmdParamGenerator(eventType))
                        totalEventsGenerated = totalEventsGenerated + 1
                    elif eventType == "inactiveUser":
                        self.do_inactiveUser(cmdParamGenerator(eventType))
                        totalEventsGenerated = totalEventsGenerated + 1
                    elif eventType == "disabledUser":
                        self.do_disabledUser(cmdParamGenerator(eventType))
                        totalEventsGenerated = totalEventsGenerated + 1
                    elif eventType == "timeoutPin":
                        self.do_timeoutPin(cmdParamGenerator(eventType))
                        totalEventsGenerated = totalEventsGenerated + 1
                    elif eventType == "muster":
                        self.do_muster(cmdParamGenerator(eventType))
                        totalEventsGenerated = totalEventsGenerated + 1
                    elif eventType == "traceUser":
                        self.do_traceUser(cmdParamGenerator(eventType))
                        totalEventsGenerated = totalEventsGenerated + 1
                    elif eventType == "antiPassBack":
                        self.do_antiPassBack(cmdParamGenerator(eventType))
                        totalEventsGenerated = totalEventsGenerated + 1
                    i = i + 1
                time.sleep(interval * 60)
                currentTime = datetime.datetime.now()
            print "... Finish doorEvents (%s)"%currentTime
            print "... %s doorEvents generated"%totalEventsGenerated

        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)


    def do_validAccess(self, args):
        """validAccess <Door Object> <Card User Object> <entry | exit>"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_validAccess %r", args)

        try:
            if len(args) < 3:
                raise Exception ("Missing required parameters")
            newArgs = ["validAccess"]
            newArgs.extend(args)
            param = EventParam(*newArgs)
            #print param.getDeviceID(), param.getMessage()    # debugging
            this_application.doorEvent(int(param.getDeviceID()), param.getMessage())
        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)


    def do_invalidZone(self, args):
        """invalidZone <Door Object> <Card User Object>"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_invalidZone %r", args)

        try:
            if len(args) < 2:
                raise Exception ("Missing required parameters")
            newArgs = ["invalidZone"]
            newArgs.extend(args)
            param = EventParam(*newArgs)
            #print param.getDeviceID(), param.getMessage()    # debugging
            this_application.doorEvent(int(param.getDeviceID()), param.getMessage())
        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)


    def do_lostCard(self, args):
        """lostCard <Door Object> <Card User Object>"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_lostCard %r", args)

        try:
            if len(args) < 2:
                raise Exception("Missing required parameters")
            newArgs = ["lostCard"]
            newArgs.extend(args)
            param = EventParam(*newArgs)
            #print param.getDeviceID(), param.getMessage()    # debugging
            this_application.doorEvent(int(param.getDeviceID()), param.getMessage())
        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)


    def do_unrecognizedCard(self, args):
        """unrecognizedCard <Door Object>"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_unrecognizedCard %r", args)

        try:
            if len(args) < 1:
                raise Exception("Missing required parameters")
            newArgs = ["unrecognizedCard"]
            newArgs.extend(args)
            param = EventParam(*newArgs)
            #print param.getDeviceID(), param.getMessage()  # debugging
            this_application.doorEvent(int(param.getDeviceID()), param.getMessage())
        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)


    def do_invalidPin(self, args):
        """invalidPin <Door Object>"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_invalidPin %r", args)

        try:
            if len(args) < 1:
                raise Exception("Missing required parameters")
            newArgs = ["invalidPin"]
            newArgs.extend(args)
            param = EventParam(*newArgs)
            #print param.getDeviceID(), param.getMessage()  # debugging
            this_application.doorEvent(int(param.getDeviceID()), param.getMessage())
        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)


    def do_disabledCard(self, args):
        """disabledCard <Door Object> <Card User Object>"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_disabledCard %r", args)

        try:
            if len(args) < 2:
                raise Exception("Missing required parameters")
            newArgs = ["disabledCard"]
            newArgs.extend(args)
            param = EventParam(*newArgs)
            # print param.getDeviceID(), param.getMessage()    # debugging
            this_application.doorEvent(int(param.getDeviceID()), param.getMessage())
        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)

    def do_expiredUser(self, args):
        """expiredUser <Door Object> <Card User Object>"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_expiredUser %r", args)

        try:
            if len(args) < 2:
                raise Exception("Missing required parameters")
            newArgs = ["expiredUser"]
            newArgs.extend(args)
            param = EventParam(*newArgs)
            # print param.getDeviceID(), param.getMessage()    # debugging
            this_application.doorEvent(int(param.getDeviceID()), param.getMessage())
        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)

    def do_inactiveUser(self, args):
        """inactiveUser <Door Object> <Card User Object>"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_inactiveUser %r", args)

        try:
            if len(args) < 2:
                raise Exception("Missing required parameters")
            newArgs = ["inactiveUser"]
            newArgs.extend(args)
            param = EventParam(*newArgs)
            # print param.getDeviceID(), param.getMessage()    # debugging
            this_application.doorEvent(int(param.getDeviceID()), param.getMessage())
        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)

    def do_disabledUser(self, args):
        """disabledUser <Door Object> <Card User Object>"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_disabledUser %r", args)

        try:
            if len(args) < 2:
                raise Exception("Missing required parameters")
            newArgs = ["disabledUser"]
            newArgs.extend(args)
            param = EventParam(*newArgs)
            # print param.getDeviceID(), param.getMessage()    # debugging
            this_application.doorEvent(int(param.getDeviceID()), param.getMessage())
        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)


    def do_timeoutPin(self, args):
        """timeoutPin <Door Object> <Card User Object>"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_timeoutPin %r", args)

        try:
            if len(args) < 2:
                raise Exception("Missing required parameters")
            newArgs = ["timeoutPin"]
            newArgs.extend(args)
            param = EventParam(*newArgs)
            # print param.getDeviceID(), param.getMessage()    # debugging
            this_application.doorEvent(int(param.getDeviceID()), param.getMessage())
        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)


    def do_muster(self, args):
        """muster <Door Object> <Card User Object>"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_muster %r", args)

        try:
            if len(args) < 2:
                raise Exception("Missing required parameters")
            newArgs = ["muster"]
            newArgs.extend(args)
            param = EventParam(*newArgs)
            # print param.getDeviceID(), param.getMessage()    # debugging
            this_application.doorEvent(int(param.getDeviceID()), param.getMessage())
        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)


    def do_traceUser(self, args):
        """traceUser <Door Object> <Card User Object>"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_traceUser %r", args)

        try:
            if len(args) < 2:
                raise Exception("Missing required parameters")
            newArgs = ["traceUser"]
            newArgs.extend(args)
            param = EventParam(*newArgs)
            # print param.getDeviceID(), param.getMessage()    # debugging
            this_application.doorEvent(int(param.getDeviceID()), param.getMessage())
        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)


    def do_timeZone(self, args):
        """timeZone <Door Object> <Card User Object>"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_timeZone %r", args)

        try:
            if len(args) < 2:
                raise Exception("Missing required parameters")
            newArgs = ["timeZone"]
            newArgs.extend(args)
            param = EventParam(*newArgs)
            # print param.getDeviceID(), param.getMessage()    # debugging
            this_application.doorEvent(int(param.getDeviceID()), param.getMessage())
        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)

    def do_antiPassBack(self, args):
        """antiPassBack <Door Object> <Card User Object>"""
        args = args.split()
        if _debug: WhoIsIAmConsoleCmd._debug("do_antiPassBack %r", args)

        try:
            if len(args) < 2:
                raise Exception("Missing required parameters")
            newArgs = ["antiPassBack"]
            newArgs.extend(args)
            param = EventParam(*newArgs)
            # print param.getDeviceID(), param.getMessage()    # debugging
            this_application.doorEvent(int(param.getDeviceID()), param.getMessage())
        except Exception as error:
            WhoIsIAmConsoleCmd._exception("exception: %r", error)




#
#   __main__
#

def main():
    global this_device
    global this_application

    # parse the command line arguments
    args = ConfigArgumentParser(description=__doc__).parse_args()

    if _debug: _log.debug("initialization")
    if _debug: _log.debug("    - args: %r", args)

    # make a device object
    this_device = LocalDeviceObject(
        objectName=args.ini.objectname,
        objectIdentifier=int(args.ini.objectidentifier),
        maxApduLengthAccepted=int(args.ini.maxapdulengthaccepted),
        segmentationSupported=args.ini.segmentationsupported,
        vendorIdentifier=int(args.ini.vendoridentifier),
        )

    # build a bit string that knows about the bit names
    pss = ServicesSupported()
    pss['whoIs'] = 1
    pss['iAm'] = 1
    pss['readProperty'] = 1
    pss['writeProperty'] = 1

    # set the property value to be just the bits
    this_device.protocolServicesSupported = pss.value

    # make a simple application
    this_application = WhoIsIAmApplication(this_device, args.ini.address)

    # get the services supported
    services_supported = this_application.get_services_supported()
    if _debug: _log.debug("    - services_supported: %r", services_supported)

    # let the device object know
    this_device.protocolServicesSupported = services_supported.value

    # make a console
    this_console = WhoIsIAmConsoleCmd()
    if _debug: _log.debug("    - this_console: %r", this_console)

    # enable sleeping will help with threads
    enable_sleeping()

    _log.debug("running")

    run()

    _log.debug("fini")

if __name__ == "__main__":
    main()
