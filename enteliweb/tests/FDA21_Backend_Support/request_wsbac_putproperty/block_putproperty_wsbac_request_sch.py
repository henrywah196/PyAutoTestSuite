# coding: utf-8
################################################################################################
# Test Case   : Implement Back end for ESignature and block putproperty request (EWEB-22423)
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
import requests
from requests.exceptions import ConnectionError
from requests.auth import HTTPBasicAuth
import base64
import random
import string
try:
    from lxml import etree
except ImportError:
    raise Exception("this package needs lxml module, please install it first.")


# Global Settings
TEST_DATA = { "object_type" : "SCH", "site" : "$LocalSite", "device_number" : "1000", "instance_number" : "220", "object_name" : "Henry_Test_SCH220", "property_name" : "Weekly_Schedule", "property_value" : "%dynamic%", "property_name_verify" : "Weekly_Schedule", "property_value_verify" : "%dynamic%"}

VALUE_NEW  =    ('<PropertyList>'
                   '<Object ref="//$LocalSite/1000.SCH220">'
                     '<Array name="Weekly_Schedule">'
                       '<Group name="Weekly_Schedule" arrayIndex="1">'
                         '<List name="day-schedule">'
                           '<Group name="day-schedule">'
                             '<Property name="time" value="13:00:00" />'
                             '<Union name="value">'
                               '<Property name="enumerated" dataType="Enumeration" value="1" />'
                             '</Union>'
                           '</Group>'
                           '<Group name="day-schedule">'
                             '<Property name="time" value="14:00:00" />'
                             '<Union name="value">'
                               '<Property name="null" value="" isNULL="TRUE" />'
                             '</Union>'
                           '</Group>'
                         '</List>'
                       '</Group>'
                       '<Group name="Weekly_Schedule" arrayIndex="2"><List name="day-schedule"></List></Group>'
                       '<Group name="Weekly_Schedule" arrayIndex="3"><List name="day-schedule"></List></Group>'
                       '<Group name="Weekly_Schedule" arrayIndex="4"><List name="day-schedule"></List></Group>'
                       '<Group name="Weekly_Schedule" arrayIndex="5"><List name="day-schedule"></List></Group>'
                       '<Group name="Weekly_Schedule" arrayIndex="6"><List name="day-schedule"></List></Group>'
                       '<Group name="Weekly_Schedule" arrayIndex="7"><List name="day-schedule"></List></Group>'
                     '</Array>'
                   '</Object>'
                 '</PropertyList>')
        
VALUE_OLD  =    ('<PropertyList>'
                   '<Object ref="//$LocalSite/1000.SCH220">'
                     '<Array name="Weekly_Schedule">'
                       '<Group name="Weekly_Schedule" arrayIndex="1"><List name="day-schedule"/></Group>'
                       '<Group name="Weekly_Schedule" arrayIndex="2"><List name="day-schedule"/></Group>'
                       '<Group name="Weekly_Schedule" arrayIndex="3"><List name="day-schedule"/></Group>'
                       '<Group name="Weekly_Schedule" arrayIndex="4"><List name="day-schedule"/></Group>'
                       '<Group name="Weekly_Schedule" arrayIndex="5"><List name="day-schedule"/></Group>'
                       '<Group name="Weekly_Schedule" arrayIndex="6"><List name="day-schedule"/></Group>'
                       '<Group name="Weekly_Schedule" arrayIndex="7"><List name="day-schedule"/></Group>'
                     '</Array>'
                   '</Object>'
                 '</PropertyList>')


