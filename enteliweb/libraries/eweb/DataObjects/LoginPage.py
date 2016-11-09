'''
Created on Jun 11, 2013

@author: hwang
'''
from Enteliweb.libenteliwebReporting.PageObjects.BasePageObject import BasePageObject
from Enteliweb.libenteliwebReporting.PageObjects.BaseWebElement import EditBoxWebElement, ButtonWebElement
import time


class UsernameElement(EditBoxWebElement):
    def __init__(self):
        super(UsernameElement, self).__init__("login.username")
    
    def __set__(self, obj, val):
        elem = self.getElement(self.locator)
        elem.clear()
        elem.send_keys(val)

class PasswordElement(EditBoxWebElement):
    def __init__(self):
        super(PasswordElement, self).__init__("login.password")
        
    def __set__(self, obj, val):
        elem = self.getElement(self.locator)
        elem.clear()
        elem.send_keys(val)

class SubmitElement(ButtonWebElement):
    def __init__(self):
        super(SubmitElement, self).__init__("login.submit")

class LoginPageObj(BasePageObject):
    
    username = UsernameElement()
    password = PasswordElement()
    submit = SubmitElement()
        
    def __repr__(self):
        super(LoginPageObj, self).__repr__()
        
    def __str__(self):
        return "enteliWEB Login Page"
        
    def isLoaded(self):
        """
        verify the page is loaded in web browser successfully
        """
        result = True
        driver = self.driver
        titleExpected = "enteliWEB Login Page"
        titleCurrent = driver.title
        try: assert titleExpected == titleCurrent
        except AssertionError as e:
            result = False
        return result
    
        