'''
Created on Jun 11, 2013

@author: hwang
'''
from libraries.ia import locators
from BasePageObject import BasePageObject
from BaseWebElement import TextBoxWebElement, ButtonWebElement


class WelcomePageObj(BasePageObject):
    
    button_OnlineVersion = ButtonWebElement("welcome.online_version")
    
    #def __init__(self, driver):
    #    self.driver = driver
        
    def __repr__(self):
        super(WelcomePageObj, self).__repr__()
        
    def __str__(self):
        return "IA Welcome Page"
        
    def isLoaded(self):
        """
        verify the page is loaded in web browser successfully
        """
        result = True
        driver = self.driver
        titleExpected = locators["welcome.title"]
        titleCurrent = driver.title
        try: assert titleExpected == titleCurrent
        except:
            result = False
        return result
    
        