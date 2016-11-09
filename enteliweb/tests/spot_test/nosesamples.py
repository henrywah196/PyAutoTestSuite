'''
Created on Jul 27, 2015

@author: hwang
'''
# coding: utf-8
import nose
from libraries.PyAutoTestCase import *

class NoseSamples(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        super(NoseSamples, cls).setUpClass()
        print "Test class setup"
        
    @classmethod
    def tearDownClass(cls):
        super(NoseSamples, cls).tearDownClass()
        print "Test class tear down"
    
    def setUp(self):
        super(NoseSamples, self).setUp()
        print "Test setup for %s"%self.currentTest
        

    def tearDown(self):
        super(NoseSamples, self).tearDown()
        print "Test tear down for %s"%self.currentTest


    def test01(self):
        self._testMethodDoc = "Execute test 01"
        print (self._testMethodDoc)
        first_value = 1
        second_value = 1
        step = "Verify first_value '%s' equals to second_value '%s'"%(first_value, second_value)
        self.verify_IsEqual(first_value, second_value, step, HaltOnErr=False)    # continue testing if failed
        step = "Verify first_value '%s' Large than second_value '%s'"%(first_value, second_value)
        result = first_value > second_value
        self.verify_IsTrue(result, step)
        
            
                
    def test02(self):
        self._testMethodDoc = "Execute test 02"
        print (self._testMethodDoc)
        first_value = 2
        second_value = 2
        step = "Verify first_value '%s' equals to second_value '%s'"%(first_value, second_value)
        self.verify_IsEqual(first_value, second_value, step, HaltOnErr=False)
        step = "Verify first_value '%s' Large than second_value '%s'"%(first_value, second_value)
        result = first_value > second_value
        self.verify_IsTrue(result, step)
        
       
    def test03(self):
        self._testMethodDoc = "Execute test 03"
        print (self._testMethodDoc)
        first_value = 1
        second_value = 3
        step = "Verify first_value '%s' equals to second_value '%s'"%(first_value, second_value)
        self.verify_IsEqual(first_value, second_value, step, HaltOnErr=False)
        step = "Verify first_value '%s' Large than second_value '%s'"%(first_value, second_value)
        result = first_value > second_value
        self.verify_IsTrue(result, step)
        
        
    def test04(self):
        self._testMethodDoc = "Execute test 04"
        print (self._testMethodDoc)
        first_value = 4
        second_value = 4
        step = "Verify first_value '%s' equals to second_value '%s'"%(first_value, second_value)
        self.verify_IsEqual(first_value, second_value, step, HaltOnErr=False)
        step = "Verify first_value '%s' Large than second_value '%s'"%(first_value, second_value)
        result = first_value > second_value
        self.verify_IsTrue(result, step)
            

    def test05(self):
        self._testMethodDoc = "Test 05, which using regular assert"
        print (self._testMethodDoc)
        first_value = 1
        second_value = 5
        step = "Verify first_value '%s' equals to second_value '%s'"%(first_value, second_value)
        self.assertEqual(first_value, second_value, step)
        step = "Verify first_value '%s' Large than second_value '%s'"%(first_value, second_value)
        result = first_value > second_value
        self.assertTrue(result, step) 
        
        
    def test06(self):    
        self._testMethodDoc = "Execute test 06"
        print (self._testMethodDoc)
        first_value = 1
        second_value = 5
        step = "Verify first_value '%s' equals to second_value '%s'"%(first_value, second_value)
        self.verify_IsEqual(first_value, second_value, step, HaltOnErr=False)
        step = "Verify first_value '%s' Large than second_value '%s'"%(first_value, second_value)
        result = first_value > second_value
        self.verify_IsTrue(result, step, HaltOnErr=False)


if __name__ == "__main__":
    #unittest.main()
    argv = ["--verbosity=2", "--nocapture"]
    nose.main(defaultTest=__name__, argv=argv)
