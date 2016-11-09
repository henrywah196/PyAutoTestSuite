'''
Created on Jun 11, 2013

@author: hwang
'''
from libraries.SLAT.ActivationServer import locators
from basepageobject import BasePageObject
from basewebelement import EditBox, Button
import time


class LoginPage(BasePageObject):
    
    username = EditBox("login.username")
    password = EditBox("login.password")
    login = Button("login.submit")
    
    def __init__(self, driver):
        self.driver = driver
        
    def __repr__(self):
        super(LoginPage, self).__repr__()
        
    def isLoaded(self):
        """
        verify the page is loaded in web browser successfully
        """
        return self.login.isDisplayed()
    
    def submit(self):
        """ login to activation server """
        self.login.click()
        time.sleep(3)
    
        