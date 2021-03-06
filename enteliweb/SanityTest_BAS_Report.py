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
from tests.BAS_Reports.Sanity_Test.Sorting_Test import test_sorting_alphabetically
from tests.BAS_Reports.Sanity_Test.Sorting_Test import test_sorting_numerically

from tests.BAS_Reports.Sanity_Test.Complex_Property_Test import Array_Property
from tests.BAS_Reports.Sanity_Test.Complex_Property_Test import Union_Property
from tests.BAS_Reports.Sanity_Test.Complex_Property_Test import Group_Property
from tests.BAS_Reports.Sanity_Test.Complex_Property_Test import Union_Group_Property
from tests.BAS_Reports.Sanity_Test.Complex_Property_Test import Union_Group_Union_Property
from tests.BAS_Reports.Sanity_Test.Complex_Property_Test import Array_Group_Property
from tests.BAS_Reports.Sanity_Test.Complex_Property_Test import Array_Union_Group_Property
from tests.BAS_Reports.Sanity_Test.Complex_Property_Test import Array_Group_Union_Property

from tests.BAS_Reports.Sanity_Test.Commissioning_Sheets import Commissioning_Sheets_Report
from tests.BAS_Reports.Sanity_Test.Calibration import Calibration_Report
from tests.BAS_Reports.Sanity_Test.Decommissioned_Fault import Decommissioned_Fault_Report
from tests.BAS_Reports.Sanity_Test.Input_Points_List import Input_Points__List_Report
from tests.BAS_Reports.Sanity_Test.Objects_In_Manual import Objects_In_Manual_Report
from tests.BAS_Reports.Sanity_Test.Output_Points_List import Output_Points__List_Report

from tests.BAS_Reports.Sanity_Test.Object_Query.Active_Alarms_Report import ActiveAlarmsReport
from tests.BAS_Reports.Sanity_Test.Object_Query.AdHoc_Calibration_Report import AdHocCalibrationReport
from tests.BAS_Reports.Sanity_Test.Object_Query.AdHoc_Decommissioned_Fault_Report import AdHocDecommFaultReport
from tests.BAS_Reports.Sanity_Test.Object_Query.Controller_Firmware_Report import ControllerFirmwareReport
from tests.BAS_Reports.Sanity_Test.Object_Query.Data_Exchange_Settings_Report import DataExchangeSettingsReport
from tests.BAS_Reports.Sanity_Test.Object_Query.DER_Failure_Report import DERFailureReport
from tests.BAS_Reports.Sanity_Test.Object_Query.Network_Number_Report import NetworkNumberReport

from tests.BAS_Reports.Sanity_Test.Regression_Test import EWEB_21258

######################
# prepare test suites
######################
suites = []
suites.append(Calibration_Report.TestCase.suite())
#suites.append(Commissioning_Sheets_Report.TestCase.suite())
suites.append(Decommissioned_Fault_Report.TestCase.suite())
suites.append(Input_Points__List_Report.TestCase.suite())
suites.append(Objects_In_Manual_Report.TestCase.suite())
suites.append(Output_Points__List_Report.TestCase.suite())

suites.append(ActiveAlarmsReport.suite())
suites.append(AdHocCalibrationReport.suite())
suites.append(AdHocDecommFaultReport.suite())
suites.append(ControllerFirmwareReport.suite())
suites.append(DataExchangeSettingsReport.suite())
suites.append(DERFailureReport.suite())
suites.append(NetworkNumberReport.suite())

suites.append(Array_Property.TestCase.suite())
suites.append(Union_Property.TestCase.suite())
suites.append(Group_Property.TestCase.suite())
suites.append(Union_Group_Property.TestCase.suite())
suites.append(Union_Group_Union_Property.TestCase.suite())
suites.append(Array_Group_Property.TestCase.suite())
suites.append(Array_Union_Group_Property.TestCase.suite())
suites.append(Array_Group_Union_Property.TestCase.suite())

suites.append(test_sorting_alphabetically.TestCase.suite())
suites.append(test_sorting_numerically.TestCase.suite())

suites.append(EWEB_21258.TestCase.suite())


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
    