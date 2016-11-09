'''
Created on Jan 14, 2015

@author: hwang
'''
from libraries.SLAT.OnlineConfigurator import locators
from basepageobject import BasePageObject
from basewebelement import EditBox, Button
import time


class LoginPage(BasePageObject):
    
    username = EditBox("login.username")
    password = EditBox("login.password")
    login = Button("login.submit")
    
    def __init__(self):
        self.driver = None
        
    def __repr__(self):
        super(LoginPage, self).__repr__()
        
    def isLoaded(self):
        """
        verify the page is loaded in web browser successfully
        """
        return self.login.isDisplayed()
    
    def submit(self):
        """ login to Online Order Configurator """
        self.login.click()
        time.sleep(3)
    
        