'''
a simple test see if html5 drag and drop works with the js helper
    
Created on Sep 20, 2016

@author: Henry
'''
import time, unittest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from __init__ import html5DragDropHelper


class MyTest(unittest.TestCase):
    
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()
        
    def tearDown(self):
        self.driver.close()
        self.driver.quit()
    
    #@unittest.skip("")
    def test01(self):
        """
        try HTML Drag and Drop in www.w3schools.com
        """
        self.driver.get("http://www.w3schools.com/html/html5_draganddrop.asp")
        time.sleep(5)
        elemFrom = self.driver.find_element_by_id("div1")
        elemTo = self.driver.find_element_by_id("div2")
        elemDragable = self.driver.find_element_by_id("drag1")
        target = elemFrom.find_element_by_tag_name("img")
        self.assertEqual("drag1", target.get_attribute("id"), "target is under div1")
        
        strSourceID = elemDragable.get_attribute("id")
        strDestinationID = elemTo.get_attribute("id")
        html5DragDropHelper(self.driver, strSourceID, strDestinationID)
        time.sleep(5)
        
        target = elemTo.find_element_by_tag_name("img")
        self.assertEqual("drag1", target.get_attribute("id"), "target is under div2")
        
        
    def test02(self):
        """
        try HTML Drag and Drop in html5demo.com/drag
        """
        self.driver.get("http://html5demos.com/drag")
        time.sleep(5)
        
        elemOne = self.driver.find_element_by_id("one")
        elemTwo = self.driver.find_element_by_id("two")
        elemThree = self.driver.find_element_by_id("three")
        elemFour = self.driver.find_element_by_id("four")
        elemFive = self.driver.find_element_by_id("five")
        target = self.driver.find_element_by_id("bin")
        
        # perform drag and drop
        html5DragDropHelper(self.driver, "one", "bin")
        
        with self.assertRaises(NoSuchElementException):
            elemOne = self.driver.find_element_by_id("one")
    
    
if __name__ == "__main__":
    unittest.main()