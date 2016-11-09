'''
Created on Oct 29, 2015

@author: hwang
'''
import pyodbc
import settings


class CopperCubeDBObj(object):
    """ Model enteliWEB webgroup dtabase"""
    
    def __init__(self, infoHash):
        self.Driver = infoHash["DRIVER"]
        self.Server = infoHash["SERVER"]
        self.Port = infoHash["PORT"]
        self.Database = infoHash["DATABASE"]
        self.User = infoHash["USER"]
        self.Password = infoHash["PASSWORD"]
        self.cnxn = None
        self.cursor = None
        self._connect()
    
    def __repr__(self):
        super(CopperCubeDBObj, self).__repr__()
        
    def __del__(self):
        self._disConnect()
        
    def _connect(self):
        ''' start pyodbc connection'''
        self.cnxn = pyodbc.connect(self._getConnString())
        self.cursor = self.cnxn.cursor()
        
    def _disConnect(self):
        ''' stop pyodbc connection'''
        if self.cnxn is not None:
            self.cnxn.close()
            
    def _getDriverType(self):
        ''' verify whether it is MYSQL, MSSQL or PostgreSQL '''
        if 'MySQL' in self.Driver:
            return 'MYSQL'
        elif "PostgreSQL" in self.Driver:
            return "POSTGRESQL"
        else:
            return 'MSSQL'
        
    def _getConnString(self):
        ''' return the pyodbc dsnless connect string '''
        connString = 'Driver={' + self.Driver + '};Server=' + self.Server + ';Port=' + self.Port + ';Database=' + self.Database + ';UID=' + self.User + ';PWD=' + self.Password + ';'
        return connString
    
    def getTLInstanceStart(self, rawTLInstanceTable):
        """
        looking for the first timestamp for the tl instance in Historian TLData table
        """
        cursor = self.cursor.execute("select ts from %s where variant in (2, 4, 5) order by seq asc limit 1"%rawTLInstanceTable)
        row = cursor.fetchone()
        return row.ts
    
    def getSampleInterval(self, tlReference):
        """
        return the sample interval (seconds) for the given tl reference. 
        the format of tlReference is //QA_Test_Network/1100.TL201
        """
        try:
            currentDBString = self.Database
            self.Database = "arsetup"
            self._connect()
            cursor = self.cursor.execute("select samplerate from tlconfig where tlreference = ?", tlReference)
            row = cursor.fetchone()
            return row.samplerate
        finally:
            self.Database = currentDBString
            self._connect()
        
        
    
        
        
if __name__ == "__main__":
    coppercube = CopperCubeDBObj()
    del coppercube
    
    
        