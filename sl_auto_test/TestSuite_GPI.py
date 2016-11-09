'''
Created on May 11, 2013

@author: WAH
'''

import os, sys
from libraries.TestRunner import TestRunner
# import test cases
from GP_Integration.TP01_OnlineOrder_eWEB_Configurator.TC0107 import TC0107
from GP_Integration.TP02_OnlineOrder_eBRIDGE_Configurator.TC0205 import TC0205
from GP_Integration.TP03_OnlineOrder_CUBE_Configurator.TC0305 import TC0305

# prepare testing suite
suite1 = TC0107.suite()
suite2 = TC0205.suite()
suite3 = TC0305.suite()

# prepare report output path
path = os.path.dirname(sys.argv[0])

slTestRunner = TestRunner()
slTestRunner.reportTitle = 'Software Licensing Testing Report'
slTestRunner.reportDescription = 'QA Software Licensing testing automation project.'
slTestRunner.addTest(suite1)
slTestRunner.addTest(suite2)
slTestRunner.addTest(suite3)
slTestRunner.outputType = 'html'
#sampleTestRunner.reportLocation = path
slTestRunner.run()


