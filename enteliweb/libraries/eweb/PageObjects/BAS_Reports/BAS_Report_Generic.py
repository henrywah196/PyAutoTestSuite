from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from libraries.eweb.PageObjects.BasePageObject import BaseFrameObject
from libraries.eweb.PageObjects.BaseWebElement import BaseWebElement, TextBoxWebElement, EditBoxWebElement, ButtonWebElement, DropDownBoxWebElement, CheckBoxWebElement
import time, datetime
import types


class GeneratedReportLogo(BaseWebElement):
    """ Model the report logo web element in generated report """
    
    def __init__(self, locatorString):
        super(GeneratedReportLogo, self).__init__("BASReportPageObj.generatedReportLogo")
        
    def getElement(self, locator):
        """ locate the web element on page """
        driver = self.getDriver()
        driver.switch_to_default_content()
        driver.switch_to_frame("mainFrame")
        driver.switch_to_frame("resultReport")
        elementid = locator["value"]
        
        flag = "//img[starts-with(@id, '%s')]"%elementid
        elem = driver.find_element_by_xpath(flag)
        driver.switch_to_default_content()
        driver.switch_to_frame("mainFrame")
        return elem


class ReportHistoryDropDown(DropDownBoxWebElement):
    """ Model the Report History DropDown Box web element """
    def __init__(self, locatorString):
        super(ReportHistoryDropDown, self).__init__("BASReportPageObj.reportHistory", invalidIcon=False)
        
    def __set__(self, obj, val):
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
                
                
class ObjectFilterTypeDropDown(DropDownBoxWebElement):
    """ Model the Type DropDown Box web element under Object filter window """
    def __init__(self, locatorString):
        super(ObjectFilterTypeDropDown, self).__init__("ObjectFilterWindow.objectType", invalidIcon=False)
    
    def __set__(self, obj, val):
        """ select a item from the drop down box """
        dropDownList = self.getDropDownList()
        if dropDownList:
            itemObjs = dropDownList.find_elements_by_class_name('x-boundlist-item')
            target = None
            for item in itemObjs:
                if val == "AEL" and item.text == val:
                    target = item
                    break
                elif "(%s)"%val in item.text:
                    target = item
                    break
            if target:
                target.location_once_scrolled_into_view
                time.sleep(1)
                target.click()
            else:
                raise Exception("%s was not find and selected from Object Type drop down list"%val)
        else:
            raise Exception("Object Type drop down list doesn't expand and displayed")
            
        
    def getDropDownList(self): 
        """ return the drop down list web element """ 
        driver = self.getDriver()
        dropDownList = None
        
        if not self.isExpanded():
            flag = "filterObject-trigger-picker"
            elem = self.getElement(self.locator)
            divElem = elem.find_element_by_id(flag)
            divElem.click ()    # click to expand the drop down list
        
        boundLists = driver.find_elements_by_class_name('x-boundlist-list-ct')
        if boundLists:
            for boundList in boundLists:
                if boundList.is_displayed():
                    dropDownList = boundList
                    break
        del boundLists
        return dropDownList
    
    def isExpanded(self):
        """ return true if the dropdown box is expanded to show the list """
        result = False
        try:
            driver = self.getDriver()
            boundLists = driver.find_elements_by_class_name('x-boundlist-list-ct')
            for boundList in boundLists:
                if boundList.is_displayed():
                    result = True
                    break
        except:
            pass
        return result
    
    def collapse(self):
        """ collapse the drop down list """
        if self.isExpanded():
            flag = "filterObject-trigger-picker"
            elem = self.getElement(self.locator)
            divElem = elem.find_element_by_id(flag)
            divElem.click ()    # click to close dropdown list
    
    def clearSelection(self):
        """ remove all selected items from type field """
        flag = "filterObject-itemList"
        elem = self.getElement(self.locator)
        ulElem = elem.find_element_by_id(flag)
        liElems = ulElem.find_elements_by_tag_name("li")
        if len(liElems) > 1:
            liElem = liElems[0]
            flag = "x-tagfield-item-close"
            divElem = liElem.find_element_by_class_name(flag)
            divElem.click()
            self.clearSelection()
               
                
