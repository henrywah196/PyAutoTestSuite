'''
Created on Jun 11, 2013

@author: hwang
'''
from libraries.ia import locators
from libraries.ia.PageObjects import  selenium_server_connection
from libraries.ia.PageObjects import seleniumwrapper

class BaseWebElement(object):
    """ Model a Base web element """
    def __init__(self, locatorString):
        self.locatorString = locatorString
        self.locator = locators[locatorString]
    
    def __delete__(self, obj):
        pass
    
    def __str__(self):
        """ return its locator name (default, will be overwrite) """
        return self.locatorString
    
    def getElement(self, locator):
        """ locate the web element on page """
        driver = selenium_server_connection.connection
        how = locator["by"]
        what = locator["value"]
        if locator["parent"]:
            locator = locators[locator["parent"]]
            driver = self.getElement(locator)
        elem = seleniumwrapper.getElement(how, what, driver)
        return elem
    
    def click(self):
        elem = self.getElement(self.locator)
        elem.location_once_scrolled_into_view
        elem.click()
        
    def isDisplayed(self):
        """ return true if the web element is displayed on web page """
        elem = self.getElement(self.locator)
        elem.location_once_scrolled_into_view
        return elem.is_displayed()
        
class HyperLinkWebElement(BaseWebElement):
    """ Model a Hyper Link web element """
    def __init__(self, locatorString):
        self.locatorString = locatorString
        self.locator = locators[locatorString]
        
    '''
    def __get__(self, obj, objtype=None):
        """get the text content of the hyper link
           or the image filename if the hyper link is an image
        """
        elem = self.getElement(self.locator)
        if obj is None:
            return self
        if elem.tag_name == "img":
            return elem.get_attribute("src")
        return elem.text
    '''
    def __str__(self):
        """get the text content of the hyper link
           or the image filename if the hyper link is an image
        """
        elem = self.getElement(self.locator)
        if elem.tag_name == "img":
            return elem.get_attribute("src")
        return elem.text
    
        

class EditBoxWebElement(BaseWebElement):
    """ Model a Edit Box web element """
    def __init__(self, locatorString):
        self.locatorString = locatorString
        self.locator = locators[locatorString]
    
    '''    
    def __get__(self, obj, objtype=None):
        """ get the current value of the edit box"""
        elem = self.getElement(self.locator)
        if obj is None:
            return self
        return elem.get_attribute("value")
    '''
    
    def __str__(self):
        """ get the current value of the edit box"""
        elem = self.getElement(self.locator)
        return elem.get_attribute("value")
    
    
class DropDownBoxWebElement(EditBoxWebElement):
    """ Model a DropDown Box web element """
    def __init__(self, locatorString):
        self.locatorString = locatorString
        self.locator = locators[locatorString]
        self.invalidIcon = BaseWebElement(locatorString + '.invalid_icon')
        
    def __set__(self, obj, val):
        dropDownList = self._getDropDownList()
        if dropDownList:
            itemObjs = dropDownList.find_elements_by_tag_name('li')
            target = None
            for item in itemObjs:
                if item.text == val:
                    target = item
                    break
            if target:
                target.click()
     
    def _getDropDownList(self): 
        """ return the drop down list element """ 
        driver = selenium_server_connection.connection 
        dropDownList = None
        self.click()
        boundLists = driver.find_elements_by_class_name('x-boundlist-list-ct')
        if boundLists:
            for boundList in boundLists:
                if boundList.is_displayed():
                    dropDownList = boundList
                    break
        del boundLists
        return dropDownList
    
    def getListContent(self):
        """ return a list of available items from drop down list """
        myList = []
        dropDownList = self._getDropDownList()
        if dropDownList:
            itemObjs = dropDownList.find_elements_by_tag_name('li')
            for item in itemObjs:
                myList.append(item.text)
        return myList

class ButtonWebElement(BaseWebElement):
    """ Model a Button web element """
    def __init__(self, locatorString):
        self.locatorString = locatorString
        self.locator = locators[locatorString]
    
    '''    
    def __get__(self, obj, objtype=None):
        """ get the label of the button """
        elem = self.getElement(self.locator)
        if obj is None:
            return self
        locator = self.locator
        tagName = locator["tag_name"]
        if tagName == "input":
            return elem.get_attribute("value")
        if tagName == "span":
            return elem.text
    '''
        
    def __str__(self):
        """ get the label of the button """
        elem = self.getElement(self.locator)
        locator = self.locator
        tagName = locator["tag_name"]
        if tagName == "input":
            return elem.get_attribute("value")
        else:
            return elem.text
        
class TextBoxWebElement(BaseWebElement):
    """ Model a Text Box web element """
    def __init__(self, locatorString):
        self.locatorString = locatorString
        self.locator = locators[locatorString]
     
    '''    
    def __get__(self, obj, objtype=None):
        """get the text content of the hyper link
        """
        elem = self.getElement(self.locator)
        if obj is None:
            return self
        return elem.text
    '''
        
    def __str__(self):
        """get the text content of the hyper link
        """
        elem = self.getElement(self.locator)
        return elem.text
        
    