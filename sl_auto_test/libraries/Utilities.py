# FileName: Utilities.py
# Description:
# utilites function or class which will be used by test case for any special usage during the test execution.

import types, pyodbc
from settings import *


class DBConnect( ):
    """ class to model a database connection object using pyodbc"""
    def __init__( self, settingClass ):
        self.Driver = settingClass.DRIVER
        self.Server = settingClass.SERVER
        self.Port = settingClass.PORT
        self.Database = settingClass.DATABASE
        self.User = settingClass.USER
        self.Password = settingClass.PASSWORD
        self.cnxn = None
        self.cursor = None

        
    def connect(self):
        ''' start pyodbc connection'''
        #pyodbc.pooling = False
        self.cnxn = pyodbc.connect(self.getConnString())
        self.cursor = self.cnxn.cursor()
        
    def getConnString(self):
        ''' return the pyodbc dsnless connect string '''
        connString = 'Driver={' + self.Driver + '};Server=' + self.Server + ';Port=' + self.Port + ';Database=' + self.Database + ';User=' + self.User + ';Password=' + self.Password + ';'
        return connString

    def disConnect(self):
        ''' stop pyodbc connection'''
        self.cnxn.close()
        

def trimWhiteSpace(target):
    """ helper function to trim the header and tail white space """
    #if type(target) == types.UnicodeType:
    target = target.lstrip()
    target = target.rstrip()
    return target
    


if __name__ == "__main__":
    myDBConn = DBConnect(WebGroupDBConn)
    print myDBConn.getConnString()

