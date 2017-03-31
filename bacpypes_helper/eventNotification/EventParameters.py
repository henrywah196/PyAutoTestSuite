#!/usr/bin/env python

"""
Door Access Event related parameters
"""
import os
import json
import random


class CardUser(object):

    def __init__(self, objRef=None, name=None, cards=None):
        self.objRef = objRef
        self.name = name
        self.cards = cards

    def getName(self):
        return self.name

    def getObjRef(self):
        return self.objRef

    def getCard(self, index=None):
        """ return the specified card number
            if index is None or out of range
            return one randomly
            if no card assigned, raise exception
        """
        totalCards = len(self.cards)
        if totalCards == 0:
            raise Exception("Card User %s(%s) has no card assigned."%(self.name, self.objRef))
        if index is None or index >= totalCards:    # random card
            index = random.randint(0, totalCards - 1)
            return str(self.cards[index])
        else:
            return str(self.cards[index])


class Card(object):

    def __init__(self, siteCode, cardNumber):
        self.siteCode = siteCode
        self.cardNumber = cardNumber

    def __str__(self):
        return "%s(%s)"%(self.cardNumber, self.siteCode)


class Door(object):

    def __init__(self, device=None, objRef=None, name=None):
        self.device = device
        self.objRef = objRef
        self.name = name

    def getObjRef(self, includingDevice=True):
        if includingDevice:
            return "%s.%s"%(self.device, self.objRef)
        else:
            return self.objRef

    def getName(self):
        return self.name


def getCardUsers():
    result = []

    # add unknown users first
    result.append(CardUser("CU4194303", "Unknown Card User", [Card("999", "9999999")]))

    JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "CardUsers.json"))
    json_file = open(JSON_FILE_LOCATION, "r")
    json_data = (json.load(json_file))["1500"]
    for item in json_data:
        cardUser = CardUser()
        cardUser.objRef = item["object type"] + item["object number"]
        cardUser.name = item["object name"]
        cardUser.cards = []
        cardsList = item["cards"]
        for cards in cardsList:
            cardUser.cards.append(Card(cards["siteCode"], cards["cardNumber"]))
        result.append(cardUser)
    return result


def getDoors():
    result = []
    JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "Doors.json"))
    json_file = open(JSON_FILE_LOCATION, "r")
    json_data = json.load(json_file)
    for key, value in json_data.iteritems():
        deviceNumber = key
        for item in value:
            objReference = item["object type"] + item["object number"]
            objName = item["object name"]
            result.append(Door(deviceNumber, objReference, objName))
    return result

'''
CardUsers = []
CardUsers.append(CardUser("CU4194303", "Unknown Card User", [Card("999", "9999999")]))
CardUsers.append(CardUser("CU14", "Henry_Test_CU14", [Card("110", "2345678")]))
CardUsers.append(CardUser("CU15", "Henry_Test_CU15", [Card("110", "1234567")]))
CardUsers.append(CardUser("CU16", "Henry_Test_CU16", [Card("110", "3456789"), Card("110", "4567890")]))
'''
CardUsers = getCardUsers()


'''
Doors = []
Doors.append(Door("1200", "DC2", "Henry_Test_DC02 abc"))
'''
Doors = getDoors()


EventTypes = [
               "validAccess", "unrecognizedCard", "invalidPin", "disabledCard", "expiredUser",
               "inactiveUser", "disabledUser", "antiPassBack", "timeZone", "invalidZone",
               "lostCard", "timeoutPin", "traceUser", "muster"
             ]


