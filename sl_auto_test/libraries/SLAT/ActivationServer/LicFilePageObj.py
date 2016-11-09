'''
Created on Jun 11, 2013

@author: hwang
'''
from libraries.SLAT.ActivationServer import locators
from basepageobject import BasePageObject
from basewebelement import TextBox, EditBox, Button, Table
import time


class LicFilePage(BasePageObject):
    
    headLine = TextBox("licfile.Headline")
    modules = TextBox("licfile.Modules")
    modulesTable = Table("licfile.ModulesTable")
    dataArea = TextBox("licfile.DataArea")
    dataAreaTable = Table("licfile.DataAreaTable")
    
    def __init__(self, driver):
        self.driver = driver
        
    def __repr__(self):
        super(LicFilePage, self).__repr__()
        
    def isLoaded(self):
        """
        verify the page is loaded in web browser successfully
        """
        if self.headLine.isDisplayed():
            current = self.headLine.get()
            expected = "This page shows license files"
            if current == expected:
                return True
            else:
                return False
            
    def getModuleInfo(self, ModuleNumber):
        """ return a list of module information """
        targetRow = None
        rows = self.modulesTable.totalRows()
        i = 1
        while i <= rows:
            tr = self.modulesTable.getRow(i)
            result = tr.get_attribute("innerHTML")
            if (ModuleNumber in result):
                targetRow = tr
                break
            i = i + 1
        if targetRow:
            result = []
            targetRow.location_once_scrolled_into_view
            cells = targetRow.find_elements_by_tag_name("td")
            if cells:
                for item in cells:
                    result.append(item.text)
                return result
            else:
                return None
        else:
            return None
        
    def selectModule(self, ModuleNumber):
        """ select a module to load the modify a module page """
        targetRow = None
        targetCell = None
        rows = self.modulesTable.totalRows()
        i = 1
        while i <= rows:
            tr = self.modulesTable.getRow(i)
            result = tr.get_attribute("innerHTML")
            if ModuleNumber in result:
                targetRow = tr
                break
            i = i + 1
        if targetRow:
             targetCell = targetRow.find_element_by_link_text(ModuleNumber)
        if targetCell:
            targetCell.location_once_scrolled_into_view
            targetCell.click()
            time.sleep(10)
            return True
        else:
            return False
        
        
    def getDataAreaInfo(self, Parameter):
        """ return a list of Data area information """
        targetRow = None
        rows = self.dataAreaTable.totalRows()
        i = 1
        while i <= rows:
            tr = self.dataAreaTable.getRow(i)
            result = tr.get_attribute("innerHTML")
            if (Parameter in result):
                targetRow = tr
                break
            i = i + 1
        if targetRow:
            result = []
            cells = targetRow.find_elements_by_tag_name("td")
            if cells:
                for item in cells:
                    result.append(item.text)
                return result
            else:
                return None
        else:
            return None
        
    
        