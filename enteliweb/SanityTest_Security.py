#--------------------------------------------------------------------------------------
# Test Suite:    Main Test Suite for PATS
# 
#
#
# Author:        Henry Wang
# Created:       Aug 08, 2015
#--------------------------------------------------------------------------------------
import os
import test_processing
from libraries.PyAutoTestCase import *
####################
# import test cases
####################
from tests.security_test import eweb14019
from tests.security_test import eweb14157



######################
# prepare test suites
######################
suites = []
suites.append(eweb14019.TestCase.suite())
suites.append(eweb14157.TestCase.suite())




mainTestSuite = TestSuiteTemplate()
mainTestSuite.addTests(suites)


if __name__ == "__main__":
    
    test_processing.preProcessing(reportTitle="enteliWEB Security Sanity Test Report")
    
    log_file_name = "Security_Sanity_TestResult_%s"%test_processing.getReportBuildInfo()
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_file_name + '.html')
    report_title = test_processing.getReportTitle()
    report_description = test_processing.getReportDescription()
    result = mainTestSuite.execute(verbosity=2, outputtype="html", output=filePath, title=report_title, description=report_description)
    
    test_processing.postProcessing(log_file_name)
    