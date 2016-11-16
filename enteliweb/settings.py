'''
FileName: settings.py
Description: general settings which will be used by py auto test suite.
Created on Jan 31, 2013
@author: WAH
'''


###################
# General Settings
###################
TimeZones = ["America/Vancouver", "America/Sao_Paulo"]
TimeZone = TimeZones[0]
BROWSER  = "FIREFOX"
#BROWSER = "CHROME"
#BROWSER = "IE"
HOSTS = ["localhost", "delsry3860.network.com", "win-0lr5jb1f7u0.network.com", "192.168.2.146"]
HOST     = HOSTS[2]
PLATFORM = "Windows 2012 Server"
USERNAME = "Admin"
PASSWORD = "Password"


######################
# Database Connection
######################
WebGroupDBConn = {
                   "DRIVER"   : "MySQL ODBC 5.3 Unicode Driver",
                   "SERVER"   : HOST,
                   "PORT"     : "49250",
                   "DATABASE" : "webgroup",
                   "USER"     : "tester",
                   "PASSWORD" : "demo"
                 }
      
ArchiverDB = {
               "HistDBConn_webteamlinux" : {
                                             "TYPE"     : "Historian",
                                             "DRIVER"   : "MySQL ODBC 5.3 Unicode Driver",
                                             "SERVER"   : "webteamlinux.deltacontrols.com",
                                             "PORT"     : "3306",
                                             "DATABASE" : "reportverification",
                                             "USER"     : "root",
                                             "PASSWORD" : "xwing"
                                            },
               
               "HistDBConn_webteamwindows" : {
                                               "TYPE"     : "Historian",
                                               "DRIVER"   : "SQL Server",
                                               "SERVER"   : "webteamwindows",
                                               "PORT"     : "1433",
                                               "DATABASE" : "HistorianDB",
                                               "USER"     : "sa",
                                               "PASSWORD" : "WebTeamServer"
                                             },
        
               "CubeDBConn_cucube228" : {
                                          "TYPE"     : "CopperCube",
                                          "DRIVER"   : "PostgreSQL Unicode",
                                          "SERVER"   : "cucube228.network.com",
                                          "PORT"     : "5432",
                                          "DATABASE" : "artrends",
                                          "USER"     : "postgres",
                                          "PASSWORD" : ""
                                        },
    
               "CubeDBConn_cucube234" : {
                                          "TYPE"     : "CopperCube",
                                          "DRIVER"   : "PostgreSQL Unicode",
                                          "SERVER"   : "cucube234.network.com",
                                          "PORT"     : "5432",
                                          "DATABASE" : "artrends",
                                          "USER"     : "postgres",
                                          "PASSWORD" : ""
                                        }
             }


'''
# internal use only to make attribute read only
class const_value (object): 
    def __init__(self, value): 
        self.__value = value 
 
    def make_property(self): 
        return property(lambda cls: self.__value) 
 
class ROType(type): 
    def __new__(cls,classname,bases,classdict): 
        class UniqeROType (cls): 
            pass 
 
        for attr, value in classdict.items(): 
            if isinstance(value, const_value): 
                setattr(UniqeROType, attr, value.make_property()) 
                classdict[attr] = value.make_property() 
 
        return type.__new__(UniqeROType,classname,bases,classdict)
    
# this is a sample usage
class Foo(object): 
    __metaclass__=ROType 
    BAR = const_value(1) 
    BAZ = 2 
 
class Bit(object): 
    __metaclass__=ROType 
    BOO = const_value(3) 
    BAN = 4
'''   


