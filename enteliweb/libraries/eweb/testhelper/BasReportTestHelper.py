'''
Created on Dec 7, 2016

@author: hwang
'''
import settings
import requests
from requests.exceptions import ConnectionError
import socket
import errno
import re
import datetime
import time
#from test.badsyntax_future3 import result
#from unittest.test.test_program import RESULT
try:
    from lxml import etree
except ImportError:
    raise Exception("this package needs lxml module, please install it first.")
try:
    from dateutil.parser import parse
except ImportError:
    raise Exception("this package needs dateutil module, please install it first.")

PROPERTY_TYPE_OPERATOR_MAPPING = {
                                   "Signed"      : [">", ">=", "=", "<", "<=", "<>"],
                                   "Unsigned"    : [">", ">=", "=", "<", "<=", "<>"],
                                   "Text"        : ["=", "<>"],
                                   "Object Id"   : ["=", "<>"],
                                   "Time Date"   : [">", ">=", "=", "<", "<=", "<>"],
                                   "Boolean"     : ["=", "<>"],
                                   "Enumeration" : ["=", "<>"],
                                   "Bitlist"     : ["=", "<>"],
                                   "Time"        : [">", ">=", "=", "<", "<=", "<>"],
                                   "Date"        : [">", ">=", "=", "<", "<=", "<>"],
                                   "Real"        : [">", ">=", "=", "<", "<=", "<>"],
                                   "Octet"       : ["=", "<>"],
                                   
                                 }

IP_OP_TYPE_MAPPING = {
                       "IP": ["AI", "BI", "MI", "PI", "PC"],
                       "OP": ["AO", "BO", "MO", "LO"],
                       "*" : [
                                "AC", "ACC", "ACD", "ACI", "ACP", "ACR", "ACS", "ACU", "ACZ",
                                "ADT", "AE", "AG", "AI", "AIC", "AK", "AO", "AOC", "AS", "ASO",
                                "AST", "AT", "ATZ", "AV", "AVG", 
                                "BCP", "BDC", "BDE", "BI", "BMD", "BO", "BST", "BSV", "BT", 
                                "BTZ", "BV", 
                                "CAL", "CCFG", "CEL", "CMS", "CNC", "CNL", "CNS", "CO", "COM",
                                "CR", "CSV", "CU",
                                "DBI", "DC", "DEL", "DER", "DES", "DEV", "DEW", "DG", "DGL",
                                "DIA", "DPV", "DRT", "DTP", "DTV", "DV", "DWS",
                                "EC", "EL", "EMN", "ENS", "EV", "EVA", "EVC", "EVF", "EVL",
                                "EVN", "EVR", "EVS", "EVX",
                                "FIL",
                                "GCS", "GGP", "GRP", "GW", "GWD", "GWF", "GWS", "GWT",
                                "HID", "HS",
                                "INS", "IOM", "IP", "IPS", "IV", 
                                "LAV", "LC", "LCD", "LG", "LIC", "LNK", "LO", "LPT", "LS", "LSP",
                                "MDS", "MI", "MIC", "MN", "MNP", "MO", "MOC", "MT", "MV",
                                "NET", "NF", "NP", "NS", "NVS", 
                                "ODI", "OP", "ORS", "OS", "OSV",
                                "PAN", "PC", "PG", "PI", "PIV", "PRN", "PRS",
                                "RPL", "RPS", "RPT", "RS",
                                "SAT", "SCH", "SD", "SDL", "SEL", "SEM", "SNC", "SNS", "SPI",
                                "SS", "SSC", "SSS", "STA", "SUA", "SUG", "SV",
                                "TL", "TLM", "TNS", "TPV", "TRM", "TV",
                                "UNS", 
                                "V2P", "VGS",
                                "WDL", "WFS", "WSD",
                                "ZBS", "ZC", "ZF", "ZN", "ZP"
                             ]
                     }

