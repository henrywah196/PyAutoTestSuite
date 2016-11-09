'''
Created on Jun 11, 2013

@author: hwang
'''
from libraries.ia import locators
from BasePageObject import BasePageObject
from BaseWebElement import EditBoxWebElement, ButtonWebElement


class UsernameElement(EditBoxWebElement):
    def __init__(self):
        self.locatorString = "login.username"
        self.locator = locators[self.locatorString]
    
    def __set__(self, obj, val):
        elem = self.getElement(self.locator)
        elem.clear()
        elem.send_keys(val)

class PasswordElement(EditBoxWebElement):
    def __init__(self):
        self.locatorString = "login.password"
        self.locator = locators[self.locatorString]
        
    def __set__(self, obj, val):
        elem = self.getElement(self.locator)
        elem.clear()
        elem.send_keys(val)

class SubmitElement(ButtonWebElement):
    def __init__(self):
        self.locatorString = "login.submit"
        self.locator = locators[self.locatorString]

class LoginPageObj(BasePageObject):
    
    username = UsernameElement()
    password = PasswordElement()
    submit = SubmitElement()
    
    #def __init__(self, driver):
    #    self.driver = driver
        
    def __repr__(self):
        super(LoginPageObj, self).__repr__()
        
    def __str__(self):
        return "IA Passport Login Page"
        
    def isLoaded(self):
        """
        verify the page is loaded in web browser successfully
        """
        result = True
        driver = self.driver
        titleExpected = locators["login.title"]
        titleCurrent = driver.title
        try: assert titleExpected == titleCurrent
        except:
            result = False
        return result
    
        