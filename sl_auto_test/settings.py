# Filename: settings.py
# Description: settings for PyAutoTestSuite.


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
#class Foo(object): 
#    __metaclass__=ROType 
#    BAR = const_value(1) 
#    BAZ = 2 
# 
#class Bit(object): 
#    __metaclass__=ROType 
#    BOO = const_value(3) 
#    BAN = 4     


# Settings Start From Here
class General():
    """ General Settings 
    """
    __metaclass__ = ROType
    BROWSER = const_value("FIREFOX")
    #BROWSER = const_value('CHROME')
    #BROWSER = const_value('IE')
    WEBDRIVERLOCATION = const_value('D:\\PyAutoTestSuite\\')
    BASE_URL = const_value('http://192.168.1.150/')


class WebGroupDBConn():
    ''' Web Group DB Connection settings
    '''
    __metaclass__=ROType
    DRIVER = const_value('MySQL ODBC 5.1 Driver')
    SERVER = const_value('localhost')
    PORT = const_value('49250')
    DATABASE = const_value('webgroup')
    USER = const_value('root')
    PASSWORD = const_value('xwing')


if __name__ == "__main__":
    print WebGroupDBConn.DRIVER
    print WebGroupDBConn.SERVER
    print WebGroupDBConn.PORT
    print WebGroupDBConn.DATABASE
    print WebGroupDBConn.USER
    print WebGroupDBConn.PASSWORD
