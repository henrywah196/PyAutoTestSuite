'''
Created on Jun 11, 2013

@author: hwang
'''
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from BasePageObject import BaseFrameObject
from BaseWebElement import BaseWebElement, HyperLinkWebElement
import time


class AdminFrameObj(BaseFrameObject):
    
    mainBody = BaseWebElement("admin.main_body")
    meters = HyperLinkWebElement("admin.meters")
    baseUnitConfiguration = HyperLinkWebElement("admin.base_unit_configuration")
    
    def __init__(self):
        super(AdminFrameObj, self).__init__()
        self.titleExpected = "Administration"
        self.focus()
        
    def __repr__(self):
        super(AdminFrameObj, self).__repr__()
        
    def __str__(self):
        return "Administration Page"
        
    def loading(self, timeout):
        """
        wait for page loading
        """
        self.focus()
        locator = self.mainBody.locator
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.ID, locator["value"])))
        except TimeoutException:
            raise Exception("%s is not finish loading within %s seconds"%(self, timeout))
        
    def isLoaded(self):
        """
        verify if the frame is loaded successfully
        """
        result = self.mainBody.isDisplayed()
        return result
    
        
        