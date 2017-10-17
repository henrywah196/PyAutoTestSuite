# coding: utf-8
################################################################################################
# Test Case   : Implement Back end for ESignature and block createobject request (EWEB-22477)
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
try:
    from lxml import etree
except ImportError:
    raise Exception("this package needs lxml module, please install it first.")


# Global Settings
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "block_renameobject_request_02.json"))


def getTestingData():
    """
    return a list of testing data
    """
    
    class TestData():
        
        def __init__(self):
            self.obj_1 = None 
            self.obj_2 = None 
            self.find = None 
            self.replace = None 
            
    json_file = open(JSON_FILE_LOCATION, "r")
    json_data = json.load(json_file)
            
    result = []        
    for item in json_data:
        myTestData = TestData()
        myTestData.obj_1 = item["obj1"]
        myTestData.obj_2 = item["obj2"]
        myTestData.find = item["find"]
        myTestData.replace = item["replace"] 
        
        result.append(myTestData)
        
    return result


@ddt
class TestCase(TestCaseTemplate):
    
    
    @classmethod
    def setUpClass(cls):
        super(TestCase, cls).setUpClass()
        cls.Host = settings.HOST
        cls.username = settings.USERNAME
        cls.password = settings.PASSWORD
        cls.base_url = "http://%s/enteliweb"%cls.Host
        cls.webgroup = WebGroupDBObj()
        
        
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
        

    def tearDown(self):
        super(TestCase, self).tearDown()
        
        # disable ESignature feature
        self._disable_esignature()
        
        # delete testing BACnet object
        obj_1 = self.test_data.obj_1
        obj_2 = self.test_data.obj_2
        if obj_1["device_category"] != "3rd":
            self._wsbac_deleteobject(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"], obj_1["object_name"])
        if obj_2["device_category"] != "3rd":    
            self._wsbac_deleteobject(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"], obj_2["object_name"])
        
        
        # logout
        self._login(log_out=True)
        

    @data(*getTestingData())
    def test01_renameobject_wsref(self, test_data):
        
        # prepare
        self.test_data = test_data
        self._testMethodDoc = "Request 'wsbac/renameobject' for multiple objects without ESignature will be blocked if feature is enabled with optional comment"
        
        obj_1 = test_data.obj_1
        obj_2 = test_data.obj_2
        find = test_data.find
        replace = test_data.replace
        
        # create testing object
        self._wsbac_createobject(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"], obj_1["object_name"])
        self._wsbac_createobject(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"], obj_2["object_name"])
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as optional
        self._disable_comment()
        
        # send POSt request
        obj_ref_1 = "//%s/%s.%s%s"%(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"])
        obj_ref_2 = "//%s/%s.%s%s"%(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"])
        name_1 = obj_1["object_name"]
        name_2 = obj_2["object_name"]
        self._wsref_renameobject(obj_ref_1, obj_ref_2, name_1, name_2, find, replace)
        
        # verify response
        self._verify_request_blocked()
        
        # verify Object not being created
        self._verify_state_not_changed()
        
        
    @data(*getTestingData())
    def test02_renameobject_wsref(self, test_data):
        
        self.test_data = test_data
        self._testMethodDoc = "Request 'wsbac/renameobject' for multiple objects without ESignature will be blocked if feature is enabled with mandatory comment"
        
        obj_1 = test_data.obj_1
        obj_2 = test_data.obj_2
        find = test_data.find
        replace = test_data.replace
        
        # create testing object
        self._wsbac_createobject(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"], obj_1["object_name"])
        self._wsbac_createobject(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"], obj_2["object_name"])
        
        
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as mandatory
        self._enable_comment()
        
        # send POSt request
        obj_ref_1 = "//%s/%s.%s%s"%(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"])
        obj_ref_2 = "//%s/%s.%s%s"%(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"])
        name_1 = obj_1["object_name"]
        name_2 = obj_2["object_name"]
        self._wsref_renameobject(obj_ref_1, obj_ref_2, name_1, name_2, find, replace)
        
        # verify response
        self._verify_request_blocked()
        
        # verify Object not being created
        self._verify_state_not_changed()
        
    
    @data(*getTestingData())    
    def test03_renameobject_wsref(self, test_data):
        
        self.test_data = test_data
        self._testMethodDoc = "Request 'wsbac/renameobject' for multiple objects with invalid ESignature will be blocked if feature is enabled with optional comment"
        
        obj_1 = test_data.obj_1
        obj_2 = test_data.obj_2
        find = test_data.find
        replace = test_data.replace
        
        # create testing object
        self._wsbac_createobject(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"], obj_1["object_name"])
        self._wsbac_createobject(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"], obj_2["object_name"])
        
        
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as optional
        self._disable_comment()
        
        # send POSt request
        obj_ref_1 = "//%s/%s.%s%s"%(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"])
        obj_ref_2 = "//%s/%s.%s%s"%(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"])
        name_1 = obj_1["object_name"]
        name_2 = obj_2["object_name"]
        self._wsref_renameobject(obj_ref_1, obj_ref_2, name_1, name_2, find, replace, self.password)
        
        # verify response
        self._verify_request_blocked(signature_flag=2)
        
        # verify Object not being created
        self._verify_state_not_changed()
        
        
    @data(*getTestingData())    
    def test04_renameobject_wsref(self, test_data):
        
        self.test_data = test_data
        self._testMethodDoc = "Request 'wsbac/renameobject' for multiple objects with invalid ESignature will be blocked if feature is enabled with mandatory comment"
        
        obj_1 = test_data.obj_1
        obj_2 = test_data.obj_2
        find = test_data.find
        replace = test_data.replace
        
        # create test object
        self._wsbac_createobject(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"], obj_1["object_name"])
        self._wsbac_createobject(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"], obj_2["object_name"])
        
        
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as mandatory
        self._enable_comment()
        
        # send POSt request
        obj_ref_1 = "//%s/%s.%s%s"%(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"])
        obj_ref_2 = "//%s/%s.%s%s"%(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"])
        name_1 = obj_1["object_name"]
        name_2 = obj_2["object_name"]
        self._wsref_renameobject(obj_ref_1, obj_ref_2, name_1, name_2, find, replace, self.password, "esign message")
        
        # verify response
        self._verify_request_blocked(signature_flag=2)
        
        # verify Object not being created
        self._verify_state_not_changed()
        
        
    @data(*getTestingData())    
    def test05_renameobject_wsref(self, test_data):
        
        self.test_data = test_data
        self._testMethodDoc = "Request 'wsbac/renameobject' for multiple objects with valid ESignature will get through if feature is enabled with optional comment"
        
        obj_1 = test_data.obj_1
        obj_2 = test_data.obj_2
        find = test_data.find
        replace = test_data.replace
        
        # Create testing object
        self._wsbac_createobject(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"], obj_1["object_name"])
        self._wsbac_createobject(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"], obj_2["object_name"])
        
        
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as optional
        self._disable_comment()
        
        # send POSt request
        password_base64 = base64.b64encode(self.password)
        obj_ref_1 = "//%s/%s.%s%s"%(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"])
        obj_ref_2 = "//%s/%s.%s%s"%(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"])
        name_1 = obj_1["object_name"]
        name_2 = obj_2["object_name"]
        self._wsref_renameobject(obj_ref_1, obj_ref_2, name_1, name_2, find, replace, password_base64)
        
        
        
        # verify response
        self._verify_request_getthrough()
        
        # verify Object being created
        self._verify_state_changed()
        
        
    @data(*getTestingData())    
    def test06_renameobject_wsref(self, test_data):
        
        self.test_data = test_data
        self._testMethodDoc = "Request 'wsbac/renameobject' for multiple objects with valid ESignature and comment will get through if feature is enabled with mandatory comment"
        
        obj_1 = test_data.obj_1
        obj_2 = test_data.obj_2
        find = test_data.find
        replace = test_data.replace
        
        # create testing object
        self._wsbac_createobject(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"], obj_1["object_name"])
        self._wsbac_createobject(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"], obj_2["object_name"])
        
        
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as mandatory
        self._enable_comment()
        
        # send POSt request
        password_base64 = base64.b64encode(self.password)
        obj_ref_1 = "//%s/%s.%s%s"%(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"])
        obj_ref_2 = "//%s/%s.%s%s"%(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"])
        name_1 = obj_1["object_name"]
        name_2 = obj_2["object_name"]
        self._wsref_renameobject(obj_ref_1, obj_ref_2, name_1, name_2, find, replace, password_base64, "%")
        
        
        # verify response
        self._verify_request_getthrough()
        
        # verify Object being created
        self._verify_state_changed()
        
        
    @data(*getTestingData())    
    def test07_renameobject_wsref(self, test_data):
        
        self.test_data = test_data
        self._testMethodDoc = "Request 'wsbac/renameobject' for multiple objects with valid ESignature but no comment will be blocked if feature is enabled with mandatory comment"
        
        obj_1 = test_data.obj_1
        obj_2 = test_data.obj_2
        find = test_data.find
        replace = test_data.replace
        
        # create testing object
        self._wsbac_createobject(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"], obj_1["object_name"])
        self._wsbac_createobject(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"], obj_2["object_name"])
        
        
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as mandatory
        self._enable_comment()
        
        # send POSt request
        password_base64 = base64.b64encode(self.password)
        obj_ref_1 = "//%s/%s.%s%s"%(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"])
        obj_ref_2 = "//%s/%s.%s%s"%(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"])
        name_1 = obj_1["object_name"]
        name_2 = obj_2["object_name"]
        self._wsref_renameobject(obj_ref_1, obj_ref_2, name_1, name_2, find, replace, password_base64, " ")
        
        
        # verify response
        self._verify_request_blocked(signature_flag=3)
        
        # verify Object not being created
        self._verify_state_not_changed()
    
    
    @data(*getTestingData())    
    def test08_renameobject_wsref(self, test_data):
        
        self.test_data = test_data
        self._testMethodDoc = "Request 'wsbac/renameobject' for multiple objects without ESignature will get through if feature is disabled"
        
        obj_1 = test_data.obj_1
        obj_2 = test_data.obj_2
        find = test_data.find
        replace = test_data.replace
        
        # Create testing object
        self._wsbac_createobject(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"], obj_1["object_name"])
        self._wsbac_createobject(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"], obj_2["object_name"])
        
        
        
        # disable ESignature feature
        self._disable_esignature()
        
        # send POSt request
        obj_ref_1 = "//%s/%s.%s%s"%(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"])
        obj_ref_2 = "//%s/%s.%s%s"%(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"])
        name_1 = obj_1["object_name"]
        name_2 = obj_2["object_name"]
        self._wsref_renameobject(obj_ref_1, obj_ref_2, name_1, name_2, find, replace)
        
        # verify response
        self._verify_request_getthrough()
        
        # verify Object being created
        self._verify_state_changed()
        
    def _verify_state_not_changed(self):
        # verify Object name not being changed
        obj_1 = self.test_data.obj_1
        obj_2 = self.test_data.obj_2
        obj_ref_1 = "//%s/%s.%s%s"%(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"])
        obj_ref_2 = "//%s/%s.%s%s"%(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"])
        self._wsbac_getproperty(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"], obj_1["object_name"], "Object_Name")
        response_content = self.r.content
        result = 'value="%s"'%obj_1["object_name"] in response_content
        self.assertTrue(result, "Verify object name not being changed for %s failed. Respond content '%s' is not expected"%(obj_ref_1, response_content))
        self._wsbac_getproperty(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"], obj_2["object_name"], "Object_Name")
        response_content = self.r.content
        result = 'value="%s"'%obj_2["object_name"] in response_content
        self.assertTrue(result, "Verify object name not being changed for %s failed. Respond content '%s' is not expected"%(obj_ref_2, response_content))
        
        
        
    def _verify_state_changed(self):
        # verify Object being created
        time.sleep(13)
        obj_1 = self.test_data.obj_1
        obj_2 = self.test_data.obj_2
        obj_ref_1 = "//%s/%s.%s%s"%(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"])
        obj_ref_2 = "//%s/%s.%s%s"%(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"])
        self._wsbac_getproperty(obj_1["site"], obj_1["device_number"], obj_1["object_type"], obj_1["instance_number"], obj_1["object_name"], "Object_Name")
        response_content = self.r.content
        result = 'value="%s"'%obj_1["object_name_new"] in response_content
        self.assertTrue(result, "Verify object name being changed for %s failed. Respond content '%s' is not expected"%(obj_ref_1, response_content))
        self._wsbac_getproperty(obj_2["site"], obj_2["device_number"], obj_2["object_type"], obj_2["instance_number"], obj_2["object_name"], "Object_Name")
        response_content = self.r.content
        result = 'value="%s"'%obj_2["object_name_new"] in response_content
        self.assertTrue(result, "Verify object name being changed for %s failed. Respond content '%s' is not expected"%(obj_ref_2, response_content))
        
        
    def _verify_request_getthrough(self):
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
        response_content = self.r.content
        result = ':"OK"' in response_content
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
    
    
    def _wsbac_createobject(self, siteName, deviceNumber, objType, objInstance, objName, esignature=None, comment=None):
        """ create an object on target device """
        url = "%s/wsbac/createobject"%self.base_url
        payload = {"list[]"      : "//%s/%s.DEV%s"%(siteName, deviceNumber, deviceNumber),
                   "type"        : objType,
                   "instance"    : objInstance,
                   "name"        : objName,
                   "description" : "",
                   "_csrfToken"  : self.csrf_token}
        if esignature is not None:
            payload["esignature_password"] = esignature
        if comment is not None:
            payload["esignature_comment"] = comment
            
        self.r = self._post_request(url, payload)
    
    
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
        
        
    def _wsref_renameobject(self, obj_ref_1, obj_ref_2, name_1, name_2, find_text, replace_with, esignature=None, comment=None):
        
        url = "%s/wsref/renameobject"%self.base_url
        payload = {"list[]"      : obj_ref_1,
                   "list[]"      : obj_ref_2,
                   "names[]"     : name_1,
                   "names[]"     : name_2,
                   "findtext"    : find_text,
                   "replacewith" : replace_with,
                   "appendto"    : "",
                   "prependto"   : "",
                   "task[findreplace]" : "FR",
                   "_csrfToken"  : self.csrf_token}
        if esignature is not None:
            payload["esignature_password"] = esignature
        if comment is not None:
            payload["esignature_comment"] = comment
            
        self.r = self._post_request(url, payload)
    
    
    def _wsbac_getproperty(self, siteName, deviceNumber, objType, objInstance, objName, objProperty):
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
