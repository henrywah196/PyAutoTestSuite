'''
Created on Jan 14, 2014

@author: hwang
'''
from libraries.SLAT.OnlineConfigurator import locators
from basepageobject import BasePageObject
from basewebelement import TextBox, EditBox, CheckBox, DropDownBox, Button
import time
#from msilib.schema import CheckBox


class ConfigProduct(BasePageObject):
    
    wizHeader = TextBox("pdConfig.wizHeader")
    confirmSubmit = TextBox("pdConfig.confirmSubmit")
    
    
    def __init__(self):
        self.driver = None
        
    def __repr__(self):
        super(ConfigProduct, self).__repr__()
        
    def isLoaded(self):
        """
        verify the page is loaded in web browser successfully
        """
        return self.wizHeader.isDisplayed()
    
    def scroll_to_bottom(self):
        """
        scroll to page bottom
        """
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def isSubmitted(self):
        """
        verify if the order has been submitted successfully
        """
        pass
    
        