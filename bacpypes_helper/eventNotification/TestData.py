#!/usr/bin/env python

"""
Collect testing DCs and CUs from Bacnet test network
"""
import os
import requests
import time
import json
from requests.exceptions import ConnectionError
from requests.auth import HTTPBasicAuth
try:
    from lxml import etree
except ImportError:
    raise Exception("this package needs lxml module, please install it first.")

OBJECT_TYPE_MAPPING = {
                        "accumulator"       : "AC",
                        "access-credential" : "ACC",
                        "access-door"       : "ACD",
                        "access-point"      : "ACP",
                        "access-rights"     : "ACR",
                        "access-user"       : "ACU",
                        "access-zone"       : "ACZ",
                        "acs"               : "ACS",
                        "ag"                : "AG",
                        "alert-enrollment"  : "AE",
                        "analog-input"      : "AI",
                        "aic"               : "AIC",
                        "analog-output"     : "AO",
                        "aoc"               : "AOC",
                        "as"                : "AS",
                        "analog-value"      : "AV",
                        "ast"               : "AST",
                        "at"                : "AT",
                        "atz"               : "ATZ",
                        "averaging"         : "AVG",

                        "bdc": "BDC",
                        "bde": "BDE",
                        "bcp": "BCP",
                        "binary-input": "BI",
                        "bmd": "BMD",
                        "binary-output": "BO",
                        "bt": "BT",
                        "binary-value": "BV",
                        "bitstring-value": "BSV",
                        "bst": "BST",
                        "btz": "BTZ",

                        "calendar": "CAL",
                        "cel": "CEL",
                        "com": "COM",
                        "command": "CS",
                        "characterstring-value": "CSV",
                        "cr": "CR",
                        "credential-data-input": "ACI",
                        "cu": "CU",
                        "cms": "CMS",

                        "date-pattern-value": "DPV",
                        "datetime-pattern-value": "DTP",
                        "datetime-value": "DTV",
                        "date-value": "DV",
                        "dbi": "DBI",
                        "dc": "DC",
                        "del": "DEL",
                        "der": "DER",
                        "des": "DES",
                        "device": "DEV",
                        "dg": "DG",
                        "dgl": "DGL",
                        "drt": "DRT",
                        "dws": "DWS",

                        "ec": "EC",
                        "event-enrollment": "EV",
                        "event-log": "EL",
                        "eva": "EVA",
                        "evf": "EVF",
                        "evl": "EVL",
                        "evn": "EVN",
                        "evr": "EVR",
                        "evs": "EVS",
                        "evx": "EVX",
                        "ens": "ENS",

                        "file": "FIL",

                        "group": "GRP",
                        "gcs": "GCS",
                        "gw": "GW",
                        "gwt": "GWT",

                        "hs": "HS",

                        "iom": "IOM",
                        "ins": "INS",
                        "ips": "IPS",
                        "integer-value": "IV",

                        "large-analog-value": "LAV",
                        "lc": "LC",
                        "lcd": "LCD",
                        "lighting-output": "LO",
                        "lg": "LG",
                        "loop": "CO",
                        "load-control": "LS",
                        "life-safety-zone": "ZN",
                        "life-safety-point": "ZP",
                        "lnk": "LNK",
                        "lpt": "LPT",
                        "lsp": "LSP",

                        "multi-state-input": "MI",
                        "mic": "MIC",
                        "moc": "MOC",
                        "mds": "MDS",
                        "mt": "MT",
                        "mn": "MN",
                        "mnp": "MNP",
                        "multi-state-value": "MV",
                        "multi-state-output": "MO",

                        "net": "NET",
                        "notification-class": "EVC",
                        "notification-forwarder": "NF",
                        "np": "NP",
                        "nvs": "NVS",

                        "octetstring-value": "OSV",
                        "ors": "ORS",
                        "os": "OS",

                        "pan": "PAN",
                        "program": "PG",
                        "pi": "PI",
                        "pulse-converter": "PC",
                        "positive-integer-value": "PIV",

                        "rps": "RPS",
                        "rpt": "RPT",

                        "schedule": "SCH",
                        "sd": "SD",
                        "sel": "SEL",
                        "sns": "SNS",
                        "ss": "SS",
                        "sss": "SSS",
                        "sdl": "SDL",
                        "sua": "SUA",
                        "sug": "SUG",
                        "structured-view": "SV",

                        "tns": "TNS",
                        "time-pattern-value": "TPV",
                        "time-value": "TV",
                        "trend-log": "TL",
                        "trend-log-multiple": "TLM",

                        "uns": "UNS",
                        "vgs": "VGS",

                        "zc": "ZC",
                        "zf": "ZF"

}


