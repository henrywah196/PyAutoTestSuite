'''
Test Case TC0301: Examine the navigation for Education
Created on Oct 20, 2015

@author: hwang
'''
from libraries.PyAutoTestCase import *    # import test case template
from libraries.ia import Macros
from libraries.ia.PageObjects.IAMainPage import MainPageObj
from libraries.ia.PageObjects.Education.EducationPage import EducationPageObj


class TC0301(TestCaseTemplate):
    def setUp(self):
        super(TC0301, self).setUp()
        #self.driver = selenium_server_connection.connect("ia.deltacontrols.com")
        Macros.loadIA("ia.deltacontrols.com")
        self.mainPage = MainPageObj()
        self.educationPage = EducationPageObj()

    def tearDown(self):
        super(TC0301, self).tearDown()
        Macros.closeIA()
        del self.mainPage
        del self.educationPage


    def test01(self):
        """
        verify navigation between City and Education
        """
        
        # verify by click menu button
        self.mainPage.nav_Education.click()
        self.educationPage.loading(timeout=10)
        result = self.educationPage.isLoaded()
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.educationPage, True, result)
        self.assertTrue(result, errMessage)
        self.educationPage.button_BackToCity.click()
        self.mainPage.loading(timeout=10)
        result = self.mainPage.isLoaded()
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.mainPage, True, result)
        self.assertTrue(result, errMessage)
        
        # verify by click hot spot
        self.mainPage.hs_Education.click()
        self.educationPage.loading(timeout=10)
        result = self.educationPage.isLoaded() 
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.educationPage, True, result)
        self.assertTrue(result, errMessage)
        self.educationPage.button_BackToCity.click()
        self.mainPage.loading(timeout=10)
        result = self.mainPage.isLoaded()
        errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(self.mainPage, True, result)
        self.assertTrue(result, errMessage)
            

if __name__ == "__main__":
    unittest.main()