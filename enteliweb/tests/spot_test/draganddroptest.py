'''
Created on Jul 27, 2015

@author: hwang
'''
# coding: utf-8
import unittest, time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

class DragAndDrop(unittest.TestCase):
    
    def setUp(self):
        self.currentTest = self.id().split('.')[-1]
        print "Test setup for %s"%self.currentTest
        self.base_url = "http://the-internet.herokuapp.com/drag_and_drop"
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.driver.get(self.base_url)
        time.sleep(5)

    def tearDown(self):
        print "Test tear down for %s"%self.currentTest
        self.driver.quit()


    def test01(self):
        print "Execute test 01"
        
        with open('U:/PyAutoTestSuite/enteliweb' + '/drag_and_drop_helper.js') as myFile:
            dnd_javascript = myFile.read().replace('\n', '')
        self.driver.execute_script(dnd_javascript+"$('#column-a').simulateDragDrop({ dropTarget: '#column-b'});")
        time.sleep(10)
        self.assertEqual(self.driver.find_element_by_id("column-a").text, 'B', 'text should be "B"')
        self.assertEqual(self.driver.find_element_by_id("column-b").text, 'A', 'text should be "A"')    
        


if __name__ == "__main__":
    unittest.main()
