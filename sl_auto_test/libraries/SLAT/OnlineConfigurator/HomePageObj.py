'''
Created on Jan 14, 2014

@author: hwang
'''
from libraries.SLAT.OnlineConfigurator import locators
from basepageobject import BasePageObject
from basewebelement import TextBox, HyperLink
import time


class ProductLink(HyperLink):
    def click(self):
        elem = self.getElement(self.locator)
        elem.location_once_scrolled_into_view
        target = elem.find_element_by_tag_name("img")
        if target:
            target.location_once_scrolled_into_view
            target.click()

class HomePage(BasePageObject):
    
    headLine = TextBox("home.Headline")
    enteliWEBLnk = ProductLink("home.enteliWEBLnk")
    enteliBRIDGELnk = ProductLink("home.enteliBRIDGELnk")
    copperCubeLnk = ProductLink("home.copperCubeLnk")
    
    def __init__(self):
        self.driver = None
        
    def __repr__(self):
        super(HomePage, self).__repr__()
        
    def isLoaded(self):
        """
        verify the page is loaded in web browser successfully
        """
        return self.headLine.isDisplayed()
    
        