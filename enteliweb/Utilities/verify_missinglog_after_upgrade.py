# coding: utf-8
################################################################################################
#
# Description :  populate log table to make it over 1 million records
#
################################################################################################
import settings
from libraries.PyAutoTestCase import *    # import test case template
from libraries.eweb.DataObjects.WebGroup import WebGroupDBObj
import os, time


class TestCase(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        super(TestCase, cls).setUpClass()
       
        
    @classmethod
    def tearDownClass(cls):
        super(TestCase, cls).tearDownClass()
    
    
    def setUp(self):
        super(TestCase, self).setUp()
        
        self.longMessage = True
        self.maxDiff = None


    def tearDown(self):
        super(TestCase, self).tearDown()
            
            
    def test01(self):
        
        webgroup = WebGroupDBObj()
        sql_string = """select id from log order by id desc limit 10000"""
        cursor = webgroup.cursor.execute(sql_string)
        rows_a = cursor.fetchall()
        del webgroup
        
        row = rows_a[len(rows_a) - 1]
        start_id = row.id
        
        wait = raw_input("Wait for eweb upgrade. Press enter to continue")
        
        webgroup = WebGroupDBObj()
        sql_string = """select id from log where id >= %s order by id desc limit 10000"""%start_id
        cursor = webgroup.cursor.execute(sql_string)
        rows_b = cursor.fetchall()
        del webgroup
        
        print self._return_not_matches(rows_a, rows_b)
        
        
    def _return_not_matches(self, list_a, list_b):
        
        return [[x for x in list_a if x not in list_b], [x for x in list_b if x not in list_a]]
    

if __name__ == "__main__":
    unittest.main()