class EventParam(object):
    def __init__(self, *args):
        self.eventType = args[0]
        self.deviceID = None
        self.message = None

        if self.eventType == "validAccess":
            self.validAccessMessage(*args)

        elif self.eventType == "unrecognizedCard":
            self.unrecognizedCardMessage(*args)

        elif self.eventType == "invalidPin":
            self.invalidPinMessage(*args)

        elif self.eventType == "disabledCard":
            self.disabledCardMessage(*args)

        elif self.eventType == "expiredUser":
            self.expiredUserMessage(*args)

        elif self.eventType == "inactiveUser":
            self.inactiveUserMessage(*args)

        elif self.eventType == "disabledUser":
            self.disabledUserMessage(*args)

        elif self.eventType == "antiPassBack":
            self.antiPassBackMessage(*args)

        elif self.eventType == "timeZone":
            self.timeZoneMessage(*args)

        elif self.eventType == "invalidZone":
            self.invalidZoneMessage(*args)

        elif self.eventType == "lostCard":
            self.lostCardMessage(*args)

        elif self.eventType == "timeoutPin":
            self.timeoutPinMessage(*args)

        elif self.eventType == "traceUser":
            self.traceUserMessage(*args)

        elif self.eventType == "muster":
            self.musterMessage(*args)

    def getMessage(self):
        return self.message

    def getDeviceID(self):
        return self.deviceID

    def _getDoorObj(self, strDoorObj):
        doorObj = None
        for door in Doors:
            current = door.getObjRef()
            if current == strDoorObj:  # found
                doorObj = door
                break
        if doorObj is None:
            raise Exception("Door '%s' was not found." % strDoorObj)
        return doorObj

    def _getUserObj(self, strUserObj):
        userObj = None
        for cardUser in CardUsers:
            current = cardUser.getObjRef()
            if current == strUserObj:  # found
                userObj = cardUser
                break
        if userObj is None:
            raise Exception("Card User '%s' was not found." % strUserObj)
        return userObj

    def validAccessMessage(self, *args):
        strDoorObj = args[1]
        strUserObj = args[2]
        entryOrExit = args[3]

        doorObj = self._getDoorObj(strDoorObj)
        userObj = self._getUserObj(strUserObj)

        doorName = doorObj.getName()
        userName = userObj.getName()
        cardNumber = userObj.getCard()

        if entryOrExit == "entry":
            entryOrExit = 0
        else:
            entryOrExit = 1

        self.message = "Valid Access (1): %s,%s,%s,%s,\n%s\n%s"%(strDoorObj, strUserObj, cardNumber, entryOrExit, doorName, userName)
        self.deviceID = strDoorObj.split(".")[0]


    def unrecognizedCardMessage(self, *args):
        strDoorObj = args[1]

        doorObj = self._getDoorObj(strDoorObj)
        userObj = CardUsers[0]

        self.deviceID = strDoorObj.split(".")[0]
        strUserObj = "%s.%s"%(self.deviceID, userObj.getObjRef())

        doorName = doorObj.getName()
        userName = userObj.getName()
        cardNumber = userObj.getCard()

        self.message = "Unrecognized Card (2): %s,%s,%s,0,\n%s\n%s" % (
            strDoorObj, strUserObj, cardNumber, doorName, userName)


    def invalidPinMessage(self, *args):
        strDoorObj = args[1]

        doorObj = self._getDoorObj(strDoorObj)
        userObj = CardUsers[0]

        self.deviceID = strDoorObj.split(".")[0]
        strUserObj = "%s.%s"%(self.deviceID, userObj.getObjRef())

        doorName = doorObj.getName()
        userName = userObj.getName()
        cardNumber = "0(0)"

        self.message = "Invalid PIN (3): %s,%s,%s,0,\n%s\n%s" % (
            strDoorObj, strUserObj, cardNumber, doorName, userName)


    def disabledCardMessage(self, *args):
        strDoorObj = args[1]
        strUserObj = args[2]

        doorObj = self._getDoorObj(strDoorObj)
        userObj = self._getUserObj(strUserObj)

        doorName = doorObj.getName()
        userName = userObj.getName()
        cardNumber = userObj.getCard()

        self.message = "Disabled Card (4): %s,%s,%s,0,\n%s\n%s" % (
            strDoorObj, strUserObj, cardNumber, doorName, userName)
        self.deviceID = strDoorObj.split(".")[0]


    def expiredUserMessage(self, *args):
        strDoorObj = args[1]
        strUserObj = args[2]

        doorObj = self._getDoorObj(strDoorObj)
        userObj = self._getUserObj(strUserObj)

        doorName = doorObj.getName()
        userName = userObj.getName()
        cardNumber = userObj.getCard()

        self.message = "Expired User (5): %s,%s,%s,0,\n%s\n%s" % (
            strDoorObj, strUserObj, cardNumber, doorName, userName)
        self.deviceID = strDoorObj.split(".")[0]


    def inactiveUserMessage(self, *args):
        strDoorObj = args[1]
        strUserObj = args[2]

        doorObj = self._getDoorObj(strDoorObj)
        userObj = self._getUserObj(strUserObj)

        doorName = doorObj.getName()
        userName = userObj.getName()
        cardNumber = userObj.getCard()

        self.message = "Inactive User (6): %s,%s,%s,0,\n%s\n%s" % (
            strDoorObj, strUserObj, cardNumber, doorName, userName)
        self.deviceID = strDoorObj.split(".")[0]


    def disabledUserMessage(self, *args):
        strDoorObj = args[1]
        strUserObj = args[2]

        doorObj = self._getDoorObj(strDoorObj)
        userObj = self._getUserObj(strUserObj)

        doorName = doorObj.getName()
        userName = userObj.getName()
        cardNumber = userObj.getCard()

        self.message = "User Disabled (7): %s,%s,%s,0,\n%s\n%s" % (
            strDoorObj, strUserObj, cardNumber, doorName, userName)
        self.deviceID = strDoorObj.split(".")[0]


    def antiPassBackMessage(self, *args):
        strDoorObj = args[1]
        strUserObj = args[2]

        doorObj = self._getDoorObj(strDoorObj)
        userObj = self._getUserObj(strUserObj)

        doorName = doorObj.getName()
        userName = userObj.getName()
        cardNumber = userObj.getCard()

        self.message = "APB Violation (8): %s,%s,%s,0,\n%s\n%s" % (
        strDoorObj, strUserObj, cardNumber, doorName, userName)
        self.deviceID = strDoorObj.split(".")[0]


    def timeZoneMessage(self, *args):
        strDoorObj = args[1]
        strUserObj = args[2]

        doorObj = self._getDoorObj(strDoorObj)
        userObj = self._getUserObj(strUserObj)

        doorName = doorObj.getName()
        userName = userObj.getName()
        cardNumber = userObj.getCard()

        self.message = "Time Zone Violation (9): %s,%s,%s,0,\n%s\n%s" % (
        strDoorObj, strUserObj, cardNumber, doorName, userName)
        self.deviceID = strDoorObj.split(".")[0]


    def invalidZoneMessage(self, *args):
        strDoorObj = args[1]
        strUserObj = args[2]

        doorObj = self._getDoorObj(strDoorObj)
        userObj = self._getUserObj(strUserObj)

        doorName = doorObj.getName()
        userName = userObj.getName()
        cardNumber = userObj.getCard()

        self.message = "Invalid Zone Access (10): %s,%s,%s,0,\n%s\n%s" % (
        strDoorObj, strUserObj, cardNumber, doorName, userName)
        self.deviceID = strDoorObj.split(".")[0]


    def lostCardMessage(self, *args):
        strDoorObj = args[1]
        strUserObj = args[2]

        doorObj = self._getDoorObj(strDoorObj)
        userObj = self._getUserObj(strUserObj)

        doorName = doorObj.getName()
        userName = userObj.getName()
        cardNumber = userObj.getCard()

        self.message = "Lost Card (11): %s,%s,%s,0,\n%s\n%s" % (
            strDoorObj, strUserObj, cardNumber, doorName, userName)
        self.deviceID = strDoorObj.split(".")[0]


    def timeoutPinMessage(self, *args):
        strDoorObj = args[1]
        strUserObj = args[2]

        doorObj = self._getDoorObj(strDoorObj)
        userObj = self._getUserObj(strUserObj)

        doorName = doorObj.getName()
        userName = userObj.getName()
        cardNumber = "0(0)"

        self.message = "PIN Timeout (12): %s,%s,%s,0,\n%s\n%s" % (
            strDoorObj, strUserObj, cardNumber, doorName, userName)
        self.deviceID = strDoorObj.split(".")[0]


    def traceUserMessage(self, *args):
        strDoorObj = args[1]
        strUserObj = args[2]

        doorObj = self._getDoorObj(strDoorObj)
        userObj = self._getUserObj(strUserObj)

        doorName = doorObj.getName()
        userName = userObj.getName()
        cardNumber = "0(0)"
        argu = random.randint(0,1)

        self.message = "Trace User (48): %s,%s,%s,%s,\n%s\n%s" % (
            strDoorObj, strUserObj, cardNumber, argu, doorName, userName)
        self.deviceID = strDoorObj.split(".")[0]


    def musterMessage(self, *args):
        strDoorObj = args[1]
        strUserObj = args[2]

        doorObj = self._getDoorObj(strDoorObj)
        userObj = self._getUserObj(strUserObj)

        doorName = doorObj.getName()
        userName = userObj.getName()
        cardNumber = "0(0)"
        argu = random.randint(0,2)

        self.message = "Muster (65): %s,%s,%s,%s,\n%s\n%s" % (
            strDoorObj, strUserObj, cardNumber, argu, doorName, userName)
        self.deviceID = strDoorObj.split(".")[0]