class ObjectFilterWindow(BaseWebElement):
    """ Model the object filter window web element """
    
    title          = BaseWebElement("ObjectFilterWindow.title")
    objectType     = ObjectFilterTypeDropDown("ObjectFilterWindow.objectType")
    instance       = EditBoxWebElement("ObjectFilterWindow.instance") 
    btnAddRule     = ButtonWebElement("ObjectFilterWindow.btnAddRule")
    btnAddProperty = ButtonWebElement("ObjectFilterWindow.btnAddProperty")
    logicAND       = ButtonWebElement("ObjectFilterWindow.logicAND")
    logicOR        = ButtonWebElement("ObjectFilterWindow.logicOR")
    btnOK          = ButtonWebElement("ObjectFilterWindow.btnOK")
    btnCancel      = ButtonWebElement("ObjectFilterWindow.btnCancel")
    
    propertyFilterPanel = BaseWebElement("ObjectFilterWindow.propertyFilterPanel")
    
    def __init__(self, locatorString):
        super(ObjectFilterWindow, self).__init__("BASReportPageObj.objectFilterWindow")
        
    def changePropertyFilterLogic(self, theLogic):
        """ change the logic (AND OR) of the property filters """
        if theLogic not in ["AND", "OR"]:
            raise Exception("theLogic should be either 'AND' or 'OR'.")
        if theLogic == 'AND':
            self.logicAND.click()
        else:
            self.logicOR.click()
            
    def addProperty(self, propertyValueComparison, retry=3):
        """ add a new property based on propertyValueComparison.
            The propertyValueComparison is a list of [property_name, operator, value]  
        """
        self.btnAddProperty.click()
        total = self.getTotalPropertyFilters()
        if total == 0 and retry > 0:
            retry = retry - 1
            time.sleep(1)
            self.addProperty(propertyValueComparison, retry)
        else:
            if total == 0:
                raise Exception("new item was not added to property comparison list")
            else:
                targetElem = self.getPropertyFilter(total)
                self._modifyProperty(targetElem, propertyValueComparison)
        
    def addRule(self, propertyValueComparisonRule):
        """ Add a new property rule based on propertyValueComparisonRule.
            The propertyValueComparisonRule is a dictionary of {logic, list of propertyValueComparison}
        """
        self.btnAddRule.click()
        total = self.getTotalPropertyFilters()
        targetRuleElem = self.getPropertyFilter(total)
        
        listOfPropertyValueComparison = propertyValueComparisonRule["Properties"]
        i =  0
        while i < len(listOfPropertyValueComparison):
            if not i == 0:
                self.addPropertyToRule(targetRuleElem)
            total = self.getTotalPropertyFromRule(targetRuleElem)
            targetElem = self.getPropertyFromRule(targetRuleElem, total)
            self._modifyProperty(targetElem, listOfPropertyValueComparison[i])
            i = i + 1
        theLogic = propertyValueComparisonRule["Rule Logic"]
        self.changePropertyRuleLogic(targetRuleElem, theLogic)
        
    def getTotalPropertyFilters(self):
        """ return total number of property or rule in property filter panel """
        divElem = self.propertyFilterPanel.getElement(self.propertyFilterPanel.locator)
        childElems = divElem.find_elements_by_xpath("*")
        return len(childElems)
    
    def getPropertyFilter(self, position):
        """ return the propetyFilter elem specified by position """
        divElem = self.propertyFilterPanel.getElement(self.propertyFilterPanel.locator)
        childElems = divElem.find_elements_by_xpath("*")
        if position <= len(childElems):
            return childElems[position - 1]
        else:
            raise Exception("position '%s' is out of boundary"%position)
        
    def deletePropertyFilter(self, position):
        """ delete the property filter specified by position """
        propertyFilterElem = self.getPropertyFilter(position)
        if self._isPropertyRule(propertyFilterElem):
            self._deletePropertyRule(propertyFilterElem)
        else:
            self._deleteProperty(propertyFilterElem)
            
    def _isPropertyRule(self, propertyFilterElem):
        """ return true if the give elem is a rule, return false if the give elem is property """
        flag = "propertyFilterLevel"
        idString = propertyFilterElem.get_attribute("id")
        return flag in idString
                
    def _deletePropertyRule(self, propertyRuleElem):
        """ delete the specified propertyRule elem """
        aElem = propertyRuleElem.find_element_by_xpath(".//a[contains(@onclick, 'deleteSubFilter')]")
        aElem.click()
    
    def _deleteProperty(self, propertyElem):
        """ delete the specified property elem """
        aElem = propertyElem.find_element_by_xpath(".//a[contains(@onclick, 'deletePropertyFilter')]")
        aElem.click()
        
    def _modifyProperty(self, propertyElem, propertyValueComparison):
        """ Modify the property name, operator and value of the specific property element.
            The propertyValueComparison is a list of [property_name, operator, value]
        """
        flag = propertyElem.get_attribute("id") + '-targetEl'
        self.getDriver()
        divElem = self.driver.find_element_by_id(flag)
        childElems = divElem.find_elements_by_xpath("*")
        propertyNameElem = childElems[0]
        propertyOperatorElem = childElems[1]
        propertyValueElem = childElems[2]
        self._modifyPropertyItem(propertyNameElem, propertyValueComparison[0])
        self._modifyPropertyItem(propertyOperatorElem, propertyValueComparison[1])
        self._modifyPropertyItem(propertyValueElem, propertyValueComparison[2])
    
    def _modifyPropertyItem(self, propertyItemElem, strPropertyItemValue):
        strID = propertyItemElem.get_attribute("id")
        if "propertyOp" in strID:
            # special handling of the operator drop down
            driver = self.getDriver()
            target = driver.find_element_by_id("%s-trigger-picker"%strID)
            target.click()
            time.sleep(1)
            target = driver.find_element_by_id("%s-picker-listEl"%strID)
            liElements = target.find_elements_by_tag_name("li")
            for liElem in liElements:
                if liElem.text == strPropertyItemValue:
                    liElem.click()
                    break
        else:
            inputElem = propertyItemElem.find_element_by_tag_name("input")
            inputElem.click()
            inputElem.clear()
            inputElem.send_keys(strPropertyItemValue)
    
    def getTotalPropertyFromRule(self, propertyRuleElem):
        """ return total number of properties under the specified rule """ 
        divElem = propertyRuleElem.find_element_by_xpath(".//div[contains(@id, 'propertyFilterPanelSub_') and contains(@id, 'targetEl')]")
        childElems = divElem.find_elements_by_xpath("*")
        return len(childElems)
        
    def addPropertyToRule(self, propertyRuleElem):
        """ add a property to the specified property rule """
        aElem = propertyRuleElem.find_element_by_xpath(".//a[contains(@onclick, 'addProperty')]")
        aElem.click()
        
    def changePropertyRuleLogic(self, propertyRuleElem, theLogic):
        """ change the logic (AND OR) of the specified property rule """
        if theLogic not in ["AND", "OR"]:
            raise Exception("theLogic should be either 'AND' or 'OR'.")
        else:
            divElem = propertyRuleElem.find_element_by_xpath(".//table[contains(@id, 'logic_sub_')]")
            tdElem = divElem.find_element_by_xpath(".//tbody/tr/td[1]")
            if theLogic == 'OR':
                tdElem = divElem.find_element_by_xpath(".//tbody/tr/td[2]")
            inputElem = tdElem.find_element_by_tag_name("input")
            inputElem.click()
        
    def getPropertyFromRule(self, propertyRuleElem, position):
        """ return the property elem under the specified property rule by its position """
        divElem = propertyRuleElem.find_element_by_xpath(".//div[contains(@id, 'propertyFilterPanelSub_') and contains(@id, 'targetEl')]")
        childElems = divElem.find_elements_by_xpath("*")
        if position <= len(childElems):
            return childElems[position - 1]
        else:
            raise Exception("position '%s' is out of boundary"%position)
        
    def deletePropertyFromRule(self, propertyRuleElem, position):
        """ delete a property from the specified property rule specified by position """
        targetElem = self.getPropertyFromRule(propertyRuleElem, position)
        aElem = targetElem.find_element_by_xpath(".//a[contains(@onclick, 'deletePropertyFilter')]")
        aElem.click()
        
        
