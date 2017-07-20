# coding: utf-8
################################################################################################
# Test Case   : Implement Back end for ESignature and block putpropertyvalue request (EWEB-22474)
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
try:
    from lxml import etree
except ImportError:
    raise Exception("this package needs lxml module, please install it first.")


# Global Settings
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "block_putpropertyvalues_request.json"))


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
            
    json_file = open(JSON_FILE_LOCATION, "r")
    json_data = json.load(json_file)
            
    result = []        
    for item in json_data:
        myTestData = TestData()
        myTestData.object_type = item["object_type"]
        myTestData.site = item["site"]
        myTestData.device_number = item["device_number"] 
        myTestData.instance_number = item["instance_number"] 
        myTestData.object_name = item["object_name"]
        myTestData.property_name = item["property_name"]
        myTestData.property_value = item["property_value"]
        myTestData.property_name_verify = item["property_name_verify"]
        myTestData.property_value_verify = item["property_value_verify"]
        
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
            

    def tearDown(self):
        super(TestCase, self).tearDown()
        
        # disable ESignature feature
        self._disable_esignature()
        
        # delete testing BACnet object
        self._wsbac_deleteobject(self.test_data.site, self.test_data.device_number, self.test_data.object_type, self.test_data.instance_number, self.test_data.object_name)
        
        # logout
        self._login(log_out=True)


    @data(*getTestingData())
    def test01_setmultiplevalue_wsref(self, test_data):
        
        self.test_data = test_data
        if test_data.object_type == 'PG':
            self._testMethodDoc = "Request 'wsbac/putpropertyvalues' for '%s' without ESignature will be blocked if feature is enabled"%test_data.getObjRef()
        else:
            self._testMethodDoc = "Request 'wsref/setmultiplevalue' for '%s' without ESignature will be blocked if feature is enabled"%test_data.getObjRef()
        
        # create testing BACnet object
        self._wsbac_createobject(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.object_name)
        
        # enable ESignature feature
        self._enable_esignature()
        
        # send POST request
        if test_data.object_type == 'PG':
            self._wsbac_putpropertyvalues(test_data)
        else:
            self._wsref_setmultiplevalue(test_data)
        
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
        response_content = self.r.content
        result = "QERR_CODE_NEEDS_SIGNATURE" in response_content
        self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
        
        # verify Object property not being changed
        self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
        response_content = self.r.content
        result = ('status="OK"' in response_content) and ('value="%s"'%test_data.property_value_verify not in response_content)
        self.assertTrue(result, "Verify object property not being changed failed. Respond content '%s' is not expected"%response_content)
        
        
    @data(*getTestingData())   
    def test02_setmultiplevalue_wsref(self, test_data):
        
        self.test_data = test_data
        if test_data.object_type == "PG":
            self._testMethodDoc = "Request 'wsbac//putpropertyvalues' for '%s' with invalid ESignature will be blocked if feature is enabled"%test_data.getObjRef()
        else:
            self._testMethodDoc = "Request 'wsref//setmultiplevalue' for '%s' with invalid ESignature will be blocked if feature is enabled"%test_data.getObjRef()
        
        # create testing BACnet object
        self._wsbac_createobject(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.object_name)
                
        # enable ESignature feature
        self._enable_esignature()
        
        # send POST request
        if test_data.object_type == 'PG':
            self._wsbac_putpropertyvalues(test_data, self.password)
        else:
            self._wsref_setmultiplevalue(test_data, self.password)
        
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
        response_content = self.r.content
        result = "QERR_CODE_INVALID_SIGNATURE" in response_content
        self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
        
        # verify Object property not being changed
        self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
        response_content = self.r.content
        result = ('status="OK"' in response_content) and ('value="%s"'%test_data.property_value_verify not in response_content)
        self.assertTrue(result, "Verify object property not being changed failed. Respond content '%s' is not expected"%response_content)
        
    
    @data(*getTestingData())
    def test03_setmultiplevalue_wsref(self, test_data):
        
        self.test_data = test_data
        if test_data.object_type == 'PG':
            self._testMethodDoc = "Request 'wsbac//putpropertyvalues' for '%s' with valid ESignature will get through if feature is enabled"%test_data.getObjRef()
        else:
            self._testMethodDoc = "Request 'wsref//setmultiplevalue' for '%s' with valid ESignature will get through if feature is enabled"%test_data.getObjRef()
        
        # create testing BACnet object
        self._wsbac_createobject(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.object_name)
        
        # enable ESignature feature
        self._enable_esignature()
        
        # send POST request
        password_base64 = base64.b64encode(self.password)
        if test_data.object_type == 'PG':
            self._wsbac_putpropertyvalues(test_data, password_base64)
        else:
            self._wsref_setmultiplevalue(test_data, password_base64)
        
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
        response_content = self.r.content
        result = 'status="OK"' in response_content
        if test_data.object_type == 'PG':
            result = '"status":"OK"' in response_content
        self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
        
        # verify Object property get changed
        self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
        response_content = self.r.content
        result = ('status="OK"' in response_content) and ('value="%s"'%test_data.property_value_verify in response_content)
        self.assertTrue(result, "Verify object property get changed failed. Respond content '%s' is not expected"%response_content)
        
        
        
    @data(*getTestingData())  
    def test04_setmultiplevalue_wsref(self, test_data):
        
        self.test_data = test_data
        if test_data.object_type == 'PG':
            self._testMethodDoc = "Request 'wsbac//putpropertyvalues' for '%s' without ESignature will get through if feature is disabled"%test_data.getObjRef()
        else:
            self._testMethodDoc = "Request 'wsref//setmultiplevalue' for '%s' without ESignature will get through if feature is disabled"%test_data.getObjRef()
        
        # create testing BACnet object
        self._wsbac_createobject(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.object_name)
        
        # send POST request
        if test_data.object_type == 'PG':
            self._wsbac_putpropertyvalues(test_data)
        else:
            self._wsref_setmultiplevalue(test_data)
        
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
        response_content = self.r.content
        result = 'status="OK"' in response_content
        if test_data.object_type == 'PG':
            result = '"status":"OK"' in response_content
        self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
        
        # verify Object property get changed
        self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
        response_content = self.r.content
        result = ('status="OK"' in response_content) and ('value="%s"'%test_data.property_value_verify in response_content)
        self.assertTrue(result, "Verify object property get changed failed. Respond content '%s' is not expected"%response_content)
    
    
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
        
        
    def _wsref_setmultiplevalue(self, parameters, esignature=None):
        """ create an object on target device """
        url = "%s/wsref/setmultiplevalue"%self.base_url
        payload = {"value"       : parameters.property_value,
                   "property"    : parameters.property_name,
                   "ObjRef"      : '["%s"]'%parameters.getObjRef(),
                   "_csrfToken"  : self.csrf_token}
        if esignature is not None:
            payload["esignature_password"] = esignature
            
        self.r = self._post_request(url, payload)
        
        
    def _wsbac_putpropertyvalues(self, parameters, esignature=None):
        url = "%s/wsbac/putpropertyvalues"%self.base_url
        obj_ref = "%s.%s"%(parameters.getObjRef(), parameters.property_name)
        payload = {"value"       : parameters.property_value,
                   "ObjRef"      : '["%s"]'%obj_ref,
                   "format"      : "JSON",
                   "_csrfToken"  : self.csrf_token}
        if esignature is not None:
            payload["esignature_password"] = esignature
            
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
