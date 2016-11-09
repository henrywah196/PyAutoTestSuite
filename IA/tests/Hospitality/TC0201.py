'''
Test Case TC0201: Examine the navigation for Hospitality
Created on Oct 20, 2015

@author: hwang
'''
from libraries.PyAutoTestCase import *    # import test case template
from libraries.ia import Macros
from libraries.ia.PageObjects.IAMainPage import MainPageObj
from libraries.ia.PageObjects.Hospitality.HospitalityPage import HospitalityPageObj


class TC0201(TestCaseTemplate):
    def setUp(self):
        super(TC0201, self).setUp()
        #self.driver = selenium_server_connection.connect("ia.deltacontrols.com")
        Macros.loadIA("ia.deltacontrols.com")
        self.mainPage = MainPageObj()
        self.hospitalityPage = HospitalityPageObj()

    def tearDown(self):
        super(TC0201, self).tearDown()
        Macros.closeIA()
        del self.mainPage
        del self.hospitalityPage


    def test01(self):
        """
        verify navigation between City and Hospitality
        """
        
        # verify by click menu button
        self.mainPage.nav_Hospitality.click()
        self.hospitalityPage.loading(timeout=10)
        result = self.hospitalityPage.isLoaded()
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.hospitalityPage, True, result)
        self.assertTrue(result, errMessage)
        self.hospitalityPage.button_BackToCity.click()
        self.mainPage.loading(timeout=10)
        result = self.mainPage.isLoaded()
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.mainPage, True, result)
        self.assertTrue(result, errMessage)
        
        # verify by click hot spot
        self.mainPage.hs_Hospitality.click()
        self.hospitalityPage.loading(timeout=10)
        result = self.hospitalityPage.isLoaded() 
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.hospitalityPage, True, result)
        self.assertTrue(result, errMessage)
        self.hospitalityPage.button_BackToCity.click()
        self.mainPage.loading(timeout=10)
        result = self.mainPage.isLoaded()
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.mainPage, True, result)
        self.assertTrue(result, errMessage)
            

if __name__ == "__main__":
    unittest.main()