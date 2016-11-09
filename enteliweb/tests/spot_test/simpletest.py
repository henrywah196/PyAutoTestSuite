'''
Created on Sep 19, 2016

@author: user
'''
import settings
import unittest
from libraries.eweb.PageObjects.LoginPage import LoginPageObj
from libraries.eweb.PageObjects.Header import HeaderPageObj
from libraries.eweb.PageObjects.AdminFrame import AdminFrameObj
from libraries.eweb.PageObjects.Accordion import AccordionPageObj
from libraries.eweb import Macros
import os, time


# Common variables for entire test case
driver = None
HOSTNAME = "192.168.2.191"
BROWSER = "FIREFOX"
USERNAME = "Admin"
PASSWORD = "Password" 

Accordion = None


class SimpleTest(unittest.TestCase):
    
    def setUp(self):
        Macros.LoadEnteliWEB(HOSTNAME, BROWSER, USERNAME, PASSWORD)
        
        global Accordion
        Accordion = AccordionPageObj()
        

    def tearDown(self):
        Macros.CloseEnteliWEB()
        global Accordion
        del Accordion
        
    def test01(self):
        if not Accordion.reportTree.isDisplayed():
            Accordion.select(Accordion.reports)
            time.sleep(3)
            
if __name__ == "__main__":
    unittest.main()