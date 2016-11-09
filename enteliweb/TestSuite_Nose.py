#--------------------------------------------------------------------------------------
# Test Suite:    Main Test Suite for PATS
# 
#
#
# Author:        Henry Wang
# Created:       Aug 08, 2015
#--------------------------------------------------------------------------------------
import os, nose
import post_processing

####################
# import test cases
####################
from tests.energy_reports.TP11_Data_Integrity.TC1105A_Data_Interpolation import *
#from tests.energy_reports.TP11_Data_Integrity.TC1105B_Data_Aggregation import *


if __name__ == "__main__":
    #execute test suite
    log_file_name = "TestSuite_Result"
    argv = ["fake", "--verbosity=2", "--logging-clear-handlers", "--with-html", "--html-file=%s.html"%os.path.join(os.path.dirname(os.path.abspath(__file__)), log_file_name)]
    nose.main(defaultTest=__name__, argv=argv, exit=False)
    post_processing.processing(log_file_name)






