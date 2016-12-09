'''
Created on Dec 7, 2016

@author: hwang
'''
import settings
import requests
import re
try:
    from lxml import etree
except ImportError:
    raise Exception("this package needs lxml modeule, please install it first.")


OBJECT_TYPE_MAPPING = { 
                        "access-credential"     : "ACC",
                        "acs"                   : "ACS",
                        "ag"                    : "AG",
                        "analog-input"          : "AI",
                        "aic"                   : "AIC",
                        "analog-output"         : "AO",
                        "aoc"                   : "AOC",
                        "as"                    : "AS",
                        "analog-value"          : "AV",
                        "ast"                   : "AST", 
                        
                        "bdc"                   : "BDC",
                        "binary-input"          : "BI",
                        "bmd"                   : "BMD",
                        "binary-output"         : "BO",
                        "bt"                    : "BT",
                        "binary-value"          : "BV",
                        
                        "calendar"              : "CAL",
                        "cel"                   : "CEL",
                        "cr"                    : "CR",
                        "credential-data-input" : "ACI",
                        "cu"                    : "CU",
                        
                        "dbi"                   : "DBI",
                        "dc"                    : "DC",
                        "der"                   : "DER",
                        "des"                   : "DES",
                        "device"                : "DEV",
                        "dg"                    : "DG",
                        
                        "ec"                    : "EC",
                        "event-enrollment"      : "EV",
                        "eva"                   : "EVA",
                        "evl"                   : "EVL",
                        "evn"                   : "EVN",
                        "evr"                   : "EVR",
                        "evs"                   : "EVS",
                        "evx"                   : "EVX",
                        
                        "file"                  : "FIL",
                        
                        "iom"                   : "IOM",
                        "ips"                   : "IPS",
                        
                        "lc"                    : "LC",
                        "lighting-output"       : "LO",
                        "loop"                  : "CO",
                        
                        "multi-state-input"     : "MI",
                        "mic"                   : "MIC",
                        "moc"                   : "MOC",
                        "mt"                    : "MT",
                        "multi-state-value"     : "MV",
                        "multi-state-output"    : "MO",
                        
                        "net"                   : "NET",
                        "notification-class"    : "EVC",
                        "np"                    : "NP",
                        
                        "pan"                   : "PAN",
                        "program"               : "PG",
                        "pi"                    : "PI",
                        
                        "schedule"              : "SCH",
                        "sel"                   : "SEL",
                        "sdl"                   : "SDL",
                        "sua"                   : "SUA",
                        "sug"                   : "SUG",
                        "structured-view"       : "SV",
                        
                        "trend-log"             : "TL"
                        
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
        
    def getDevicesList(self, siteName):
        """ get a list of Devices on a site """
        url = "%s/api/.bacnet/%s/"%(self.base_url, siteName)
        self.r = requests.get(url, cookies=self.cookie)
        root = etree.fromstring(self.r.content)
        elements = root.getchildren()
        result = []
        for elem in elements:
            objDic = {}
            objDic["device number"] = elem.get("name")
            objDic["device name"] = elem.get("displayName")
            result.append(objDic)
        return result
        
    def getNumberOfObjects(self, siteName, deviceNumber):
        """ return the total number of objects in a device """
        url = "%s/wsbac/getproperty?ObjRef=//%s/%s.DEV%s.Object_List[0]"%(self.base_url, siteName, deviceNumber, deviceNumber)
        self.r = requests.get(url, cookies=self.cookie)
        root = etree.fromstring(self.r.content)
        result = root.find("./Object/Property")
        return result.get("value")
        
        
    def getObjectsList(self, siteName, deviceNumber):
        """ return a list of objects in a device """
        numberOfObjects = self.getNumberOfObjects(siteName, deviceNumber)
        url = "%s/api/.bacnet/%s/%s?max-results=%s"%(self.base_url, siteName, deviceNumber, numberOfObjects)
        self.r = requests.get(url, cookies=self.cookie)
        root = etree.fromstring(self.r.content)
        elements = root.getchildren()
        result = []
        for elem in elements:
            objDic = {}
            objReference = elem.get("name")
            objReference = objReference.split(",")
            try: objDic["object type"] = OBJECT_TYPE_MAPPING[objReference[0]]
            except KeyError: objDic["object type"] = objReference[0]
            objDic["object number"] = objReference[1]
            objDic["object name"] = elem.get("displayName")
            result.append(objDic)
        return result
    
    def getPropertyList(self, siteName, deviceNumber, objectReference):
        """ return a list of property which the objectReference is supported """
        url = "%s/wsbac/getpropertyall?ObjRef=//%s/%s.%s"%(self.base_url, siteName, deviceNumber, objectReference)
        self.r = requests.get(url, cookies=self.cookie)
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
    
    def getPropertyValue(self, siteName, deviceNumber, objectReference, propertyName):
        """ return property value in differetn format based on the data type of the property """
        url = "%s/wsbac/getproperty?ObjRef=//%s/%s.%s.%s"%(self.base_url, siteName, deviceNumber, objectReference, propertyName)
        self.r = requests.get(url, cookies=self.cookie)
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
            
    
        
            
            
            
            
        
            
            
        
                 
                
            
    
