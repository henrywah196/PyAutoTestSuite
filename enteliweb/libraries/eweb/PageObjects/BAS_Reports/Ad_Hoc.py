'''
Created on Nov 9, 2016

@author: hwang
'''
from BAS_Report_Generic import BASReportPageObj
from libraries.eweb.PageObjects.BaseWebElement import BaseWebElement, EditBoxWebElement, DropDownBoxWebElement, CheckBoxWebElement, ButtonWebElement
from selenium.common.exceptions import NoSuchElementException
import time
from selenium.webdriver.common.action_chains import ActionChains


###################################
# Column Format Window web element
###################################
class AlignmentDropDownBox(DropDownBoxWebElement):
    """ Model the Alignment dropdown box web element """
    
    def __init__(self, locatorString):
        super(AlignmentDropDownBox, self).__init__("ColumnFormatWindow.alignment")
     
    def getDropDownList(self): 
        """ return the drop down list element """ 
        driver = self.getDriver() 
        dropDownList = None
        self.click()
        boundLists = driver.find_elements_by_id('alignmentCombo-picker-listEl')
        if boundLists:
            for boundList in boundLists:
                if boundList.is_displayed():
                    dropDownList = boundList
                    break
        del boundLists
        return dropDownList
        
class ValueFormatDropDownBox(DropDownBoxWebElement):
    """ Model the Value Format dropdown box web element """
    
    def __init__(self, locatorString):
        super(ValueFormatDropDownBox, self).__init__("ColumnFormatWindow.valueFormat")
        
    def __set__(self, obj, val):
        """ select a item from the drop down box """
        dropDownList = self.getDropDownList()
        if dropDownList:
            itemObjs = dropDownList.find_elements_by_class_name('x-boundlist-item')
            target = None
            for item in itemObjs:
                if item.text == val:
                    target = item
                    break
            if target:
                target.location_once_scrolled_into_view
                target.click()
     
    def getDropDownList(self): 
        """ return the drop down list element """ 
        driver = self.getDriver()
        dropDownList = None
        self.click()
        boundLists = driver.find_elements_by_id('formatCombo-picker-listEl')
        if boundLists:
            for boundList in boundLists:
                if boundList.is_displayed():
                    dropDownList = boundList
                    break
        del boundLists
        return dropDownList

class ColumnFormatWindow(BaseWebElement):
    """ Model the column format popup window web element """
    
    columnName     = EditBoxWebElement("ColumnFormatWindow.columnName")
    columnProperty = EditBoxWebElement("ColumnFormatWindow.columnProperty")
    alignment      = AlignmentDropDownBox("ColumnFormatWindow.alignment")
    valueFormat    = ValueFormatDropDownBox("ColumnFormatWindow.valueFormat")
    visible        = CheckBoxWebElement("ColumnFormatWindow.visible")
    ok             = ButtonWebElement("ColumnFormatWindow.ok")
    cancel         = ButtonWebElement("ColumnFormatWindow.cancel")
    
    def __init__(self, locatorString):
        super(ColumnFormatWindow, self).__init__("ReportFormatWindow.columnFormatWindow")


###################################
# Report Format Window web element
###################################
class GroupSortPropertyDropDownBox(DropDownBoxWebElement):
    """ Model the Sort Groups By property dropdown box web element """
    
    def __init__(self, locatorString):
        super(GroupSortPropertyDropDownBox, self).__init__("ReportFormatWindow.groupSortProperty")
     
    def getDropDownList(self): 
        """ return the drop down list element """ 
        driver = self.getDriver()
        dropDownList = None
        self.click()
        boundLists = driver.find_elements_by_id('sortProperty-picker-listEl')
        if boundLists:
            for boundList in boundLists:
                if boundList.is_displayed():
                    dropDownList = boundList
                    break
        del boundLists
        return dropDownList
    
