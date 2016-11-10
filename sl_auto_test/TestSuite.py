#--------------------------------------------------------------------------------------
# Test Suite:    Main Test Suite for software Licensing 
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

# TP01_LicGen_Web_Services
from tests.License_Components.TP01_LicGen_Web_Services.TC0101 import *
from tests.License_Components.TP01_LicGen_Web_Services.TC0103 import *
from tests.License_Components.TP01_LicGen_Web_Services.TC0104 import *
# TP02_License_Generator
from tests.License_Components.TP02_License_Generator.TC0201A import *
from tests.License_Components.TP02_License_Generator.TC0202A import *
from tests.License_Components.TP02_License_Generator.TC0202B import *
from tests.License_Components.TP02_License_Generator.TC0202C import *


if __name__ == "__main__":
    #execute test suite
    log_file_name = "TestSuite_Result"
    argv = ["fake", "--verbosity=2", "--logging-clear-handlers", "--with-html", "--html-file=%s.html"%os.path.join(os.path.dirname(os.path.abspath(__file__)), log_file_name)]
    nose.main(defaultTest=__name__, argv=argv, exit=False)
    post_processing.processing(log_file_name)





