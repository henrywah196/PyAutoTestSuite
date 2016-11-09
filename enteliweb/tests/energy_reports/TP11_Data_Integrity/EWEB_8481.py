# coding: utf-8
'''
Regression for EWEB-8481
Synopsis: change base units may not force resetting all meters and datapoints
Test methods:
1. setup areas and meters, setup base Units to default metric units
2. wait all datapoint get data imported and optimized.
3. manually stop eweb connect service
4. change all the base units.
5. verify report_rate_tlinstance table, Record count should be 0, state field should be 1, Start = Finish, BaselineFinish should be NULL
5. verify datapoint_group table, all fields suppose to be NULL
6. verify datapoint_group_data table, all fields suppose to be NULL

step 1 and 2 need to be manually done before run the script.

Created on Jul 25, 2013
@author: hwang
'''
from prj_enteliweb.libraries.PATS.PyAutoTestCase import *
from prj_enteliweb.libraries.enteliweb import Utilities
from prj_enteliweb.settings import WebGroupDBConn
from prj_enteliweb.libraries.enteliweb.PageObjects import selenium_server_connection
from prj_enteliweb.libraries.enteliweb.PageObjects.LoginPage import LoginPageObject
from prj_enteliweb.libraries.enteliweb.PageObjects.MainPage import MainPageObject
from prj_enteliweb.libraries.enteliweb.PageObjects.AdminFrame import AdminFrameObject
from prj_enteliweb.libraries.enteliweb.PageObjects.UnitsFrame import UnitsFrameObject

import time
import win32serviceutil


class RegressionEWEB8481(TestCaseTemplate):
    
    def setUp(self):
        super(RegressionEWEB8481, self).setUp()
        
        # make direct DB connect to webgroup database
        self.myDBConn = Utilities.DBConnect(WebGroupDBConn)
        self.myDBConn.connect()
        
        # load web browser
        self.driver = selenium_server_connection.connect("localhost", "FIREFOX")
        
        # verify login page loaded
        loginPage = LoginPageObject(self.driver)
        result = loginPage.isLoaded()
        errMessage = "Load Login Page (Expected, Current): %s, %s" %(True, result)
        self.assertTrue(result, errMessage)
        
        # login to enteliWEB
        loginPage.username = "Admin"
        loginPage.password = "Password"
        loginPage.click(LoginPageObject.submit)
        time.sleep(3)
        
        # verify enteliWEB Main page loaded
        mainPage = MainPageObject(self.driver)
        result = mainPage.isLoaded()
        errMessage = "Load enteliWEB Main Page (Expected, Current): %s, %s" %(True, result)
        self.assertTrue(result, errMessage)
        
        # load Administration Frame
        mainPage.click(MainPageObject.adminlink)
        time.sleep(3)
        adminFrame = AdminFrameObject(self.driver)
        result = adminFrame.isLoaded()
        errMessage = "Load Administration Frame (Expected, Current): %s, %s" %(True, result)
        self.assertTrue(result, errMessage)
        
        # load Base Units Configuration Frame
        adminFrame.click(AdminFrameObject.baseUnitConfiguration)
        time.sleep(3)
        baseUnitsFrame = UnitsFrameObject(self.driver)
        result = baseUnitsFrame.isLoaded()
        errMessage = "Load Base Unit Configuration Frame (Expected, Current): %s, %s" %(True, result)
        self.assertTrue(result, errMessage)
        
        # change all base units
        self.Change_Base_Units()
        time.sleep(5)
        
        
    def tearDown(self):
        super(RegressionEWEB8481, self).tearDown()
        
        self.myDBConn.disConnect()
        
        self.mouse = None
        self.driver = None
        selenium_server_connection.stop()
        time.sleep(3)
        
        
    def test_Main(self):
        try:
            self.Verify_ReportRateTlinstance()
            self.Verify_DatapointGroup()
        except AssertionError, e: self.verificationErrors.append(str(e))
        self.verifyErrors()
        
        
    def Verify_ReportRateTlinstance(self):
        """ 
        Verify reset on Report_Rate_Tlinstance table
        """
        myDBConn = self.myDBConn
        cursor = myDBConn.cursor.execute("select * from report_rate_tlinstance where not (RecordCount = 0 and State = 1 and Start = Finish and BaselineFinish is NULL)")
        rows = cursor.fetchall()
        if rows:
            errMessage = "Verify Report_Rate_Tlinstance table: found following inconsistent entries"
            for row in rows:
                errMessage = errMessage + "\n" + "%s, %s, %s, %s, %s, %s, %s" %(row.ID, row.FullRef, row.RecordCount, row.State, row.Start, row.Finish, row.BaselineFinish)
            self.verificationErrors.append(errMessage)
        
        
    def Verify_DatapointGroup(self):
        """ 
        Verify reset on Datapoint_Group table
        """
        myDBConn = self.myDBConn
        cursor = myDBConn.cursor.execute("select * from datapoint_group where not (Start is NULL and Finish is NULL and FrameFinish is NULL and DirtyStart is NULL and DirtyFinish is NULL)")
        rows = cursor.fetchall()
        if rows:
            errMessage = "Verify Datapoint_Group table: found following inconsistent entries"
            for row in rows:
                errMessage = errMessage + "\n" + "%s, %s, %s, %s, %s, %s" %(row.ID, row.Start, row.Finish, row.FrameFinish, row.DirtyStart, row.DirtyFinish)
            self.verificationErrors.append(errMessage)        
    
        
    def Change_Base_Units(self):
        """ change all the base units from units page """       
        baseUnitsFrame = UnitsFrameObject(self.driver)
        outdoorTemp = baseUnitsFrame.outdoorTemp
        if outdoorTemp == u'°F':
            baseUnitsFrame.click(UnitsFrameObject.setDefaultMetric)
        else:
            baseUnitsFrame.click(UnitsFrameObject.setDefaultImperial)
            baseUnitsFrame.electricityConsumption = u'MJ'
            baseUnitsFrame.electricityDemand = u'MJ/h'
            baseUnitsFrame.apparentConsumption = u'GVAh'
            baseUnitsFrame.apparentDemand = u'MVA'
        baseUnitsFrame.saveChange()
        
    
    def StartEWEBConnect(self):
        """ Start EWEB connection service on local machine"""
        if win32serviceutil.QueryServiceStatus("Delta enteliWEB Connection service", "localhost")[1] != 4:
            win32serviceutil.StartService("Delta enteliWEB Connection service", "localhost")
            time.sleep(30)
        status = win32serviceutil.QueryServiceStatus("Delta enteliWEB Connection service", "localhost")[1]
        if status == 4:
            return True
        else:
            return False
    
    
    def StopEWEBConnect(self):
        """ Stop EWEB Connection service on local machine"""
        

if __name__ == "__main__":
    unittest.main()