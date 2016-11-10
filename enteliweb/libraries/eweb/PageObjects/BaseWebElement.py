'''
Created on Jun 11, 2013

@author: hwang
'''
from libraries.eweb.PageObjects import seleniumwrapper
from libraries.eweb import Locators
from libraries.eweb.PageObjects import selenium_server_connection
import time

class BaseWebElement(object):
    """ Model a Base web element """
    def __init__(self, locatorString):
        self.locatorString = locatorString
        self.locators = Locators()
        self.locator = self.locators.get(locatorString)
    
    def __delete__(self, obj):
        pass
    
    def __str__(self):
        """ return its locator name, will be overwrited """
        return self.locatorString
    
    def getDriver(self):
        """ connect to an actived web driver """
        self.driver = selenium_server_connection.connection
        return self.driver
    
    def getElement(self, locator):
        """ locate the web element on page """
        driver = selenium_server_connection.connection
        how = locator["by"]
        what = locator["value"]
        if locator["parent"]:
            locator = self.locators.get(locator["parent"])
            driver = self.getElement(locator)
        elem = seleniumwrapper.getElement(how, what, driver)
        return elem
    
    def click(self):
        elem = self.getElement(self.locator)
        if elem is not None:
            elem.location_once_scrolled_into_view
            elem.click()
        else:
            raise Exception("'%s' cannot be located on page."%self.locatorString)
        
    def isDisplayed(self):
        """ return true if the web element is displayed on web page """
        elem = self.getElement(self.locator)
        if elem is not None:
            elem.location_once_scrolled_into_view
            return elem.is_displayed()
        else:
            return False
        
        
class HyperLinkWebElement(BaseWebElement):
    """ Model a Hyper Link web element """
    
    def __str__(self):
        """ return the hyperlink text or
            return the image file name if it is a icon
        """
        elem = self.getElement(self.locator)
        if elem.tag_name == "img":
            return elem.get_attribute("srv")
        return elem.text


class EditBoxWebElement(BaseWebElement):
    """ Model a Edit Box web element """
   
    ''' 
    # obsolated, will be replaced by __str__()   
    def __get__(self, obj, objtype=None):
        """ get the current value of the edit box"""
        elem = self.getElement(self.locator)
        if obj is None:
            return self
        return elem.get_attribute("value")
    '''
    
    def __str__(self):
        """ get the current value of the edit box"""
        elem = self.getElement(self.locator)
        return elem.get_attribute("value")
    
    def __set__(self, obj, val):
        """ set the current value of the edit box """
        elem = self.getElement(self.locator)
        elem.clear()
        elem.send_keys(val)
    
    def isInvalid(self):
        """ return true if the web element is in invalid state """
        elem = self.getElement(self.locator)
        elem.location_once_scrolled_into_view
        classString = elem.get_attribute("class")
        if "x-form-invalid-field" in classString:
            return True
        else:
            return False


class CheckBoxWebElement(BaseWebElement):
    """ Model a check box web element """
    
    def isChecked(self):
        """ verify and return True if the check box is checked """
        elem = self.getElement(self.locator)
        elem.location_once_scrolled_into_view
        if elem.is_selected() == True:
            return True
        parent = elem.find_element_by_xpath("../../../../..")
        parentclass = parent.get_attribute("class")
        if "x-form-cb-checked" in parentclass:
            return True
        else:
            return False
       
    
class DropDownBoxWebElement(EditBoxWebElement):
    """ Model a DropDown Box web element """
    def __init__(self, locatorString, invalidIcon=False):
        super(DropDownBoxWebElement, self).__init__(locatorString)
        if invalidIcon:
            self.invalidIcon = BaseWebElement(locatorString + '.invalid_icon')
        
    def __set__(self, obj, val):
        """ select a item from the drop down box """
        dropDownList = self.getDropDownList()
        if dropDownList:
            itemObjs = dropDownList.find_elements_by_tag_name('li')
            target = None
            for item in itemObjs:
                if item.text == val:
                    target = item
                    break
            if target:
                target.click()
     
    def getDropDownList(self): 
        """ return the drop down list element """ 
        driver = selenium_server_connection.connection 
        dropDownList = None
        self.click()
        boundLists = driver.find_elements_by_class_name('x-boundlist-list-ct')
        if boundLists:
            for boundList in boundLists:
                if boundList.is_displayed():
                    dropDownList = boundList
                    break
        del boundLists
        return dropDownList
    
    def getListContent(self):
        """ return a list of available items from drop down list """
        myList = []
        dropDownList = self.getDropDownList()
        if dropDownList:
            itemObjs = dropDownList.find_elements_by_tag_name('li')
            for item in itemObjs:
                myList.append(item.text)
        return myList


