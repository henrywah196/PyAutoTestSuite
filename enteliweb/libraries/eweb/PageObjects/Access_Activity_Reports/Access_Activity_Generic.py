'''
Created on Nov 9, 2016

@author: hwang
'''
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from libraries.eweb.PageObjects.BasePageObject import BaseFrameObject
from libraries.eweb.PageObjects.BaseWebElement import BaseWebElement, TextBoxWebElement, EditBoxWebElement, ButtonWebElement, DropDownBoxWebElement, CheckBoxWebElement
from libraries.eweb.PageObjects.BAS_Reports.BAS_Report_Generic import ReportHistoryDropDown, DeleteConfirmWindow, GeneratedReportLogo
from libraries.eweb.PageObjects.BAS_Reports.Ad_Hoc import ReportFormatWindow
import time, datetime
import types


ACCESS_EVENT_TYPES = {0 : ["None"              , ""],
                      1 : ["Valid Access"      , "CU"],
                      2 : ["Unrecognized Card" , "CU"],
                      3 : ["Invalid PIN"       , "CU"],
                      4 : ["Disabled Card"     , "CU"],
                      5 : ["Expired User"      , "CU"],
                      6 : ["Inactive User"     , "CU"],
                      7 : ["User Disabled"     , "CU"],
                      8 : ["APB Violation"     , "CU"],
                      9 : ["Time Zone Violation" , "CU"],
                      10 : ["Invalid Zone Access" , "CU"],
                      11 : ["Lost Card"           , "CU"],
                      12 : ["PIN Timeout"         , "CU"],
                      13 : ["Access Inhibit"      , ""],
                      14 : ["Forced Open"         , "DC"],
                      15 : ["Forced Open Restored" , "DC"],
                      16 : ["Trouble"              , "DC"],
                      17 : ["Trouble Ended"        , "DC"],
                      18 : ["Life Safety On"       , "DC"],
                      19 : ["Life Safety Off"      , "DC"],
                      20 : ["Manual Control"       , "DC"],
                      21 : ["Manual Locked"        , "DC"],
                      22 : ["Manual Unlocked"      , "DC"],
                      23 : ["Manual Life Safety"   , "DC"],
                      24 : ["Manual Lock Down"     , "DC"],
                      25 : ["Manual Emergency"     , "DC"],
                      26 : ["Manual Relinquish"    , "DC"],
                      27 : ["Lock Schedule Active" , "DC"],
                      28 : ["Lock Schedule Relinquished"   , "DC"],
                      29 : ["Unlock Schedule"              , "DC"],
                      30 : ["Unlock Schedule Pending"      , "DC"],
                      31 : ["Unlock Schedule Relinquished" , "DC"],
                      32 : ["Relock Mode Timeout"          , "DC"],
                      33 : ["Relock Mode Locked"           , "DC"],
                      34 : ["Relock Mode Unlocked"         , "DC"],
                      35 : ["Relock Mode Schedule Locked"  , "DC"],
                      36 : ["Relock Mode Enabled"          , "DC"],
                      37 : ["Motion Unlocked Door"         , "DC"],
                      38 : ["Motion Locked Door"           , "DC"],
                      39 : ["GCL+ Control"                 , "DC"],
                      40 : ["GCL+ Relinquished"            , "DC"],
                      41 : ["Door Group Manual Unlocked"   , "DC"],
                      42 : ["Door Group Manual Locked"     , "DC"],
                      43 : ["Door Group Manual Life Safety"   , "DC"],
                      44 : ["Door Group Manual Lock Down"     , "DC"],
                      45 : ["Door Group Control Relinquished" , "DC"],
                      46 : ["Door Ajar"                       , "DC"],
                      47 : ["Door Ajar Ended"                 , "DC"],
                      48 : ["Trace User"                      , "CU"],
                      49 : ["Elevator Hatch Open"             , ""],
                      50 : ["Elevator Hatch Closed"           , ""],
                      51 : ["Public Mode"                     , ""],
                      52 : ["Secure Mode"                     , ""],
                      53 : ["Floor Override"                  , ""],
                      54 : ["Elevator Bypass On"              , ""],
                      55 : ["Elevator Bypass Off"             , ""],
                      56 : ["Elevator Emergency On"           , ""],
                      57 : ["Elevator Emergency Off"          , ""],
                      58 : ["Time Change"                     , ""],
                      59 : ["Device Online"                   , ""],
                      60 : ["Device Offline"                  , ""],
                      61 : ["Device Reset"                    , ""],
                      62 : ["Request To Exit"                 , "DC"],
                      63 : ["Approval Denied"                 , "DC"],
                      64 : ["Relock Mode Relinquished"        , "DC"],
                      65 : ["Muster"                          , "CU"],
                      66 : ["Database Load"                   , ""],
                      67 : ["Database Save"                   , ""],
                      68 : ["Database Cleared"                , ""],
                      69 : ["Two Man Fail Timeout"            , ""],
                      70 : ["Two Man Fail Authentication"     , ""],
                      71 : ["Two Man Valid Access"            , ""],
                      72 : ["Two Man Initiated"               , ""],
                      73 : ["Manual Bypass"                   , "DC"],
                      74 : ["Dead Battery"                    , ""],
                      75 : ["Single Phase Fault"              , ""],
                      76 : ["Command Failure"                 , ""],
                      77 : ["Status On"                       , ""],
                      78 : ["Status Off"                      , ""],
                      79 : ["Under Voltage"                   , ""],
                      80 : ["Over Voltage"                    , ""],
                      81 : ["Alarm Output Activated"          , ""],
                      82 : ["Alarm Output Acknowledged"       , ""],
                      83 : ["Invalid Status"                  , ""],
                      84 : ["Invalid Status Restored"         , ""],
                      85 : ["Single Phase Fault Restored"     , ""],  
                      86 : ["Over Voltage Restored"           , ""],
                      87 : ["Under Voltage Restored"          , ""],
                      88 : ["Dead Battery Restored"           , ""],
                      89 : ["Command Failure Restored"        , ""],
                      90 : ["Breaker Shorted"                 , ""],
                      91 : ["Breaker Short Restored"          , ""],
                      92 : ["Alarm Input Active"              , ""],
                      93 : ["Alarm Input Restored"            , ""],
                      94 : ["Reserved"                        , ""] 
                               }


