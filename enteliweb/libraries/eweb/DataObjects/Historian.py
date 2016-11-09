'''
Created on Oct 29, 2015

@author: hwang
'''
import pyodbc
import settings


class HistorianDBObj(object):
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
        super(HistorianDBObj, self).__repr__()
        
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
        if self._getDriverType == 'MYSQL':
            connString = 'Driver={' + self.Driver + '};Server=' + self.Server + ';Port=' + self.Port + ';Database=' + self.Database + ';User=' + self.User + ';Password=' + self.Password + ';'
        return connString
    
    def getTLInstanceStart(self, rawTLInstanceID):
        """
        looking for the first timestamp for the tl instance in Historian TLData table
        """
        cursor = None
        if self._getDriverType() == 'MSSQL':
            cursor = self.cursor.execute("select Top 1 Timestamp from TLData where tlinstance = ? and type = 0 order by RecordNumber asc", rawTLInstanceID)
        else:
            cursor = self.cursor.execute("select Timestamp from TLData where tlinstance = ? and type = 0 order by RecordNumber asc limit 1", rawTLInstanceID)
        row = cursor.fetchone()
        return row.Timestamp
    
    def getSampleInterval(self, tlReference):
        """
        return the sample interval (seconds) for the given tl reference. 
        @tlReference - tlinstance ID 
        """
        cursor = self.cursor.execute("select LogInterval from tl where TLInstance = ?", tlReference)
        row = cursor.fetchone()
        return row.LogInterval  
    
    
        
        
        
if __name__ == "__main__":
    historian = HistorianDBObj()
    del historian
    
    
        