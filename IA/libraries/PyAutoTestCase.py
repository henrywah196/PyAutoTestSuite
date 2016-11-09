import sys
import unittest
from xml.sax.handler import ContentHandler
from xml.sax import parseString

class TestCaseTemplate(unittest.TestCase):
    
    def setUp(self):
        self.verificationErrors = []
        self.addCleanup(self.verifyErrors)

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
        try: self.assertEqual([], self.verificationErrors, self.genErrorsMessage())
        finally: self.verificationErrors = []
    
    def verify_IsEqual(self, expected, current, errMessage, HaltOnErr=True, ScreenCapture=False):
        """verify if current is equal to expected"""   
        if (type(expected) is dict) and (type(current) is dict):
            expectedString = ''.join('{}:{} '.format(key, val) for key, val in sorted(expected.items()))
            currentString = ''.join('{}:{} '.format(key, val) for key, val in sorted(current.items()))
            errMessage = "%s\nExpected: %s\nCurrent: %s" %(errMessage, expectedString, currentString)
        else:
            errMessage = "%s\nExpected: %s\nCurrent: %s" %(errMessage, expected, current)
        if HaltOnErr:
            self.assertEqual(expected, current, errMessage)
        else:
            try: self.assertEqual(expected, current, errMessage)
            except AssertionError, e: self.verificationErrors.append(str(e))
            
    def verify_IsTrue(self, result, errMessage, HaltOnErr=True, ScreenCapture=False):
        "verify is result is True"
        errMessage = "%s\nExpected: %s\nCurrent: %s" %(errMessage, True, result)
        if HaltOnErr:
            self.assertTrue(result, errMessage)
        else:
            try: self.assertTrue(result, errMessage)
            except AssertionError, e: self.verificationErrors.append(str(e))
            
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
                errMessage = "XML string is NOT well-formed! %s"%str(e)
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
    def execute(cls):
        unittest.main()