OBJECT_TYPE_MAPPING = { 
                        "accumulator"           : "AC",
                        "access-credential"     : "ACC",
                        "access-door"           : "ACD",
                        "access-point"          : "ACP",
                        "access-rights"         : "ACR",
                        "access-user"           : "ACU",
                        "access-zone"           : "ACZ",
                        "acs"                   : "ACS",
                        "ag"                    : "AG",
                        "alert-enrollment"      : "AE",
                        "analog-input"          : "AI",
                        "aic"                   : "AIC",
                        "analog-output"         : "AO",
                        "aoc"                   : "AOC",
                        "as"                    : "AS",
                        "analog-value"          : "AV",
                        "ast"                   : "AST",
                        "at"                    : "AT", 
                        "atz"                   : "ATZ",
                        "averaging"             : "AVG",
                        
                        "bdc"                   : "BDC",
                        "bde"                   : "BDE", 
                        "bcp"                   : "BCP",
                        "binary-input"          : "BI",
                        "bmd"                   : "BMD",
                        "binary-output"         : "BO",
                        "bt"                    : "BT",
                        "binary-value"          : "BV",
                        "bitstring-value"       : "BSV",
                        "bst"                   : "BST",
                        "btz"                   : "BTZ",
                        
                        "calendar"              : "CAL",
                        "cel"                   : "CEL",
                        "com"                   : "COM",
                        "command"               : "CS",
                        "characterstring-value" : "CSV",
                        "cr"                    : "CR",
                        "credential-data-input" : "ACI",
                        "cu"                    : "CU",
                        "cms"                   : "CMS",
                        
                        "date-pattern-value"     : "DPV",
                        "datetime-pattern-value" : "DTP",
                        "datetime-value"         : "DTV",
                        "date-value"             : "DV",
                        "dbi"                    : "DBI",
                        "dc"                     : "DC",
                        "del"                    : "DEL", 
                        "der"                    : "DER",
                        "des"                    : "DES",
                        "device"                 : "DEV",
                        "dg"                     : "DG",
                        "dgl"                    : "DGL",
                        "drt"                    : "DRT",
                        "dws"                    : "DWS",
                        
                        
                        "ec"                    : "EC",
                        "event-enrollment"      : "EV",
                        "event-log"             : "EL",
                        "eva"                   : "EVA",
                        "evf"                   : "EVF",
                        "evl"                   : "EVL",
                        "evn"                   : "EVN",
                        "evr"                   : "EVR",
                        "evs"                   : "EVS",
                        "evx"                   : "EVX",
                        "ens"                   : "ENS",
                        
                        "file"                  : "FIL",
                        
                        "group"                 : "GRP",
                        "gcs"                   : "GCS",
                        "gw"                    : "GW",
                        "gwt"                   : "GWT",
                        
                        "hs"                    : "HS", 
                        
                        "iom"                   : "IOM",
                        "ins"                   : "INS",
                        "ips"                   : "IPS",
                        "integer-value"         : "IV",
                        
                        "large-analog-value"    : "LAV",
                        "lc"                    : "LC",
                        "lcd"                   : "LCD",
                        "lighting-output"       : "LO",
                        "lg"                    : "LG", 
                        "loop"                  : "CO",
                        "load-control"          : "LS",
                        "life-safety-zone"      : "ZN",
                        "life-safety-point"     : "ZP",
                        "lnk"                   : "LNK",
                        "lpt"                   : "LPT",
                        "lsp"                   : "LSP",
                        
                        "multi-state-input"     : "MI",
                        "mic"                   : "MIC",
                        "moc"                   : "MOC",
                        "mds"                   : "MDS",
                        "mt"                    : "MT",
                        "mn"                    : "MN",
                        "mnp"                   : "MNP",
                        "multi-state-value"     : "MV",
                        "multi-state-output"    : "MO",
                        
                        "net"                    : "NET",
                        "notification-class"     : "EVC",
                        "notification-forwarder" : "NF",
                        "np"                     : "NP",
                        "nvs"                    : "NVS",
                        
                        "octetstring-value"     : "OSV",
                        "ors"                   : "ORS",
                        "os"                    : "OS",
                        
                        "pan"                    : "PAN",
                        "program"                : "PG",
                        "pi"                     : "PI",
                        "pulse-converter"        : "PC",
                        "positive-integer-value" : "PIV",
                        
                        "rps"                   : "RPS",
                        "rpt"                   : "RPT",
                        
                        "schedule"              : "SCH",
                        "sd"                    : "SD",
                        "sel"                   : "SEL",
                        "sns"                   : "SNS",
                        "ss"                    : "SS",
                        "sss"                   : "SSS",
                        "sdl"                   : "SDL",
                        "sua"                   : "SUA",
                        "sug"                   : "SUG",
                        "structured-view"       : "SV",
                        
                        "tns"                   : "TNS",
                        "time-pattern-value"    : "TPV",
                        "time-value"            : "TV",
                        "trend-log"             : "TL",
                        "trend-log-multiple"    : "TLM",
                        
                        "uns"                   : "UNS",
                        "vgs"                   : "VGS",
                        
                        "zc"                    : "ZC",
                        "zf"                    : "ZF"
                        
                      }