class DeleteConfirmWindow(BaseWebElement):
    """ Model the delete confirmation window web element """
    
    btnYes = ButtonWebElement("DeleteConfirmWindow.btnYes")
    btnNo  = ButtonWebElement("DeleteConfirmWindow.btnNo")
    
    def __init__(self, locatorString):
        super(DeleteConfirmWindow, self).__init__("BASReportPageObj.deleteConfirmWindow")
    

class BASReportPageObj(BaseFrameObject):
    """ generic BAS report page object module """
    
    configPanel           =  BaseWebElement("BASReportPageObj.configPanel")
    configPanel_Collapsed =  BaseWebElement("BASReportPageObj.configPanel_Collapsed")
    configPanel_Header    =  BaseWebElement("BASReportPageObj.configPanel_Header")
    
    reportHistory = ReportHistoryDropDown("BASReportPageObj.reportHistory")  
    
    save     = ButtonWebElement("BASReportPageObj.save")
    run      = ButtonWebElement("BASReportPageObj.run")
    delete   = ButtonWebElement("BASReportPageObj.delete")
    copy     = ButtonWebElement("BASReportPageObj.copy")
    schedule = ButtonWebElement("BASReportPageObj.schedule")
    email    = ButtonWebElement("BASReportPageObj.email")
    
    reportName  = EditBoxWebElement("BASReportPageObj.reportName")
    reportTitle = EditBoxWebElement("BASReportPageObj.reportTitle")
    site        = DropDownBoxWebElement("BASReportPageObj.site") 
    deviceRange = EditBoxWebElement("BASReportPageObj.deviceRange")
    
    addFilter    = ButtonWebElement("BASReportPageObj.addFilter")
    filterPanel  = BaseWebElement("BASReportPageObj.filterPanel")
    
    objectFilterWindow = ObjectFilterWindow("BASReportPageObj.objectFilterWindow")
    
    deleteConfirmWindow = DeleteConfirmWindow("BASReportPageObj.deleteConfirmWindow")
    
    
    loadingMask = TextBoxWebElement("BASReportPageObj.loadingMask")
    
    generatedReportLogo = GeneratedReportLogo("BASReportPageObj.generatedReportLogo")
    
    
    def __init__(self):
        super(BASReportPageObj, self).__init__()
        self.titleExpected = "Report Form"
        self.focus()
        
    def __repr__(self):
        super(BASReportPageObj, self).__repr__()
        
    def __str__(self):
        return "Generic BAS Report Configuration Page"
    
    def isLoaded(self):
        """
        verify if the report frame is loaded successfully
        """
        self.focus()
        if self.configPanel_Header.isDisplayed():
            elem = self.configPanel_Header.getElement(self.configPanel_Header.locator)
            titleCurrent = elem.text
            titleExpected = self.__str__()
            result = titleExpected in titleCurrent
            return result
        else:
            return False
        
    def saveChange(self, timeout=10):
        """ click the save button and wait page refreshed"""
        self.save.click()    # click the save button
        time.sleep(2)
        locator = self.configPanel_Header.locator
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.ID, locator["value"])))
        except TimeoutException:
            raise Exception("%s Setup UI is not finish loading within %s seconds"%(self, timeout))
        
    def deleteInstance(self, timeout=10):
        """ click the delete button and select yes in popup and wait page refresh """
        self.focus()
        self.delete.click()
        result = self.deleteConfirmWindow.isDisplayed()
        if not result:
            raise Exception("Delete confirm window is not displayed after click the Delete button")
        self.deleteConfirmWindow.btnYes.click()
        time.sleep(2)
        locator = self.configPanel_Header.locator
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.ID, locator["value"])))
        except TimeoutException:
            raise Exception("%s Setup UI is not finish loading within %s seconds"%(self, timeout))
        
        
    def isReportUITimeOut(self):
        """ return true if the generating report UI timeout
        """
        flag = "Time out generating report"
        driver = self.driver
        return flag in driver.page_source
                    
        
    def generatingReport(self, timeout, clickRun=True):
        """ command to click run button and waits till the report is generated and if the waitting time exceed time limit
            it give timeout warning and return false otheer wise it will return true
            
            @param string timeout    timeout time for the report generating (seconds)
            @return boolean          return true if the node is successively created under the specified path.
        """
        result = False
        driver = self.driver
        try:
            self.focus()
            if clickRun:
                self.run.click()
                # wait 8 seconds first
                time.sleep(8)
            # waiting for loading mask finish up
            elementID = self.loadingMask.locator.get("value")
            errMessage = "Report doesn't finish generating within %s seconds"%timeout
            WebDriverWait(driver, timeout).until(EC.invisibility_of_element_located((By.ID, elementID)), errMessage)
            # examine the report logo
            errMessage = "Generated report is not as expected"
            elementID = self.generatedReportLogo.locator.get("value")
            flag = "//img[starts-with(@id, '%s')]"%elementID
            elem = WebDriverWait(driver, 3).until(self._elem_available_cb(flag), errMessage)
            if elem:
                result = True
        except Exception, e:
            print "generatingReport(): get Exception: %s"%e 
            result = False
        return result
    
    def _elem_available_cb(self, flag):
        """ helper function for generatingReport()
            return a callback that checks whether the element is available
        """
        def callback(Inputdriver):
            result = True
            try:
                Inputdriver.switch_to_default_content()
                Inputdriver.switch_to_frame("mainFrame")
                Inputdriver.switch_to_frame("resultReport")
                elem = Inputdriver.find_element_by_xpath(flag)
            except Exception, e:
                result = False
            return result
        return callback
        
        
    def addObjectFilter(self, dicObjectFilter):
        """ click the Add filter button to load the object filter window """
        self.addFilter.click()
        time.sleep(1)
        result = self.objectFilterWindow.isDisplayed()
        if not result:
            raise Exception("object filter window is not displayed after click Add filter button")
        
        objectTypes = dicObjectFilter["Type"]
        for objectType in objectTypes:
            self.objectFilterWindow.objectType = objectType
        self.objectFilterWindow.objectType.collapse()
        
        objectInstance = dicObjectFilter["Instance"]
        self.objectFilterWindow.instance = objectInstance
        
        time.sleep(3)
        
        if "Properties" in dicObjectFilter:
            properties = dicObjectFilter["Properties"]
            if properties != None:
                for property in properties:
                    if isinstance(property, types.ListType):
                        self.objectFilterWindow.addProperty(property)
                    else:
                        self.objectFilterWindow.addRule(property)
            
                if len(properties) > 1:
                    propertyLogic = dicObjectFilter["Property Logic"]
                    if propertyLogic == "OR":
                        self.objectFilterWindow.logicOR.click()
                    else:
                        self.objectFilterWindow.logicAND.click()
            
        self.objectFilterWindow.btnOK.click()
        
        
    def _getObjectFilter(self, position):
        """ return the specified object filter elemetn under filter panel """
        elem = self.filterPanel.getElement(self.filterPanel.locator)
        childElems = elem.find_elements_by_xpath("*")
        if position <= len(childElems):
            return childElems[position - 1]
        else:
            raise Exception("position '%s' is out of boundary"%position)
    
    def editObjectFilter(self, position):
        """ click the edit filter button by the specified position to load object filter window """
        divElem = self._getObjectFilter(position)
        aElem = divElem.find_element_by_xpath(".//a[contains(@onclick, 'displayFilter')]")
        aElem.click()
    
    def deleteObjectFilter(self, position):
        """ click the delete filter button by the specified position to remove a object filter """
        divElem = self._getObjectFilter(position)
        aElem = divElem.find_element_by_xpath(".//a[contains(@onclick, 'deleteFilter')]")
        aElem.click()
        
        
    ##################################
    # generated report related method
    ##################################
    def generatedReportHasNoData(self):
        """ return true if the generated has no data to display
        """
        driver = self.driver
        driver.switch_to_default_content()
        driver.switch_to_frame("mainFrame")
        driver.switch_to_frame("resultReport")
        try:
            elem = driver.find_element_by_xpath("//*[contains(text(), 'No data to display')]")
            result = elem.is_displayed()
        except Exception:
            result = False
        driver.switch_to_default_content()
        driver.switch_to_frame("mainFrame")
        return result
        
    