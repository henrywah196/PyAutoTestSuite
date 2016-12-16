'''
Created on Dec 7, 2016

@author: hwang
'''
import settings
import requests
import re
import datetime
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
                       "IP": ["AI", "BI", "MI", "PI"],
                       "OP": ["AO", "BO", "MO", "LO"]
                     }

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
    
    def isPropertyExisting(self, siteName, deviceNumber, objectReference, propertyName):
        """ helper to verify if the specified object reference contain the specified property """
        url = "%s/wsbac/getproperty?ObjRef=//%s/%s.%s.%s"%(self.base_url, siteName, deviceNumber, objectReference, propertyName)
        self.r = requests.get(url, cookies=self.cookie)
        root = etree.fromstring(self.r.content)
        elemObject = root.find("./Object")
        element = (elemObject.getchildren())[0]
        status = element.get("status")
        if status == "OK":
            return True
        else:
            return False
        
    def propertyValueIsNull(self, siteName, deviceNumber, objectReference, propertyName):
        """ helper to verify and return true if the web service has isNULL="TRUE" returned """
        url = "%s/wsbac/getproperty?ObjRef=//%s/%s.%s.%s"%(self.base_url, siteName, deviceNumber, objectReference, propertyName)
        self.r = requests.get(url, cookies=self.cookie)
        root = etree.fromstring(self.r.content)
        elemObject = root.find("./Object")
        element = (elemObject.getchildren())[0]
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
        """ helper to return list of object based on the given object reference """
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
            if item in ("IP", "OP"):
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
        operator = propertyValueCompare[1]
        propertyValue = propertyValueCompare[2]
        
        propertyValueInfo = self.getPropertyValue(siteName, deviceNumber, objectReference, propertyName)
        
        if isinstance(propertyValueInfo, list):      # complex property or array
            pass
        else:
            currentPropertyValue = propertyValueInfo["value"]
            currentPropertyDataType = propertyValueInfo["data type"]
            
            # dealing with special marker 'NULL'
            if propertyValue.lower() == "null":
                isNull = self.propertyValueIsNull(siteName, deviceNumber, objectReference, propertyName)
                return self._valueCompareNull(isNull, operator)
            
            # dealing with Priority_Array
            elif "Priority_Array" in propertyName:
                self.siteName        = siteName
                self.deviceNumber    = deviceNumber
                self.objectReference = objectReference
                return self._valueComparePresentValue(currentPropertyDataType, currentPropertyValue, propertyValue, operator)
            
            # dealing property with multiple data type, such as Present_Value
            elif propertyName in ("Present_Value", "Manual_Override"):
                self.siteName        = siteName
                self.deviceNumber    = deviceNumber
                self.objectReference = objectReference
                return self._valueComparePresentValue(currentPropertyDataType, currentPropertyValue, propertyValue, operator)
            
            # dealing with number value
            elif currentPropertyDataType in ("Signed", "Unsigned", "Real"):
                return self._valueCompareNumber(currentPropertyValue, propertyValue, operator)
            
            # dealing with string value
            elif currentPropertyDataType in ("Text", "Bitlist"):
                return self._valueCompareString(currentPropertyValue, propertyValue, operator)
            
            # dealing with date time value
            elif currentPropertyDataType in ("Time Date", "Time", "Date"):
                return self._valueCompareDateTime(currentPropertyDataType, currentPropertyValue, propertyValue, operator)
            
            # dealing with other value for exactly match
            elif currentPropertyDataType in ("Object Id", "Boolean", "Enumeration", "Octet"):
                return self._valueCompare(currentPropertyValue, propertyValue, operator)
            
    def _valueCompare(self, valueCurrent, valueExpected, operator):
        """ the basic value compare """
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
                    valueCurrent = valueInfo["value"]
                elif valueCurrent == "inactive":
                    valueInfo = self.getPropertyValue(self.siteName, self.deviceNumber, self.objectReference, "Inactive_Text")
                    valueCurrent = valueInfo["value"]
                return self._valueCompare(valueCurrent, valueExpected, operator)
            
        elif objType in ("MI", "MO", "MV"):
            isNativeValue = True
            try: int(valueExpected)
            except ValueError: isNativeValue = False
            if isNativeValue:    # verify native value
                return self._valueCompareNumber(valueCurrent, valueExpected, operator)
            else:                # verify state text
                valueInfo = self.getPropertyValue(self.siteName, self.deviceNumber, self.objectReference, "State_Text")
                idx = int(valueExpected)
                valueInfo = valueInfo[idx - 1]
                valueCurrent = valueInfo["value"]
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
            return False
        
        
                   
                    
        
        
        
            
    
        
            
            
            
            
        
            
            
        
                 
                
            
    
