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
from libraries.ia.PageObjects import  selenium_server_connection
from BasePageObject import BasePageObject
from BaseWebElement import BaseWebElement, ButtonWebElement


class HealthCareHotSpotElement(BaseWebElement):
    def __init__(self):
        self.locatorString = "main.hs_healthcare"
        self.locator = "healthcare"
        
    def getElement(self, locator):
        """ locate the web element on page """
        driver = selenium_server_connection.connection
        divs = driver.find_elements_by_class_name("top")
        elem = None
        for item in divs:
            if item.get_attribute("data-href") == locator:
                elem = item
                break
        return elem

class HospitalityHotSpotElement(BaseWebElement):
    def __init__(self):
        self.locatorString = "main.hs_hospitality"
        self.locator = "hospitality"
        
    def getElement(self, locator):
        """ locate the web element on page """
        driver = selenium_server_connection.connection
        divs = driver.find_elements_by_class_name("top")
        elem = None
        for item in divs:
            if item.get_attribute("data-href") == locator:
                elem = item
                break
        return elem

class EducationHotSpotElement(BaseWebElement):
    def __init__(self):
        self.locatorString = "main.hs_education"
        self.locator = "education"
        
    def getElement(self, locator):
        """ locate the web element on page """
        driver = selenium_server_connection.connection
        divs = driver.find_elements_by_class_name("top")
        elem = None
        for item in divs:
            if item.get_attribute("data-href") == locator:
                elem = item
                break
        return elem
        
class CommercialHotSpotElement(BaseWebElement):
    def __init__(self):
        self.locatorString = "main.hs_commercial"
        self.locator = "commercial"
        
    def getElement(self, locator):
        """ locate the web element on page """
        driver = selenium_server_connection.connection
        divs = driver.find_elements_by_class_name("top")
        elem = None
        for item in divs:
            if item.get_attribute("data-href") == locator:
                elem = item
                break
        return elem
        
class DataCentreHotSpotElement(BaseWebElement):
    def __init__(self):
        self.locatorString = "main.hs_datacentre"
        self.locator = "data-centre"
        
    def getElement(self, locator):
        """ locate the web element on page """
        driver = selenium_server_connection.connection
        divs = driver.find_elements_by_class_name("top")
        elem = None
        for item in divs:
            if item.get_attribute("data-href") == locator:
                elem = item
                break
        return elem


class MainPageObj(BasePageObject):
    
    navigator = BaseWebElement("main.navigator")
    
    nav_HealthCare = ButtonWebElement("main.nav_healthcare")
    nav_Hospitality = ButtonWebElement("main.nav_hospitality")
    nav_Education = ButtonWebElement("main.nav_education")
    nav_Commercial = ButtonWebElement("main.nav_commercial")
    nav_DataCentre = ButtonWebElement("main.nav_datacentre")

    hs_HealthCare = HealthCareHotSpotElement()
    hs_Hospitality = HospitalityHotSpotElement()
    hs_Education = EducationHotSpotElement()
    hs_Commercial = CommercialHotSpotElement()
    hs_DataCentre = DataCentreHotSpotElement()
    
    #def __init__(self, driver):
    #    self.driver = driver
        
    def __repr__(self):
        super(MainPageObj, self).__repr__()
        
    def __str__(self):
        return "IA Main Paget"
    
    def loading(self, timeout):
        """
        wait for page loading
        """
        locator = self.navigator.locator
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
        titleExpected = locators["main.title"]
        titleCurrent = driver.title
        try: 
            assert titleExpected == titleCurrent
            assert self.navigator.isDisplayed() is True
        except:
            result = False
        return result
    
        