'''
Created on Jun 11, 2013

@author: hwang
'''
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from libraries.ia import locators
from BasePageObject import BasePageObject
from BaseWebElement import BaseWebElement, ButtonWebElement


class HotSpotBuildingObj(BasePageObject):
    
    button_BackToCity = ButtonWebElement("building.backtocity")
    navigator         = BaseWebElement("building.navigator")
    nav_Previous      = ButtonWebElement("building.nav_previous")
    nav_Next          = ButtonWebElement("building.nav_next")
    image             = BaseWebElement("building.image")
    
    def __repr__(self):
        super(HotSpotBuildingObj, self).__repr__()
        
    def __str__(self):
        return "IA Generic HotSpot Building Page Object"
    
    def loading(self, timeout):
        """
        wait for page loading
        """
        locator = self.button_BackToCity.locator
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, locator["value"])))
            time.sleep(3)
        except TimeoutException:
            raise Exception("%s is not finish loading within %s seconds"%(self, timeout))
        
        
    def isLoaded(self):
        """
        verify the page is loaded in web browser successfully
        """
        result = True
        driver = self.driver
        titleExpected = locators["building.title"]
        titleCurrent = driver.title
        try: 
            assert titleExpected == titleCurrent
            assert self.navigator.isDisplayed() is True
        except:
            result = False
        return result
    
        