'''
Created on Jun 11, 2013

@author: hwang
'''
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class SeleniumWrapper(object):
    
    # singleton
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SeleniumWrapper, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def connect(self, host="ia.deltacontrols.com", browser=None):
        self.browser = browser
        self.base_url = "http://%s/" %host
        self.connection = getFirefoxDriver()
            
        self.connection.implicitly_wait(30)
        self.connection.maximize_window()
        
        self.connection.get(self.base_url)
        
        return self.connection
        
    def stop(self):
        self.mouse = None
        self.connection.quit()
        
        
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