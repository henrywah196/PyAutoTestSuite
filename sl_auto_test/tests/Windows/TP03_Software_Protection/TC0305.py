#-------------------------------------------------------------------------------
# Test Case:     TC03.05 - Software Trial (TC0305.py)
# Purpose:       The test case verify the client software has the ability to 
#                create / delete / query trial modules using SL API if the client
#                software license support try-before -you-buy.
#
# Preconditions: 1. testing machine, with a supported windows OS installed.
#                2. testing machine, install the test version of windows 
#                   license manager.
#                3. testing machine, install the Delta Controls SL Test Shell, 
#                   which is the same version as the windows license manager.
#                4. internal license generator, generate testing client software 
#                   license. let's say generate license for eweb-pro.
#                6. testing machine, activate the testing client software license 
#                   on windows license manager.
#
# Author:        Henry Wang
# Created:       Jun 16, 2014
#-------------------------------------------------------------------------------
import settings
from libraries.PyAutoTestCase import *
from libraries.SLAT.TestShell import *
import time, datetime

LICENSE = {'product name'      : 'enteliWEB_V2',
           'serial number'     : '1l8Vf-65dF6-QzGa0-4WEEa-Nb5MO-0o5zQ',
           'available modules' : [{'name'  : 'SL_MODULE_WEB_POINTS',
                                   'type'  : 'SL_MODULE_TYPE_COUNTER',
                                   'value' : 5000},
                                  {'name'  : 'SL_MODULE_KAIZEN_ENTELIWEB',
                                   'type'  : 'SL_MODULE_TYPE_BOOLEAN',
                                   'value' : 1},
                                  {'name'  : 'SL_MODULE_KAIZEN_LOCAL',
                                   'type'  : 'SL_MODULE_TYPE_BOOLEAN',
                                   'value' : 1},
                                  {'name'  : 'SL_MODULE_ENTELIVIZ',
                                   'type'  : 'SL_MODULE_TYPE_BOOLEAN',
                                   'value' : 1},
                                  {'name'  : 'SL_MODULE_WEB_APPS',
                                   'type'  : 'SL_MODULE_TYPE_BOOLEAN',
                                   'value' : 1},
                                  {'name'  : 'SL_MODULE_VMACT',
                                   'type'  : 'SL_MODULE_TYPE_BOOLEAN',
                                   'value' : 1}]}