class GroupSortDirectionDropDownBox(DropDownBoxWebElement):
    """ Model the Sort Groups By property dropdown box web element """
    
    def __init__(self, locatorString):
        super(GroupSortDirectionDropDownBox, self).__init__("ReportFormatWindow.groupSortDirection")
     
    def getDropDownList(self): 
        """ return the drop down list element """ 
        driver = self.getDriver()
        dropDownList = None
        self.click()
        boundLists = driver.find_elements_by_id('sortDirection-picker-listEl')
        if boundLists:
            for boundList in boundLists:
                if boundList.is_displayed():
                    dropDownList = boundList
                    break
        del boundLists
        return dropDownList

class ReportFormatWindow(BaseWebElement):
    """ Model the Edit Report Format window web element """
    
    addColumn           = ButtonWebElement("ReportFormatWindow.addColumn")
    columnFormatWindow  = ColumnFormatWindow("ReportFormatWindow.columnFormatWindow")
    groupSortProperty   = GroupSortPropertyDropDownBox("ReportFormatWindow.groupSortProperty")
    groupSortDirection  = GroupSortDirectionDropDownBox("ReportFormatWindow.groupSortDirection")
    ok                  = ButtonWebElement("ReportFormatWindow.ok")
    cancel              = ButtonWebElement("ReportFormatWindow.cancel")
    
    def __init__(self, locatorString):
        super(ReportFormatWindow, self).__init__("AdHocPageObj.reportFormatWindow")
        
    def setSortGroupBy(self, columnName, direction="Ascending"):
        """ setup Sort Group By field """
        self.groupSortProperty = columnName
        self.groupSortDirection = direction
        
    def setGroupBy(self, columnName, clearGroupBy=False):
        """ set or clear Group By """
        menuItemName = "Group By This Field"
        if clearGroupBy:
            menuItemName = "Show in Groups"
        
        target = None
        driver = self.getDriver()
        columnsHeaderInfo = self._getColumnsHeaderElemID()
        for item in columnsHeaderInfo:
            if item[0] == columnName:
                target = item
                break
        if target is not None:
            targetElem = driver.find_element_by_id(item[1])
            targetElem.click()
            time.sleep(1)
            targetElem = driver.find_element_by_id(item[2])
            targetElem.click()
            time.sleep(1)
            result = self.isContextMenuDisplayed()
            if result:
                menuItem = self._getContextMenuItem(menuItemName)
                if menuItemName == "Show in groups" and self._isContextMenuItemEnabled(menuItemName):
                    menuItem.click()
                elif menuItemName == "Group By This Field":
                    menuItem.click()
        
    def setSortBy(self, columnName, sorting="Sort Ascending"):
        """ set sort by the specific column
            sorting could be Sort Ascending, Sort Descending or Clear Sort
        """
        target = None
        driver = self.getDriver()
        columnsHeaderInfo = self._getColumnsHeaderElemID()
        for item in columnsHeaderInfo:
            if item[0] == columnName:
                target = item
                break
        if target is not None:
            targetElem = driver.find_element_by_id(item[1])
            targetElem.click()
            time.sleep(1)
            targetElem = driver.find_element_by_id(item[2])
            targetElem.click()
            time.sleep(1)
            result = self.isContextMenuDisplayed()
            if result:
                menuItem = self._getContextMenuItem(sorting)
                menuItem.click()
        
    def addNewColumn(self, dicColumnSetting):
        """ add a new column to preview grid """
        columnHeading = dicColumnSetting["Heading"]    # must have this
        columnProperty = dicColumnSetting["Property"]    # must have this
        columnAlignment = None
        if "Alignment" in dicColumnSetting:
            columnAlignment = dicColumnSetting["Alignment"]
        columnFormat = None
        if "Format" in dicColumnSetting:
            columnFormat = dicColumnSetting["Format"]
        columnVisible = None
        if "Visible" in dicColumnSetting:
            columnVisible = dicColumnSetting["Visible"]
        
        self.addColumn.click()
        result = self.columnFormatWindow.isDisplayed()
        if not result:
            raise Exception("Edit Report Format - Add Column window is not displayed")
        if columnHeading is not None:
            self.columnFormatWindow.columnName = columnHeading
        if columnProperty is not None:
            self.columnFormatWindow.columnProperty = columnProperty
        if columnAlignment is not None:
            self.columnFormatWindow.alignment = columnAlignment
        if columnFormat is not None:
            self.columnFormatWindow.valueFormat = columnFormat
        if columnVisible is not None:
            self.columnFormatWindow.visible = columnVisible
        self.columnFormatWindow.ok.click()
        time.sleep(1)
        
    def isColumnExist(self, columnName):
        """ return true if the specified column exist in preview grid """
        result = False
        columnsHeaderInfo = self._getColumnsHeaderElemID()
        for item in columnsHeaderInfo:
            if item[0] == columnName:
                result = True
                break
        return result
        
    def deleteColumn(self, columnName):
        """ Remove column from current column view grid """
        target = None
        driver = self.getDriver()
        columnsHeaderInfo = self._getColumnsHeaderElemID()
        for item in columnsHeaderInfo:
            if item[0] == columnName:
                target = item
                break
        if target is not None:
            targetElem = driver.find_element_by_id(item[1])
            targetElem.click()
            time.sleep(1)
            targetElem = driver.find_element_by_id(item[2])
            targetElem.click()
            time.sleep(1)
            result = self.isContextMenuDisplayed()
            if result:
                menuItem = self._getContextMenuItem("Remove Column")
                menuItem.click()
            else:
                raise Exception("deleteColumn(): Context Menu is not displayed in time")
                
    def getColumnHeaders(self):
        """ return a list of existing column headers """
        result = []
        columnsHeaderInfo = self._getColumnsHeaderElemID()
        for item in columnsHeaderInfo:
            result.append(item[0])
        return result
    
    def isContextMenuDisplayed(self):
        """ return true if the context menu is displayed """
        idString = self._getContexMenuElemID()
        driver = self.getDriver()
        target = driver.find_element_by_id(idString)
        return target.is_displayed()
    
    def _getColumnsHeaderElemID(self):
        """" Helper to return a list of column header web element id.
             Each item in the list contains the column header name and 
             its web element id.
        """
        result = []
        formatPreviewGridElem = self.getElement(self.locators.get("ReportFormatWindow.formatPreviewGrid"))
        headerContainerElem = formatPreviewGridElem.find_element_by_class_name("x-grid-header-ct")
        idString = headerContainerElem.get_attribute("id")
        idString = idString + "-targetEl"
        headerContainerElem = formatPreviewGridElem.find_element_by_id(idString)
        gridColumnsElems = headerContainerElem.find_elements_by_xpath('./div')
        for item in gridColumnsElems:
            itemList = []
            idString = item.get_attribute("id")
            targetElem = item.find_element_by_id(idString + "-textInnerEl")
            if targetElem.text == ' ':
                continue
            itemList.append(targetElem.text)
            itemList.append(idString + "-textEl")
            itemList.append(idString + "-triggerEl")
            result.append(itemList)
        return result
    
    def _getContexMenuElemID(self):
        """ helper to return the context menu web element id """
        flag = "x-menu"
        driver = self.getDriver()
        target = driver.find_element_by_class_name(flag)
        return target.get_attribute("id")
    
    def _getContextMenuItems(self):
        """ helper to return a list of context menu  menuitem web elements """
        result = []
        flag = "x-menu-item"
        driver = self.getDriver()
        menuItems = driver.find_elements_by_class_name(flag)
        if menuItems:
            for item in menuItems:
                idString = item.get_attribute("id")
                if "menuseparator" in idString:
                    continue
                else:
                    result.append(item)
        return result
    
    def _getContextMenuItem(self, menuItemName):
        """ helper to return a specified context menuitem web element """
        result = None
        contextMenuItems = self._getContextMenuItems()
        for item in contextMenuItems:
            idString = item.get_attribute("id")
            idString = idString + "-textEl"
            target = item.find_element_by_id(idString)
            if target.text == menuItemName:
                result = target
                break
        return result
    
    def _isContextMenuItemEnabled(self, menuItemName):
        """ helper to return true if the specified menu item is enabled """
        flag = "x-menu-item-disabled"
        target = self._getContextMenuItem(menuItemName)
        classString = target.get_attribute("class")
        if flag in classString:
            return False
        else:
            return True
    

