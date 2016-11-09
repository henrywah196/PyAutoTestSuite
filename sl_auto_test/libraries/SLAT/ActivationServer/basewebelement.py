'''
Created on Jan 12, 2013

@author: WAH
'''
from libraries import Utilities
from libraries import Actions
from libraries.SLAT.ActivationServer import webdriver_connection, locators
import time


class BaseWebElement(object):
    """ Model a Base web element """
    def __init__(self, locatorString):
        self.locatorString = locatorString
        self.locator = locators[locatorString]
    
    def __delete__(self, obj):
        pass
    
    def __str__(self):
        """ return its locator name """
        return self.locatorString
    
    def getElement(self, locator):
        """ locate the web element on page """
        driver = webdriver_connection.connection
        how = locator["by"]
        what = locator["value"]
        if locator["parent"]:
            locator = locators[locator["parent"]]
            driver = self.getElement(locator)
        elem = Actions.getElement(how, what, driver)
        return elem
    
    def click(self):
        elem = self.getElement(self.locator)
        elem.location_once_scrolled_into_view
        elem.click()
        
    def isDisplayed(self):
        """ return true if the web element is displayed on web page """
        elem = self.getElement(self.locator)
        if elem:
            elem.location_once_scrolled_into_view
            return elem.is_displayed()
        else:
            return False
    

class TextBox(BaseWebElement):
    """ Model a Text Box web element """
    def __init__(self, locatorString):
        self.locatorString = locatorString
        self.locator = locators[locatorString]
        
    def get(self):
        """get the text content of the web element
        """
        elem = self.getElement(self.locator)
        if elem:
            return elem.text
        else:
            return None
        
        
class HyperLink(BaseWebElement):
    """ Model a Hyper Link web element """
    def __init__(self, locatorString):
        self.locatorString = locatorString
        self.locator = locators[locatorString]
        
    def get(self):
        """get the text content of the hyper link
           or the image filename if the hyper link is an image
        """
        elem = self.getElement(self.locator)
        if elem.tag_name == "img":
            return elem.get_attribute("src")
        return elem.text
    

class Button(BaseWebElement):
    """ Model a Button web element """
    def __init__(self, locatorString):
        self.locatorString = locatorString
        self.locator = locators[locatorString]
        
    def get(self):
        """ get the label of the button """
        elem = self.getElement(self.locator)
        locator = self.locator
        tagName = locator["tag_name"]
        if tagName == "input":
            return elem.get_attribute("value")
        if tagName == "span":
            return elem.text


class EditBox(BaseWebElement):
    """ Model a Edit Box web element """
    def __init__(self, locatorString):
        self.locatorString = locatorString
        self.locator = locators[locatorString]
    
    def __set__(self, obj, val):
        elem = self.getElement(self.locator)
        if elem:
            elem.clear()
            elem.send_keys(val)
        
    def get(self):
        """ get the current value of the edit box"""
        elem = self.getElement(self.locator)
        if elem:
            return elem.get_attribute("value")
        else:
            return None
    
    
class DropDownBox(EditBox):
    """ Model a DropDown Box web element """
    def __init__(self, locatorString):
        self.locatorString = locatorString
        self.locator = locators[locatorString]
        
    def __set__(self, obj, val):
        target = None
        elem = self.getElement(self.locator)
        #elem.click()
        #time.sleep(2)
        itemObjs = elem.find_elements_by_tag_name('option')
        if itemObjs:
            for item in itemObjs:
                if Utilities.trimWhiteSpace(item.text) == val:
                    target = item
                    break
            if target:
                target.click()
     
    
    def getListContent(self):
        """ return a list of available items from drop down list """
        elem = self.getElement(self.locator)
        myList = []
        itemObjs = elem.find_elements_by_tag_name('option')
        if itemObjs:
            for item in itemObjs:
                myList.append(Utilities.trimWhiteSpace(item.text))
        return myList
    
    
    def get(self):
        pass
    
    
class Table(BaseWebElement):
    """ Model a table web element """
    def __init__(self, locatorString):
        self.locatorString = locatorString
        self.locator = locators[locatorString]
        
    def getRow(self, rowNumber):
        """ reutrn a row web element """
        tr = None
        elem = self.getElement(self.locator)
        if rowNumber == 1:
            tr = elem.find_element_by_xpath("./tbody/tr")
        else:
            tr = elem.find_element_by_xpath("./tbody/tr[%s]"%rowNumber)
        return tr
    
    def totalRows(self):
        """ return a number to represent total number of rows """
        elem = self.getElement(self.locator)
        trs = elem.find_elements_by_tag_name("tr")
        if trs:
            return len(trs)
        else:
            return None
    

