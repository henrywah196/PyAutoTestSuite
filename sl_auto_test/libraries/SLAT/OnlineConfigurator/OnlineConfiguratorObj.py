'''
Created on Jan 14, 2015

@author: Henry Wang
'''
from libraries.SLAT.OnlineConfigurator import webdriver_connection
from LoginPageObj import *
from HomePageObj import *
from ConfigEWEBPageObj import *
from ConfigEBRIDGEPageObj import *
from ConfigCUCUBEPageObj import *
import time

class OnlineConfigurator():
    ''' class to model internal Online Order Configurator WEB UI '''
    
    def __init__(self, url=None):  
        self.browser = 'FIREFOX'
        self.base_url = 'http://config.deltacontrols.com/'
        if url:
            self.base_url = url
        self.driver = None
        
        self.loginPage = LoginPage()
        self.homePage = HomePage()
        self.ewebConfig = ConfigenteliWEB()
        self.ebridgeConfig = ConfigenteliBRIDGE()
        self.cucubeConfig = ConfigCopperCube()
        #self.modulePage = ModulePage(self.driver)
        
        
    def launch(self):
        ''' load activation server page '''
        self.driver = webdriver_connection.connect(self.base_url, self.browser)
        self.loginPage.driver = self.driver
        self.homePage.driver = self.driver
        self.ewebConfig.driver = self.driver
        self.ebridgeConfig.driver = self.driver
        self.cucubeConfig.driver = self.driver
        time.sleep(3)
        
    def close(self):
        ''' close this WEB UI '''
        if self.driver:
            self.driver = None
            webdriver_connection.stop()
            time.sleep(3)
