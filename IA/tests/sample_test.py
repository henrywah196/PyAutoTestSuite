# coding: utf-8
from libraries.PyAutoTestCase import *    # import test case template
from libraries.ia import Macros
from libraries.ia.PageObjects import selenium_server_connection
from libraries.ia.PageObjects.IAWelcomePage import WelcomePageObj
from libraries.ia.PageObjects.IAPassportLoginPage import LoginPageObj
from libraries.ia.PageObjects.IAMainPage import MainPageObj
import os, time


class Sample_Test(TestCaseTemplate):
    def setUp(self):
        super(Sample_Test, self).setUp()
        #self.driver = selenium_server_connection.connect("ia.deltacontrols.com")
        Macros.loadIA("ia.deltacontrols.com")
        

    def tearDown(self):
        super(Sample_Test, self).tearDown()
        selenium_server_connection.stop()


    def test01(self):

        '''
        # verify welcome page loaded
        welcomePage = WelcomePageObj()
        result = welcomePage.isLoaded()
        errMessage = "Load welcome Page (Expected, Current): %s, %s" %(True, result)
        self.assertTrue(result, errMessage)
        welcomePage.button_OnlineVersion.click()
        time.sleep(3)
        
        # login to enteliWEB
        loginPage = LoginPageObj()
        result = loginPage.isLoaded()
        errMessage = "Load login Page (Expected, Current): %s, %s" %(True, result)
        self.assertTrue(result, errMessage)
        loginPage.username = "hwang@deltacontrols.com"
        loginPage.password = "passwahpass"
        loginPage.click(loginPage.submit)
        time.sleep(3)
        
        # verify IA Main page loaded
        mainPage = MainPageObj()
        result = mainPage.isLoaded()
        errMessage = "Load IA Main Page (Expected, Current): %s, %s" %(True, result)
        self.assertTrue(result, errMessage)
        '''
        
        
            

if __name__ == "__main__":
    unittest.main()
