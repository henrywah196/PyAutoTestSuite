'''
Name: TC1104_Base_Units.py
Description: verify the imported data have right base unit normalization.
Created on June 05, 2013
@author: hwang
'''
import os, time
from libraries.PyAutoTestCase import *
try: 
    import xlrd
    from xlutils.copy import copy
except ImportError, e: 
    print '"ERROR" %s, please install this module before start.'%str(e)
    exit()

class TC1104_Base_Units(TestCaseTemplate):
    
    def setUp(self):
        super(TC1104_Base_Units, self).setUp()
        self.WorkBookFileName = os.path.join(os.path.dirname(__file__), "TC1104_Base_Units.xls")
        
    def tearDown(self):
        super(TC1104_Base_Units, self).tearDown()
        
    
    def test_sample01(self):
        """ unit test sample 01
        """
        self._prepare_test_sheet()
        
        
    def _prepare_test_sheet(self):
        rb = xlrd.open_workbook(self.WorkBookFileName)
        wb = copy(rb)
        wb.add_sheet("4.0.553")
        wb.save(self.WorkBookFileName)
        
        

if __name__ == "__main__":
    unittest.main()
