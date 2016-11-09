import os, sys
import unittest, time
from libraries import TestRunner
# import test cases
import TP01_Configuration.TC0101_BaseUnit


#class Reports(unittest.TestCase):

#    def test_main(self):
#        # organize test cases
#        self.suite = unittest.TestSuite_Nose()
#        self.suite.addTest(unittest.makeSuite(TC0101_BaseUnit))

#        # prepare test result folder
#        if not os.path.exists(os.path.join(os.path.dirname(sys.argv[0]), 'TestResults')):
#            os.mkdir(os.path.join(os.path.dirname(sys.argv[0]), 'TestResults'))
#        dateTimeStamp = time.strftime('%Y%m%d_%H_%M_%S')
#        htmlFileName = "TestReport" + "_" + dateTimeStamp + ".html"
#        buf = file(os.path.join(os.path.dirname(sys.argv[0]), 'TestResults', htmlFileName), 'wb')
#        runner = HTMLTestRunner.HTMLTestRunner(stream=buf, title='<demo test>', description='thisis demo')
#        runner.run(self.suite)
#        buf.close()

# prepare testing suite
suite1 = TP01_Configuration.TC0101_BaseUnit.suite()

# prepare report output path
path = os.path.dirname(sys.argv[0])

reportTestRunner = TestRunner()
reportTestRunner.addTest(suite1)
reportTestRunner.reportType = 'html'
reportTestRunner.reportLocation = path
reportTestRunner.run()

# prepare test result folder
if not os.path.exists(os.path.join(os.path.dirname(sys.argv[0]), 'TestResults')):
    os.mkdir(os.path.join(os.path.dirname(sys.argv[0]), 'TestResults'))
dateTimeStamp = time.strftime('%Y%m%d_%H_%M_%S')
htmlFileName = "TestReport" + "_" + dateTimeStamp + ".html"
buf = file(os.path.join(os.path.dirname(sys.argv[0]), 'TestResults', htmlFileName), 'wb')
runner = HTMLTestRunner.HTMLTestRunner(stream=buf, title='<demo test>', description='thisis demo')
runner.run(suite)
buf.close()