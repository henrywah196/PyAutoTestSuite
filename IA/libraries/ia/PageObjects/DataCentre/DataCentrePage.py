'''
Created on Oct 21, 2015

@author: hwang
'''
from libraries.ia import locators
from libraries.ia.PageObjects.HotSpotBuilding import HotSpotBuildingObj
from libraries.ia.PageObjects.BaseWebElement import BaseWebElement, ButtonWebElement


class DataCentrePageObj(HotSpotBuildingObj):
    
    def __repr__(self):
        super(DataCentrePageObj, self).__repr__()
        
    def __str__(self):
        return "Health Care Building Page"
        
    def isLoaded(self):
        """
        verify the page is loaded in web browser successfully
        """
        result = True
        try: 
            assert super(DataCentrePageObj, self).isLoaded() is True
            
            elem = self.image.getElement(self.image.locator)
            img = elem.find_element_by_tag_name("img")
            src = img.get_attribute("src")
            assert ("data-centres-stillhighlights.jpg" in src) is True
            
        except:
            result = False
        return result