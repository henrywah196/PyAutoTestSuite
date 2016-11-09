# coding: utf-8
'''
Regression for EWEB-8963
Synopsis: More than one demand entries are displayed for month


Created on Jul 25, 2013
@author: hwang
'''
import time
from prj_enteliweb.libraries.PATS.PyAutoTestCase import *
from prj_enteliweb.libraries.enteliweb import Utilities
from prj_enteliweb.settings import WebGroupDBConn


DEMAND = ['Apparent_Power_Electric',
          'Power_Electric',
          'Flow_Volume_Gas',
          'Power_Gas',
          'Flow_Volume_Water',
          'Flow_Volume_Fuel',
          'Power_Thermal',
          'Flow_Mass_Steam']


class RegressionEWEB8963(TestCaseTemplate):
    
    def setUp(self):
        super(RegressionEWEB8963, self).setUp()
        
        # make direct DB connect to webgroup database
        self.myDBConn = Utilities.DBConnect(WebGroupDBConn)
        self.myDBConn.connect()
        
        # obtain engine info
        self.EngineList = []
        myDBConn = self.myDBConn
        cursor = myDBConn.cursor.execute("select ID, Name from report_rate_engine order by ID")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                EUT = Engine()
                EUT.Name = row.Name
                EUT.ID = row.ID                
                self.EngineList.append(EUT)
        if self.EngineList:
            for EUT in self.EngineList:
                cursor = myDBConn.cursor.execute("select distinct type from report_rate where engine = ?", EUT.ID)
                rows = cursor.fetchall()
                if rows:
                    for row in rows:
                        if row.type in DEMAND:
                            EUT.Type.append(row.type)
        
        
    def tearDown(self):
        super(RegressionEWEB8963, self).tearDown()
        
        self.myDBConn.disConnect()
        
       
        
        
    def test_Main(self):
        try:
            for EUT in self.EngineList:
                print "verify Engine: " + EUT.Name
                self.Verify_DemandSamples(EUT)
        except AssertionError, e: self.verificationErrors.append(str(e))
        self.verifyErrors()
        
    
    def Verify_DemandSamples(self, EUT):
        myDBConn = self.myDBConn
        for energyType in EUT.Type:
            monthList = []
            cursor = myDBConn.cursor.execute("select distinct date_format(timestamp, '%Y-%m') as month from report_rate where engine = ? and type = ?", EUT.ID, energyType)
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    monthList.append(row.month)
            if monthList:
                for month in monthList:
                    cursor = myDBConn.cursor.execute("select * from report_rate where engine = ? and type = ? and date_format(timestamp, '%Y-%m') = ?", EUT.ID, energyType, month)
                    rows = cursor.fetchall()
                    if len(rows) > 1:
                        errMsg = "Engine: " + EUT.Name + "\n"
                        for row in rows:
                            errMsg = errMsg + str(row.Engine) + ", " + str(row.Rate) + ", " + str(row.Value) + ", " + row.Type + ", " + str(row.Timestamp) + "\n"
                        self.verificationErrors.append(errMsg)
                


class Engine():
    def __init__(self):
        self.Name = None
        self.ID = None
        self.Type = []



        
          
    
        
    
        

if __name__ == "__main__":
    unittest.main()