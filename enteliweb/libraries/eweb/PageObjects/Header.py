'''
Created on Jun 11, 2013

@author: hwang
'''
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from BasePageObject import BasePageObject
from BaseWebElement import HyperLinkWebElement, TextBoxWebElement
import time


class AdminLinkElement(HyperLinkWebElement):
    def __init__(self):
        super(AdminLinkElement, self).__init__("main.administration")
        
    def __str__(self, obj, objtype=None):
        """override, get the image file
        """
        elem = self.getElement(self.locator)
        elem = elem.find_element_by_tag_name("img")
        return elem.get_attribute("src")

class HeaderPageObj(BasePageObject):
    """ model enteliweb main page header """
    
    welcomeString = TextBoxWebElement("main.welcome")
    settings = HyperLinkWebElement("main.settings")
    logout = HyperLinkWebElement("main.logout")
    adminlink = AdminLinkElement()
    helplink = HyperLinkWebElement("main.help")
    
    def __init__(self):
        super(HeaderPageObj, self).__init__()
        self.focus()
        
    def __repr__(self):
        super(HeaderPageObj, self).__repr__()
        
    def __str__(self):
        return "enteliWEB Main Page Header"
    
    def loading(self, timeout):
        """
        wait for page loading
        """
        locator = self.welcomeString.locator
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.ID, locator["value"])))
        except TimeoutException:
            raise Exception("%s is not finish loading within %s seconds"%(self, timeout))
        
    def isLoaded(self):
        """
        verify the page is loaded in web browser successfully
        """
        result = True
        driver = self.driver
        titleExpected = "enteliWEB"
        titleCurrent = driver.title
        try: assert (titleExpected in titleCurrent) is True
        except AssertionError, e:
            result = False
        return result
    
        
        