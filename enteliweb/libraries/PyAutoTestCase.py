import sys
import unittest
#import xmlrunner
from libraries import HTMLTestRunner
from xml.sax.handler import ContentHandler
from xml.sax import parseString

__unittest = True    # hide detailed traceback


class TestSuiteTemplate(unittest.TestSuite):
    
    def execute(self, verbosity=1, outputtype="default", output="", title="Test Report Title", description="Test Report Description"):
        """ execute the test suite using the assigned test runner """
        if outputtype == "xml":
            with open(output, 'wb') as output:
                testRunner = xmlrunner.XMLTestRunner(verbosity=verbosity, output=output)
                result = testRunner.run(self)
        elif outputtype == "html":
            with open(output, 'wb') as output:
                testRunner = HTMLTestRunner.HTMLTestRunner(stream=output, verbosity=verbosity, title=title, description=description)
                result = testRunner.run(self)
        else:
            testRunner = unittest.TextTestRunner(verbosity=verbosity)
            result = testRunner.run(self)
            
        return result


class TestCaseTemplate(unittest.TestCase):
    
    def setUp(self):
        self.verificationErrors = []
        self.addCleanup(self.verifyErrors)
        self.currentTest = self.id().split('.')[-1]

    def tearDown(self):
        #try: self.assertEqual([], self.verificationErrors, self.genErrorsMessage())
        #except: 
        #    self._resultForDoCleanups.addFailure(self, sys.exc_info())
        pass
    
           
    def doCleanups(self):
        """override the original TestCase.doCleanups() not add error to result for verifyErrors()"""
        result = self._resultForDoCleanups
        ok = True
        while self._cleanups:
            function, args, kwargs = self._cleanups.pop(-1)
            try:
                function(*args, **kwargs)
            except KeyboardInterrupt:
                raise
            except:
                ok = False
                if function == self.verifyErrors:
                    result.addFailure(self, sys.exc_info())
                else:
                    result.addError(self, sys.exc_info())
        return ok

    def genErrorsMessage(self):
        """ format the error messages before it is used by test report
        """
        errMessage = ''
        if len(self.verificationErrors) != 0:
            for err in self.verificationErrors:
                if errMessage == '':
                    errMessage = '\n' + err
                else:
                    errMessage = errMessage + '\n\n' + err
        return errMessage

    def verifyErrors(self):
        """ verify if the container is blank
        """
        try:
            longMessageState = self.longMessage
            self.longMessage = False 
            result = not self.verificationErrors
            self.assertTrue(result, self.genErrorsMessage())
        finally: 
            self.verificationErrors = []
            self.longMessage = longMessageState
            
    def verify_IsAlmostEqual(self, expected, current, places=7, errMessage=None, HaltOnErr=True, ScreenCapture=False):
        """  verify expected and current are almost equal
             which is used to compare flosting / decimal value
        """
        errMessage = "%s\nExpected: %s\nCurrent: %s" %(errMessage, expected, current)
        try:
            longMessageState = self.longMessage
            self.longMessage = False
            if HaltOnErr:
                self.assertAlmostEqual(expected, current, places, errMessage)
            else:
                try: self.assertAlmostEqual(expected, current, places, errMessage)
                except AssertionError, e: self.verificationErrors.append(unicode(e))
        finally:
            self.longMessage = longMessageState
    
    def verify_IsEqual(self, expected, current, errMessage, HaltOnErr=True, ScreenCapture=False):
        """verify if current is equal to expected"""   
        if (type(expected) is dict) and (type(current) is dict):
            self.verify_IsDicEqual(expected, current, errMessage, HaltOnErr, ScreenCapture)
        elif (type(expected) is list) and (type(current) is list):
            self.verify_IsListEqual(expected, current, errMessage, HaltOnErr, ScreenCapture)
        else:
            errMessage = "%s\nExpected: %s\nCurrent: %s" %(errMessage, expected, current)
            try:
                longMessageState = self.longMessage
                self.longMessage = False
                if HaltOnErr:
                    self.assertEqual(expected, current, errMessage)
                else:
                    try: self.assertEqual(expected, current, errMessage)
                    except AssertionError, e: self.verificationErrors.append(unicode(e))
            finally:
                self.longMessage = longMessageState
    
    def verify_IsListEqual(self, expected, current, errMessage, HaltOnErr=True, ScreenCapture=False):
        """
        verify if list current and expected are equal
        """        
        errMessage = "%s\nExpected: %s\nCurrent: %s" %(errMessage, expected, current)
        try:
            longMessageState = self.longMessage
            self.longMessage = False
            if HaltOnErr:
                self.assertListEqual(expected, current, errMessage)
            else:
                try: self.assertListEqual(expected, current, errMessage)
                except AssertionError, e: self.verificationErrors.append(unicode(e))
        finally:
            self.longMessage = longMessageState
            
            
    def verify_IsDicEqual(self, expected, current, errMessage, HaltOnErr=True, ScreenCapture=False):
        """
        verify if dictionary current and expected are equal
        """
        expectedString = ''.join('{}:{} '.format(key, val) for key, val in sorted(expected.items()))
        currentString = ''.join('{}:{} '.format(key, val) for key, val in sorted(current.items()))
        errMessage = "%s\nExpected: %s\nCurrent: %s" %(errMessage, expectedString, currentString)
        try:
            longMessageState = self.longMessage
            self.longMessage = False
            if HaltOnErr:
                self.assertEqual(expected, current, errMessage)
            else:
                try: self.assertEqual(expected, current, errMessage)
                except AssertionError, e: self.verificationErrors.append(unicode(e))
        finally:
            self.longMessage = longMessageState
        
            
    def verify_IsTrue(self, result, errMessage, HaltOnErr=True, ScreenCapture=False):
        "verify is result is True"
        errMessage = "%s\nExpected: %s\nCurrent: %s" %(errMessage, True, result)
        try:
            longMessageState = self.longMessage
            self.longMessage = False
            if HaltOnErr:
                self.assertTrue(result, errMessage)
            else:
                try: self.assertTrue(result, errMessage)
                except AssertionError, e: self.verificationErrors.append(unicode(e))
        finally:
            self.longMessage = longMessageState
            
    def verify_XML_IsWellFormed(self, result, errMessage=None, HaltOnErr=True):
        """ verify the XML string is well-formed """
        try:
            parseString(result, ContentHandler())
            #print "XML string is well-formed"
        except Exception, e:
            #print "XML string is NOT well-formed! %s"%str(e)
            if errMessage:
                errMessage = "%s: %s" %(errMessage, str(e))
            else:
                errMessage = "XML string is NOT well-formed! %s"%unicode(e)
            if HaltOnErr:
                raise AssertionError(errMessage)
            else:
                self.verificationErrors.append(errMessage)
    
    @classmethod
    def suite(cls):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(cls))
        return suite
        
    @classmethod
    def execute(cls, verbosity=2):
        unittest.main(verbosity=verbosity)