'''
Created on Jan 17, 2013

@author: WAH
'''
import os
import settings
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import Image


class WebdriverWrapper(object):
    
    # singleton
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WebdriverWrapper, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def connect(self, base_url, browser='FIREFOX'):
        self.browser = browser
        self.base_url = base_url
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
        self.mouse = ActionChains(self.connection)
        
        self.connection.get(self.base_url)
        
        return self.connection
        
    def stop(self):
        self.mouse = None
        self.connection.quit()


def getIEDriver(webDriverLocation):
    """ return a IE Webdriver
    """
    iedriver = webDriverLocation + "IEDriverServer"
    os.environ["webdriver.ie.driver"] = iedriver
    driver = webdriver.Ie(iedriver)
    return driver

def getChromeDriver(webDriverLocation):
    """ return a Chrome Webdriver
    """
    chromedriver = webDriverLocation + "chromedriver"
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

def is_element_present(how, what, driver):
    """ verify if the selected WebElement existing
    """
    try: 
        driver.find_element(by=how, value=what)
    except NoSuchElementException, e: 
        return False
    return True

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

def screencapture(driver, element):
    """ screen capture the specified web element
    """
    #save screenshot of whole page to a file
    driver.save_screenshot('.//screenshot//screencapture.png')
    # load image file using PIL
    img = Image.open('.//screenshot//screencapture.png')
    obj = driver.execute_script('return arguments[0].getBoundingClientRect()', element)
    box = (int(obj['left']), int(obj['top']), int(obj['right']), int(obj['bottom']))
    region = img.crop(box)
    region.save('.//screenshot//screencapture.png', 'PNG')
    
def mousehoverJsHelper(driver, targetElement):
    """ javascript based mouse over to the target web element
    """
    javaScript = "var evObj = document.createEvent('MouseEvents');" + "evObj.initMouseEvent(\"mouseover\",true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);" + "arguments[0].dispatchEvent(evObj);"
    driver.execute_script(javaScript, targetElement)

def dragdropJsHelper(driver, LocatorFrom, LocatorTo):
    """ javascript based drag and drop which works across browsers.
    """
    xto = str((LocatorTo.location)['x'])
    yto = str((LocatorTo.location)['y'])
    driver.execute_script("function simulate(f,c,d,e){var b,a=null;for(b in eventMatchers)if(eventMatchers[b].test(c)){a=b;break}if(!a)return!1;document.createEvent?(b=document.createEvent(a),a==\"HTMLEvents\"?b.initEvent(c,!0,!0):b.initMouseEvent(c,!0,!0,document.defaultView,0,d,e,d,e,!1,!1,!1,!1,0,null),f.dispatchEvent(b)):(a=document.createEventObject(),a.detail=0,a.screenX=d,a.screenY=e,a.clientX=d,a.clientY=e,a.ctrlKey=!1,a.altKey=!1,a.shiftKey=!1,a.metaKey=!1,a.button=1,f.fireEvent(\"on\"+c,a));return!0} var eventMatchers={HTMLEvents:/^(?:load|unload|abort|error|select|change|submit|reset|focus|blur|resize|scroll)$/,MouseEvents:/^(?:click|dblclick|mouse(?:down|up|over|move|out))$/}; " +
    "simulate(arguments[0],\"mousedown\",0,0); simulate(arguments[0],\"mousemove\",arguments[1],arguments[2]); simulate(arguments[0],\"mouseup\",arguments[1],arguments[2]); ",
    LocatorFrom,xto,yto)
    
def dragdropJSHelper2(driver, source, target):
    try:
        js_file_path = "D:\workspace\PyAutoTestSuite\drag_and_drop_helper.js"
        js_file = open(js_file_path)
        lines = js_file.readlines()
        js_file.close()
        java_script = ""
        for line in lines:
            java_script = java_script + line
        driver.execute_script(java_script+"$('#{source}').simulateDragDrop({ dropTarget: '#{target}'});")
    except Exception as e:
        print "dragdropJSHelper2() get Exception: %s" %e

