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
from tests.BAS_Reports.Commissioning_Sheets.Generating_Report.C88436 import TC88436
from tests.BAS_Reports.Commissioning_Sheets.Generating_Report.C88437 import TC88437
from tests.BAS_Reports.Commissioning_Sheets.Generating_Report.C88439 import TC88439

from tests.BAS_Reports.Ad_Hoc.Generating_Report.C1722294 import TC1722294

######################
# prepare test suites
######################
c88436 = TC88436.suite()
c88437 = TC88437.suite()
c88439 = TC88439.suite()

c1722294 = TC1722294.suite()

mainTestSuite = TestSuiteTemplate()
mainTestSuite.addTests((c88436, c88437, c88439, c1722294))


if __name__ == "__main__":
    
    test_processing.preProcessing()
    
    log_file_name = "BAS_Report_TestResult_%s"%test_processing.getReportBuildInfo()
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_file_name + '.html')
    report_title = test_processing.getReportTitle()
    report_description = test_processing.getReportDescription()
    result = mainTestSuite.execute(verbosity=2, outputtype="html", output=filePath, title=report_title, description=report_description)
    
    test_processing.postProcessing(log_file_name)
    