'''
Test Case TC0501: Examine the navigation for DataCentre
Created on Oct 20, 2015

@author: hwang
'''
from libraries.PyAutoTestCase import *    # import test case template
from libraries.ia import Macros
from libraries.ia.PageObjects.IAMainPage import MainPageObj
from libraries.ia.PageObjects.DataCentre.DataCentrePage import DataCentrePageObj


class TC0501(TestCaseTemplate):
    def setUp(self):
        super(TC0501, self).setUp()
        #self.driver = selenium_server_connection.connect("ia.deltacontrols.com")
        Macros.loadIA("ia.deltacontrols.com")
        self.mainPage = MainPageObj()
        self.dataCentrePage = DataCentrePageObj()

    def tearDown(self):
        super(TC0501, self).tearDown()
        Macros.closeIA()
        del self.mainPage
        del self.dataCentrePage


    def test01(self):
        """
        verify navigation between City and DataCentre
        """
        
        # verify by click menu button
        self.mainPage.nav_DataCentre.click()
        self.dataCentrePage.loading(timeout=10)
        result = self.dataCentrePage.isLoaded()
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.dataCentrePage, True, result)
        self.assertTrue(result, errMessage)
        self.dataCentrePage.button_BackToCity.click()
        self.mainPage.loading(timeout=10)
        result = self.mainPage.isLoaded()
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.mainPage, True, result)
        self.assertTrue(result, errMessage)
        
        # verify by click hot spot
        self.mainPage.hs_DataCentre.click()
        self.dataCentrePage.loading(timeout=10)
        result = self.dataCentrePage.isLoaded() 
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.dataCentrePage, True, result)
        self.assertTrue(result, errMessage)
        self.dataCentrePage.button_BackToCity.click()
        self.mainPage.loading(timeout=10)
        result = self.mainPage.isLoaded()
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.mainPage, True, result)
        self.assertTrue(result, errMessage)
            

if __name__ == "__main__":
    unittest.main()