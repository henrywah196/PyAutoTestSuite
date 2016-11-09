# coding: utf-8
import settings
from libraries.PyAutoTestCase import *    # import test case template
from libraries.eweb.PageObjects.LoginPage import LoginPageObj
from libraries.eweb.PageObjects.Header import HeaderPageObj
from libraries.eweb.PageObjects.AdminFrame import AdminFrameObj
from libraries.eweb.PageObjects.Accordion import AccordionPageObj
from libraries.eweb import Macros
import os, time


class Sample_Test(TestCaseTemplate):
    def setUp(self):
        super(Sample_Test, self).setUp()
        self.Browser = settings.BROWSER
        self.Host = settings.HOST
        self.Username = settings.USERNAME
        self.Password = settings.PASSWORD
        Macros.LoadEnteliWEB(self.Host, self.Browser, self.Username, self.Password)
        
        self.accordion = AccordionPageObj()
        

    def tearDown(self):
        super(Sample_Test, self).tearDown()
        Macros.CloseEnteliWEB()
        
        del self.accordion


    def test01(self):

        result = self.accordion.isLoaded()
        self.assertTrue(result, "Verify enteliWEB Main Page Left Pane is loaded")
        
        self.accordion.select(self.accordion.reports)            
                
    
        

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Sample_Test))
    return suite


if __name__ == "__main__":
    unittest.main()
