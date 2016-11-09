'''
Created on Jun 18, 2014

@author: User
'''
from libraries.SLAT.ActivationServer import webdriver_connection
from LoginPageObj import *
from HomePageObj import *
from LicFilePageObj import *
from ModulePageObj import *
import time

class ActivationServer():
    ''' class to model internal Activation Server UI '''
    
    def __init__(self, url=None):  
        self.browser = 'FIREFOX'
        self.base_url = 'http://192.168.50.99/lpweb/'
        if url:
            self.base_url = url
        self.driver = None
        
        self.loginPage = LoginPage(self.driver)
        self.homePage = HomePage(self.driver)
        self.licFilePage = LicFilePage(self.driver)
        self.modulePage = ModulePage(self.driver)
        
        
    def launch(self):
        ''' load activation server page '''
        self.driver = webdriver_connection.connect(self.base_url, self.browser)
        time.sleep(3)
        
    def close(self):
        ''' close Activation server UI '''
        if self.driver:
            self.driver = None
            webdriver_connection.stop()
            time.sleep(3)
