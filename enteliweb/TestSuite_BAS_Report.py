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
from tests.BAS_Reports.Ad_Hoc.Generating_Report.C1722295 import TC1722295
from tests.BAS_Reports.Ad_Hoc.Generating_Report.C1722296 import TC1722296
from tests.BAS_Reports.Ad_Hoc.Generating_Report.C1722297 import TC1722297
from tests.BAS_Reports.Ad_Hoc.Generating_Report.C1722299 import TC1722299

######################
# prepare test suites
######################
c88436 = TC88436.suite()
c88437 = TC88437.suite()
c88439 = TC88439.suite()

c1722294 = TC1722294.suite()
c1722295 = TC1722295.suite()
c1722296 = TC1722296.suite()
c1722297 = TC1722297.suite()
c1722299 = TC1722299.suite()

mainTestSuite = TestSuiteTemplate()
mainTestSuite.addTests((c1722294,c1722295,c1722296,c1722297,c1722299))


if __name__ == "__main__":
    
    test_processing.preProcessing()
    
    log_file_name = "BAS_Report_TestResult_%s"%test_processing.getReportBuildInfo()
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_file_name + '.html')
    report_title = test_processing.getReportTitle()
    report_description = test_processing.getReportDescription()
    result = mainTestSuite.execute(verbosity=2, outputtype="html", output=filePath, title=report_title, description=report_description)
    
    test_processing.postProcessing(log_file_name)
    