class BasReportTestHelper(object):
    """ Model a base web page"""
    
    def __init__(self, webDriver):
        self.cookie_name = "enteliWebID"
        self.cookie_value = None
        self.cookie_info = webDriver.get_cookie(self.cookie_name)
        if self.cookie_info is not None:
            self.cookie_value = self.cookie_info["value"]
        self.cookie = {self.cookie_name : self.cookie_value}
        self.r = None
        self.base_url = "http://%s/enteliweb" %settings.HOST
    
    def __repr__(self):
        super(BasReportTestHelper, self).__repr__()
        
    def _getRequest(self, url, retry=3):
        """ helper to dealing with request return 10054 error """
        try:
            result =  requests.get(url, cookies=self.cookie)
            if result is None:
                if retry >=1:
                    time.sleep(10)
                    retry = retry - 1
                    self._getRequest(url, retry)
            return result
        except ConnectionError:
            if retry >=1:
                time.sleep(60)
                retry = retry - 1
                
                print "debug: retry get request after Connection aborted"
                
                self._getRequest(url, retry)
            else:
                raise
        
    def getDevicesList(self, siteName, reTry=3):
        """ get a list of Devices on a site """
        url = "%s/api/.bacnet/%s/"%(self.base_url, siteName)
        self.r = self._getRequest(url)
        if self.r is None:
            if reTry >= 1:
                reTry = reTry - 1
                time.sleep(60)
                self.getDevicesList(siteName, reTry)
            else:
                raise Exception("No responding from request '%s'"%url)
        else:
            root = etree.fromstring(self.r.content)
            elements = root.getchildren()
            result = []
            for elem in elements:
                objDic = {}
                objDic["device number"] = elem.get("name")
                objDic["device name"] = elem.get("displayName")
                result.append(objDic)
            return result
        
    def getNumberOfObjects(self, siteName, deviceNumber, reTry=3):
        """ return the total number of objects in a device """
        url = "%s/wsbac/getproperty?ObjRef=//%s/%s.DEV%s.Object_List[0]"%(self.base_url, siteName, deviceNumber, deviceNumber)
        self.r = self._getRequest(url)
        if self.r is None:
            reTry = reTry -1
            if reTry > 0:
                time.sleep(60)
                self.getNumberOfObjects(siteName, deviceNumber, reTry)
            else:
                raise Exception("requests in getNumberOfObjects(%s, %s) returns null."%(siteName, deviceNumber))
        root = etree.fromstring(self.r.content)
        result = root.find("./Object/Property")
        try: return str(int((result.get("value")).strip()) + 10)   # try handling inconsistent of total objects in device.
        except ValueError: return result.get("value")
        
        
    def getObjectsList(self, siteName, deviceNumber, reTry=3):
        """ return a list of objects in a device """
        numberOfObjects = self.getNumberOfObjects(siteName, deviceNumber)
        url = "%s/api/.bacnet/%s/%s?max-results=%s"%(self.base_url, siteName, deviceNumber, numberOfObjects)
        self.r = self._getRequest(url)
        if self.r is None:
            if reTry >= 1:
                reTry = reTry - 1
                time.sleep(60)
                self.getObjectsList(siteName, deviceNumber, reTry=3)
            else:
                raise Exception("No responding from request '%s'"%url)
        else:
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
                    try: int(objReference[1])
                    except ValueError: continue 
            
                    #print deviceNumber, objReference
                    try: objDic["object type"] = OBJECT_TYPE_MAPPING[objReference[0]]
                    except KeyError: objDic["object type"] = objReference[0]
                    objDic["object number"] = objReference[1]
                    objDic["object name"] = elem.get("displayName")
                    result.append(objDic)
            return result
    
    def getPropertyList(self, siteName, deviceNumber, objectReference, reTry=3):
        """ return a list of property which the objectReference is supported """
        url = "%s/wsbac/getpropertyall?ObjRef=//%s/%s.%s"%(self.base_url, siteName, deviceNumber, objectReference)
        self.r = self._getRequest(url)
        if self.r is None:
            if reTry >= 1:
                reTry = reTry - 1
                time.sleep(60)
                self.getPropertyList(siteName, deviceNumber, objectReference, reTry)
        else:
            root = etree.fromstring(self.r.content)
            elemObject = root.find("./Object")
            elements = elemObject.getchildren()
            result = []
            for elem in elements:
                objDic = {}
                tagName = elem.tag
                status = elem.get("status")
                if tagName == "Property" and status == "OK":
                    objDic["name"] = elem.get("name")
                    objDic["data type"] = elem.get("dataType")
                elif tagName in ("Array", "List", "Union") and (status == "OK" or status == None):
                    objDic["name"] = elem.get("name")
                    objDic["data type"] = tagName
                else:
                    continue
                result.append(objDic)
            return result
    
    def _propertyValueObjComposer(self, element):
        """ helper used by getPropertyValue() to compose and return property as an object """ 
        
        class Property():
            def __init__(self):
                self.name     = None
                self.status   = None
                self.dataType = None
                self.isNull   = None
                self.value    = None
                
            def __str__(self):
                return "Property(name: %s, status: %s, dataType: %s, isNull: %s, value: %s)"%(self.name, self.status, self.dataType, self.isNull, self.value)
                
        class Union():
            def __init__(self):
                self.name   = None
                self.status = None
                
            def __str__(self):
                return "Union(name: %s, status: %s)"%(self.name, self.status)
                
        class Group():
            def __init__(self):
                self.name = None
                self.status = None
                
            def __str__(self):
                return "Group(name: %s)"%self.name
            
        class ArrayList(list):
            def __init__(self):
                super(ArrayList, self).__init__()
                self.name = None
                
        tagName = element.tag
        
        if tagName == "Property":
            propertyObj = Property()
            propertyObj.name = element.get("name")
            propertyObj.status = element.get("status")
            propertyObj.dataType = element.get("dataType")
            propertyObj.value = element.get("value")
            return propertyObj
        
        elif tagName in ("Array", "List"):
            result = ArrayList()
            result.name = element.get("name")
            elements = element.getchildren()
            if len(elements) > 0:
                #result.append(len(elements))
                for elem in elements:
                    result.append(self._propertyValueObjComposer(elem))
            return result
        
        elif tagName == "Union":
            unionObj = Union()
            unionObj.name = element.get("name")
            unionObj.status = element.get("status")
            elements = element.getchildren()
            if len(elements) > 0:
                for elem in elements:
                    elemObj = self._propertyValueObjComposer(elem)
                    setattr(unionObj, elemObj.name, elemObj)
            return unionObj
                    
        elif tagName == "Group":
            groupObj = Group()
            groupObj.name = element.get("name")
            groupObj.status = element.get("status")
            elements = element.getchildren()
            if len(elements) > 0:
                for elem in elements:
                    elemObj = self._propertyValueObjComposer(elem)
                    setattr(groupObj, elemObj.name, elemObj)
            return groupObj
    
    def getPropertyValue(self, siteName, deviceNumber, objectReference, propertyName, reTry=3):
        """ return property vlaue in different format based on the data type of the property """
        
        url = "%s/wsbac/getproperty?ObjRef=//%s/%s.%s.%s"%(self.base_url, siteName, deviceNumber, objectReference, propertyName)
        self.r = self._getRequest(url)
        if self.r is None:
            if reTry >=1:
                reTry = reTry - 1
                time.sleep(60)
                self.getPropertyValue(siteName, deviceNumber, objectReference, propertyName, reTry)
            else:
                raise Exception("No responding from request '%s'"%url)
        else:
            root = etree.fromstring(self.r.content)
            elemObject = root.find("./Object")
            element = (elemObject.getchildren())[0]
        
            #print deviceNumber, objectReference    # debug info
            return self._propertyValueObjComposer(element)
    
    def getPresentValueStateText(self, siteName, deviceNumber, objectReference):
        """ return Active / Inactive text for binary object, state_text for multi-state object
            based on its present_value. for 3rd party devices which has no state_text, just return
            the present_value. the function will return a list containing two item, the first item
            is its present_value, the second item is its state_text
        """
        result = []
        objType = self._getObjTypeFromObjRef(objectReference)
        propertyValue = self.getPropertyValue(siteName, deviceNumber, objectReference, "Present_Value")
        propertyValue = propertyValue.value
        
        if objType in ("BI", "BO", "BV"):
            result.append(propertyValue)
            if propertyValue == "active":
                valueInfo = self.getPropertyValue(siteName, deviceNumber, objectReference, "Active_Text")
                valueCurrent = valueInfo.value
                result.append(valueCurrent)
            elif propertyValue == "inactive":
                valueInfo = self.getPropertyValue(siteName, deviceNumber, objectReference, "Inactive_Text")
                valueCurrent = valueInfo.value
                result.append(valueCurrent)
            else:
                result.append(propertyValue)
            return result
            
        elif objType in ("MI", "MO", "MV"): 
            result.append(propertyValue)          
            valueInfo = self.getPropertyValue(siteName, deviceNumber, objectReference, "State_Text")
            if not isinstance(valueInfo, list):    # handling object has no State_Text property
                result.append(propertyValue)
                return result
            else:    # verify state text
                try: 
                    idx = int(propertyValue)
                    valueInfo = valueInfo[idx - 1]
                    valueCurrent = valueInfo.value
                    result.append(valueCurrent)
                    return result
                except ValueError:
                    result.append(propertyValue)
                    return result
        else:
            return [propertyValue, propertyValue]
    
    
    def getPropertyValue_old(self, siteName, deviceNumber, objectReference, propertyName):
        """ return property value in differetn format based on the data type of the property """
        url = "%s/wsbac/getproperty?ObjRef=//%s/%s.%s.%s"%(self.base_url, siteName, deviceNumber, objectReference, propertyName)
        self.r = self._getRequest(url)
        root = etree.fromstring(self.r.content)
        elemObject = root.find("./Object")
        element = (elemObject.getchildren())[0]
        tagName = element.tag
        if tagName == "Property":
            objDic = {}
            objDic["property type"] = "Property"
            objDic["name"] = element.get("name")
            objDic["status"] = element.get("status")
            objDic["data type"] = element.get("dataType")
            objDic["value"] = element.get("value")
            return objDic
        elif tagName == "Array":
            result = []
            status = element.get("status")
            elements = element.getchildren()
            if len(elements) > 0:
                for elem in elements:
                    objDic = {}
                    objDic["property type"] = "Array"
                    objDic["name"] = elem.get("name")
                    objDic["status"] = elem.get("status")
                    objDic["data type"] = elem.get("dataType")
                    objDic["value"] = elem.get("value")
                    result.append(objDic)
            elif status is not None:
                objDic = {}
                objDic["property type"] = "Array"
                objDic["name"] = element.get("name")
                objDic["status"] = element.get("status")
                result = objDic
            return result
        elif tagName == "List":
            result = []
            status = element.get("status")
            elements = element.getchildren()
            if len(elements) > 0:
                for elem in elements:
                    localTag = tagName + "." + elem.tag
                    if localTag == "List.Union":
                        subElem = (elem.getchildren())[0]
                        if subElem.tag == "Property":
                            objDic = {}
                            objDic["property type"] = localTag
                            objDic["name"] = subElem.get("name")
                            objDic["status"] = elem.get("status")
                            objDic["data type"] = subElem.get("dataType")
                            objDic["value"] = subElem.get("value")
                            result.append(objDic)
                        elif subElem.tag == "Group":
                            groupSubElements = subElem.getchildren()
                            groupList = []
                            for item in groupSubElements:
                                objDic = {}
                                objDic["property type"] = localTag + ".Group"
                                objDic["name"] = subElem.get("name") + "." + item.get("name")
                                objDic["status"] = elem.get("status")
                                objDic["data type"] = item.get("dataType")
                                objDic["value"] = item.get("value")
                                groupList.append(objDic)
                            result.append(groupList) 
            elif status is not None:
                objDic = {}
                objDic["property type"] = "List"
                objDic["name"] = element.get("name")
                objDic["status"] = element.get("status")
                result = objDic
            return result
        elif tagName == "Union":
            result = []
            status = element.get("status")
            elements = element.getchildren()
            if len(elements) > 0:
                for elem in elements:
                    localTag = tagName + "." + elem.tag
                    if localTag == "Union.Group":
                        groupSubElements = elem.getchildren()
                        groupList = []
                        for item in groupSubElements:
                            objDic = {}
                            objDic["property type"] = "Union.Group"
                            objDic["name"] = elem.get("name") + "." + item.get("name")
                            objDic["status"] = status
                            objDic["data type"] = item.get("dataType")
                            objDic["value"] = item.get("value")
                            groupList.append(objDic)
                        result.append(groupList) 
                    elif localTag == "Union.Property":
                        objDic = {}
                        objDic["property type"] = "Union"
                        objDic["name"] = elem.get("name")
                        objDic["status"] = status
                        objDic["data type"] = elem.get("dataType")
                        objDic["value"] = elem.get("value")
                        result.append(objDic)
            elif status is not None:
                objDic = {}
                objDic["property type"] = "Union"
                objDic["name"] = element.get("name")
                objDic["status"] = element.get("status")
                result = objDic
            return result
    
    def isPropertyExisting(self, siteName, deviceNumber, objectReference, propertyName, reTry=3):
        """ helper to verify if the specified object reference contain the specified property """
        
        # verify if property name containing sub property
        propertyNameList = propertyName.split('.')
        propertyName = propertyNameList[0]
        
        # verify if property name is array list with wild card
        array_list_with_wildcard = False
        if "[*]" in propertyName:
            array_list_with_wildcard = True
            propertyName = re.sub('\[\*\]$', '', propertyName)
        
        url = "%s/wsbac/getproperty?ObjRef=//%s/%s.%s.%s"%(self.base_url, siteName, deviceNumber, objectReference, propertyName)
        self.r = self._getRequest(url)
        if self.r is None:
            if reTry >= 1:
                reTry = reTry - 1
                time.sleep(60)
                self.isPropertyExisting(siteName, deviceNumber, objectReference, propertyName, reTry)
            else:
                raise Exception("No responding from request '%s'"%url)
        else:
            root = etree.fromstring(self.r.content)
            elemObject = root.find("./Object")
            element = (elemObject.getchildren())[0]
            if array_list_with_wildcard:
                elements = element.getchildren()
                if len(elements) > 0:
                    element = elements[0]
                else:
                    return False
            status = element.get("status")
            if status == "OK":
                return True
            else:
                return False
        
        '''
        propertyValueObj = self._propertyValueObjComposer(element)
        propertyName = propertyName.split('.')    # propertyName is a list now
        if len(propertyName) > 1:
            i = 1
            while i < len(propertyName):
                attrName = propertyName[i]
                if hasattr(propertyValueObj, attrName):
                    propertyValueObj = getattr(propertyValueObj, attrName)
                    i = i + 1
                else:
                    return False
                if propertyValueObj.status == "OK":
                    return True
                else:
                    return False
        else:
            if propertyValueObj.status == "OK":
                return True
            else:
                return False
        '''
        
        
    def propertyValueIsNull(self, siteName, deviceNumber, objectReference, propertyName, reTry=3):
        """ helper to verify and return true if the web service has isNULL="TRUE" returned """
        url = "%s/wsbac/getproperty?ObjRef=//%s/%s.%s.%s"%(self.base_url, siteName, deviceNumber, objectReference, propertyName)
        #self.r = requests.get(url, cookies=self.cookie)
        self.r = self._getRequest(url)
        if self.r is None:
            if reTry >= 1:
                reTry = reTry - 1
                time.sleep(60)
                self.propertyValueIsNull(siteName, deviceNumber, objectReference, propertyName, reTry)
            else:
                raise Exception("No responding from request '%s'"%url)
        else:
            root = etree.fromstring(self.r.content)
            elemObject = root.find("./Object")
            element = (elemObject.getchildren())[0]
            if (objectReference[0:3] == "SCH") and (propertyName in ("Manual_Override", "Present_Value", "Schedule_Default")):   # special handling of SCH, which is Union
                if len(list(element)) > 0:
                    return False
                else:
                    return True
            else:
                result = element.get("isNULL")
                if result == "TRUE":
                    return True
                else:
                    return False
        
    def isObjectExisting(self, siteName, deviceNumber, objectReference):
        """ return true if the specified object reference existing in device
            objectReference could be a type of object, which means any object
            reference of that type.
        """
        objectList = self.getObjectsList(siteName, deviceNumber)
        objectReference = self._splitObjectRef(objectReference)
        if objectReference[1] is None:    # object type
            for item in objectList:
                if item["object type"] == objectReference[0]:
                    return True
        else:                             # object reference
            for item in objectList:
                if item["object type"] == objectReference[0] and item["object number"] == objectReference[1]:
                    return True
        return False
    
    def _getObjTypeFromObjRef(self, objectReference):
        """ helper to return adn object type part string from the object reference string
            for example, return AV from AV100
        """
        return re.sub(r'\d+', '', objectReference)
    
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
    
    def objQueryGetDeviceList(self, siteName, deviceRangeString):
        """ return a list of device based on object query's device range string """
        deviceList = self.getDevicesList(siteName)
        deviceRangeList = None
        if deviceRangeString.strip() == "*":
            return deviceList
        elif "," in deviceRangeString:
            deviceRangeList = [x.strip() for x in deviceRangeString.split(',')]
        else:
            deviceRangeList = deviceRangeString.split()
        if "*" in deviceRangeList:
            return deviceList
        else:
            result = []
            for item in deviceRangeList:
                if "-" in item:
                    item = [x.strip() for x in item.split('-')]
                else:
                    item = int(item)
                for device in deviceList:
                    deviceNumber = int(device["device number"])
                    if isinstance(item, list):
                        if deviceNumber in range(int(item[0]), int(item[1]) + 1):
                            result.append(device)
                    else:
                        if deviceNumber == item:
                            result.append(device)
                            break
            return result
    
    def objQueryGetObjectList(self, siteName, deviceNumber, objectFilters):
        """ if param deviceNumber is string, return a list of object based on object query's object filter
            if param deviceNumber is a list, return a dic of device and associated list of objects.
        """
        if isinstance(deviceNumber, list):    # its a list of device numbers
            result = {}
            for item in deviceNumber:
                objList = self.objQueryGetObjectList(siteName, item["device number"], objectFilters)
                if len(objList) > 0:
                    result[item["device number"]] = objList 
            return result
        else:
            result = []
            for dicObjectFilter in objectFilters:                                 # a string to represent a device number 
                objectType = dicObjectFilter["Type"]
                objectInstance = dicObjectFilter["Instance"]
                dicObjectReference = self._objectReferenceFormatHelper(objectType, objectInstance)
                objectList = self._objQueryGetObjListByObjRef(siteName, deviceNumber, dicObjectReference)
                if not "Properties" in dicObjectFilter:
                    for item in objectList:
                        if item not in result:
                            result.append(item)
                else:
                    dicPropertyValueComparison = {}
                    dicPropertyValueComparison["Property Logic"] = dicObjectFilter["Property Logic"]
                    dicPropertyValueComparison["Properties"] = dicObjectFilter["Properties"]
                    for obj in objectList:
                        strObjRef = obj["object type"] + obj["object number"]
                        if self._meetPropertyCriteria(siteName, deviceNumber, strObjRef, dicPropertyValueComparison):
                            if obj not in result:
                                result.append(obj)
            return result
                
    
    def _objQueryGetObjListByObjRef(self, siteName, deviceNumber, dicObjectReference):
        """ helper to return a list of object which were found on the device based on 
            the given object reference
        """
        result = []
        objectList = self.getObjectsList(siteName, deviceNumber)
        for key, value in dicObjectReference.items():
            for instance in value:
                for object in objectList:
                    objectType = object["object type"]
                    objectNumber = object["object number"]
                    if isinstance(instance, list):
                        if (key == objectType) and (int(objectNumber) in range(int(instance[0]), int(instance[1]) + 1)):
                            result.append(object)
                    elif instance == "*":
                        if key == objectType:
                            result.append(object)
                    else:
                        if (key == objectType) and (int(instance) == int(objectNumber)):
                            result.append(object)
                            break
        return result    
    
    def _objectReferenceFormatHelper(self, objectType, objectInstance):
        """ helper method used by objQueryGetObjectList.
            the helper will composite the paramters and return a dict of object reference.
            with object type as key and list of instance as value.
        """
        result = {}
        typeList = []
        for item in objectType:
            if item in ("IP", "OP", "*"):
                item = IP_OP_TYPE_MAPPING[item]
            if isinstance(item, list):
                for subItem in item:
                    if subItem not in typeList:
                        typeList.append(subItem)
            else:
                if item not in typeList:
                    typeList.append(item)
        for item in typeList:
            result[item] = None
            
        instanceList = []
        instanceRangeList = None
        if objectInstance.strip() == "*":
            instanceRangeList = ["*"]
        elif "," in objectInstance:
            instanceRangeList = [x.strip() for x in objectInstance.split(',')]
        else:
            instanceRangeList = objectInstance.split()
        if "*" in instanceRangeList:
            instanceList = instanceRangeList
        else:
            for item in instanceRangeList:
                if "-" in item:
                    item = [x.strip() for x in item.split('-')]
                instanceList.append(item)
        for key in result:
            result[key] = instanceList
            
        return result
    
    def _meetPropertyCriteria(self, siteName, deviceNumber, objectReference, dicPropertyValueComparison):
        """ helper to verify if the give object reference meet the property value comparison criteria """
        
        if not self.isObjectExisting(siteName, deviceNumber, objectReference):
            return False
        else:
            propertyLogic = dicPropertyValueComparison["Property Logic"]
            propertyComparisonList = dicPropertyValueComparison["Properties"]
            propertyCompResultList = []
            for propertyValueComparison in propertyComparisonList:
                if isinstance(propertyValueComparison, dict):    # property rule entry
                    dicPropertyRuleComparison = {}
                    dicPropertyRuleComparison["Property Logic"] = propertyValueComparison["Rule Logic"]
                    dicPropertyRuleComparison["Properties"] = propertyValueComparison["Properties"]
                    if self._meetPropertyCriteria(siteName, deviceNumber, objectReference, dicPropertyRuleComparison):
                        propertyCompResultList.append(True)
                    else:
                        propertyCompResultList.append(False)
                else:
                    propertyName = propertyValueComparison[0]
                    logicOperator = propertyValueComparison[1]
                    propertyValue = propertyValueComparison[2]
                    if self.isPropertyExisting(siteName, deviceNumber, objectReference, propertyName):
                        if self. _propertyValueCompareHelper(siteName, deviceNumber, objectReference, propertyValueComparison):
                            propertyCompResultList.append(True)
                        else:
                            propertyCompResultList.append(False)
                    else:
                        if logicOperator == "=" and propertyValue.lower() == "null":    # case: Unknonw_Property = NULL
                            propertyCompResultList.append(True)
                        else:
                            propertyCompResultList.append(False)
            if propertyLogic == "OR":
                if True in propertyCompResultList:
                    return True
                else:
                    return False
            else:    # AND
                if False in propertyCompResultList:
                    return False
                else:
                    return True
                
                        
    def _propertyValueCompareHelper(self, siteName, deviceNumber, objectReference, propertyValueCompare):
        """ helper method used by _meetPropertyCriteria method. return true if 
            the object reference meet the specific property value comparison
        """
        
        propertyName = propertyValueCompare[0]
        
        # dealing with sub properties
        propertyName = propertyName.split('.')    # propertyName is a list now
        
        operator = propertyValueCompare[1]
        propertyValue = propertyValueCompare[2]
        
        propertyValueInfo = self.getPropertyValue(siteName, deviceNumber, objectReference, propertyName[0])
        
        propertyValueInfoList = []
        if isinstance(propertyValueInfo, list):      # list or array
            propertyValueInfoList = propertyValueInfo
        else:
            propertyValueInfoList.append(propertyValueInfo)
            
        result = []
        for propertyValueInfo in propertyValueInfoList:
            currentPropertyValue = None
            currentPropertyDataType = None
            if len(propertyName) > 1:
                targetObj = propertyValueInfo
                i = 1
                while i < len(propertyName) and targetObj != None:
                    attrName = propertyName[i]
                    if hasattr(targetObj, attrName):
                        targetObj = getattr(targetObj, attrName)
                        i = i + 1
                    else:
                        targetObj = None
                if targetObj is not None:
                    currentPropertyValue = targetObj.value
                    currentPropertyDataType = targetObj.dataType
                    
            else:
                #print "debug: //%s/%s.%s.%s"%(siteName, deviceNumber, objectReference, propertyName[0])
                currentPropertyValue = None
                currentPropertyDataType = None
                if (objectReference[0:3] == "SCH") and (propertyName[0] in ("Manual_Override", "Present_Value", "Schedule_Default")):   # special handling of SCH, which is Union
                    attrList = dir(propertyValueInfo)
                    if "real" in attrList:
                        currentPropertyValue = propertyValueInfo.real.value
                        currentPropertyDataType = propertyValueInfo.real.dataType
                    elif "enumerated" in attrList:
                        currentPropertyValue = propertyValueInfo.enumerated.value
                        currentPropertyDataType = propertyValueInfo.enumerated.dataType
                    elif "unsigned" in attrList:
                        currentPropertyValue = propertyValueInfo.unsigned.value
                        currentPropertyDataType = propertyValueInfo.unsigned.dataType
                    elif "boolean" in attrList:
                        currentPropertyValue = propertyValueInfo.boolean.value
                        currentPropertyDataType = propertyValueInfo.boolean.dataType
                    else:   # is NULL
                        currentPropertyValue = ""
                        currentPropertyDataType = None
                elif (objectReference[0:3] == "ACI") and (propertyName[0] in ("Manual_Override", "Present_Value")):   # special handling of ACI, which is Group
                    currentPropertyValue = propertyValueInfo.value.value
                    currentPropertyDataType = propertyValueInfo.value.dataType
                else:
                    currentPropertyValue = propertyValueInfo.value
                    currentPropertyDataType = propertyValueInfo.dataType
            
            # dealing with special marker 'NULL'
            if propertyValue.lower() == "null":
                isNull = self.propertyValueIsNull(siteName, deviceNumber, objectReference, propertyName[0])
                result.append(self._valueCompareNull(isNull, operator))
            
            # dealing with Priority_Array
            elif "Priority_Array" in propertyName[0]:
                self.siteName        = siteName
                self.deviceNumber    = deviceNumber
                self.objectReference = objectReference
                result.append(self._valueComparePresentValue(currentPropertyValue, propertyValue, operator))
            
            # dealing property with multiple data type, such as Present_Value
            elif propertyName[0] in ("Present_Value", "Manual_Override", "Schedule_Default"):
                self.siteName        = siteName
                self.deviceNumber    = deviceNumber
                self.objectReference = objectReference
                result.append(self._valueComparePresentValue(currentPropertyValue, propertyValue, operator))
            
            # dealing with number value
            elif currentPropertyDataType in ("Signed", "Unsigned", "Real"):
                result.append(self._valueCompareNumber(currentPropertyValue, propertyValue, operator))
            
            # dealing with string value
            elif currentPropertyDataType in ("Text", "Bitlist", "Ref", "Device Object Property Reference"):
                result.append(self._valueCompareString(currentPropertyValue, propertyValue, operator))
            
            # dealing with date time value
            elif currentPropertyDataType in ("Time Date", "Time", "Date"):
                result.append(self._valueCompareDateTime(currentPropertyDataType, currentPropertyValue, propertyValue, operator))
            
            # dealing with other value for exactly match
            elif currentPropertyDataType in ("Object Id", "Boolean", "Enumeration", "Octet"):
                result.append(self._valueCompare(currentPropertyValue, propertyValue, operator))
                
        if True in result:
            return True
        else:
            return False
            
            
    def _valueCompare(self, valueCurrent, valueExpected, operator):
        """ the basic value compare """
        if isinstance(valueCurrent, str) or isinstance(valueCurrent, unicode):
            valueCurrent = valueCurrent.lower()
        if isinstance(valueExpected, str) or isinstance(valueExpected, unicode):
            valueExpected = valueExpected.lower()
        if operator == "=":
            return valueCurrent == valueExpected
        elif operator == "<>":
            return valueCurrent != valueExpected
        else:
            return False
    
    def _valueCompareNull(self, isNull, operator):
        """ helper used by _propertyValueCompareHelper() to dealing with special marker 'NULL' """
        if operator == "=":
            if isNull:
                return True
            else: return False
        elif operator == "<>":
            if isNull:
                return False
            else:
                return True
        else:
            return False
        
    def _valueComparePresentValue(self, valueCurrent, valueExpected, operator):
        """ helper used by _propertyValueCompareHelper()  to compare  value for
            property which multiple data types, such as Present_Value, Manual_Override
        """
        objType = self._getObjTypeFromObjRef(self.objectReference)
        if objType in ("AI", "AO", "AV"):
            return self._valueCompareNumber(valueCurrent, valueExpected, operator)
        
        elif objType in ("BI", "BO", "BV"):
            if valueExpected.lower() in ("active", "inactive"):    # verify native value
                return self._valueCompare(valueCurrent, valueExpected, operator)
            else:                                                  # verify Active/Inactive Text
                if valueCurrent == "active":
                    valueInfo = self.getPropertyValue(self.siteName, self.deviceNumber, self.objectReference, "Active_Text")
                    valueCurrent = valueInfo.value
                elif valueCurrent == "inactive":
                    valueInfo = self.getPropertyValue(self.siteName, self.deviceNumber, self.objectReference, "Inactive_Text")
                    valueCurrent = valueInfo.value
                return self._valueCompare(valueCurrent, valueExpected, operator)
            
        elif objType in ("MI", "MO", "MV"):
            
            #print "debug: %s, %s: %s, %s"%(self.deviceNumber, self.objectReference, valueCurrent, valueExpected)
            
            isNativeValue = True
            try: int(valueExpected)
            except ValueError: isNativeValue = False
            if isNativeValue:    # verify native value
                return self._valueCompareNumber(valueCurrent, valueExpected, operator)
            else:
                valueInfo = self.getPropertyValue(self.siteName, self.deviceNumber, self.objectReference, "State_Text")
                if not isinstance(valueInfo, list):    # handling object has no State_Text property
                    return self._valueCompareNumber(valueCurrent, valueExpected, operator)
                else:    # verify state text
                    try: 
                        idx = int(valueCurrent)
                        valueInfo = valueInfo[idx - 1]
                        valueCurrent = valueInfo.value
                        return self._valueCompare(valueCurrent, valueExpected, operator)
                    except ValueError:
                        return self._valueCompare(valueCurrent, valueExpected, operator)
        elif objType in ("SCH"):
            pass
                
    def _valueCompareNumber(self, valueCurrent, valueExpected, operator):
        """ helper used by _propertyValueCompareHelper()  to compare number value"""
        try:
            valueLeft = float(valueCurrent)
            valueRight = float(valueExpected)
            if operator ==">":
                if valueCurrent == valueExpected:
                    return False
                else:
                    return valueLeft > valueRight
            elif operator == ">=":
                if valueCurrent == valueExpected:
                    return True
                else:
                    return valueLeft >= valueRight
            elif operator == "=":
                return valueCurrent == valueExpected
            elif operator == "<":
                if valueCurrent == valueExpected:
                    return False
                else:
                    return valueLeft < valueRight
            elif operator == "<=":
                if valueCurrent == valueExpected:
                    return True
                else:
                    return valueLeft <= valueRight
            elif operator == "<>":
                return valueCurrent != valueExpected
            else:
                return False
        except ValueError:
            return False
        
    def _valueCompareString(self, valueCurrent, valueExpected, operator):
        """ helper used by _propertyValueCompareHelper(), which support string containing wildcard """
        if len(valueExpected) > 0:
            startChar = valueExpected[0]
            endChar = valueExpected[len(valueExpected) - 1]
            if startChar == "*" and endChar == "*":                                     # containing string
                targetString = valueExpected[1:-1]
                if operator == "=":
                    return targetString.lower() in valueCurrent.lower()
                elif operator == "<>":
                    return targetString.lower() not in valueCurrent.lower()
            elif startChar == "*":                                                      # end with string
                targetString = valueExpected[1:]
                if operator == "=":
                    return (valueCurrent.lower()).endswith(targetString.lower())
                elif operator == "<>":
                    return not (valueCurrent.lower()).endswith(targetString.lower())
            elif endChar == "*":                                                        # start with string
                targetString = valueExpected[:-1]
                if operator == "=":
                    return (valueCurrent.lower()).startswith(targetString.lower())
                elif operator == "<>":
                    return not (valueCurrent.lower()).startswith(targetString.lower())
            else:                                                                       # exactly matching
                if operator == "=":
                    return valueCurrent.lower() == valueExpected.lower()
                elif operator == "<>":
                    return valueCurrent.lower() != valueExpected.lower()
        else:
            if operator == "=":
                return valueCurrent.lower() == valueExpected.lower()
            elif operator == "<>":
                return valueCurrent.lower() != valueExpected.lower()
            
    def _valueCompareDateTime(self, dataType, valueCurrent, valueExpected, operator):
        """ helper used by _propertyValueCompareHelper(), to compare date time value """
        try:
            valueLeft = None
            valueRight = None
            if dataType == "Time Date":
                valueLeft = parse(valueCurrent)
                valueRight = parse(valueExpected)
            elif dataType == "Time":
                valueLeft = parse(valueCurrent).time()
                valueRight = parse(valueExpected).time()
            elif dataType == "Date":
                valueLeft = parse(valueCurrent).date()
                valueRight = parse(valueExpected).date()
        
            if operator == ">":
                if valueCurrent == valueExpected:
                    return False
                else:
                    return valueLeft > valueRight
            elif operator == ">=":
                if valueCurrent == valueExpected:
                    return True
                else:
                    return valueLeft >= valueRight
            elif operator == "=":
                return valueCurrent == valueExpected
            elif operator == "<":
                if valueCurrent == valueExpected:
                    return False
                else:
                    return valueLeft < valueRight
            elif operator == "<=":
                if valueCurrent == valueExpected:
                    return True
                else:
                    return valueLeft <= valueRight
            elif operator == "<>":
                return valueCurrent != valueExpected
            else:
                return False
        except ValueError:
            return self._valueCompare(valueCurrent, valueExpected, operator)
        
        
    def dataFormatHelper(self, dataRaw, valueFormatType, valueFormat=None):
        """ helper to preformat the expected data before comparing """
        result = dataRaw
        if valueFormatType == "DateTime":
            if valueFormat == "MMMM d,y hh:mm a":
                try:
                    datetimeObj = parse(dataRaw)
                    result = datetimeObj.strftime("%B %d,%Y %I:%M %p")
                except ValueError:
                    result = dataRaw
            else:
                try:
                    datetimeObj = parse(dataRaw)
                    result = datetimeObj.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    result = dataRaw
                
        return result
                
        
        
        
                   
                    
        
        
        
            
    
        
            
            
            
            
        
            
            
        
                 
                
            
    
