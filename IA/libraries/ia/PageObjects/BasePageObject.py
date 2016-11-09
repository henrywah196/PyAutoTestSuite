'''
Created on Jun 11, 2013

@author: hwang
'''
from libraries.ia import locators
from libraries.ia.PageObjects import  selenium_server_connection
from BaseWebElement import HyperLinkWebElement, TextBoxWebElement, EditBoxWebElement, DropDownBoxWebElement, ButtonWebElement

class BasePageObject(object):
    """ Model a base web page"""
    
    def __init__(self):
        self.driver = selenium_server_connection.connection
    
    def __repr__(self):
        super(BasePageObject, self).__repr__()
        
    def click(self, webElement):
        """ mouse click the target web element """
        webElement.click()
    
    def locate(self, locatorString):
        """ locate and return a wrapped web element on web page"""
        elem = None
        locator = locators[locatorString]
        elemType = locator["type"]
        if elemType == "TextBox":
            elem = TextBoxWebElement(locator)
        elif elemType == "EditBox":
            elem = EditBoxWebElement(locator)
        elif elemType == "DropDownBox":
            elem = DropDownBoxWebElement(locator)
        elif elemType == "HyperLink":
            elem = HyperLinkWebElement(locator)
        elif elemType == "Button":
            elem = ButtonWebElement(locator)
        return elem
    
    def isElementDisplayed(self, webElement):
        """ verify if the target web element is displayed in web page  """
        return webElement.isDisplayed()
    
    def getContent(self, webElement):
        """ return the element value or name if the element is a link or text box"""
        return webElement.__get__(self)       