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
JSON_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "block_putproperty_wsbac_request.json"))


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
        if self.test_data.object_type != 'DEV':
            self._wsbac_deleteobject(self.test_data.site, self.test_data.device_number, self.test_data.object_type, self.test_data.instance_number, self.test_data.object_name)
            
        # logout
        self._login(log_out=True)    


    @data(*getTestingData())
    def test01_putpropety_wsbac(self, test_data):
        
        self.test_data = test_data
        self._testMethodDoc = "Request 'wsbac/putproperty' for '%s' without ESignature will be blocked if feature is enabled"%test_data.getObjRef()
        
        if test_data.object_type == "DEV":
            self._test_DEV(test_data)
        elif test_data.object_type == "PI":
            self._test_PI(test_data)
        elif test_data.object_type == "LO":
            self._test_LO(test_data)
        elif test_data.object_type == "SCH":
            self._test_SCH(test_data)
        
        
    @data(*getTestingData())   
    def test02_putpropety_wsbac(self, test_data):
        
        self.test_data = test_data
        self._testMethodDoc = "Request 'wsbac//putproperty' for %s with invalid ESignature will be blocked if feature is enabled"%test_data.getObjRef()
        
        if test_data.object_type == "DEV":
            self._test_DEV(test_data)
        elif test_data.object_type == "PI":
            self._test_PI(test_data)
        elif test_data.object_type == "LO":
            self._test_LO(test_data)
        elif test_data.object_type == "SCH":
            self._test_SCH(test_data)
        
    
    @data(*getTestingData())
    def test03_putpropety_wsbac(self, test_data):
        
        self.test_data = test_data
        self._testMethodDoc = "Request 'wsbac//putproperty' for %s with valid ESignature will get through if feature is enabled"%test_data.getObjRef()
        
        if test_data.object_type == "DEV":
            self._test_DEV(test_data)
        elif test_data.object_type == "PI":
            self._test_PI(test_data)
        elif test_data.object_type == "LO":
            self._test_LO(test_data)
        elif test_data.object_type == "SCH":
            self._test_SCH(test_data)
        
        
    @data(*getTestingData())  
    def test04_putpropety_wsbac(self, test_data):
        
        self.test_data = test_data
        self._testMethodDoc = "Request 'wsbac//putproperty' for %s without ESignature will get through if feature is disabled"%test_data.getObjRef()
        
        if test_data.object_type == "DEV":
            self._test_DEV(test_data)
        elif test_data.object_type == "PI":
            self._test_PI(test_data)
        elif test_data.object_type == "LO":
            self._test_LO(test_data)
        elif test_data.object_type == "SCH":
            self._test_SCH(test_data)
        
        
    def _test_SCH(self, test_data):
        
        value_new     =    ('<PropertyList>'
                              '<Object ref="//$LocalSite/1300.SCH220">'
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
        
        value_old     =    ('<PropertyList>'
                              '<Object ref="//$LocalSite/1300.SCH220">'
                                '<Array name="Weekly_Schedule">'
                                  '<Group name="Weekly_Schedule" arrayIndex="1"><List name="day-schedule"></List></Group>'
                                  '<Group name="Weekly_Schedule" arrayIndex="2"><List name="day-schedule"></List></Group>'
                                  '<Group name="Weekly_Schedule" arrayIndex="3"><List name="day-schedule"></List></Group>'
                                  '<Group name="Weekly_Schedule" arrayIndex="4"><List name="day-schedule"></List></Group>'
                                  '<Group name="Weekly_Schedule" arrayIndex="5"><List name="day-schedule"></List></Group>'
                                  '<Group name="Weekly_Schedule" arrayIndex="6"><List name="day-schedule"></List></Group>'
                                  '<Group name="Weekly_Schedule" arrayIndex="7"><List name="day-schedule"></List></Group>'
                                '</Array>'
                              '</Object>'
                            '</PropertyList>')
        
        # create testing BACnet object
        self._wsbac_createobject(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.object_name)
        
        if "test01" in self._testMethodDoc:
            
            # enable ESignature feature
            self._enable_esignature()
        
            # send POST request
            test_data.property_value = value_new
            self._wsbac_putproperty(test_data)
        
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
            response_content = self.r.content
            result = "QERR_CODE_NEEDS_SIGNATURE" in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
            
            # verify Object property not being changed
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            self.assertEqual(response_content, value_old, "Verify object property not being changed failed")
        
        elif "test02" in self._testMethodDoc:
            
            # enable ESignature feature
            self._enable_esignature()
        
            # send POST request
            test_data.property_value = value_new
            self._wsbac_putproperty(test_data, self.password)
        
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
            response_content = self.r.content
            result = "QERR_CODE_INVALID_SIGNATURE" in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
            
            # verify Object property not being changed
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            self.assertEqual(response_content, value_old, "Verify object property not being changed failed")
        
        elif "test03" in self._testMethodDoc:
            
            # enable ESignature feature
            self._enable_esignature()
        
            # send POST request
            password_base64 = base64.b64encode(self.password)
            test_data.property_value = value_new
            self._wsbac_putproperty(test_data, password_base64)
        
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
            response_content = self.r.content
            result = 'status="OK"' in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
            
            # verify Object property get changed
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            self.assertEqual(response_content, value_new, "Verify object property get changed failed")
        
        elif "test04" in self._testMethodDoc:
            
            # send POST request
            test_data.property_value = value_new
            self._wsbac_putproperty(test_data)
        
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
            response_content = self.r.content
            result = 'status="OK"' in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
        
            # verify Object property get changed
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            self.assertEqual(response_content, value_new, "Verify object property get changed failed")
            
    
    def _test_LO(self, test_data):
        
        # create testing BACnet object
        self._wsbac_createobject(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.object_name)
        
        if "test01" in self._testMethodName:
            
            # enable ESignature feature
            self._enable_esignature()
        
            # send POST request
            self._wsbac_putproperty(test_data)
        
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
            response_content = self.r.content
            result = "QERR_CODE_NEEDS_SIGNATURE" in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
            
            # verify Object property not being changed
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            result = ('status="OK"' in response_content) and ('value="0"' in response_content)
            self.assertTrue(result, "Verify object property not being changed failed. Respond content '%s' is not expected"%response_content)
            
        elif "test02" in self._testMethodName:
            
            # enable ESignature feature
            self._enable_esignature()
        
            # send POST request
            self._wsbac_putproperty(test_data, self.password)
        
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
            response_content = self.r.content
            result = "QERR_CODE_INVALID_SIGNATURE" in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
            
            # verify Object property not being changed
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            result = ('status="OK"' in response_content) and ('value="0"' in response_content)
            self.assertTrue(result, "Verify object property not being changed failed. Respond content '%s' is not expected"%response_content)
        
        elif "test03" in self._testMethodName:
            
            # enable ESignature feature
            self._enable_esignature()
        
            # send POST request
            password_base64 = base64.b64encode(self.password)
            self._wsbac_putproperty(test_data, password_base64)
        
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
            response_content = self.r.content
            result = 'status="OK"' in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
            
            # verify Object property get changed
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            value_after_test = self._fetch_property_value(response_content)
            result = int(value_after_test) > 0
            self.assertTrue(result, "Verify object property get changed failed.")
        
        elif "test04" in self._testMethodName:
            
            # send POST request
            self._wsbac_putproperty(test_data)
        
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
            response_content = self.r.content
            result = 'status="OK"' in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
        
            # verify Object property get changed
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            value_after_test = self._fetch_property_value(response_content)
            result = int(value_after_test) > 0
            self.assertTrue(result, "Verify object property get changed failed.")
    
    
    def _test_PI(self, test_data):
        
        # create testing BACnet object
        self._wsbac_createobject(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.object_name)
        
        # obtain current value of PI.Last_Reset
        self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
        response_content = self.r.content
        value_before_test = self._fetch_property_value(response_content)
        #print "Before test, PI.Last_Reset = %s"%value_before_test
        
        if "test01" in self._testMethodName:
            
            # enable ESignature feature
            self._enable_esignature()
        
            # send POST request
            self._wsbac_putproperty(test_data)
        
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
            response_content = self.r.content
            result = "QERR_CODE_NEEDS_SIGNATURE" in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
            
            # verify Object property not being changed
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            result = ('status="OK"' in response_content) and ('value="%s"'%value_before_test in response_content)
            self.assertTrue(result, "Verify object property not being changed failed. Respond content '%s' is not expected"%response_content)
            
        elif "test02" in self._testMethodName:
            
            # enable ESignature feature
            self._enable_esignature()
        
            # send POST request
            self._wsbac_putproperty(test_data, self.password)
        
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
            response_content = self.r.content
            result = "QERR_CODE_INVALID_SIGNATURE" in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
            
            # verify Object property not being changed
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            result = ('status="OK"' in response_content) and ('value="%s"'%value_before_test in response_content)
            self.assertTrue(result, "Verify object property not being changed failed. Respond content '%s' is not expected"%response_content)
            
        elif "test03" in self._testMethodName:
            
            time.sleep(1)
            
            # enable ESignature feature
            self._enable_esignature()
        
            # send POST request
            password_base64 = base64.b64encode(self.password)
            self._wsbac_putproperty(test_data, password_base64)
        
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
            response_content = self.r.content
            result = 'status="OK"' in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
            
            # verify Object property get changed
            time.sleep(3)
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            value_after_test = self._fetch_property_value(response_content)
            self.assertNotEqual(value_before_test, value_after_test, "Verify object property get changed failed.")
        
            
        elif "test04" in self._testMethodName:
            
            time.sleep(1)
            
            # send POST request
            self._wsbac_putproperty(test_data)
        
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
            response_content = self.r.content
            result = 'status="OK"' in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
        
            # verify Object property get changed
            time.sleep(3)
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            value_after_test = self._fetch_property_value(response_content)
            self.assertNotEqual(value_before_test, value_after_test, "Verify object property get changed failed.")
    
    
    def _test_DEV(self, test_data):
        
        # obtain current value of DEV.Time_Sync_Timer
        self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
        response_content = self.r.content
        value_before_test = self._fetch_property_value(response_content)
        #print "Before test, DEV.Time_Sync_Timer = %s"%value_before_test
        
        if "test01" in self._testMethodName:
            
            # enable ESignature feature
            self._enable_esignature()
            
            # send POST request
            self._wsbac_putproperty(test_data)
            
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
            response_content = self.r.content
            result = "QERR_CODE_NEEDS_SIGNATURE" in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
            
            # verify Object property not being changed
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            value_after_test = self._fetch_property_value(response_content)
            result = int(value_before_test) >= int(value_after_test)
            self.assertTrue(result, "Verify object property not being changed failed")
        
        elif "test02" in self._testMethodName:
            
            # enable ESignature feature
            self._enable_esignature()
            
            # send POST request
            self._wsbac_putproperty(test_data, self.password)
            
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 403, "Expect request return HTTP code 403 failed")
        
            response_content = self.r.content
            result = "QERR_CODE_INVALID_SIGNATURE" in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
            
            # verify Object property not being changed
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            value_after_test = self._fetch_property_value(response_content)
            result = int(value_before_test) >= int(value_after_test)
            self.assertTrue(result, "Verify object property not being changed failed")
        
        elif "test03" in self._testMethodName:
            
            # enable ESignature feature
            self._enable_esignature()
            
            # send POST request
            password_base64 = base64.b64encode(self.password)
            self._wsbac_putproperty(test_data, password_base64)
            
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
            response_content = self.r.content
            result = 'status="OK"' in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
            
            # verify Object property get changed
            time.sleep(5)
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            value_after_test = self._fetch_property_value(response_content)
            #print "After test, DEV.Time_Sync_Timer = %s"%value_after_test
            result = int(value_before_test) < int(value_after_test)
            self.assertTrue(result, "Verify object property being changed failed")
        
        elif "test04" in self._testMethodName:
            
            # send POST request
            self._wsbac_putproperty(test_data)
            
            # verify response
            result = self.r.status_code
            self.assertEqual(result, 200, "Expect request return HTTP code 200 failed")
        
            response_content = self.r.content
            result = 'status="OK"' in response_content
            self.assertTrue(result, "Respond content '%s' is not expected"%response_content)
            
            # verify Object property get changed
            time.sleep(5)
            self._wsbac_getproperty(test_data.site, test_data.device_number, test_data.object_type, test_data.instance_number, test_data.property_name_verify)
            response_content = self.r.content
            value_after_test = self._fetch_property_value(response_content)
            #print "After test, DEV.Time_Sync_Timer = %s"%value_after_test
            result = int(value_before_test) < int(value_after_test)
            self.assertTrue(result, "Verify object property being changed failed")
            
    
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
        
        
    def _wsbac_putproperty(self, parameters, esignature=None):
        """ create an object on target device """
        
        url = "%s/wsbac/putproperty"%self.base_url
        
        self._wsbac_getproperty(parameters.site, parameters.device_number, parameters.object_type, parameters.instance_number, parameters.property_name)
        old_xml_string = self.r.content
        new_xml_string = self._compose_xml(old_xml_string, parameters.property_value)
        
        payload = {"format"      : "TEXT",
                   "xmlstr"      : new_xml_string,
                   "oldxml"      : old_xml_string,
                   "logcomment"  : "",
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
