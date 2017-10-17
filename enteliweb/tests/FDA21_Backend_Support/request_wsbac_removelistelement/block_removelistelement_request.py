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
            
        def getObjRef(self):
            return "//%s/%s.%s%s"%(self.site, self.device_number, self.object_type, self.instance_number)
            
    myTestData = TestData()
    myTestData.object_type = "SEL"
    myTestData.site = "$LocalSite"
    myTestData.device_number = "2100" 
    myTestData.instance_number = "1" 
        
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
        
        # item to be deleted
        self.item_to_be_deleted = (self._wsobjdlg_selreadrangebyindex(self.test_data.getObjRef(), count=5))["rows"][0]
            

    def tearDown(self):
        super(TestCase, self).tearDown()
        
        # logout
        self._login(log_out=True)


    def test01_removelistelement_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac/removelistelement' for '%s' without ESignature will be blocked if feature is enabled with optional comment"%test_data.getObjRef()
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as option
        self._disable_comment()
        
        # send POST request
        self._wsbac_removelistelement(test_data.getObjRef(), self.item_to_be_deleted)
        
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
        response_content = self.r.content
        result = "QERR_CODE_NEEDS_SIGNATURE" in response_content
        self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
        
        # verify item not being deleted
        item_to_be_verified = (self._wsobjdlg_selreadrangebyindex(self.test_data.getObjRef(), count=5))["rows"][0]
            
        self.assertDictEqual(item_to_be_verified, self.item_to_be_deleted, "Verify item not being deleted failed")
        
        
    def test02_removelistelement_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac/removelistelement' for '%s' without ESignature will be blocked if feature is enabled with mandatory comment"%test_data.getObjRef()
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as mandatory
        self._enable_comment()
        
        # send POST request
        self._wsbac_removelistelement(test_data.getObjRef(), self.item_to_be_deleted)
        
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
        response_content = self.r.content
        result = "QERR_CODE_NEEDS_SIGNATURE" in response_content
        self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
        
        # verify item not being deleted
        item_to_be_verified = (self._wsobjdlg_selreadrangebyindex(self.test_data.getObjRef(), count=5))["rows"][0]
            
        self.assertDictEqual(item_to_be_verified, self.item_to_be_deleted, "Verify item not being deleted failed")
        
    
    def test03_removelistelement_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac//removelistelement' for '%s' with invalid ESignature will be blocked if feature is enabled with optional comment"%test_data.getObjRef()
                
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as option
        self._disable_comment()
        
        # send POST request
        self._wsbac_removelistelement(test_data.getObjRef(), self.item_to_be_deleted, self.password)
        
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
        response_content = self.r.content
        result = "QERR_CODE_INVALID_USER_CREDENTIALS" in response_content
        self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
        
        # verify item not being deleted
        item_to_be_verified = (self._wsobjdlg_selreadrangebyindex(self.test_data.getObjRef(), count=5))["rows"][0]
            
        self.assertDictEqual(item_to_be_verified, self.item_to_be_deleted, "Verify item not being deleted failed")
        
        
    def test04_removelistelement_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac//removelistelement' for '%s' with invalid ESignature will be blocked if feature is enabled with mandatory comment"%test_data.getObjRef()
                
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as mandatory
        self._enable_comment()
        
        # send POST request
        self._wsbac_removelistelement(test_data.getObjRef(), self.item_to_be_deleted, self.password, "esign message")
        
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
        response_content = self.r.content
        result = "QERR_CODE_INVALID_USER_CREDENTIALS" in response_content
        self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
        
        # verify item not being deleted
        item_to_be_verified = (self._wsobjdlg_selreadrangebyindex(self.test_data.getObjRef(), count=5))["rows"][0]
            
        self.assertDictEqual(item_to_be_verified, self.item_to_be_deleted, "Verify item not being deleted failed")
        
    
    def test05_removelistelement_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac//removelistelement' for '%s' with valid ESignature will get through if feature is enabled with optional comment"%test_data.getObjRef()
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as option
        self._disable_comment()
        
        # send POST request
        password_base64 = base64.b64encode(self.password)
        self._wsbac_removelistelement(test_data.getObjRef(), self.item_to_be_deleted, password_base64)
        
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
        response_content = self.r.content
        result = '<Group name="Log_Buffer" status="OK" dataType="Group">' in response_content
        self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
        
        # verify item being deleted
        item_to_be_verified = (self._wsobjdlg_selreadrangebyindex(self.test_data.getObjRef(), count=5))["rows"][0]
            
        self.assertNotEqual(item_to_be_verified, self.item_to_be_deleted, "Verify item being deleted failed")
        
        
    def test06_removelistelement_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac//removelistelement' for '%s' with valid ESignature and comment will get through if feature is enabled with mandatory comment"%test_data.getObjRef()
        
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as option
        self._enable_comment()
        
        # send POST request
        password_base64 = base64.b64encode(self.password)
        self._wsbac_removelistelement(test_data.getObjRef(), self.item_to_be_deleted, password_base64, "esign message")
        
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
        response_content = self.r.content
        result = '<Group name="Log_Buffer" status="OK" dataType="Group">' in response_content
        self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
        
        # verify item being deleted
        item_to_be_verified = (self._wsobjdlg_selreadrangebyindex(self.test_data.getObjRef(), count=5))["rows"][0]
            
        self.assertNotEqual(item_to_be_verified, self.item_to_be_deleted, "Verify item being deleted failed")
    
        
    def test07_removelistelement_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac//removelistelement' for '%s' with valid ESignature but no comment will be blocked if feature is enabled with mandatory comment"%test_data.getObjRef()
                
        # enable ESignature feature
        self._enable_esignature()
        
        # set comment as mandatory
        self._enable_comment()
        
        # send POST request
        password_base64 = base64.b64encode(self.password)
        self._wsbac_removelistelement(test_data.getObjRef(), self.item_to_be_deleted, password_base64, "")
        
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
        response_content = self.r.content
        result = "QERR_CODE_INVALID_COMMENT" in response_content
        self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
        
        # verify item not being deleted
        item_to_be_verified = (self._wsobjdlg_selreadrangebyindex(self.test_data.getObjRef(), count=5))["rows"][0]
            
        self.assertDictEqual(item_to_be_verified, self.item_to_be_deleted, "Verify item not being deleted failed")
        
    
    def test08_removelistelement_wsbac(self):
        
        test_data = self.test_data
        self._testMethodDoc = "Request 'wsbac//removelistelement' for '%s' without ESignature will get through if feature is disabled"%test_data.getObjRef()
        
        # send POST request
        self._wsbac_removelistelement(test_data.getObjRef(), self.item_to_be_deleted)
        
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
        response_content = self.r.content
        result = '<Group name="Log_Buffer" status="OK" dataType="Group">' in response_content
        self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
        
        # verify item being deleted
        item_to_be_verified = (self._wsobjdlg_selreadrangebyindex(self.test_data.getObjRef(), count=5))["rows"][0]
            
        self.assertNotEqual(item_to_be_verified, self.item_to_be_deleted, "Verify item being deleted failed")
    
    
    def _wsobjdlg_selreadrangebyindex(self, obj_ref, count=10):
        
        url = "%s/wsobjdlg/selreadrangebyindex"%self.base_url
        payload = {"Format"      : "JSON",
                   "ObjRef"      : obj_ref,
                   "Index"       : "1",
                   "Count"       : str(count),
                   "_csrfToken"  : self.csrf_token}
            
        self.r = self._post_request(url, payload)
        
        if self.r.status_code != 200:
            raise Exception("Request 'wsobjdlg/selreadrangebyindex' for '%s' return unexpected result"%obj_ref)
        
        json_data = json.loads(self.r.text)
        
        return json_data
    
    def _wsbac_removelistelement(self, obj_ref, item_dic, esignature=None, comment=None):
        
        xml_string  =    ('<PropertyList>'
                            '<Object ref="%s">'
                              '<List name="Log_Buffer">'
                                '<Group name="Log_Buffer" status="OK" dataType="Group">'
                                  '<Property name="Event_Time" dataType="Time Date" value="%s"></Property>'
                                  '<Property name="Event_Type" dataType="Enumeration" value="%s"></Property>'
                                  '<Property name="Event_Source" dataType="Enumeration" value="%s"></Property>'
                                  '<Property name="Event_Reference" dataType="Object Id" value="%s"></Property>'
                                  '<Property name="Occurence_Count" dataType="Unsigned" value="%s"></Property>'
                                  '<Property name="Sequence_Number" dataType="Unsigned" value="%s"></Property>'
                                  '<Property name="Message" dataType="Text" value="%s"></Property>'
                                '</Group>'
                              '</List>'
                            '</Object>'
                          '</PropertyList>')
        
        event_time = item_dic["Event_Time"]
        event_type = item_dic["Event_Type"]
        event_source = item_dic["Event_Source"]
        event_reference = item_dic["Event_Reference"]
        occurence_count = item_dic["Occurence_Count"]
        sequence_number = item_dic["Sequence_Number"]
        message = item_dic["Message"]
        
        xml_string = xml_string%(obj_ref,event_time,event_type,event_source,event_reference,occurence_count,sequence_number,message)
        
        url = "%s/wsbac/removelistelement"%self.base_url
        
        payload = {"xmlstr"      : xml_string,
                   "_csrfToken"  : self.csrf_token}
        if esignature is not None:
            payload["esignature_password"] = esignature
        if comment is not None:
            payload["esignature_comment"] = comment
            
        self.r = self._post_request(url, payload)
        
        #if self.r.status_code != 200:
        #    raise Exception("request 'wsbac/removelistelement' for '%s' return unexpected result"%obj_ref)
        
        
    
    
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