VALUE_NEW_VERIFY = ('<?xml version="1.0" encoding="UTF-8"?>'
                    '\n<PropertyList>'
                    '\n    <Object ref="//$LocalSite/1000.SCH220">'
                    '\n        <Array name="Weekly_Schedule">'
                    '\n            <Group name="Weekly_Schedule" status="OK" dataType="Group" arrayIndex="1">'
                    '\n                <List name="day-schedule">'
                    '\n                    <Group name="day-schedule" dataType="Group">'
                    '\n                        <Property name="time" dataType="Time" value="13:00:00.00"/>'
                    '\n                        <Union name="value" dataType="Union">'
                    '\n                            <Property name="enumerated" dataType="Enumeration" value="1"/>'
                    '\n                        </Union>'
                    '\n                    </Group>'
                    '\n                    <Group name="day-schedule" dataType="Group">'
                    '\n                        <Property name="time" dataType="Time" value="14:00:00.00"/>'
                    '\n                        <Union name="value" dataType="Union">'
                    '\n                            <Property name="null" dataType="Null" isNULL="TRUE" value=""/>'
                    '\n                        </Union>'
                    '\n                    </Group>'
                    '\n                </List>'
                    '\n            </Group>'
                    '\n            <Group name="Weekly_Schedule" status="OK" dataType="Group" arrayIndex="2">'
                    '\n                <List name="day-schedule"/>'
                    '\n            </Group>'
                    '\n            <Group name="Weekly_Schedule" status="OK" dataType="Group" arrayIndex="3">'
                    '\n                <List name="day-schedule"/>'
                    '\n            </Group>'
                    '\n            <Group name="Weekly_Schedule" status="OK" dataType="Group" arrayIndex="4">'
                    '\n                <List name="day-schedule"/>'
                    '\n            </Group>'
                    '\n            <Group name="Weekly_Schedule" status="OK" dataType="Group" arrayIndex="5">'
                    '\n                <List name="day-schedule"/>'
                    '\n            </Group>'
                    '\n            <Group name="Weekly_Schedule" status="OK" dataType="Group" arrayIndex="6">'
                    '\n                <List name="day-schedule"/>'
                    '\n            </Group>'
                    '\n            <Group name="Weekly_Schedule" status="OK" dataType="Group" arrayIndex="7">'
                    '\n                <List name="day-schedule"/>'
                    '\n            </Group>'
                    '\n        </Array>'
                    '\n    </Object>'
                    '\n</PropertyList>\n')


VALUE_OLD_VERIFY = ('<?xml version="1.0" encoding="UTF-8"?>'
                    '\n<PropertyList>'
                    '\n    <Object ref="//$LocalSite/1000.SCH220">'
                    '\n        <Array name="Weekly_Schedule">'
                    '\n            <Group name="Weekly_Schedule" status="OK" dataType="Group" arrayIndex="1">'
                    '\n                <List name="day-schedule"/>'
                    '\n            </Group>'
                    '\n            <Group name="Weekly_Schedule" status="OK" dataType="Group" arrayIndex="2">'
                    '\n                <List name="day-schedule"/>'
                    '\n            </Group>'
                    '\n            <Group name="Weekly_Schedule" status="OK" dataType="Group" arrayIndex="3">'
                    '\n                <List name="day-schedule"/>'
                    '\n            </Group>'
                    '\n            <Group name="Weekly_Schedule" status="OK" dataType="Group" arrayIndex="4">'
                    '\n                <List name="day-schedule"/>'
                    '\n            </Group>'
                    '\n            <Group name="Weekly_Schedule" status="OK" dataType="Group" arrayIndex="5">'
                    '\n                <List name="day-schedule"/>'
                    '\n            </Group>'
                    '\n            <Group name="Weekly_Schedule" status="OK" dataType="Group" arrayIndex="6">'
                    '\n                <List name="day-schedule"/>'
                    '\n            </Group>'
                    '\n            <Group name="Weekly_Schedule" status="OK" dataType="Group" arrayIndex="7">'
                    '\n                <List name="day-schedule"/>'
                    '\n            </Group>'
                    '\n        </Array>'
                    '\n    </Object>'
                    '\n</PropertyList>\n')


