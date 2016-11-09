'''
Created on Jun 11, 2013

@author: hwang
'''
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from Enteliweb.libenteliwebReporting.PageObjects import  selenium_server_connection
from Enteliweb.libenteliwebReporting.locators import Locators
from Enteliweb.libenteliwebReporting.PageObjects.BaseWebElement import BaseWebElement, HyperLinkWebElement, TextBoxWebElement, EditBoxWebElement, DropDownBoxWebElement, ButtonWebElement

class BasePageObject(object):
    """ Model a base web page"""
    
    def __init__(self):
        self.driver = selenium_server_connection.connection
    
    def __repr__(self):
        super(BasePageObject, self).__repr__()
        
    def click(self, webElement):
        """ mouse click the target web element """
        webElement.click()
        
    def focus(self):
        """ focus on current web page """
        self.driver.switch_to.default_content()
        #self.driver.switch_to_frame("mainFrame")
        print("debug: switch back to default")
    
    def locate(self, locatorString):
        """ locate and return a wrapped web element on web page"""
        elem = None
        locators = Locators()
        locator = locators.get(locatorString)
        elemType = locator["type"]
        if elemType == "TextBox":
            elem = TextBoxWebElement(locatorString)
        elif elemType == "EditBox":
            elem = EditBoxWebElement(locatorString)
        elif elemType == "DropDownBox":
            elem = DropDownBoxWebElement(locatorString)
        elif elemType == "HyperLink":
            elem = HyperLinkWebElement(locatorString)
        elif elemType == "Button":
            elem = ButtonWebElement(locatorString)
        else:
            elem = BaseWebElement(locatorString)
        return elem
    
    def select(self, webElement):
        """ mouse click the target web element  """
        webElement.click()
    
    def mouseHoverUp(self, webElement):
        """ simulate a mouse hover over the target web element"""
        driver = self.driver
        elem = webElement.getElement(webElement.locator)
        elem.location_once_scrolled_into_view
        hov = ActionChains(driver).move_to_element(elem)
        hov.perform()
        
    def getContent(self, webElement):
        """
        return the content of webelement
        """
        return webElement.__str__()
        
        
class BaseFrameObject(BasePageObject):
    """ Model a base web iFrame """
    
    def __repr__(self):
        super(BaseFrameObject, self).__repr__()
        
    def focus(self):
        """ focus on current web page """
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame("mainFrame")
        print("debug: switch to frame mainFrame")
        
    
    def loading(self, timeout):
        """
        wait for page loading in main frame
        """
        self.focus()
        locator = self.headerTitle.locator
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.ID, locator["value"])))
        except TimeoutException:
            raise Exception("%s is not finish loading within %s seconds"%(self, timeout))
    
    
    def isLoaded(self):
        """
        verify if the frame is loaded successfully
        """
        if self.headerTitle.isDisplayed():
            titleCurrent = self.headerTitle.__str__()
            titleExpected = self.titleExpected
            result = titleExpected in titleCurrent
            return result
        else:
            return False
    
    
    def getDropDownListContent(self, webElement):
        """ return a list of available items from the target DropDownBox web element """
        result = webElement.getListContent()
        webElement.click()    # click to close the dropdown list
        return result
        
    
    
        