'''
Test Case TC0401: Examine the navigation for Commercial
Created on Oct 20, 2015

@author: hwang
'''
from libraries.PyAutoTestCase import *    # import test case template
from libraries.ia import Macros
from libraries.ia.PageObjects.IAMainPage import MainPageObj
from libraries.ia.PageObjects.Commercial.CommercialPage import CommercialPageObj


class TC0401(TestCaseTemplate):
    def setUp(self):
        super(TC0401, self).setUp()
        #self.driver = selenium_server_connection.connect("ia.deltacontrols.com")
        Macros.loadIA("ia.deltacontrols.com")
        self.mainPage = MainPageObj()
        self.commercialPage = CommercialPageObj()

    def tearDown(self):
        super(TC0401, self).tearDown()
        Macros.closeIA()
        del self.mainPage
        del self.commercialPage


    def test01(self):
        """
        verify navigation between City and Commercial
        """
        
        # verify by click menu button
        self.mainPage.nav_Commercial.click()
        self.commercialPage.loading(timeout=10)
        result = self.commercialPage.isLoaded()
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.commercialPage, True, result)
        self.assertTrue(result, errMessage)
        self.commercialPage.button_BackToCity.click()
        self.mainPage.loading(timeout=10)
        result = self.mainPage.isLoaded()
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.mainPage, True, result)
        self.assertTrue(result, errMessage)
        
        # verify by click hot spot
        self.mainPage.hs_Commercial.click()
        self.commercialPage.loading(timeout=10)
        result = self.commercialPage.isLoaded() 
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.commercialPage, True, result)
        self.assertTrue(result, errMessage)
        self.commercialPage.button_BackToCity.click()
        self.mainPage.loading(timeout=10)
        result = self.mainPage.isLoaded()
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.mainPage, True, result)
        self.assertTrue(result, errMessage)
            

if __name__ == "__main__":
    unittest.main()