class ObjectSelectWindow(BaseWebElement):
    """ Model the find object popup window web element """
    
    popupWindowBody = BaseWebElement("ObjectSelectWindow.popupWindowBody")
    optionPanel     = BaseWebElement("ObjectSelectWindow.optionPanel")
    toolBarPanel    = BaseWebElement("ObjectSelectWindow.toolBarPanel")
    mainPanel       = BaseWebElement("ObjectSelectWindow.mainPanel")
    headerPanel     = BaseWebElement("ObjectSelectWindow.headerPanel")
    gridPanel       = BaseWebElement("ObjectSelectWindow.gridPanel")
    pagingPanel     = BaseWebElement("ObjectSelectWindow.pagingPanel")
    bottomPanel     = BaseWebElement("ObjectSelectWindow.bottomPanel")
    
    btnByName     = ButtonWebElement("ObjectSelectWindow.btnByName")
    btnByKeyword  = ButtonWebElement("ObjectSelectWindow.btnByKeyword")
    
    btnSelectAll   = ButtonWebElement("ObjectSelectWindow.btnSelectAll")
    btnUnselectAll = ButtonWebElement("ObjectSelectWindow.btnUnselectAll")
    filterBy       = EditBoxWebElement("ObjectSelectWindow.filterBy")
    
    pageNumber = EditBoxWebElement("ObjectSelectWindow.pageNumber")
    
    btnOK     = ButtonWebElement("ObjectSelectWindow.btnOK")
    btnCancel = ButtonWebElement("ObjectSelectWindow.btnCancel")
    
    
    
    def __init__(self, locatorString):
        super(ObjectSelectWindow, self).__init__(locatorString)
        
    
    def getCurrentPageNumber(self):
        """ return the current page number """
        elem = self.pageNumber.getElement(self.pageNumber.locator)
        return elem.get_attribute("aria-valuenow")
        
    def getTotalPageNumber(self):
        """ return total page number """
        target = self.pagingPanel.getElement(self.pagingPanel.locator)
        flag = target.get_attribute("id")
        flag = flag + "-targetEl"
        driver = self.getDriver()
        target = driver.find_element_by_id(flag)
        target = target.find_element_by_xpath("./div[4]")
        result = (target.text).strip()
        return result[3:]
    
    def setCurrentPage(self, pageNumber):
        """ select a specific page as current page """
        self.pageNumber = pageNumber
        elem = self.pageNumber.getElement(self.pageNumber.locator)
        elem.send_keys(Keys.RETURN)
        
    def _getGridHeaders(self):
        """ return a list of grid header """
        result = []
        elem = self.headerPanel.getElement(self.headerPanel.locator)
        spans = elem.find_elements_by_xpath(".//span[starts-with(@id, 'gridcolumn-')]")
        for span in spans:
            result.append((span.text).strip())
        return result
        
    def _getGridContent(self):
        """ return a list of web elements from the current page of the grid """
        elem = self.gridPanel.getElement(self.gridPanel.locator)
        trs = elem.find_elements_by_tag_name("tr")
        return trs
    
    def getObjectsList(self):
        "return a list of object info from the current page of the grid"
        result = []
        trs = self._getGridContent()
        for tr in trs:
            item = []
            tds = tr.find_elements_by_xpath(".//td[contains(@class, '-gridcolumn-')]")
            for td in tds:
                item.append((td.text).strip())
            result.append(item)
        return result
    
    def _selectRow(self, tr, click=True):
        """ check the check box of the specific row element """
        flag = "x-grid-checkcolumn-checked"
        tr.location_once_scrolled_into_view
        if click:
            td = tr.find_element_by_xpath("./td[1]")
            div = td.find_element_by_xpath(".//div[@role='button']")
            result = div.get_attribute("class")
            if not flag in result:
                div.click()
        
    
    def selectObject(self, target):
        """ select a object from the current page of the grid """
        result = self.getObjectsList()
        if isinstance(target, int):
            if target >= 0 and target < len(result):
                trs = self._getGridContent()
                tr = trs[target]
                self._selectRow(tr)
            elif target >= len(result) and target < 100:
                trs = self._getGridContent()
                tr = trs[len(result) - 1]
            else:
                raise Exception("%s was not found in the current page of the grid"%target)
        else:
            idx = None
            if target in result:
                idx = result.index(target)
            if idx is not None:
                self.selectObject(idx)
            else:
                raise Exception("'%s' was not found in the current page of the grid"%target)
            

