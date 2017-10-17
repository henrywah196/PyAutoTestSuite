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
from tests.Access_Activity_Report.Sanity_Test.Card_Access_Activity import Card_Access_Activity_Report
from tests.Access_Activity_Report.Sanity_Test.Card_Access_Activity_by_Card_User import Card_Access_Activity_by_Card_User_Report
from tests.Access_Activity_Report.Sanity_Test.Card_User_Activity_by_Door import Card_User_Activity_by_Door_Report
from tests.Access_Activity_Report.Sanity_Test.Door_Activity import Door_Activity_Report
from tests.Access_Activity_Report.Sanity_Test.Transactions_by_Event_Type import Transactions_by_Event_Type_Report
from tests.Access_Activity_Report.Sanity_Test.Card_Access_Activity import EWEB_22010 as EWEB_22010_1
from tests.Access_Activity_Report.Sanity_Test.Card_Access_Activity_by_Card_User import EWEB_22010 as EWEB_22010_2
from tests.Access_Activity_Report.Sanity_Test.Card_User_Activity_by_Door import EWEB_22010 as EWEB_22010_3
from tests.Access_Activity_Report.Sanity_Test.Door_Activity import EWEB_22010 as EWEB_22010_4
from tests.Access_Activity_Report.Sanity_Test.Transactions_by_Event_Type import EWEB_22010 as EWEB_22010_5



######################
# prepare test suites
######################
suites = []
suites.append(DB_Test.TestCase.suite())
suites.append(Card_Access_Activity_Report.TestCase.suite())
suites.append(Card_Access_Activity_by_Card_User_Report.TestCase.suite())
suites.append(Card_User_Activity_by_Door_Report.TestCase.suite())
suites.append(Door_Activity_Report.TestCase.suite())
suites.append(Transactions_by_Event_Type_Report.TestCase.suite())

suites.append(EWEB_22010_1.TestCase.suite())
suites.append(EWEB_22010_2.TestCase.suite())
suites.append(EWEB_22010_3.TestCase.suite())
suites.append(EWEB_22010_4.TestCase.suite())
suites.append(EWEB_22010_5.TestCase.suite())




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
    