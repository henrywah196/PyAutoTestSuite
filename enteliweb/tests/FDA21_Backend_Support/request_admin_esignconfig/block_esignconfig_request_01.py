# coding: utf-8
################################################################################################
# Test Case   : 
#
# Description : change config from esign: true, comment: false to esign: false, comment: false
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
        
        # enable ESignature feature
        self._enable_esignature()
        
        # disable comment
        self._disable_comment()
            

    def tearDown(self):
        super(TestCase, self).tearDown()
        
        # disable ESignature feature
        self._disable_esignature()
        
        # logout
        self._login(log_out=True)


    def test01_esignconfig_admin(self):
        
        self._testMethodDoc = "Request 'admin/esignconfig' to disable esignature without ESignature password"
        
        # send POST request
        self._admin_esignconfig()
        
        # verify response
        self._verify_request_blocked()
        
        # verify esign configure setting not changed
        self._verify_state_not_changed()
        
        
    def test02_esignconfig_admin(self):
        
        self._testMethodDoc = "Request 'admin/esignconfig' to disable esignature with incorrect ESignature password"
        
        # send POST request
        self._admin_esignconfig(self.password)
        
        # verify response
        self._verify_request_blocked(signature_flag=2)
        
        # verify esign config not changed
        self._verify_state_not_changed()
    
       
    def test03_esignconfig_admin(self):
        
        self._testMethodDoc = "Request 'admin/esignconfig' to disable esignature with correct ESignature password"
        
        # send POST request
        password_base64 = base64.b64encode(self.password)
        self._admin_esignconfig(password_base64)
        
        # verify response
        self._verify_request_getthrough()
        
        # verify esign config changed
        self._verify_state_changed
    
        
    def _verify_state_changed(self):
        self.webgroup.cnxn.commit()
        cursor = self.webgroup.cursor.execute("select Name, Value from settings_global where type = 'ESignature'")
        rows = cursor.fetchall()
        for row in rows:
            name = row.Name
            value = row.Value
            self.assertEqual(value, '0', "verify  '%s' setting is changed to 0 failed"%name)
    
    
    def _verify_state_not_changed(self):
        self.webgroup.cnxn.commit()
        cursor = self.webgroup.cursor.execute("select Name, Value from settings_global where type = 'ESignature'")
        rows = cursor.fetchall()
        for row in rows:
            name = row.Name
            value = row.Value
            if name == "ElectronicSignature":
                self.assertEqual(value, '1', "verify  '%s' setting is still 1 failed"%name)
            elif name == "ElectronicSignatureComment":
                self.assertEqual(value, '0', "verify  '%s' setting is still 0 failed"%name)
        
        
    def _verify_request_getthrough(self):
        # verify response
        result = self.r.status_code
        self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
        response_content = self.r.content
        result = '"status":"OK"' in response_content
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
        
        
    def _admin_esignconfig(self, esignature=None, comment=None):
        """ create an object on target device """
        url = "%s/admin/esignconfig"%self.base_url
        payload = {"esign"      : 'false',
                   "commentReq" : 'false',
                   "btnSubmit"  : 'saveBtn',
                   "_csrfToken"  : self.csrf_token}
        if esignature is not None:
            payload["esignature_password"] = esignature
        if comment is not None:
            payload["esignature_comment"] = comment
            
        self.r = self._post_request(url, payload)
    
    
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
