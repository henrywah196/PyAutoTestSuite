'''
Created on Nov 27, 2012

@author: WAH
'''
import os, sys, time
import unittest
from libraries.PATS import HTMLTestRunner


class TestRunner():
    def __init__(self):
        self.suite = unittest.TestSuite()
        self.outputType = None
        self.outputPath = None
        self.reportName = None
        self.reportTitle = None
        self.reportDescription = None
        
    
    def addTest(self, suite):
        self.suite.addTest(suite)
    
    
    def run(self):
        try:
            if (self.outputType == 'html' or self.outputType == 'xml'):
                # prepare test result folder
                if self.outputPath == None:
                    if not os.path.exists(os.path.join(os.path.dirname(sys.argv[0]), 'TestResults')):
                        os.mkdir(os.path.join(os.path.dirname(sys.argv[0]), 'TestResults'))
                    self.outputPath = os.path.join(os.path.dirname(sys.argv[0]), 'TestResults')
                else:
                    try:
                        if not os.path.exists(self.outputPath):
                            os.mkdir(self.outputPath)
                    except Exception, e:
                        raise Exception('outputPath error: ' + str(e))
            
                # prepare file name
                dateTimeStamp = time.strftime('%Y%m%d_%H_%M_%S')
                fileName = "TestReport" + "_" + dateTimeStamp
                if self.outputType == 'html':
                    self.reportName = fileName + ".html"
                if self.outputType == 'xml':
                    self.reportName = fileName + ".xml"
            
            # run test suite
            if self.outputType == 'html':
                # test output to html file
                buf = file(os.path.join(self.outputPath, self.reportName), 'wb')
                runner = HTMLTestRunner.HTMLTestRunner(stream=buf, title=self.reportTitle, description=self.reportDescription)
                runner.run(self.suite)
                buf.close()
            elif self.outputType == 'xml':
                # test output to xml file
                try: import junitxml
                except ImportError, e:
                    raise Exception(str(e) + '. Download and install model from Internet.')
                buf = file(os.path.join(self.outputPath, self.reportName), 'wb')
                result = junitxml.JUnitXmlResult(buf)
                result.startTestRun()
                self.suite.run(result)
                result.stopTestRun()
                buf.close()
            else:
                # test output to console
                runner = unittest.TextTestRunner(verbosity=2)
                runner.run(self.suite)
                
        except Exception, e:      
            print '\nTestRunner Exception!\n\t' + str(e)
            sys.exit(0)