class TC0305_Software_Trial(TestCaseTemplate):

    def setUp(self):
        super(TC0305_Software_Trial, self).setUp()
        self.TS = TestShell(LICENSE['product name'])    # define test shell
        time.sleep(5)
        currentTest = self.id().split('.')[-1]
        print "\nTest: %s" %currentTest
        
        # setup for test02 
        if currentTest == 'test02':
            self.ExpiryDates = {}    # define expiry dates under test
            self.ExpiryDates['today']     = datetime.date.today()
            self.ExpiryDates['next day']   = datetime.date.today() + datetime.timedelta(days=1)
            self.ExpiryDates['day in future'] = datetime.date.today() + datetime.timedelta(days=183)
            
        # setup for test03
        if currentTest == 'test03':
            # define invalid expiry dates under test
            year = (datetime.date.today()).year + 1
            self.InvalidDates = [{'year' : year,     'month' : 2, 'day' : 30},
                                 {'year' : year,     'month' : 9, 'day' : 31},
                                 {'year' : year - 2, 'month' : 1, 'day' : 1}]  
        
        # setup for test04    
        if currentTest == 'test04':
            self.ModuleTypes = [{'name'  : 'SL_MODULE_TYPE_COUNTER', 'value' : 500},
                                {'name'  : 'SL_MODULE_TYPE_VALUE',   'value' : 123}]      

    def tearDown(self):
        super(TC0305_Software_Trial, self).tearDown()
        del self.TS    # remove test shell
        time.sleep(10)
        
    def _getAvailableTrialModules(self):
        ''' test case helper method to return a list of string of trial module names '''
        availableTrialModulesTmp = self.TS.getAvailableTrialModules()
        if availableTrialModulesTmp:
            return availableTrialModulesTmp.keys()
        else:
            return None

    def test01(self):
        ''' Verify add and query all available modules to trial license '''
        ts = self.TS
        current = ts.getLicenseSerial()
        expected = LICENSE['serial number']
        self.verify_IsEqual(expected, current, "Verify client software license serial.")
        
        # verify all available modules can be added to trial license
        step = "\nVerify all available modules can be added to trial license ..."
        print step
        for licenseModule in LICENSE['available modules']:
            ts.addTrialModule(licenseModule['name'], licenseModule['type'], licenseModule['value'])
            time.sleep(50)
        availableTrialModules = self._getAvailableTrialModules()    # available modules in trial license
        for licenseModule in LICENSE['available modules']:
            result = licenseModule['name'] in availableTrialModules
            errMessage = "module '%s' is not found in trial license" %licenseModule['name']
            self.verify_IsTrue(result, errMessage, HaltOnErr=False)
        
        # Verify modules added without issue an expiry date.
        step = "\nVerify modules added without issue an expiry date ..."
        print step
        for licenseModule in availableTrialModules:
            expected = "No expiry"
            current = ts.getModuleExpiry(licenseModule, trialModule=True)
            errMessage = "Verify expiry date for trial module '%s'." %licenseModule
            self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
        
    def test02(self):
        ''' Verify add a module with an valid expire date '''
        ts = self.TS
        current = ts.getLicenseSerial()
        expected = LICENSE['serial number']
        self.verify_IsEqual(expected, current, "Verify client software license serial.")
        
        for key in self.ExpiryDates.keys():
            step = "\nVerify add a module with %s's date as expire date ..." %key
            print step
            licenseModule = LICENSE['available modules'][0]    # trial module under test
            # delete the testing trial module if it existing in trial license
            availableTrialModules = self._getAvailableTrialModules()    # available modules in trial license
            if licenseModule['name'] in availableTrialModules:
                ts.deleteTrialModule(licenseModule['name'])
                time.sleep(50)
            availableTrialModules = self._getAvailableTrialModules()    # available modules in trial license
            result = not (licenseModule['name'] in availableTrialModules)
            errMessage = "Failed deleting trial module '%s'" %licenseModule['name']
            self.verify_IsTrue(result, errMessage)
        
            dateUnderTest = self.ExpiryDates[key]
            expiryYear = dateUnderTest.year
            expiryMonth = dateUnderTest.month
            expiryDay = dateUnderTest.day
            ts.addTrialModule(licenseModule['name'], licenseModule['type'], licenseModule['value'], expiryYear, expiryMonth, expiryDay)
            time.sleep(50)
            availableTrialModules = self._getAvailableTrialModules()    # available modules in trial license
            result = licenseModule['name'] in availableTrialModules
            errMessage = "verify add trial module '%s'" %licenseModule['name']
            self.verify_IsTrue(result, errMessage)
            expected = dateUnderTest.strftime("%Y/%m/%d/* 23:59:59.99")
            current = ts.getModuleExpiry(licenseModule['name'], trialModule=True)
            errMessage = "verify expiry date for trial moduel '%s'" %licenseModule['name']
            self.verify_IsEqual(expected, current, errMessage, HaltOnErr=False)
        
    def test03(self):
        ''' Verify add a module with an invalid expire date '''
        ts = self.TS
        current = ts.getLicenseSerial()
        expected = LICENSE['serial number']
        self.verify_IsEqual(expected, current, "Verify client software license serial.")
        
        # verify module cannot be added if an invalid date is issued as expiry date.
        for invalidDate in self.InvalidDates:
            step = "\nVerify module cannot be added if an invalid date '%s-%s-%s' is issued as expiry date ..." %(invalidDate['year'], invalidDate['month'], invalidDate['day'])
            print step
            licenseModule = LICENSE['available modules'][0]    # trial module under test
            # delete the testing trial module if it existing in trial license
            availableTrialModules = self._getAvailableTrialModules()    # available modules in trial license
            if licenseModule['name'] in availableTrialModules:
                ts.deleteTrialModule(licenseModule['name'])
                time.sleep(50)
            availableTrialModules = self._getAvailableTrialModules()    # available modules in trial license
            result = not (licenseModule['name'] in availableTrialModules)
            errMessage = "Failed deleting trial module '%s'" %licenseModule['name']
            self.verify_IsTrue(result, errMessage)
        
            expiryYear = invalidDate['year']
            expiryMonth = invalidDate['month']
            expiryDay = invalidDate['day']
            ts.addTrialModule(licenseModule['name'], licenseModule['type'], licenseModule['value'], expiryYear, expiryMonth, expiryDay)
            time.sleep(50)
            availableTrialModules = self._getAvailableTrialModules()    # available modules in trial license
            result = licenseModule['name'] not in availableTrialModules
            errMessage = "verify trial module '%s' not being added with invalid date '%s-%s-%s'" %(licenseModule['name'], invalidDate['year'], invalidDate['month'], invalidDate['day'])
            self.verify_IsTrue(result, errMessage, HaltOnErr=False)
        
    def test04(self):
        ''' verify trial module can be added with any module type '''
        ts = self.TS
        current = ts.getLicenseSerial()
        expected = LICENSE['serial number']
        self.verify_IsEqual(expected, current, "Verify client software license serial.")
        
        # verify trial module can be added with any module type
        licenseModule = LICENSE['available modules'][1]    # trial module under test
        for moduleType in self.ModuleTypes:
            step = "\nVerify add trial module '%s' with module type '%s' ..." %(licenseModule['name'], moduleType['name'])
            print step
            # delete the testing trial module if it existing in trial license
            availableTrialModules = self._getAvailableTrialModules()    # available modules in trial license
            if licenseModule['name'] in availableTrialModules:
                ts.deleteTrialModule(licenseModule['name'])
                time.sleep(50)
            availableTrialModules = self._getAvailableTrialModules()    # available modules in trial license
            result = not (licenseModule['name'] in availableTrialModules)
            errMessage = "Failed deleting trial module '%s'" %licenseModule['name']
            self.verify_IsTrue(result, errMessage)
        
            nameOfModule = licenseModule['name']
            typeOfModule = moduleType['name']
            valueOfModule = moduleType['value']
            ts.addTrialModule(nameOfModule, typeOfModule, valueOfModule)
            time.sleep(50)
            availableTrialModules = self._getAvailableTrialModules()    # available modules in trial license
            result = nameOfModule in availableTrialModules
            errMessage = "Verify add trial module '%s' with module type '%s'" %(nameOfModule, typeOfModule)
            self.verify_IsTrue(result, errMessage, HaltOnErr=False)
        
    
    def test05(self):
        ''' Verify delete trial modules '''
        ts = self.TS
        current = ts.getLicenseSerial()
        expected = LICENSE['serial number']
        self.verify_IsEqual(expected, current, "Verify client software license serial.")
        
        # delete all existing trial modules
        step = "\nVerify deleting all existing trial modules right away ..."
        print step
        availableTrialModules = self._getAvailableTrialModules()    # available modules in trial license
        if availableTrialModules:
            for trialModule in availableTrialModules:
                ts.deleteTrialModule(trialModule)
                time.sleep(50)
        current = self._getAvailableTrialModules()    # available modules in trial license
        expected = None
        self.verify_IsEqual(expected, current, "Verify all existing trial modules have been removed")
        
        step = "\nVerify deleting an non expiry module in a day..."
        print step
        licenseModule = LICENSE['available modules'][1]    # trial module under test
        nameOfModule = licenseModule['name']
        typeOfModule = licenseModule['type']
        valueOfModule = licenseModule['value']
        ts.addTrialModule(nameOfModule, typeOfModule, valueOfModule)
        time.sleep(50)
        availableTrialModules = self._getAvailableTrialModules()    # available modules in trial license
        result = nameOfModule in availableTrialModules
        errMessage = "Verify add trial module '%s' with no expiry date" %nameOfModule
        self.verify_IsTrue(result, errMessage)
        # set the trial module to be deleted in a day
        ts.deleteTrialModule(nameOfModule, 1)
        time.sleep(50)
        current = ts.getTrialModuleDeleteDate(nameOfModule)
        dateToBeDeleted = datetime.date.today() + datetime.timedelta(days=1)
        expected = dateToBeDeleted.strftime('%Y/%m/%d/* 00:00:00.00')
        errMessage = "Verify the delete date for trial module '%s'" %nameOfModule
        self.verify_IsEqual(expected, current, errMessage)
        outputMessage = "\nPlease manually verify the trial module '%s' has been removed after the system time passing 4AM on %s-%s-%s" %(nameOfModule, dateToBeDeleted.year, dateToBeDeleted.month, dateToBeDeleted.day)
        print outputMessage
        
        
    def test06(self):
        ''' Verify auto delete expired trial modules '''
        ts = self.TS
        current = ts.getLicenseSerial()
        expected = LICENSE['serial number']
        self.verify_IsEqual(expected, current, "Verify client software license serial.")
        
        # define trial module under test
        licenseModule = LICENSE['available modules'][0]
        nameOfModule = licenseModule['name']
        typeOfModule = licenseModule['type']
        valueOfModule = licenseModule['value']
        
        # delete the testing trial module if it existing in trial license
        step = "\nDelete the testing trial module if it existing in trial license..."
        print step
        availableTrialModules = self._getAvailableTrialModules()    # available modules in trial license
        if licenseModule['name'] in availableTrialModules:
            ts.deleteTrialModule(licenseModule['name'])
            time.sleep(50)
        availableTrialModules = self._getAvailableTrialModules()    # available modules in trial license
        result = not (licenseModule['name'] in availableTrialModules)
        errMessage = "Failed deleting the existing trial module '%s'" %licenseModule['name']
        self.verify_IsTrue(result, errMessage)
        
        # add a trial modules with next day as expiry date under test
        step = "\nAdd the test trial module with next day as expiry date under test..."
        print step
        dateToBeExpired = datetime.date.today() + datetime.timedelta(days=1)
        expiryYear = dateToBeExpired.year
        expiryMonth = dateToBeExpired.month
        expiryDay = dateToBeExpired.day
        ts.addTrialModule(nameOfModule, typeOfModule, valueOfModule, expiryYear, expiryMonth, expiryDay)
        time.sleep(50)
        availableTrialModules = self._getAvailableTrialModules()    # available modules in trial license
        result = nameOfModule in availableTrialModules
        errMessage = "Verify add trial module '%s' with expiry date '%s-%s-%s'" %(nameOfModule, expiryYear, expiryMonth, expiryDay)
        self.verify_IsTrue(result, errMessage)
        current = ts.getModuleExpiry(nameOfModule, trialModule=True)
        expected = dateToBeExpired.strftime('%Y/%m/%d/* 23:59:59.99')
        errMessage = "Verify the expire date for trial module '%s'" %nameOfModule
        self.verify_IsEqual(expected, current, errMessage)
        outputMessage = "\nPlease manually verify the trial module '%s' has been removed after the system time passing 4AM on %s-%s-%s" %(nameOfModule, expiryYear, expiryMonth, expiryDay)
        print outputMessage
        

if __name__ == "__main__":
    TC0305_Software_Trial.execute()