def cmdParamGenerator(eventType):
    """ randomly generate console cmd params for  access event """
    if eventType == "validAccess":
        objDoor = Doors[random.randint(0, len(Doors) - 1)]
        strDoor = objDoor.getObjRef()
        objUser = CardUsers[random.randint(1, len(CardUsers) - 1)]
        strUser = objUser.getObjRef()
        strType = random.choice(["entry", "exit"])
        return "%s %s %s"%(strDoor, strUser, strType)

    elif eventType == "unrecognizedCard":
        objDoor = Doors[random.randint(0, len(Doors) - 1)]
        strDoor = objDoor.getObjRef()
        return "%s"%strDoor

    elif eventType == "invalidPin":
        objDoor = Doors[random.randint(0, len(Doors) - 1)]
        strDoor = objDoor.getObjRef()
        return "%s" % strDoor

    elif eventType == "disabledCard":
        objDoor = Doors[random.randint(0, len(Doors) - 1)]
        strDoor = objDoor.getObjRef()
        objUser = CardUsers[random.randint(1, len(CardUsers) - 1)]
        strUser = objUser.getObjRef()
        return "%s %s" % (strDoor, strUser)

    elif eventType == "expiredUser":
        objDoor = Doors[random.randint(0, len(Doors) - 1)]
        strDoor = objDoor.getObjRef()
        objUser = CardUsers[random.randint(1, len(CardUsers) - 1)]
        strUser = objUser.getObjRef()
        return "%s %s"%(strDoor, strUser)

    elif eventType == "inactiveUser":
        objDoor = Doors[random.randint(0, len(Doors) - 1)]
        strDoor = objDoor.getObjRef()
        objUser = CardUsers[random.randint(1, len(CardUsers) - 1)]
        strUser = objUser.getObjRef()
        return "%s %s" % (strDoor, strUser)

    elif eventType == "disabledUser":
        objDoor = Doors[random.randint(0, len(Doors) - 1)]
        strDoor = objDoor.getObjRef()
        objUser = CardUsers[random.randint(1, len(CardUsers) - 1)]
        strUser = objUser.getObjRef()
        return "%s %s" % (strDoor, strUser)

    elif eventType == "antiPassBack":
        objDoor = Doors[random.randint(0, len(Doors) - 1)]
        strDoor = objDoor.getObjRef()
        objUser = CardUsers[random.randint(1, len(CardUsers) - 1)]
        strUser = objUser.getObjRef()
        return "%s %s"%(strDoor, strUser)

    elif eventType == "timeZone":
        objDoor = Doors[random.randint(0, len(Doors) - 1)]
        strDoor = objDoor.getObjRef()
        objUser = CardUsers[random.randint(1, len(CardUsers) - 1)]
        strUser = objUser.getObjRef()
        return "%s %s"%(strDoor, strUser)

    elif eventType == "invalidZone":
        objDoor = Doors[random.randint(0, len(Doors) - 1)]
        strDoor = objDoor.getObjRef()
        objUser = CardUsers[random.randint(1, len(CardUsers) - 1)]
        strUser = objUser.getObjRef()
        return "%s %s"%(strDoor, strUser)

    elif eventType == "lostCard":
        objDoor = Doors[random.randint(0, len(Doors) - 1)]
        strDoor = objDoor.getObjRef()
        objUser = CardUsers[random.randint(1, len(CardUsers) - 1)]
        strUser = objUser.getObjRef()
        return "%s %s"%(strDoor, strUser)

    elif eventType == "timeoutPin":
        objDoor = Doors[random.randint(0, len(Doors) - 1)]
        strDoor = objDoor.getObjRef()
        objUser = CardUsers[random.randint(1, len(CardUsers) - 1)]
        strUser = objUser.getObjRef()
        return "%s %s" % (strDoor, strUser)

    elif eventType == "traceUser":
        objDoor = Doors[random.randint(0, len(Doors) - 1)]
        strDoor = objDoor.getObjRef()
        objUser = CardUsers[random.randint(1, len(CardUsers) - 1)]
        strUser = objUser.getObjRef()
        return "%s %s" % (strDoor, strUser)

    elif eventType == "muster":
        objDoor = Doors[random.randint(0, len(Doors) - 1)]
        strDoor = objDoor.getObjRef()
        objUser = CardUsers[random.randint(1, len(CardUsers) - 1)]
        strUser = objUser.getObjRef()
        return "%s %s" % (strDoor, strUser)



