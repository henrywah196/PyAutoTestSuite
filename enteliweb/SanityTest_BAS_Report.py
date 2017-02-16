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
from tests.BAS_Reports.Sanity_Test.Complex_Property_Test import Array_Property
from tests.BAS_Reports.Sanity_Test.Complex_Property_Test import Union_Property
from tests.BAS_Reports.Sanity_Test.Object_Query.Active_Alarms_Report import ActiveAlarmsReport
from tests.BAS_Reports.Sanity_Test.Object_Query.AdHoc_Calibration_Report import AdHocCalibrationReport
from tests.BAS_Reports.Sanity_Test.Object_Query.AdHoc_Decommissioned_Fault_Report import AdHocDecommFaultReport
from tests.BAS_Reports.Sanity_Test.Object_Query.Controller_Firmware_Report import ControllerFirmwareReport
from tests.BAS_Reports.Sanity_Test.Object_Query.Data_Exchange_Settings_Report import DataExchangeSettingsReport
from tests.BAS_Reports.Sanity_Test.Object_Query.DER_Failure_Report import DERFailureReport
from tests.BAS_Reports.Sanity_Test.Object_Query.Network_Number_Report import NetworkNumberReport

######################
# prepare test suites
######################
suites = []
suites.append(ActiveAlarmsReport.suite())
suites.append(AdHocCalibrationReport.suite())
suites.append(AdHocDecommFaultReport.suite())
suites.append(ControllerFirmwareReport.suite())
suites.append(DataExchangeSettingsReport.suite())
suites.append(DERFailureReport.suite())
suites.append(NetworkNumberReport.suite())

suites.append(Array_Property.TestCase.suite())
suites.append(Union_Property.TestCase.suite())


mainTestSuite = TestSuiteTemplate()
mainTestSuite.addTests(suites)


if __name__ == "__main__":
    
    test_processing.preProcessing()
    
    log_file_name = "BAS_Report_Sanity_TestResult_%s"%test_processing.getReportBuildInfo()
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_file_name + '.html')
    report_title = test_processing.getReportTitle()
    report_description = test_processing.getReportDescription()
    result = mainTestSuite.execute(verbosity=2, outputtype="html", output=filePath, title=report_title, description=report_description)
    
    test_processing.postProcessing(log_file_name)
    