from libraries.eweb.PageObjects import selenium_server_connection
from libraries.eweb.PageObjects.LoginPage import LoginPageObj
from libraries.eweb.PageObjects.Header import HeaderPageObj
from libraries.eweb.PageObjects.AdminFrame import AdminFrameObj
from libraries.eweb.PageObjects.UnitsFrame import UnitsFrameObj
from libraries.eweb.PageObjects.Accordion import AccordionPageObj
import time, datetime


#############
# General 
#############
def LoadEnteliWEB(hostName, browserType, userName, passWord, ff_profile=None):
    """
    load browser, input base url
    wait for enteliWEB login page
    input username and password click login
    wait for enteliWEB header
    """
    selenium_server_connection.connect(hostName, browserType, ff_profile)    # must run at first
    
    loginPage = LoginPageObj()
    eWEBHeader = HeaderPageObj()
    
    # verify login page loaded
    result = loginPage.isLoaded()
    errMessage = "Verify Login Page is loaded (Expected, Current): %s, %s" %(True, result)
    assert result == True, errMessage
    
    # login to enteliWEB
    loginPage.username = userName
    loginPage.password = passWord
    loginPage.click(LoginPageObj.submit)
    
    # verify enteliWEB header loaded
    eWEBHeader.loading(timeout = 30)
    result = eWEBHeader.isLoaded()
    errMessage = "Verify enteliWEB Main Page Header is loaded (Expected, Current): %s, %s" %(True, result)
    assert result == True, errMessage
    
    
def CloseEnteliWEB():
    """
    finish and close testing web browser
    """
    selenium_server_connection.stop()
    
    
def GoToAdministrationPage():
    """
    click the Administration link to load Admin page
    """
    
    # verify enteliWEB header loaded
    eWEBHeader = HeaderPageObj()
    result = eWEBHeader.isLoaded()
    errMessage = "Verify enteliWEB Main Page Header is loaded (Expected, Current): %s, %s" %(True, result)
    assert result == True, errMessage
    
    # go to Administration main frame
    eWEBHeader.adminlink.click()
    adminFrame = AdminFrameObj()
    adminFrame.loading(timeout = 10)
    result = adminFrame.isLoaded()
    errMessage = "Verify Administration Frame is loaded (Expected, Current): %s, %s" %(True, result)
    assert result == True, errMessage
    
    
def GoToBaseUnitsConfiguration():
    """
    verify admin page is loaded then click link to load Base Unit Configuraiton page
    """
    
    # verify administration page is loaded
    adminFrame = AdminFrameObj()
    result = adminFrame.isLoaded()
    errMessage = "Verify Administration Frame is loaded (Expected, Current): %s, %s" %(True, result)
    assert result == True, errMessage
    
    # go to Base Units Configuration frame
    adminFrame.baseUnitConfiguration.click()
    baseUnitsFrame = UnitsFrameObj()
    baseUnitsFrame.loading(timeout = 10)
    result = baseUnitsFrame.isLoaded()
    errMessage = "Verify Base Unit Configuration Frame is loaded (Expected, Current): %s, %s" %(True, result)
    assert result == True, errMessage
    

#########################
# report related
#########################
def isReportInstanceExisting(PathName):
    """
    return true is the report instnace is displayed in report tree
    
    @param string PathName        A string of path which uniquely identify the tree node in report tree
    """
    accordion = AccordionPageObj()
    accordion.select(accordion.reports)
    time.sleep(2)
    if not accordion.reportTree.isDisplayed():
        accordion.select(accordion.reports)
        time.sleep(2)
    result = accordion.reportTree.expandTreeNode(PathName)
    if not accordion.reportTree.verifyTreeNodeDisplayed(PathName):
        time.sleep(2)
        result = accordion.reportTree.expandTreeNode(PathName)    # try one more time if tree not expanded
    return result
    

def SelectReportInstance(PathName):
    """
    Command to select a report instance from the left report tree

    @param string PathName        A string of path which uniquely identify the tree node in report tree
    """

    accordion = AccordionPageObj()
    accordion.select(accordion.reports)
    time.sleep(2)
    if not accordion.reportTree.isDisplayed():
        accordion.select(accordion.reports)
        time.sleep(2)
    result = accordion.reportTree.expandTreeNode(PathName)
    if not accordion.reportTree.verifyTreeNodeDisplayed(PathName):
        time.sleep(2)
        result = accordion.reportTree.expandTreeNode(PathName)    # try one more time if tree not expanded
    if result:    
        targetNode = accordion.reportTree._getTreeNode(PathName)
        if targetNode:
            targetNode.click()
            time.sleep(3)
            result = True
    errMessage = "Verify the report instance '%s' is selected (Expected, Current): %s, %s" %(PathName, True, result)
    assert result == True, errMessage
    
    
def GenerateReport(RptPageObj, reportName, timeOut=600):
    """ Commend to run and wait for a report generating
    """
    # generating report
    startTime = datetime.datetime.now()
    finishTime = startTime + datetime.timedelta(seconds=timeOut)
    result = RptPageObj.generatingReport(timeout=600)
    if not result:
        if RptPageObj.isReportUITimeOut():
            SelectReportInstance(reportName)
        currentTime = datetime.datetime.now()
        while currentTime <= finishTime:
            result = RptPageObj.generatingReport(timeout=600, clickRun=False)
            if result:
                break
            else:
                currentTime = datetime.datetime.now()
    assert result == True, "failed to generate report"
    currentTime = datetime.datetime.now()
    print "generating report '%s' take %s"%(reportName, currentTime - startTime)
    
    
    
if __name__ == "__main__":
    LoadEnteliWEB("localhost")
    CloseEnteliWEB()


