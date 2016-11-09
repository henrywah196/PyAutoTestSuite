'''
Created on Jun 11, 2013

@author: hwang
'''
from libraries.SLAT.ActivationServer import locators
from basepageobject import BasePageObject
from basewebelement import TextBox, EditBox, Button, Table
import time


class HomePage(BasePageObject):
    
    headLine = TextBox("home.Headline")
    searchValue = EditBox("home.SearchValue")
    searchButton = Button("home.SearchButton")
    noRecordFound = TextBox("home.NoResult")
    licFilesTable = Table("home.LicFilesTable")
    keyListTable = Table("home.KeyListTable")
    
    def __init__(self, driver):
        self.driver = driver
        
    def __repr__(self):
        super(HomePage, self).__repr__()
        
    def isLoaded(self):
        """
        verify the page is loaded in web browser successfully
        """
        return self.headLine.isDisplayed()
    
    def search(self, param):
        ''' search for a specific license by parameter '''
        self.searchValue = param
        self.searchButton.click()
        time.sleep(40)
        
        if self.noRecordFound.isDisplayed():
            return False
        else:
            return True
        
    def selectLicFile(self, ProductName, FileDescription="Default"):
        ''' select and load license file page '''
        targetRow = None
        targetCell = None
        rows = self.licFilesTable.totalRows()
        i = 1
        while i <= rows:
            tr = self.licFilesTable.getRow(i)
            result = tr.get_attribute("innerHTML")
            if ProductName in result:
                if (ProductName == "enteliWEB") and ("enteliWEB V2" in result):
                    pass
                else:
                    targetRow = tr
                    break
            i = i + 1
        if targetRow:
             targetCell = targetRow.find_element_by_link_text(FileDescription)
        if targetCell:
            targetCell.location_once_scrolled_into_view
            targetCell.click()
            time.sleep(10)
            return True
        else:
            return False
        
    def getKeyList(self, ProductName, KeyType):
        """ return a list of key info """
        targetRow = None
        rows = self.keyListTable.totalRows()
        i = 1
        while i <= rows:
            tr = self.keyListTable.getRow(i)
            result = tr.get_attribute("innerHTML")
            if (ProductName in result) and (KeyType in result):
                if (ProductName == "enteliWEB") and ("enteliWEB V2" in result):
                    pass
                else:
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
        
                
            
        
        
    
        