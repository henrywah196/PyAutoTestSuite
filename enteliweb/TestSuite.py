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
from tests.energy_reports.TP11_Data_Integrity import *
from tests.energy_reports.TP11_Data_Integrity.TC1105A_Data_Interpolation import TC1105A_DataInterpolation
from tests.energy_reports.TP11_Data_Integrity.TC1105B_Data_Aggregation import TC1105B_DataAggregation
from tests.energy_reports.TP11_Data_Integrity.TC1105C_Data_AggreConsistent import TC1105C_Data_AggreConsistent
from tests.energy_reports.TP11_Data_Integrity.TC1105D_Data_Accuracy import TC1105D_Data_Accuracy

######################
# prepare test suites
######################
suite1 = TC1105A_DataInterpolation.suite()
suite2 = TC1105B_DataAggregation.suite()
suite3 = TC1105C_Data_AggreConsistent.suite()
suite4 = TC1105D_Data_Accuracy.suite()


if __name__ == "__main__":
    
    test_processing.preProcessing()
    
    log_file_name = "TestResult_%s"%test_processing.getReportBuildInfo()
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_file_name + '.html')
    report_title = test_processing.getReportTitle()
    report_description = test_processing.getReportDescription()
    mainTestSuite = TestSuiteTemplate()
    mainTestSuite.addTests((suite1, suite2))
    result = mainTestSuite.execute(verbosity=2, outputtype="html", output=filePath, title=report_title, description=report_description)
    
    test_processing.postProcessing(log_file_name)
    