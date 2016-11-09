'''
Created on Jul 27, 2015

@author: hwang
'''
# coding: utf-8
import nose
from libraries.PyAutoTestCase import TestCaseTemplate
from ddt import ddt, data, unpack


def getTestingData():
    """
    return a list of testing data in the format of [(1, 1), (2, 2), (3, 1), (4, 4), (5, 1)]
    """
    return [(1, 1), (2, 2), (3, 1), (4, 4), (5, 1)]


@ddt
class NoseSamples02(TestCaseTemplate):
    
    @classmethod
    def setUpClass(cls):
        super(NoseSamples02, cls).setUpClass()
        print "Test class setup"
        
    @classmethod
    def tearDownClass(cls):
        super(NoseSamples02, cls).tearDownClass()
        print "Test class tear down"
    
    def setUp(self):
        super(NoseSamples02, self).setUp()
        print "Test setup for %s"%self.currentTest
        

    def tearDown(self):
        super(NoseSamples02, self).tearDown()
        print "Test tear down for %s"%self.currentTest

    @data((1, 1), (2, 2), (3, 1), (4, 4), (5, 1))
    @unpack
    def test_01(self, first_value, second_value):
        self._testMethodDoc = "Verify first_value '%s' equals to second_value '%s'"%(first_value, second_value)
        print ("Execute %s"%self.currentTest)
        self.verify_IsEqual(first_value, second_value, self._testMethodDoc)
        
    @data(*getTestingData())
    def test_02(self, testData):
        first_value = testData[0]
        second_value = testData[1]
        self._testMethodDoc = "Verify first_value '%s' Large than second_value '%s'"%(first_value, second_value)
        print ("Execute %s"%self.currentTest)
        result = first_value > second_value
        self.verify_IsTrue(result, self._testMethodDoc)


if __name__ == "__main__":
    #unittest.main()
    argv = ["--verbosity=2", "--nocapture"]
    nose.main(defaultTest=__name__, argv=argv)
