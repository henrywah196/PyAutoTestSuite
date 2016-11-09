'''
Test Case TC0101: Examine the navigation for Health Care
Created on Oct 20, 2015

@author: hwang
'''
from libraries.PyAutoTestCase import *    # import test case template
from libraries.ia import Macros
from libraries.ia.PageObjects.IAMainPage import MainPageObj
from libraries.ia.PageObjects.HealthCare.HealthCarePage import HealthCarePageObj


class TC0101(TestCaseTemplate):
    def setUp(self):
        super(TC0101, self).setUp()
        #self.driver = selenium_server_connection.connect("ia.deltacontrols.com")
        Macros.loadIA("ia.deltacontrols.com")
        self.mainPage = MainPageObj()
        self.healthCarePage = HealthCarePageObj()

    def tearDown(self):
        super(TC0101, self).tearDown()
        Macros.closeIA()
        del self.mainPage
        del self.healthCarePage


    def test01(self):
        """
        verify navigation between City and Health Care
        """
        
        # verify by click menu button
        self.mainPage.nav_HealthCare.click()
        self.healthCarePage.loading(timeout=10)
        result = self.healthCarePage.isLoaded()
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.healthCarePage, True, result)
        self.assertTrue(result, errMessage)
        self.healthCarePage.button_BackToCity.click()
        self.mainPage.loading(timeout=10)
        result = self.mainPage.isLoaded()
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.mainPage, True, result)
        self.assertTrue(result, errMessage)
        
        # verify by click hot spot
        self.mainPage.hs_HealthCare.click()
        self.healthCarePage.loading(timeout=10)
        result = self.healthCarePage.isLoaded() 
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.healthCarePage, True, result)
        self.assertTrue(result, errMessage)
        self.healthCarePage.button_BackToCity.click()
        self.mainPage.loading(timeout=10)
        result = self.mainPage.isLoaded()
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.mainPage, True, result)
        self.assertTrue(result, errMessage)
            

if __name__ == "__main__":
    unittest.main()