class AccessActivityReportPageObj(BaseFrameObject):
    """ generic access activity report page object module """
    
    configPanel           =  BaseWebElement("AccessActivityReportPageObj.configPanel")
    configPanel_Collapsed =  BaseWebElement("AccessActivityReportPageObj.configPanel_Collapsed")
    configPanel_Header    =  BaseWebElement("AccessActivityReportPageObj.configPanel_Header")
    
    reportHistory = ReportHistoryDropDown("AccessActivityReportPageObj.reportHistory")  
    
    save     = ButtonWebElement("AccessActivityReportPageObj.save")
    run      = ButtonWebElement("AccessActivityReportPageObj.run")
    delete   = ButtonWebElement("AccessActivityReportPageObj.delete")
    copy     = ButtonWebElement("AccessActivityReportPageObj.copy")
    schedule = ButtonWebElement("AccessActivityReportPageObj.schedule")
    email    = ButtonWebElement("AccessActivityReportPageObj.email")
    
    reportName     = EditBoxWebElement("AccessActivityReportPageObj.reportName")
    reportTitle    = EditBoxWebElement("AccessActivityReportPageObj.reportTitle")
    site           = DropDownBoxWebElement("AccessActivityReportPageObj.site") 
    datetimeFormat = DropDownBoxWebElement("AccessActivityReportPageObj.datetimeFormat") 
    
    dateRange       = DropDownBoxWebElement("AccessActivityReportPageObj.dateRange")
    dateFrom        = EditBoxWebElement("AccessActivityReportPageObj.dateFrom")
    dateFromTrigger = ButtonWebElement("AccessActivityReportPageObj.dateFromTrigger")
    timeFrom        = EditBoxWebElement("AccessActivityReportPageObj.timeFrom")
    timeFromTrigger = ButtonWebElement("AccessActivityReportPageObj.timeFromTrigger")
    dateTo          = EditBoxWebElement("AccessActivityReportPageObj.dateTo")
    dateToTrigger   = ButtonWebElement("AccessActivityReportPageObj.dateToTrigger")
    timeTo          = EditBoxWebElement("AccessActivityReportPageObj.timeTo")
    timeToTrigger   = ButtonWebElement("AccessActivityReportPageObj.timeToTrigger")
    
    cardsDelete  = ButtonWebElement("AccessActivityReportPageObj.cardsDelete")
    doorsDelete  = ButtonWebElement("AccessActivityReportPageObj.doorsDelete")
    eventsDelete = ButtonWebElement("AccessActivityReportPageObj.eventsDelete")
    cardsEdit    = ButtonWebElement("AccessActivityReportPageObj.cardsEdit")
    doorsEdit    = ButtonWebElement("AccessActivityReportPageObj.doorsEdit")
    eventsEdit   = ButtonWebElement("AccessActivityReportPageObj.eventsEdit")
    
    cardNumber = EditBoxWebElement("AccessActivityReportPageObj.cardNumber")
    siteCode   = EditBoxWebElement("AccessActivityReportPageObj.siteCode")
    
    findCardUsersWindow = ObjectSelectWindow("AccessActivityReportPageObj.findCardUsersWindow")
    findDoorsWindow     = ObjectSelectWindow("AccessActivityReportPageObj.findDoorsWindow")
    selectEventsWindow  = ObjectSelectWindow("AccessActivityReportPageObj.selectEventsWindow")
    
    editFormat         = ButtonWebElement("AccessActivityReportPageObj.editFormat")
    reportFormatWindow = ReportFormatWindow("AccessActivityReportPageObj.reportFormatWindow")
    
    deleteConfirmWindow = DeleteConfirmWindow("AccessActivityReportPageObj.deleteConfirmWindow")
    
    loadingMask = TextBoxWebElement("AccessActivityReportPageObj.loadingMask")
    
    generatedReportLogo = GeneratedReportLogo("AccessActivityReportPageObj.generatedReportLogo")
    
    
    def __init__(self):
        super(AccessActivityReportPageObj, self).__init__()
        self.titleExpected = "Report Form"
        self.focus()
        
    def __repr__(self):
        super(AccessActivityReportPageObj, self).__repr__()
        
    def __str__(self):
        return "Generic Access Activity Report Configuration Page"
    
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
        
        
    def setupDateRange(self, settingDateRange):
        """ setup date range based on the given settings """
        dateRange = settingDateRange[0]
        self.dateRange = dateRange
        if dateRange == "Custom":
            dateFrom = settingDateRange[1]
            dateTo = settingDateRange[2]
            self.dateFrom = self._getDateString(dateFrom[0])
            self.timeFrom = dateFrom[1]
            self.timeFromTrigger.click()
            self.timeFromTrigger.click()
            self.dateTo = self._getDateString(dateTo[0])
            self.timeTo = dateTo[1]
            self.timeToTrigger.click()
            self.timeToTrigger.click()
            
            
    def _getDateString(self, dateString):
        """ helper used by setupDateRange() """
        if dateString == "%today%":
            return datetime.date.today().strftime("%Y-%m-%d")
        elif dateString == "%yesterday%":
            result = datetime.date.today() - datetime.timedelta(days=1)
            return result.strftime("%Y-%m-%d")
        elif dateString == "%tomorrow%":
            result = datetime.date.today() + datetime.timedelta(days=1)
            return result.strftime("%Y-%m-%d")
        else:
            return dateString
        
    
    def setupCareUsers(self, settingCardUsers):
        """ setup card users criteria based on the given settings """
        if self.cardsDelete.isDisplayed():
            self.cardsDelete.click()
        if settingCardUsers is not None:
            self.cardsEdit.click()
            result = self.findCardUsersWindow.isDisplayed()
            if result:
                option = settingCardUsers["Find Option"]
                filterBy = settingCardUsers["Filter By"]
                if option == "Find by Keyword":
                    self.findCardUsersWindow.btnByKeyword.click()
                    self.findCardUsersWindow.filterBy = filterBy
                elif option == "Find and Select by Name":
                    self.findCardUsersWindow.btnByName.click()
                    for item in filterBy:
                        self.findCardUsersWindow.filterBy = item[0]
                        time.sleep(1)
                        self.findCardUsersWindow.selectObject(item)
                self.findCardUsersWindow.btnOK.click()
            else:
                raise Exception("Find Card Users Window doesn't pop up.")
            
    
    def setupDoors(self, settingDoors):
        """ setup doors criteria based on the given settings """
        if self.doorsDelete.isDisplayed():
            self.doorsDelete.click()
        if settingDoors is not None:
            self.doorsEdit.click()
            result = self.findDoorsWindow.isDisplayed()
            if result:
                option = settingDoors["Find Option"]
                filterBy = settingDoors["Filter By"]
                if option == "Find by Keyword":
                    self.findDoorsWindow.btnByKeyword.click()
                    self.findDoorsWindow.filterBy = filterBy
                elif option == "Find and Select by Name":
                    self.findDoorsWindow.btnByName.click()
                    for item in filterBy:
                        self.findDoorsWindow.filterBy = item[0]
                        time.sleep(1)
                        self.findDoorsWindow.selectObject(item)
                self.findDoorsWindow.btnOK.click()
            else:
                raise Exception("Find Doors window doesn't pop up")
    
    
    def setupEvents(self, settingEvents):
        """ setup events criteria based on the given settings """
        self.eventsEdit.click()
        result = self.selectEventsWindow.isDisplayed()
        if result:
            self.selectEventsWindow.btnUnselectAll.click()
            if isinstance(settingEvents, list):
                for item in settingEvents:
                    eventType = ACCESS_EVENT_TYPES[item][0]
                    self.selectEventsWindow.filterBy = eventType
                    time.sleep(1)
                    self.selectEventsWindow.selectObject([eventType])
            elif settingEvents == "ALL":
                self.selectEventsWindow.btnSelectAll.click()
                
            self.selectEventsWindow.btnOK.click()
        else:
            raise Exception("Select Events window doesn't pop up")
        
        
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
                        result.append((item.text).strip())
                    return result
                else:
                    return []
            else:
                return self._generatedReportGetObjInfo()
        finally:
            driver.switch_to_default_content()
            driver.switch_to_frame("mainFrame")
            
            
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
                            rowDic[columnHeaders[j]] =  (tdElements[j].text).strip()
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
                        rowDic[columnHeaders[i]] = (tdElements[i].text).strip()
                        i = i + 1
                    
                    result.append(rowDic)
                return result
            
    
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
        
        
    def _generatedReportGetLabelRowElemClassName(self):
        """ helper to return the class name of the tr element of the report label row """
        driver = self.driver
        try:
            target = driver.find_element_by_xpath("//table/tbody/tr[2]/td/table[4]/tbody/tr[1]")
            return target.get_attribute("class")
        except NoSuchElementException, e:
            print "Exception on AdHocPageObj._generatedReportGetLabelRowElemClassName(): %s"%str(e)
            return None
    
    
    def _generatedReportGetGroupLabel(self, trElem):
        """ helper to return the label string of the group label row element """
        return (trElem.text).strip()
    
    
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
    
    
            
    
    