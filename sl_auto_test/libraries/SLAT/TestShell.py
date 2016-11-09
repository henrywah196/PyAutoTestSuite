#-------------------------------------------------------------------------------
# Name:        TestShell.py
# Purpose:     test api which using SL test shell python model
#
# Author:      wah
# Created:     09/04/2014
#-------------------------------------------------------------------------------
import time
import sltest

class TestShell(object):
    """ class to model SL test shell python model """
    
    def __init__(self, clientName):
        #import sltest
        self.Modules = dict((v,k) for k, v in sltest.SL_MODULE_DICT.iteritems())
        
        # workaround for enteliBRIDGE protocol modules
        self.Modules["SL_MODULE_GW_ModBusTCP"] = str(sltest.SL_MODULE_GW_PROTOCOL0 + 2)
        self.Modules["SL_MODULE_GW_N2Open"] = str(sltest.SL_MODULE_GW_PROTOCOL0 + 4)
        self.Modules["SL_MODULE_GW_TestProto1"] = str(sltest.SL_MODULE_GW_PROTOCOL0 + 100)
    
        self.ModuleTypes = {0 : 'SL_MODULE_TYPE_INVALID',
                            1 : 'SL_MODULE_TYPE_BOOLEAN',
                            2 : 'SL_MODULE_TYPE_VALUE',
                            3 : 'SL_MODULE_TYPE_COUNTER'}
    
        self.Clients = {}
        self.Clients['BACnet Server'] = sltest.SL_CLIENT_BNSERVER
        self.Clients['Earthright Energy Dashboard'] = sltest.SL_CLIENT_ENERGYDASHBOARD
        self.Clients['enteliBRIDGE'] = sltest.SL_CLIENT_GATEWAY
        self.Clients['Kaizen Energy Local'] = sltest.SL_CLIENT_KAIZEN_ENERGY_LOCAL
        self.Clients['Python API'] = sltest.SL_CLIENT_PYTS
        self.Clients['enteliWEB'] = sltest.SL_CLIENT_WEBSERVER
        self.Clients['enteliWEB_V2'] = sltest.SL_CLIENT_WEBSERVER_V2
        try: # a work around for an error BACnetException: 65::1027
            self.sl = sltest.sl(self.Clients[clientName])
        except:
            time.sleep(3)
            self.sl = sltest.sl(self.Clients[clientName])
        self.clientName = clientName
            
    def __del__(self):
        del self.sl
        
    def isLicenseEnabled(self):
        """ verify if the specified client license is enabled """
        result = True
        SL = self.sl
        try:
            SL.getserial()
        except:
            result = False
        return result
    
    def getLicenseSerial(self):
        """ return the license serial number """
        result = None
        SL = self.sl
        try:
            result = SL.getserial()
        except:
            result = None
        return result
    
    def getSubscriptionStatus(self):
        """ return the license subscription status """
        result = None
        SL = self.sl
        try:
            result = SL.getmoduleexpiry(sltest.SL_MODULE_SUBSCRIPTION)
        except:
            result = None
        return result
    
    def getActivationStatus(self):
        """ return the license activation status """
        result = None
        SL = self.sl
        try:
            result = SL.getmoduleexpiry(sltest.SL_MODULE_ACTIVE)
        except:
            result = None
        return result
    
    def getCounterPoints(self, ModuleName, trialModule=False):
        """ return the counter points of a counter module or trial module """
        result = None
        SL = self.sl
        hdl = None
        try:
            if trialModule:
                trialModules = self.getAvailableTrialModules()
                if trialModules:
                    if ModuleName in trialModules:
                        if self.getModuleType(ModuleName, trialModule=True)== 'SL_MODULE_TYPE_COUNTER':
                            hdl = self.openTrial()
                            result = SL.auxmodulevalidatecount(hdl, int(self.Modules[ModuleName]))
            else:
                if self.getModuleType(ModuleName) == 'SL_MODULE_TYPE_COUNTER':
                    result = SL.modulevalidatecount(int(self.Modules[ModuleName]))
        except:
            result = None
        if hdl:
            self.closeTrial(hdl)
        return result  
    
    def getModuleType(self, ModuleName, trialModule=False, byNumber=False):
        """ return the type of the module or trial Module 
            if byNumber is True return the number only """
        result = None
        SL = self.sl
        hdl = None
        try:
            if trialModule:
                trialModules = self.getAvailableTrialModules()
                if trialModules:
                    if ModuleName in trialModules:
                        hdl = self.openTrial()
                        number = SL.auxgetmoduletype(hdl, int(self.Modules[ModuleName]))
                        if byNumber:
                            result = number
                        else:
                            result = self.ModuleTypes[number]
            else:
                number = SL.getmoduletype(int(self.Modules[ModuleName]))
                if byNumber:
                    result = number
                else:
                    result = self.ModuleTypes[number]
        except:
            result = None
        if hdl:
            self.closeTrial(hdl)
        return result  
    
    def getModuleExpiry(self, ModuleName, trialModule=False):
        """ Gets the expiry date of the module in the license """
        result = None
        SL = self.sl
        hdl = None
        try:
            if trialModule:
                hdl = self.openTrial()
                result = SL.auxgetmoduleexpiry(hdl, int(self.Modules[ModuleName]))
            else:
                result = SL.getmoduleexpiry(int(self.Modules[ModuleName]))
        except:
            result = None
        if hdl:
            self.closeTrial(hdl)
        return result
    
    def getAvailableModules(self):
        """ return a dic of modules which the license have """
        result = None
        SL = self.sl
        for key, value in self.Modules.iteritems():
            errFound = False
            try:
                SL.modulevalidateboolean(int(value))
                if not result:
                    result = {}
                result[key] = value
            except Exception, e:
                errFound = True
            if errFound:
                try:
                    SL.modulevalidatecount(int(value))
                    if not result:
                        result = {}
                    result[key] = value
                    errFound = False
                except Exception, e:
                    errFound = True
            if errFound:
                try:
                    SL.modulevalidatevalue(int(value))
                    if not result:
                        result = {}
                    result[key] = value
                    errFound = False
                except Exception, e:
                    pass
        return result
    
    def openTrial(self):
        """ return the handler of trial license """
        SL = self.sl
        try: return SL.auxopentrial()
        except: return SL.trialinit()
    
    def closeTrial(self, handle):
        """ close an opened trial license """
        SL = self.sl
        SL.auxclose(handle)
    
    def getAvailableTrialModules(self):
        """ return a dic of modules which the trial license have """
        result = None
        SL = self.sl
        hdl = self.openTrial()
        for key, value in self.Modules.iteritems():
            errFound = False
            try:
                SL.auxmodulevalidateboolean(hdl, int(value))
                if not result:
                    result = {}
                result[key] = value
            except Exception, e:
                errFound = True
            if errFound:
                try:
                    SL.auxmodulevalidatecount(hdl, int(value))
                    if not result:
                        result = {}
                    result[key] = value
                    errFound = False
                except Exception, e:
                    errFound = True
            if errFound:
                try:
                    SL.auxmodulevalidatevalue(hdl, int(value))
                    if not result:
                        result = {}
                    result[key] = value
                    errFound = False
                except Exception, e:
                    pass
        self.closeTrial(hdl)
        return result
    
    def addTrialModule(self, ModuleName, ModuleType, ModuleValue, expiryYear=None, expiryMonth=None, expiryDay=None):
        """ Creates a new module in the trial license """
        SL = self.sl
        hdl = self.openTrial()
        try:
            moduleType = None
            for key, value in self.ModuleTypes.iteritems():
                if value == ModuleType:
                    moduleType = key
                    break
            if moduleType:
                if expiryYear == None and expiryMonth == None and expiryDay == None:
                    SL.auxmodulecreate(hdl, int(self.Modules[ModuleName]), moduleType, ModuleValue)
                else:
                    SL.auxmodulecreate(hdl, int(self.Modules[ModuleName]), moduleType, ModuleValue, expiryYear, expiryMonth, expiryDay)
        except Exception, e:
            self.closeTrial(hdl)
            raise Exception(str(e))
        self.closeTrial(hdl)
    
    def deleteTrialModule(self, ModuleName, numberOfDays=None):
        """ delete a module from trial license in number of days """
        SL = self.sl
        hdl = self.openTrial()
        try:
            if numberOfDays:
                SL.auxmoduledelete(hdl, int(self.Modules[ModuleName]), numberOfDays)
            else:
                SL.auxmoduledelete(hdl, int(self.Modules[ModuleName]))
        except Exception, e:
            self.closeTrial(hdl)
            raise Exception(str(e))
        self.closeTrial(hdl)
        
    def getTrialModuleDeleteDate(self, ModuleName):
        """ Gets the future delete date of the module in the trial license """
        result = None
        SL = self.sl
        hdl = self.openTrial()
        try:
            result = SL.auxgetmoduledeletedate(hdl, int(self.Modules[ModuleName]))
        except:
            result = None
        self.closeTrial(hdl)
        return result

def main():
    client = 'enteliWEB_V2'
    ts = TestShell(client)
    result = ts.getModuleType('SL_MODULE_SUBSCRIPTION')
    print result
    result = ts.getModuleType('SL_MODULE_KAIZEN_ENTELIWEB', trialModule=True)
    print result
    ts.addTrialModule('SL_MODULE_KAIZEN_ENTELIWEB', 'SL_MODULE_TYPE_BOOLEAN', 1, 2014, 12, 31)
    

if __name__ == '__main__':
    main()
