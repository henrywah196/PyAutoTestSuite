'''
Created on Jun 11, 2013

@author: hwang
'''
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from libraries.eweb import Locators
from libraries.eweb.PageObjects.BasePageObject import BasePageObject
from libraries.eweb.PageObjects.BaseWebElement import ButtonWebElement, XTree
import time


class ReportTree(XTree):
    def __init__(self):
        super(ReportTree, self).__init__("accordion.report_tree")
        
    def __str__(self, obj, objtype=None):
        return "report tree under left pane"
    
    def WaitForUpdate(self):
        """ wait for tree node add/remove from tree"""
        time.sleep(3)
    
    def GetTreeRootNodes(self):
        """
        Command to return a list of tree node name which are root nodes for the target tree.
        @return List                               return a list of tree node name.
        """
        result = None
        rootNodes = self._getRootNodes()
        if rootNodes:
            result = []
            for item in rootNodes:
                result.append(self._getTreeNodeName(item))
        return result
    
    
    def IsTreeNodeHighLighted(self, PathName):
        """
        Command to verify if the target tree node is highlighted, which is used for Report tree.

        @param string PathName                     A string of path which uniquely identify the tree node.
        @return boolean                            return True or False.
        """
        result = True
        flag = u'x-grid-row-selected x-grid-row-focused'
        try:
            treeNode = self._getTreeNode(PathName)
            if flag not in treeNode.get_attribute('class'):
                result = False
        except Exception as e:
            print( "IsTreeNodeHighLighted() get Exception: %s" %e)
            result = False
        return result
    

class AccordionPageObj(BasePageObject):
    """ model enteliweb main page left pane """
    
    reports = ButtonWebElement("accordion.reports")
    reportTree = ReportTree()
    
    
    def __init__(self):
        super(AccordionPageObj, self).__init__()
        self.focus()
        
    def __repr__(self):
        super(AccordionPageObj, self).__repr__()
        
    def __str__(self):
        return "enteliWEB Main Page left pane"
    
    
        
    def isLoaded(self):
        """
        verify the page is loaded in web browser successfully
        """
        result = True
        elem = self.locate("main.accordion")
        try: assert elem.isDisplayed() is True
        except AssertionError as e:
            result = False
        return result
    
        
        