'''
Created on Jun 11, 2013

@author: hwang
'''
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class SeleniumWrapper(object):
    
    # singleton
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SeleniumWrapper, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def connect(self, host, browser="FIREFOX"):
        self.browser = browser
        self.base_url = "http://%s/enteliweb" %host
        self.connection = None
        self.mouse = None
        
        if self.browser == 'CHROME':
            self.connection = getChromeDriver()
        elif self.browser == 'IE':
            self.connection = getIEDriver()
        else:
            self.connection = getFirefoxDriver()
            
        self.connection.implicitly_wait(30)
        self.connection.maximize_window()
        
        self.connection.get(self.base_url)
        
        return self.connection
        
    def stop(self):
        self.connection.quit()
        

def getIEDriver():
    """ return a IE Webdriver
    """
    osPath =  os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir))
    iedriver = os.path.join(osPath, "IEDriverServer")
    os.environ["webdriver.ie.driver"] = iedriver
    driver = webdriver.Ie(iedriver)
    return driver


def getChromeDriver():
    """ return a Chrome Webdriver
    """
    osPath =  os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir))
    chromedriver = os.path.join(osPath, "chromedriver")
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    return driver


def getFirefoxDriver(ff_profile=None):
    """ return a Firefox Webdriver
    """
    driver = None
    if ff_profile:
        driver = webdriver.Firefox(ff_profile)
    else:
        driver = webdriver.Firefox()
    return driver


def getElement(how, what, driver):
    ''' obtain and return the selected WebElement
    '''
    myElement = None
    try:
        if how == "class_name":
            myElement = driver.find_element_by_class_name(what)
        elif how == "tag_name":
            myElement = driver.find_element_by_tag_name(what)
        else:
            myElement = driver.find_element(by=how, value=what)
    except NoSuchElementException, e:
        myElement = None
    return myElement


if __name__ == "__main__":
    driver = getChromeDriver()
    print driver