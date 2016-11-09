'''
Created on Jun 11, 2013

@author: hwang
'''
import unittest
from selenium.webdriver.common.action_chains import ActionChains
from libraries.SLAT.OnlineConfigurator import locators
from basewebelement import *


class BasePageObject(unittest.TestCase):
    """ Model a base web page"""
    def __repr__(self):
        super(BasePageObject, self).__repr__()
        
    def click(self, webElement):
        """ mouse click the target web element """
        webElement.click()
        
    def focus(self):
        """ focus on current web page """
        self.driver.switch_to_default_content()
        #self.driver.switch_to_frame("mainFrame")
        print "debug: switch back to default"
    
    def locate(self, locatorString):
        """ locate and return a wrapped web element on web page"""
        elem = None
        locator = locators[locatorString]
        elemType = locator["type"]
        if elemType == "TextBox":
            elem = TextBox(locator)
        if elemType == "EditBox":
            elem = EditBox(locator)
        if elemType == "DropDownBox":
            elem = DropDownBox(locator)
        if elemType == "HyperLink":
            elem = HyperLink(locator)
        if elemType == "Button":
            elem = HyperLink(locator)
        return elem
    
    def mouseHoverUp(self, webElement):
        """ simulate a mouse hover over the target web element"""
        driver = self.driver
        elem = webElement.getElement(webElement.locator)
        elem.location_once_scrolled_into_view
        hov = ActionChains(driver).move_to_element(elem)
        hov.perform()
        
    
    
        
