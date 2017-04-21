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
from tests.Access_Activity_Report.DB_Test import DB_Test



######################
# prepare test suites
######################
suites = []
suites.append(DB_Test.TestCase.suite())




mainTestSuite = TestSuiteTemplate()
mainTestSuite.addTests(suites)


if __name__ == "__main__":
    
    test_processing.preProcessing(reportTitle="enteliWEB Access Activity Sanity Test")
    
    log_file_name = "Access_Activity_Report_Sanity_TestResult_%s"%test_processing.getReportBuildInfo()
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_file_name + '.html')
    report_title = test_processing.getReportTitle()
    report_description = test_processing.getReportDescription()
    result = mainTestSuite.execute(verbosity=2, outputtype="html", output=filePath, title=report_title, description=report_description)
    
    test_processing.postProcessing(log_file_name)
    