############################################
# Object Query Bas Report Page Object Model
############################################
class AdHocPageObj(BASReportPageObj):
    """ BAS Dynamic Columns Report page object module """
    
    editFormat         = ButtonWebElement("AdHocPageObj.editFormat")
    reportFormatWindow = ReportFormatWindow("AdHocPageObj.reportFormatWindow")
    
        
    def __repr__(self):
        super(AdHocPageObj, self).__repr__()
        
    def __str__(self):
        return "Report: Object Query"
    
    
    def editReportFormat(self, listDynamicColumns, dicSortGroup):
        """ load edit report format windows and modify the settings """
        self.editFormat.click()
        time.sleep(1)
        result = self.reportFormatWindow.isDisplayed()
        if not result:
            raise Exception("Edit Format Window is not displayed after click Edit Format button")
        
        # removing all existing columns
        columnHeaders = self.reportFormatWindow.getColumnHeaders()
        for item in columnHeaders:
            self.reportFormatWindow.deleteColumn(item)
        
        # add new columns
        for item in listDynamicColumns:
            self.reportFormatWindow.addNewColumn(item)
            
        # Setup sort and group
        if "Sort By" in dicSortGroup:
            sortBy = dicSortGroup["Sort By"]
            self.reportFormatWindow.setSortBy(sortBy[0], sortBy[1])
        if "Group By" in dicSortGroup:
            groupBy = dicSortGroup["Group By"]
            self.reportFormatWindow.setGroupBy(groupBy)
            self.reportFormatWindow.setSortBy(groupBy, "Clear Sort")
        if "Sort Group By" in dicSortGroup:
            sortGroupBy = dicSortGroup["Sort Group By"]
            self.reportFormatWindow.setSortGroupBy(sortGroupBy[0], sortGroupBy[1])
            
        self.reportFormatWindow.ok.click()
        
        
    ##################################
    # generated report related method
    ##################################
    def generatedReportGetData(self, strKeyWord=None):
        """ return data from generated report
        """
        try:
            driver = self.driver
            driver.switch_to_default_content()
            driver.switch_to_frame("mainFrame")
            driver.switch_to_frame("resultReport")
            if strKeyWord == "grouping label":    # ask for grouping label only
                tocElements = self._generatedReportGetKeyTOCElements()
                if len(tocElements) > 0:
                    result = []
                    for item in tocElements:
                        groupLabel = self._generatedReportGetGroupLabel(item)
                        result.append(groupLabel)
                    return result
                else:
                    return []
            else:
                return self._generatedReportGetObjInfo()
        finally:
            driver.switch_to_default_content()
            driver.switch_to_frame("mainFrame")
    
    def _generatedReportGetLabelRowElemClassName(self):
        """ helper to return the class name of the tr element of the report label row """
        driver = self.driver
        try:
            target = driver.find_element_by_xpath("//table/tbody/tr[2]/td/table[2]/tbody/tr[1]")
            return target.get_attribute("class")
        except NoSuchElementException, e:
            print "Exception on AdHocPageObj._generatedReportGetLabelRowElemClassName(): %s"%str(e)
            return None
            
    
    def _generatedReportGetDataRowElemClassName(self):
        """ helper to return the class name of the tr element of the report data row """
        driver = self.driver
        tocElements = self._generatedReportGetKeyTOCElements()
        className = self._generatedReportGetLabelRowElemClassName()
        if className is None:
            return None
        else:
            target = driver.find_element_by_class_name(className)
            if len(tocElements) > 0:    # report is grouped
                target = tocElements[0]
            nextSiblingElements = target.find_elements_by_xpath("./following-sibling::tr[starts-with(@class, 'style_')]")
            return nextSiblingElements[0].get_attribute("class")
    
    def _generatedReportGetRowLabel(self):
        """ helper to return a list of data table column header """
        result = []
        className = self._generatedReportGetLabelRowElemClassName()
        if className is None:
            return []
        else:
            trElem = self.driver.find_element_by_class_name(className)
            tdElements = trElem.find_elements_by_tag_name("th")
            for tdElem in tdElements:
                divElem = tdElem.find_element_by_xpath("./div/div")
                result.append(divElem.text)
            return result
    
    def _generatedReportGetGroupLabel(self, trElem):
        """ helper to return the label string of the group label row element """
        
        # special case for device name and device number combined
        #spanElem = trElem.find_element_by_xpath("./td[1]/span[1]")
        #deviceName = spanElem.text
        #spanElem = trElem.find_element_by_xpath("./td[1]/span[2]")
        #deviceNumber = spanElem.text
        #return "%s %s"%(deviceName, deviceNumber)
        return (trElem.text).strip()
        
            
    
    def _generatedReportGetKeyTOCElements(self):
        """ helper to return a list of [__TOC_0, __TOC_1, ...] elements
            which represent the group label row in the generated report
        """
        result = []
        driver = self.driver
        elements = driver.find_elements_by_xpath("//tr[starts-with(@id, '__TOC_')]")
        if len(elements) > 0:
            for elem in elements:
                idString = elem.get_attribute("id")
                result.append(elem) 
        return result
    
    def _generatedReportGetRowElems(self, startElem, endElem=None):
        """ helper to return a list of tr elements between tartElem and endElem
            it is used when grouping in generated report
        """
        className = self._generatedReportGetDataRowElemClassName()
        if endElem is not None:
            result = []
            #nextSiblingElements = startElem.find_elements_by_xpath("./following-sibling::tr")
            flag = endElem.get_attribute("id")
            nextSiblingElements = startElem.find_elements_by_xpath("./following-sibling::tr[starts-with(@class, 'style_')] | ./following-sibling::tr[@id='%s']"%flag)
            for elem in nextSiblingElements:
                if elem == endElem:
                    break
                else:
                    result.append(elem)
            return result
        else:
            nextSiblingElements = startElem.find_elements_by_xpath("./following-sibling::tr[starts-with(@class, 'style_')]")
            return nextSiblingElements
        
    def _generatedReportGetObjInfo(self):
        """ helper to return the object list in the data table """
        columnHeaders = self._generatedReportGetRowLabel()
        if len(columnHeaders) == 0:
            return []    # no data at all
        else:
            tocElements = self._generatedReportGetKeyTOCElements()
            if len(tocElements) > 0:   # grouping in generated report
                result = {}
                i = 0
                while i < len(tocElements):
                    startElem = tocElements[i]
                    groupLabel = self._generatedReportGetGroupLabel(startElem)
                    endElem = None
                    if (i + 1) < len(tocElements):
                        endElem = tocElements[i + 1]
                    dataRowElements = self._generatedReportGetRowElems(startElem, endElem)
                    groupResult = []
                    for dataRowElem in dataRowElements:
                        rowDic = {}
                        tdElements = dataRowElem.find_elements_by_tag_name("td")
                        j = 0
                        while j < len(tdElements):
                            try:
                                divElem = tdElements[j].find_element_by_xpath("./div/div")
                                rowDic[columnHeaders[j]] = divElem.text
                            except NoSuchElementException:
                                rowDic[columnHeaders[j]] = ""
                            j = j + 1
                        groupResult.append(rowDic)
                    result[groupLabel] = groupResult
                    i = i + 1
                return result
                    
            else:    # no grouping in generated report
                result = []
                className = self._generatedReportGetDataRowElemClassName()
                dataRowElements = self.driver.find_elements_by_class_name(className)
                for dataRowElem in dataRowElements:
                    rowDic = {}
                    tdElements = dataRowElem.find_elements_by_tag_name("td")
                    i = 0
                    while i < len(tdElements):
                        try:
                            divElem = tdElements[i].find_element_by_xpath("./div/div")
                            rowDic[columnHeaders[i]] = divElem.text
                        except NoSuchElementException:
                            rowDic[columnHeaders[i]] = ""
                        i = i + 1
                    result.append(rowDic)
                return result
            
    
    