class GetTestData(object):
    """ collect DCs and CUs from test network """

    def __init__(self, hostName, userName, passWord):
        self.r = None
        self.s = requests.session()
        self.base_url = "http://%s/enteliweb"%hostName
        self.userName = userName
        self.passWord = passWord
        result = self._login()
        if not result:
            raise Exception("Login to enteliWEB '%s' failed"%hostName)


    def _getRequest(self, url, retry=3):
        """ helper to dealing with request return 10054 error """
        try:
            #result = requests.get(url, auth=HTTPBasicAuth(self.userName, self.passWord))
            result = self.s.get(url)
            if result is None:
                if retry >= 1:
                    time.sleep(10)
                    retry = retry - 1
                    self._getRequest(url, retry)
            return result
        except ConnectionError:
            if retry >= 1:
                time.sleep(60)
                retry = retry - 1

                print "debug: retry get request after Connection aborted"

                self._getRequest(url, retry)
            else:
                raise


    def _login(self):
        url = "%s/api/auth/basiclogin?username=%s&password=%s" % (self.base_url, self.userName, self.passWord)
        self.r = self.s.get(url)
        root = etree.fromstring(self.r.content)
        csrfToken = root.get("_csrfToken")
        if csrfToken:
            return True    # login successfully
        else:
            return False


    def _getDevicesList(self, siteName):
        """ get a list of Devices on a site """
        url = "%s/api/.bacnet/%s/" % (self.base_url, siteName)
        self.r = self._getRequest(url)
        root = etree.fromstring(self.r.content)
        elements = root.getchildren()
        result = []
        for elem in elements:
            objDic = {}
            objDic["device number"] = elem.get("name")
            objDic["device name"] = elem.get("displayName")
            result.append(objDic)
        return result


    def _getNumberOfObjects(self, siteName, deviceNumber, reTry=3):
        """ return the total number of objects in a device """
        url = "%s/wsbac/getproperty?ObjRef=//%s/%s.DEV%s.Object_List[0]" % (
        self.base_url, siteName, deviceNumber, deviceNumber)
        self.r = self._getRequest(url)
        if self.r is None:
            reTry = reTry - 1
            if reTry > 0:
                time.sleep(3)
                self._getNumberOfObjects(siteName, deviceNumber, reTry)
            else:
                raise Exception("requests in getNumberOfObjects(%s, %s) returns null." % (siteName, deviceNumber))
        root = etree.fromstring(self.r.content)
        result = root.find("./Object/Property")
        try:
            return str(int((result.get("value")).strip()) + 10)  # try handling inconsistent of total objects in device.
        except ValueError:
            return result.get("value")


    def _getObjectsList(self, siteName, deviceNumber):
        """ return a list of objects in a device """
        numberOfObjects = self._getNumberOfObjects(siteName, deviceNumber)
        url = "%s/api/.bacnet/%s/%s?max-results=%s" % (self.base_url, siteName, deviceNumber, numberOfObjects)
        self.r = self._getRequest(url)
        root = etree.fromstring(self.r.content)
        elements = root.getchildren()
        result = []
        for elem in elements:
            objDic = {}
            objReference = elem.get("name")
            if objReference is not None:
                objReference = objReference.split(",")

                # objReference validation before contineu
                if len(objReference) != 2:
                    continue
                try:
                    int(objReference[1])
                except ValueError:
                    continue

                # print deviceNumber, objReference
                try:
                    objDic["object type"] = OBJECT_TYPE_MAPPING[objReference[0]]
                except KeyError:
                    objDic["object type"] = objReference[0]
                objDic["object number"] = objReference[1]
                objDic["object name"] = elem.get("displayName")
                result.append(objDic)
        return result


    def getDoorObjects(self, siteName):
        """ return all DC objects from given site """
        result = {}
        devices = self._getDevicesList(siteName)
        for device in devices:
            objectList = self._getObjectsList(siteName, device["device number"])
            dcList = []
            for obj in objectList:
                if obj["object type"] == "DC":
                    dcList.append(obj)
            if len(dcList) > 0:
                result[device["device number"]] = dcList
        return result


    def getCardUserObjects(self, siteName, masterPanel=None):
        """ return all CU objects from give site  """
        result = {}
        devices = []
        if masterPanel is not None:
            devices.append(masterPanel)
        else:
            devices = self._getDevicesList(siteName)
        for device in devices:
            objectList = self._getObjectsList(siteName, device["device number"])
            cuList = []
            for obj in objectList:
                if obj["object type"] == "CU":
                    cardList = self.getCardList(siteName, device["device number"], obj["object type"]+obj["object number"])
                    if len(cardList) > 0:
                        obj["cards"] = cardList
                        cuList.append(obj)
            if len(cuList) > 0:
                result[device["device number"]] = cuList
        return result


    def getCardList(self, siteName, deviceNumber, objCU):
        """ return card list of the specified CU """
        result = []
        url = "%s/wsbac/getproperty?ObjRef=//%s/%s.%s.Card_List" % (self.base_url, siteName, deviceNumber, objCU)
        self.r = self._getRequest(url)
        root = etree.fromstring(self.r.content)
        try:
            elemObject = root.find("./Object")
            elemArray = (elemObject.getchildren())[0]         # Array node
            groupElements = elemArray.getchildren()           # Group nodes
            if len(groupElements) > 0:
                for elemGroup in groupElements:
                    propertyElements = elemGroup.getchildren()    # Property nodes
                    dicCard = {}
                    for elemProperty in propertyElements:
                        propertyName = elemProperty.get("name")
                        if propertyName == "siteCode":
                            dicCard["siteCode"] = elemProperty.get("value")
                        elif propertyName == "cardNumber":
                            dicCard["cardNumber"] = elemProperty.get("value")
                        elif propertyName == "cardStatus":
                            dicCard["cardStatus"] = elemProperty.get("value")
                    result.append(dicCard)
        finally:
            return result




if __name__ == "__main__":
    testData = GetTestData("delsry3860.network.com", "Admin", "Password")
    doors = testData.getDoorObjects("$LocalSite")
    JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "Doors.json"))
    with open(JSON_FILE_LOCATION, 'w') as outfile:
        json.dump(doors, outfile, indent=2)
    users = testData.getCardUserObjects("$LocalSite")
    JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "CardUsers.json"))
    with open(JSON_FILE_LOCATION, 'w') as outfile:
        json.dump(users, outfile, indent=2)
