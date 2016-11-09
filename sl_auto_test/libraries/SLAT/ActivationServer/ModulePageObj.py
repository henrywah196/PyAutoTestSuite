'''
Created on Jun 11, 2013

@author: hwang
'''
from libraries.SLAT.ActivationServer import locators
from basepageobject import BasePageObject
from basewebelement import TextBox, EditBox, Button, Table
import time


class ModulePage(BasePageObject):
    
    headLine = TextBox("module.Headline")
    moduleNumber = EditBox("module.ModuleNumber")
    #numberOfLicense = EditBox()
    #moduleValue = EditBox()
    #moduleType = EditBox()
    validUntilDay = EditBox("module.ValidUntilDay")
    validNumberOfDays = EditBox("module.ValidNumberOfDays")
    saveButton = Button("module.Save")
    cancelButton = Button("module.Cancel")
    
    
    def __init__(self, driver):
        self.driver = driver
        
    def __repr__(self):
        super(ModulePage, self).__repr__()
        
    def isLoaded(self):
        """
        verify the page is loaded in web browser successfully
        """
        if self.headLine.isDisplayed():
            current = self.headLine.get()
            expected = "This page allows you to modify a module"
            if current == expected:
                return True
            else:
                return False
        
    
        