class ButtonWebElement(BaseWebElement):
    """ Model a Button web element """
        
    def __str__(self):
        """ get the label of the button """
        elem = self.getElement(self.locator)
        locator = self.locator
        tagName = locator["tag_name"]
        if tagName == "input":
            return elem.get_attribute("value")
        if tagName == "span":
            return elem.text
        
    def isEnabled(self):
        """return True if the button is in enabled state """
        flag = "x-disabled"
        if not self.isDisplayed():
            return False
        elem = self.getElement(self.locator)
        val = elem.get_attribute("class")
        if flag in val:
            return False
        else:
            return True
        
        
class TextBoxWebElement(BaseWebElement):
    """ Model a Text Box web element """
        
    def __str__(self):
        """get the text content of the hyper link
        """
        elem = self.getElement(self.locator)
        return elem.text
    
    
class XTree(BaseWebElement):
    """
    class to model the x-tree WebElements
    """
    def __init__(self, locatorString):
        super(XTree, self).__init__(locatorString)
        self.className = "x-grid-cell-inner-treecolumn"

    def _getTreeNodes(self):
        """ return a list of treeNode WebElements
        """
        elem = self.getElement(self.locator)
        tableElems = elem.find_elements_by_tag_name('table')
        #elem = elem.find_elements_by_tag_name('tr')
        #elem = elem.find_elements_by_xpath("./tbody/tr[not(@class='x-grid-header-row')]")
        return tableElems

    def _getTreeNodeName(self, treeNodeObj):
        """return the text string of the treeNode object
        """
        divElem = treeNodeObj.find_element_by_class_name(self.className)
        childElems = divElem.find_elements_by_css_selector("*")
        elem = childElems[len(childElems) - 1]
        return elem.text

    def _getTreeNodeLayer(self, treeNodeObj):
        """ the helper method return the layer number of the treeNode object
            the root node object suppose return number 0
            the direct underneath of the root suppose return number 1
        """
        divElem = treeNodeObj.find_element_by_class_name(self.className)
        childElems = divElem.find_elements_by_css_selector("*")
        layer = len(childElems) - 3
        return layer

    def _expandTreeNode(self, treeNodeObj):
        """ click the elbow of the assigned tree node
            if the tree node already expended then do nothing
            if the tree node doesn't has elbow then do nothing

            @return boolean    return true if no error found during execution
        """
        classNames = ['x-grid-tree-node-expanded', 'x-grid-tree-node-leaf']
        result = True
        try:
            trElem = treeNodeObj.find_element_by_tag_name("tr")
            classString = trElem.get_attribute('class')
            if (classNames[0] not in classString) and (classNames[1] not in classString):
                divElem = treeNodeObj.find_element_by_class_name(self.className)
                childElems = divElem.find_elements_by_css_selector("*")
                treeElbowElem = childElems[len(childElems) - 3]
                treeElbowElem.click()
                time.sleep(5)
                self.TreeNodes = self._getTreeNodes()
        except Exception as e:
            print( "XTree._expandTreeNode() get Exception: %s" %e )
            result = False
        return result


    def _collapseTreeNode(self, treeNodeObj):
        """ click the elbow of the assigned tree node
            if the tree node already collapsed then do nothing
            if the tree node doesn't has elbow then do nothing

            @return boolean    return true if no error found during execution
        """
        className = 'x-grid-tree-node-expanded'
        result = True
        try:
            trElem = treeNodeObj.find_element_by_tag_name("tr")
            if className in trElem.get_attribute('class'):
                divElem = treeNodeObj.find_element_by_class_name(self.className)
                childElems = divElem.find_elements_by_css_selector("*")
                treeElbowElem = childElems[len(childElems) - 3]
                treeElbowElem.click()
                time.sleep(5)
                self.TreeNodes = self._getTreeNodes()
        except Exception as e:
            print( "XTree._collapseTreeNode() get Exception: %s" %e )
            result = False
        return result

    def _getRootNodes(self):
        """ return a list of tree node which are all root nodes
        """
        result = []
        self.TreeNodes = self._getTreeNodes()
        for treeNode in self.TreeNodes:
            if self._getTreeNodeLayer(treeNode) == 0:
                result.append(treeNode)
        return result

    def _getChildNodes(self, treeNodeObj):
        """ return a list of displayed children nodes which is underneath the specified tree node
        """
        result = []
        layer = self._getTreeNodeLayer(treeNodeObj) + 1
        i = self.TreeNodes.index(treeNodeObj) + 1
        while i < len(self.TreeNodes):
            target = self.TreeNodes[i]
            if self._getTreeNodeLayer(target) == layer:
                result.append(target)
            elif self._getTreeNodeLayer(target) < layer:
                break
            i = i + 1
        return result

    def _genTreeNodeList(self, nodePath):
        """ convert the nodePath string to a list of tree node name string and return the list
            for example: 'A\B\C' converted to ['A', 'B', 'C']
        """
        result = nodePath.split('\\')
        return result

    def _genTreePathList(self, nodePath):
        """ convert the assigned tree node name list to a list of tree node path
            for example: 'A\B\C' converted to ['A', 'A\B', 'A\B\C']
        """
        result = []
        treeNodeList = self._genTreeNodeList(nodePath)
        for treeNode in treeNodeList:
            pathStr =''
            i = 0
            while i <= treeNodeList.index(treeNode):
                if i == 0:
                    pathStr = pathStr + treeNodeList[i]
                else:
                    pathStr = pathStr + '\\' + treeNodeList[i]
                i = i + 1
            result.append(pathStr)
        return result

    def _getParentNodePath(self, nodePath):
        """ if node path is A\B\C return A\B
        """
        myList = self._genTreePathList(nodePath)
        return myList[len(myList) - 2]

    def _getNodeNameFromPath(self, nodePath):
        """ if node path is A\B\C return C
        """
        myList = self._genTreeNodeList(nodePath)
        return myList[len(myList) - 1]


    def _getTreeNode(self, nodePath):
        """ return the tree node which is displayed in the tree
        """
        result = None
        try:
            treePath = self._genTreeNodeList(nodePath)

            # backslash handling
            tmpList = []
            for item in treePath:
                tmpList.append(self._CharacterReplaceHelper(item, Reverse=True))
            treePath = tmpList

            parentNode = None
            treeNodes = None
            for target in treePath:
                if treePath.index(target) == 0:
                    treeNodes = self._getRootNodes()
                else:
                    treeNodes = self._getChildNodes(parentNode)
                parentNode = None
                for treeNode in treeNodes:
                    if self._getTreeNodeName(treeNode) == target:
                        parentNode = treeNode
                        break
                if not parentNode:
                    err = ''
                    i = 0
                    while i <= treePath.index(target):
                        if i == 0:
                            err = err + treePath[i]
                        else:
                            err = err + '\\' + treePath[i]
                        i = i + 1
                    raise Exception("tree node '" + err + "' was not found.")
            result = parentNode
        except Exception as e:
            print( "XTree._getTreeNode(): %s" %e )
            result = None
        return result

    def updateTree(self):
        """ update the TreeNodes list in case there are tree nodes added or removed.
        """
        self.TreeNodes = self._getTreeNodes()

    def expandTreeNode(self, nodePath):
        """ expand tree nodes based on the giving node path

            @return boolean    return true if no error found during command execution
        """
        result = False
        try:
            treePathList = self._genTreePathList(nodePath)
            for treePath in treePathList:
                treeNode = self._getTreeNode(treePath)
                if treeNode:
                    treeNode.location_once_scrolled_into_view
                    result = self._expandTreeNode(treeNode)
                else:
                    result = False
                    break
        except Exception as e:
            print( "XTree.expandTreeNode() get Exception: %s" %e )
            result = False
        return result

    def collapseTreeNode(self, nodePath):
        """ collapse the specified tree node based on the giving node path
            @return boolean    return true if no error found during command execution
        """
        result = False
        try:
            treeNode = self._getTreeNode(nodePath)
            if treeNode:
                treeNode.location_once_scrolled_into_view
                result = self._collapseTreeNode(treeNode)
            else:
                result = False
        except Exception as e:
            print( "XTree.collapseTreeNode() get Exception: %s" %e )
            result = False
        return result

    def verifyTreeNodeDisplayed(self, nodePath):
        """ verify and return True if the specified tree node is displayed in the tree
        """
        result = True
        treeNode = self._getTreeNode(nodePath)
        if not treeNode:
            result = False
        return result

    def verifyTreeNodeEnabled(self, treeNodeObj):
        """ verify and return true if the specified tree node is displayed and not grey out
        """
        result = True
        flag = "tree-node-disabled"
        td = treeNodeObj.find_element_by_tag_name("td")
        if flag in td.get_attribute("class"):
            result = False
        return result
    
    def _CharacterReplaceHelper(self, TargetString, Reverse=False, From="\\", To="%92%"):
        """
        using this helper function to replace character(s) in the assigned the string
        the function will be used by Tree() class to handling backslach, which is used as
        tree patch separater.

        @param string TargetString        the string under modify.
        @param Boolean Reverse            if False, using From to replace TO, if True, using To to replace From
        @param string From                the character in target string which need to be replaced
        @param string To                  the character(s) which will be used to replace the character in target string

        @return string                    return a modified string
    """
        if Reverse:
            tmp = From
            From = To
            To = tmp
        if From not in TargetString:
            return TargetString
        else:
            return TargetString.replace(From, To)
        
    