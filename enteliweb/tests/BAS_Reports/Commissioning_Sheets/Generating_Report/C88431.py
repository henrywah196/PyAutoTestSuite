# coding: utf-8
import settings
from libraries.eweb import Macros
from libraries.PyAutoTestCase import *    # import test case template
from libraries.eweb.PageObjects.Accordion import AccordionPageObj
import os, time


class TC88431(TestCaseTemplate):
    
    def setUp(self):
        super(TC88431, self).setUp()
        self.Browser = settings.BROWSER
        self.Host = settings.HOST
        self.Username = settings.USERNAME
        self.Password = settings.PASSWORD
        Macros.LoadEnteliWEB(self.Host, self.Browser, self.Username, self.Password)

    def tearDown(self):
        super(TC88431, self).tearDown()
        Macros.CloseEnteliWEB()

    #@unittest.skip("")
    def test01(self):
        
        accordion = AccordionPageObj()
        
        


if __name__ == "__main__":
    unittest.main()