def getTestingData():
    """
    return a list of testing data
    """
    
    class TestData():
        
        def __init__(self):
            self.object_type = None 
            self.site = None 
            self.device_number = None 
            self.instance_number = None 
            self.object_name = None
            self.property_name = None
            self.property_value = None
            self.property_name_verify = None
            self.property_value_verify = None
            
        def getObjRef(self):
            return "//%s/%s.%s%s"%(self.site, self.device_number, self.object_type, self.instance_number)
            
    myTestData = TestData()
    myTestData.object_type = TEST_DATA["object_type"]
    myTestData.site = TEST_DATA["site"]
    myTestData.device_number = TEST_DATA["device_number"] 
    myTestData.instance_number = TEST_DATA["instance_number"] 
    myTestData.object_name = TEST_DATA["object_name"]
    myTestData.property_name = TEST_DATA["property_name"]
    myTestData.property_value = TEST_DATA["property_value"]
    myTestData.property_name_verify = TEST_DATA["property_name_verify"]
    myTestData.property_value_verify = TEST_DATA["property_value_verify"]
        
    return myTestData


class TestCase(TestCaseTemplate):
    
    
    @classmethod
    def setUpClass(cls):
        super(TestCase, cls).setUpClass()
        cls.Host = settings.HOST
        cls.username = settings.USERNAME
        cls.password = settings.PASSWORD
        cls.base_url = "http://%s/enteliweb"%cls.Host
        cls.webgroup = WebGroupDBObj()
        
        cls.test_data = getTestingData()
        cls.value_old = VALUE_OLD
        cls.value_new = VALUE_NEW
        cls.value_old_verify = VALUE_OLD_VERIFY
        cls.value_new_verify = VALUE_NEW_VERIFY
        
        
    @classmethod
    def tearDownClass(cls):
        super(TestCase, cls).tearDownClass()
        
        cls._disable_esignature() # disable ESignature feature
        del cls.webgroup
    
    
    @classmethod
    def _enable_esignature(cls):
        # enable ESignature feature
        cls.webgroup.cursor.execute("update settings_global set Value = 1 where Type = 'ESignature' and Name = 'ElectronicSignature';")
        cls.webgroup.cnxn.commit()
        cursor = cls.webgroup.cursor.execute("select Value from settings_global where Type = 'ESignature' and Name = 'ElectronicSignature';")
        row = cursor.fetchone()
        if row.Value != u'1':
            raise Exception("Enabling ESignature feature on remote machine failed")
        
        
    @classmethod    
    def _disable_esignature(cls):
        # disable ESignature feature
        cls.webgroup.cursor.execute("update settings_global set Value = 0 where Type = 'ESignature' and Name = 'ElectronicSignature';")
        cls.webgroup.cnxn.commit()
        cursor = cls.webgroup.cursor.execute("select Value from settings_global where Type = 'ESignature' and Name = 'ElectronicSignature';")
        row = cursor.fetchone()
        if row.Value != u'0':
            raise Exception("Disabling ESignature feature on remote machine failed")
        
        
    @classmethod
    def _enable_comment(cls):
        # enable ESignature feature
        cls.webgroup.cursor.execute("update settings_global set Value = 1 where Type = 'ESignature' and Name = 'ElectronicSignatureComment';")
        cls.webgroup.cnxn.commit()
        cursor = cls.webgroup.cursor.execute("select Value from settings_global where Type = 'ESignature' and Name = 'ElectronicSignatureComment';")
        row = cursor.fetchone()
        if row.Value != u'1':
            raise Exception("Enabling ESignature Comment as Mandatory on remote machine failed")
        
        
    @classmethod    
    def _disable_comment(cls):
        # disable ESignature feature
        cls.webgroup.cursor.execute("update settings_global set Value = 0 where Type = 'ESignature' and Name = 'ElectronicSignatureComment';")
        cls.webgroup.cnxn.commit()
        cursor = cls.webgroup.cursor.execute("select Value from settings_global where Type = 'ESignature' and Name = 'ElectronicSignatureComment';")
        row = cursor.fetchone()
        if row.Value != u'0':
            raise Exception("Disabling ESignature Comment as Mandatory on remote machine failed")
        
    
    def setUp(self):
        super(TestCase, self).setUp()
        self.longMessage = True
        self.maxDiff = None
        
        self.r = None
        self.s = requests.session()
        self.csrf_token = None
        
        # login enteliWEB
        self._login()
        
        # disable ESignature feature
        self._disable_esignature()
        
        # create testing BACnet object
        self._wsbac_createobject(self.test_data.site, self.test_data.device_number, self.test_data.object_type, self.test_data.instance_number, self.test_data.object_name)
            

    def tearDown(self):
        super(TestCase, self).tearDown()
        
        # disable ESignature feature
        self._disable_esignature()
        
        # delete testing BACnet object
        self._wsbac_deleteobject(self.test_data.site, self.test_data.device_number, self.test_data.object_type, self.test_data.instance_number, self.test_data.object_name)
            
        # logout
        self._login(log_out=True)    


    def test01_putpropety_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac/putproperty' for '%s' without ESignature will be blocked if feature is enabled with optional comment"%test_data.getObjRef()
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as option
        self._disable_comment()
        
        # send POST request
        test_data.property_value = self.value_new
        self._wsbac_putproperty(test_data)
        
        # verify response
        self._verify_request_blocked()
            
        # verify Object property not being changed
        self._verify_state_not_changed_sch()
        
        
    def test02_putpropety_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac/putproperty' for '%s' without ESignature will be blocked if feature is enabled with mandatory comment"%test_data.getObjRef()
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as option
        self._enable_comment()
        
        # send POST request
        test_data.property_value = self.value_new
        self._wsbac_putproperty(test_data)
        
        # verify response
        self._verify_request_blocked()
            
        # verify Object property not being changed
        self._verify_state_not_changed_sch()
        
          
    def test03_putpropety_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac//putproperty' for %s with invalid ESignature will be blocked if feature is enabled with optional comment"%test_data.getObjRef()
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as option
        self._disable_comment()
        
        # send POST request
        test_data.property_value = self.value_new
        self._wsbac_putproperty(test_data, self.password)
        
        # verify response
        self._verify_request_blocked(signature_flag=2)
            
        # verify Object property not being changed
        self._verify_state_not_changed_sch()
        
        
    def test04_putpropety_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac//putproperty' for %s with invalid ESignature will be blocked if feature is enabled with mandatory comment"%test_data.getObjRef()
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as mandatory
        self._enable_comment()
        
        # send POST request
        test_data.property_value = self.value_new
        self._wsbac_putproperty(test_data, self.password, "esign message")
        
        # verify response
        self._verify_request_blocked(signature_flag=2)
            
        # verify Object property not being changed
        self._verify_state_not_changed_sch()
        
    
    def test05_putpropety_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac//putproperty' for %s with valid ESignature will get through if feature is enabled with optional comment"%test_data.getObjRef()
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as option
        self._disable_comment()
        
        # send POST request
        password_base64 = base64.b64encode(self.password)
        test_data.property_value = self.value_new
        self._wsbac_putproperty(test_data, password_base64)
        
        # verify response
        self._verify_request_getthrough()
            
        # verify Object property get changed
        self._verify_state_changed_sch()
        
        
    def test06_putpropety_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac//putproperty' for %s with valid ESignature and comment will get through if feature is enabled with mandatory comment"%test_data.getObjRef()
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as option
        self._enable_comment()
        
        # send POST request
        password_base64 = base64.b64encode(self.password)
        test_data.property_value = self.value_new
        self._wsbac_putproperty(test_data, password_base64, "&")
        
        # verify response
        self._verify_request_getthrough()
            
        # verify Object property get changed
        self._verify_state_changed_sch()
        
        
    def test07_putpropety_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac//putproperty' for %s with valid ESignature but no comment will be blocked if feature is enabled with mandatory comment"%test_data.getObjRef()
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as mandatory
        self._enable_comment()
        
        # send POST request
        password_base64 = base64.b64encode(self.password)
        test_data.property_value = self.value_new
        self._wsbac_putproperty(test_data, password_base64, " ")
        
        # verify response
        self._verify_request_blocked(signature_flag=3)
            
        # verify Object property not being changed
        self._verify_state_not_changed_sch()
        
        
    def test08_putpropety_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac//putproperty' for %s without ESignature will get through if feature is disabled"%test_data.getObjRef()
        
        # send POST request
        test_data.property_value = self.value_new
        self._wsbac_putproperty(test_data)
        
        # verify response
        self._verify_request_getthrough()
        
        # verify Object property get changed
        self._verify_state_changed_sch()
            
            
    def _verify_state_not_changed_sch(self):
        # verify Object property not being changed
        self._wsbac_getproperty(self.test_data.site, self.test_data.device_number, self.test_data.object_type, self.test_data.instance_number, self.test_data.property_name_verify)
        response_content = self.r.content
        self.assertEqual(response_content, self.value_old_verify, "Verify object property not being changed failed")
        
        
    def _verify_state_changed_sch(self):
        # verify Object property get changed
        self._wsbac_getproperty(self.test_data.site, self.test_data.device_number, self.test_data.object_type, self.test_data.instance_number, self.test_data.property_name_verify)
        response_content = self.r.content
        self.assertEqual(response_content, self.value_new_verify, "Verify object property get changed failed")
            
            
    def _verify_request_getthrough(self):
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
        response_content = self.r.content
        result = 'status="OK"' in response_content
        self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
            
            
    def _verify_request_blocked(self, signature_flag=1):
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
        response_content = self.r.content
        result = None
        if signature_flag == 1:    # no signature
            result = "QERR_CODE_NEEDS_SIGNATURE" in response_content
        elif signature_flag == 2:    # invalid signature with mandatory comment
            result = "QERR_CODE_INVALID_USER_CREDENTIALS" in response_content
        elif signature_flag == 3:    # invalid comment with mandatory comment
            result = "QERR_CODE_INVALID_COMMENT" in response_content
        self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
            
    
    def _fetch_property_value(self, xml_string):
        """ helper function to obtain the value from the property xml string """
        
        value_string = None
        m = re.search('value=".*"', xml_string)
        if m:
            value_string = m.group(0)
        if value_string is not None:
            return value_string[7:-1]
        else:
            raise Exception("%s is not found in xml string %s"%('value=".*"', xml_string))
        
    
    def _wsbac_createobject(self, siteName, deviceNumber, objType, objInstance, objName, esignature=None):
        """ create an object on target device """
        
        obj_ref = "//%s/%s.DEV%s"%(siteName, deviceNumber, deviceNumber)
        url = "%s/wsbac/createobject"%self.base_url
        payload = {"list[]"      : obj_ref,
                   "type"        : objType,
                   "instance"    : objInstance,
                   "name"        : objName,
                   "description" : "",
                   "_csrfToken"  : self.csrf_token}
        if esignature is not None:
            payload["esignature_password"] = esignature
            
        self.r = self._post_request(url, payload)
        
        if self.r.status_code != 200:
            obj_ref = "//%s/%s.%s%s"%(siteName, deviceNumber, objType, objInstance)
            raise Exception("Creating test BACnet object '%s' failed"%obj_ref)
        
        
    def _wsbac_deleteobject(self, siteName, deviceNumber, objType, objInstance, objName, esignature=None):
        """ create an object on target device """
        obj_ref = "//%s/%s.%s%s"%(siteName, deviceNumber, objType, objInstance)
        url = "%s/wsbac/deleteobject"%self.base_url
        payload = {"ref"      : '["%s"]'%obj_ref,
                   "_csrfToken"  : self.csrf_token}
        if esignature is not None:
            payload["esignature_password"] = esignature
            
        self.r = self._post_request(url, payload)
        if self.r.status_code != 200:
            raise Exception("Deleting test BACnet object '%s' failed"%obj_ref)
        
        
    def _compose_xml(self, old_xml_string, value_string):
        """ helper used by _wsobjdlg_putproperty() """
        old_string = None
        m = re.search('value=".*"', old_xml_string)
        if m:
            old_string = m.group(0)
        
        if old_string is None:
            raise Exception("%s is not found in xml string %s"%('value=".*"', old_xml_string))    
        new_string = 'value="%s"'%value_string
        return string.replace(old_xml_string, old_string, new_string)
        
        
    def _wsbac_putproperty(self, parameters, esignature=None, comment=None):
        """ create an object on target device """
        
        url = "%s/wsbac/putproperty"%self.base_url
        
        #self._wsbac_getproperty(parameters.site, parameters.device_number, parameters.object_type, parameters.instance_number, parameters.property_name)
        #old_xml_string = self.r.content
        #new_xml_string = self._compose_xml(old_xml_string, parameters.property_value)
        old_xml_string = self.value_old
        new_xml_string = self.value_new
        
        payload = {"format"      : "TEXT",
                   "xmlstr"      : new_xml_string,
                   "oldxml"      : old_xml_string,
                   "logcomment"  : "",
                   "_csrfToken"  : self.csrf_token}
        if esignature is not None:
            payload["esignature_password"] = esignature
        if comment is not None:
            payload["esignature_comment"] = comment
            
        self.r = self._post_request(url, payload)
        
        
    def _wsbac_getproperty(self, siteName, deviceNumber, objType, objInstance, objProperty):
        obj_ref = "//%s/%s.%s%s.%s"%(siteName, deviceNumber, objType, objInstance, objProperty)
        url = "%s/wsbac/getproperty?ObjRef=%s"%(self.base_url, obj_ref)
        self.r = self._get_request(url)
    
    
    def _login(self, log_out=False):
        if log_out:
            url = "%s/api/auth/logout"%self.base_url
            self.r = self.s.get(url)
        else:
            url = "%s/api/auth/basiclogin?username=%s&password=%s" % (self.base_url, self.username, self.password)
            self.r = self.s.get(url)
            root = etree.fromstring(self.r.content)
            self.csrf_token = root.get("_csrfToken")
            if not self.csrf_token:
                raise Exception("Login to enteliWEB '%s' using REST API failed"%self.Host)
        
        
    def _get_request(self, url, retry=3):
        """ helper to dealing with request return 10054 error """
        try:
            #result = requests.get(url, auth=HTTPBasicAuth(self.userName, self.passWord))
            result = self.s.get(url)
            if result is None:
                if retry >= 1:
                    time.sleep(10)
                    retry = retry - 1
                    self._get_request(url, retry)
            return result
        except ConnectionError:
            if retry >= 1:
                time.sleep(60)
                retry = retry - 1

                print "debug: retry get request after Connection aborted"

                self._get_request(url, retry)
            else:
                raise
    
    
    def _post_request(self, url, payload, retry=3):
        """ helper to dealing with request return 10054 error """
        try:
            #result = requests.get(url, auth=HTTPBasicAuth(self.userName, self.passWord))
            result = self.s.post(url, data=payload)
            if result is None:
                if retry >= 1:
                    time.sleep(10)
                    retry = retry - 1
                    self._post_request(url, payload, retry)
            return result
        except ConnectionError:
            if retry >= 1:
                time.sleep(60)
                retry = retry - 1

                print "debug: retry post request after Connection aborted"

                self._post_request(url, payload, retry)
            else:
                raise
        

if __name__ == "__main__":
    unittest.main()
