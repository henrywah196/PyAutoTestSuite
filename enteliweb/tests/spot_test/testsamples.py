'''
Created on Jul 27, 2015

@author: hwang
'''
# coding: utf-8
from libraries.PyAutoTestCase import TestCaseTemplate

class TestCaseSample(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        print "Test class setup"
        
    @classmethod
    def tearDownClass(cls):
        print "Test class tear down"
    
    def setUp(self):
        super(TestCaseSample, self).setUp()
        print "Test setup for %s"%self.getCurrentTestName()

    def tearDown(self):
        print "Test tear down for %s"%self.getCurrentTestName()

    def test01(self):
        self.setCurrentTestDoc("Execute test 01")
        print self.getCurrentTestDoc()
        first_value = 1
        second_value = 2
        step = "Verify first_value '%s' equals to second_value '%s'"%(first_value, second_value)
        self.perform(self.assertEqual, first_value, second_value, step)    # continue testing if failed
        step = "Verify first_value '%s' Large than second_value '%s'"%(first_value, second_value)
        result = first_value > second_value
        self.perform(self.assertTrue, result, step)
        

if __name__ == "__main__":
    TestCaseSample.execute()
