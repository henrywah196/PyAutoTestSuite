import nose    # using nose assert
from libraries.ia.PageObjects import selenium_server_connection
from libraries.ia.PageObjects.IAWelcomePage import WelcomePageObj
from libraries.ia.PageObjects.IAPassportLoginPage import LoginPageObj
from libraries.ia.PageObjects.IAMainPage import MainPageObj
import time


def loadIA(hostName):
    """
    load browser, input ia.deltacontrols.com
    select IA online version
    login Delta passport
    wait IA main page load.
    """
    selenium_server_connection.connect(hostName)    # must run at first
    
    welcomePage = WelcomePageObj()
    loginPage = LoginPageObj()
    mainPage = MainPageObj()
    
    # verify welcome page loaded
    result = welcomePage.isLoaded()
    errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(welcomePage, True, result)
    nose.tools.assert_true(result, errMessage)
    welcomePage.button_OnlineVersion.click()
    time.sleep(3)
    
    # login to Delta Passport
    result = loginPage.isLoaded()
    errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(loginPage, True, result)
    nose.tools.assert_true(result, errMessage)
    loginPage.username = "hwang@deltacontrols.com"
    loginPage.password = "passwahpass"
    loginPage.click(loginPage.submit)
    time.sleep(3)
    
    # verify IA Main page loaded
    result = mainPage.isLoaded()
    errMessage = "Verify %s is loaded (Expected, Current): %s, %s" %(mainPage, True, result)
    nose.tools.assert_true(result, errMessage)
    
    
def closeIA():
    """
    finish and close testing web browser
    """
    selenium_server_connection.stop()
    


