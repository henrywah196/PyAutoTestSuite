'''
Created on Dec 7, 2016

@author: hwang
'''
import settings
import requests

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
        
    def getNumberOfObjects(self, siteName, deviceNumber):
        """ return the total number of objects in a device """
        url = "%s/wsbac/getproperty?ObjRef=//%s/%s.DEV%s.Object_List[0]"%(self.base_url, siteName, deviceNumber, deviceNumber)
        self.r = requests.get(url, cookies=self.cookie)
        
    def getObjectsList(self, siteName, deviceNumber):
        """ return a list of objects in a device """
        numberOfObjects = self.getNumberOfObjects(siteName, deviceNumber)
        url = "%s/api/.bacnet/%s/%s?max-results=%s"%(self.base_url, siteName, deviceNumber, numberOfObjects)
        self.r = requests.get(url, cookies=self.cookie)
    
