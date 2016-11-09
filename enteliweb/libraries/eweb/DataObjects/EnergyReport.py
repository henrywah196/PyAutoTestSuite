'''
Created on Apr 19, 2016

@author: user
'''
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from Enteliweb.libenteliwebReporting.PageObjects.BasePageObject import BaseFrameObject
from Enteliweb.libenteliwebReporting.PageObjects.BaseWebElement import BaseWebElement, TextBoxWebElement, EditBoxWebElement, ButtonWebElement, DropDownBoxWebElement, CheckBoxWebElement
from Enteliweb.libenteliwebReporting.PageObjects.BaseWebElement import XTree
#from Enteliweb.libenteliwebReporting.DataObjects.WebGroup import WebGroupDBObj
from Enteliweb.libenteliwebReporting import Macros
from Enteliweb.libenteliwebReporting.PageObjects.Accordion import AccordionPageObj
import requests
import time, datetime, cgi


##################################
# Generated Energy Report related
##################################
class GeneratedEnergyReportLogo(BaseWebElement):
    """ Model the report logo web element in generated report """
    
    def __init__(self):
        super(GeneratedEnergyReportLogo, self).__init__("energyreport.Generated_Report_Logo")
    
    def getElement(self, locator):
        """ locate the web element on page """
        driver = self.getDriver()
        driver.switch_to_default_content()
        driver.switch_to_frame("mainFrame")
        driver.switch_to_frame("resultReport")
        elementid = locator["value"]
        flag = "//img[starts-with(@id, '" + elementid + "')]"    #
        elem = driver.find_element_by_xpath(flag)
        driver.switch_to_default_content()
        driver.switch_to_frame("mainFrame")
        return elem


###########################
# Energy Report UI related
###########################
class ReportHistoryDropDown(DropDownBoxWebElement):
    """ Model the Report History DropDown Box web element """
    def __init__(self):
        super(ReportHistoryDropDown, self).__init__("energyreport.report_history", invalidIcon=False)
        
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


class EnergyReportPageObj(BaseFrameObject):
    """ generic energy report page object module """
    
    configPanel           =  BaseWebElement("energyreport.config_panel")
    configPanel_Collapsed =  BaseWebElement("energyreport.config_panel_collapse")
    configPanel_Header    =  BaseWebElement("energyreport.config_panel_header")
    selectedMeterTree     =  XTree("energyreport.selected_meter_tree")
    addNewItem            =  ButtonWebElement("energyreport.addnew_button")
    
    meterTree   = XTree("energyreport.meter_tree")
    gearButton  = ButtonWebElement("energyreport.gear_button")
    closeButton = ButtonWebElement("energyreport.close_button")
    
    reportHistory = ReportHistoryDropDown()  
    
    save     = ButtonWebElement("energyreport.save")
    run      = ButtonWebElement("energyreport.run")
    delete   = ButtonWebElement("energyreport.delete")
    copy     = ButtonWebElement("energyreport.copy")
    schedule = ButtonWebElement("energyreport.schedule")
    email    = ButtonWebElement("energyreport.email")
    
    reportName  = EditBoxWebElement("energyreport.report_name")
    reportTitle = EditBoxWebElement("energyreport.report_title")
    meterType   = DropDownBoxWebElement("energyreport.meter_type", invalidIcon=False)
    site        = EditBoxWebElement("energyreport.site") 
    
    loadingMask = TextBoxWebElement("energyreport.Report_Loading_Mask")
    
    generatedReportLogo = GeneratedEnergyReportLogo()
    
    
    def __init__(self):
        super(EnergyReportPageObj, self).__init__()
        self.titleExpected = "Report Form"
        self.focus()
        
    def __repr__(self):
        super(EnergyReportPageObj, self).__repr__()
        
    def __str__(self):
        return "Generic Energy Report Configuration Page"
    
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
    
    def _escapeSpecialChar(self, targetString):
        """ helper function used by dragAndDrop or other function
            to replace special characteers such as <, >, &, ", ' 
            in the string
        """
        result = cgi.escape(targetString, quote=True)
        if "'" in result:
            result = result.replace("'", "&#39;")
        return result
        
        
    def dragAndDrop(self, sourcePathName, destPathName, workaround=False, reportName=None):
        """
        Drag and drop a tree node from area/meter list tree 
        to selected area/meter list tree
        """
        try:
            result = None
            if workaround:
                
                sourceTree = self.meterTree
                destTree = self.selectedMeterTree
        
                result = sourceTree.expandTreeNode(sourcePathName)
                if not sourceTree.verifyTreeNodeDisplayed(sourcePathName):
                    result = sourceTree.expandTreeNode(sourcePathName)    # try one more time if tree node not expanded
                if result:
                    sourceNode = sourceTree._getTreeNode(sourcePathName)
                    sourceNode.location_once_scrolled_into_view
                    sourceNodeName = sourceTree._getTreeNodeName(sourceNode)
                    sourceDiv = (sourceTree._getTreeNode(sourcePathName)).find_element_by_tag_name('div')
                    sourceImg = sourceDiv.find_element_by_xpath("./img[contains(@class, 'x-tree-icon')]")
                    destDiv = (destTree._getTreeNode(destPathName)).find_element_by_tag_name('div')
                    destImg = destDiv.find_element_by_xpath("./img[contains(@class, 'x-tree-icon')]")

                    if sourceImg and destImg and sourceTree.verifyTreeNodeEnabled(sourceNode):
                        from dragdrophelper import pyautoguiDragDropHelper
                        pyautoguiDragDropHelper(self.driver, sourceImg, destImg)
                        destTree.updateTree()
                        result = destTree.verifyTreeNodeDisplayed(destPathName + '\\' + sourceNodeName)
                
                '''
                webgroup = WebGroupDBObj()
                # save report instance first
                self.saveChange()
                accordion = AccordionPageObj()
                accordion.reportTree.WaitForUpdate()
                Macros.SelectReportInstance(reportName)
                result = accordion.reportTree.IsTreeNodeHighLighted(reportName)
                assert result == True, "Verify '%s' is selected and highlighted in report tree"%reportName
                result = self.isLoaded()
                assert result == True, "Verify report UI for '%s' is loaded"%reportName
                
                reportID = webgroup.getEnergyReportInstanceID(reportName)
                instanceID = webgroup.getAreaMeterInstanceID(sourcePathName)
                instanceType = webgroup.getInstanceType(instanceID)
                instanceName = webgroup.getInstanceName(instanceID)
                instanceName = self._escapeSpecialChar(instanceName)
                    
                #generate a temp instanceName
                tmpInstanceName = "Node" + (datetime.datetime.today()).strftime("%Y%m%d%H%M")
                    
                Parent, Order = webgroup.getParentNOrder(reportID, destPathName)
                print("Parent: %s"%Parent)
                print("type: %s"%instanceType)
                print("meter id: %s"%instanceID)
                print("meter name: %s"%instanceName)
                print ("Order: %s"%Order)
                
                cookie_name = "enteliWebID"
                cookie_value = None
                cookie_info = self.driver.get_cookie(cookie_name)
                if cookie_info is not None:
                    cookie_value = cookie_info["value"]
                cookie = {cookie_name : cookie_value}
                httpString = "http://%s/enteliweb/energyreportqatest/addmeter/parent/%s/type/%s/instance/%s/name/%s/order/%s"%(settings.HOST, Parent, instanceType, instanceID, tmpInstanceName, Order)
                r = requests.get(httpString, cookies=cookie) 
                assert r.status_code == 200, "verify HTTP request success"
                assert "NewMeterNode was added" in r.text, "verify meter node was added"
                    
                #obtain the node ID from the returned text
                myStr = r.text
                nodeID = myStr[myStr.find("(")+1:myStr.find(")")]
                    
                # update node name using instanceName in Report_Meter table
                webgroup.updateReportMeterName(nodeID, instanceName)
                    
                Macros.SelectReportInstance(reportName)
                accordion = AccordionPageObj()
                result = accordion.reportTree.IsTreeNodeHighLighted(reportName)
                assert result == True, "Verify '%s' is selected and highlighted in report tree"%reportName
                result = self.isLoaded()
                assert result == True, "Verify report UI for '%s' is loaded"%reportName
                '''
            else:
                sourceTree = self.meterTree
                destTree = self.selectedMeterTree
        
                result = sourceTree.expandTreeNode(sourcePathName)
                if not sourceTree.verifyTreeNodeDisplayed(sourcePathName):
                    result = sourceTree.expandTreeNode(sourcePathName)    # try one more time if tree node not expanded
                if result:
                    sourceNode = sourceTree._getTreeNode(sourcePathName)
                    sourceNode.location_once_scrolled_into_view
                    sourceNodeName = sourceTree._getTreeNodeName(sourceNode)
                    sourceDiv = (sourceTree._getTreeNode(sourcePathName)).find_element_by_tag_name('div')
                    sourceImg = sourceDiv.find_element_by_xpath("./img[contains(@class, 'x-tree-icon')]")
                    destDiv = (destTree._getTreeNode(destPathName)).find_element_by_tag_name('div')
                    destImg = destDiv.find_element_by_xpath("./img[contains(@class, 'x-tree-icon')]")

                    if sourceImg and destImg and sourceTree.verifyTreeNodeEnabled(sourceNode):
                        mouse = ActionChains(self.driver)
                        #mouse.drag_and_drop(sourceImg, destImg).perform()
                        #mouse.click_and_hold(sourceImg).move_to_element_with_offset(destDiv, 1, 1).perform()
                        #time.sleep(5)
                        #mouse.release().perform()
                        mouse.move_to_element(sourceImg).perform()
                        time.sleep(3)
                        mouse.click_and_hold(sourceImg).perform()
                        time.sleep(2)
                        mouse.move_to_element(destDiv).perform()
                        time.sleep(3)
                        destTree.updateTree()
                        result = destTree.verifyTreeNodeDisplayed(destPathName + '\\' + sourceNodeName)
                    else:
                        result = False
        except Exception as e:
            print("dragAndDrop() get Exception: %s" %e)
            result = False
        return result
    
    def createMeterGroup(self, groupName):
        """ create a new group under selected area meter list """
        targetNode = self.selectedMeterTree._getTreeNode("Area/Meter List")
        targetNode = targetNode.find_element_by_tag_name('div')    # the tree root node
        mouse = ActionChains(self.driver)
        mouse.context_click(targetNode).perform()
        time.sleep(1)
        targetNode = self.driver.find_element_by_id("createNode-itemEl")    # the Create Node menu item
        targetNode.click()
        
        elem = self.driver.find_element_by_id("selectedTree-body")
        elem = elem.find_element_by_xpath("./following-sibling::div")    # find next sibling div
        elem = elem.find_element_by_tag_name('input')    # find input
        elem.clear()
        elem.send_keys(groupName)
        elem.send_keys(Keys.RETURN)
        time.sleep(1)
        self.selectedMeterTree.updateTree()
        result = self.selectedMeterTree.verifyTreeNodeDisplayed('Area/Meter List\\' + groupName)
        if not result:
            raise Exception("failed create meter group")
        
    def saveChange(self):
        """ click the save button and wait page refreshed"""
        self.save.click()    # click the save button
        
        timeout = 10
        locator = self.configPanel_Header.locator
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.ID, locator["value"])))
        except TimeoutException:
            raise Exception("%s is not finish loading within %s seconds"%(self, timeout))
        
        
    def expandBaselineSetup(self):
        """
        Command to click the toggle button in Report UI to make baseline setup fields showing up.
        """

        flag = 'x-fieldset-collapsed'
        webElement = self.driver.find_element_by_id('baselinePanel')    # get WebElement baselinePanel
        classString = webElement.get_attribute('class')    # get class attribute
        if flag in classString:
            # click the toggle button to expand Baseline field.
            webElement02 = self.driver.find_element_by_id('baselinePanel-legendTitle')
            webElement02.click()    #click toggle button


    def collapseBaselineSetup(self):
        """
        Command to click the toggle button in Report UI to make baseline setup fields collapse.
        """

        flag = 'x-fieldset-collapsed'
        webElement = self.driver.find_element_by_id('baselinePanel')    # get WebElement baselinePanel
        classString = webElement.get_attribute('class')    # get class attribute
        if not (flag in classString):
            # click the toggle button to collapse field.
            webElement02 = self.driver.find_element_by_id('baselinePanel-legendTitle')
            webElement02.click()    #click toggle button
            
            
    def expandConfigPane(self):
        """
        expand the report configuration pane
        """
        if self.configPanel_Collapsed.isDisplayed():
            elem = self.configPanel_Collapsed.getElement(self.configPanel_Collapsed.locator)
            elem = elem.find_element_by_tag_name("img")    # locate the expand button
            elem.click()
        
        
    def collapseConfigPane(self):
        """
        collapse the report configuration pane
        """
        if self.configPanel.isDisplayed():
            elem = self.configPanel_Header.getElement(self.configPanel_Header.locator)
            elem = elem.find_element_by_tag_name("img")    # locate the collapse button
            elem.click()
            
            
    def openAreaMeterPane(self):
        """
        Open the Area/Meter List pane
        """
        self.addNewItem.click()
        time.sleep(2)
        self.mouseHoverUp(self.closeButton)
        
    def closeAreaMeterPane(self):
        """
        Close the Area/Meter List pane
        """
        if self.closeButton.isDisplayed():
            self.closeButton.click()
            
            
    def WaitForReport(self, TimeLimit):
        """
        This command waits till the report is generated and if the waiting time  exceed time limit
        it give timeout warning and return false otherwise it will return true

        @param string TimeLimit            Timeout time for the report generating

        @return boolean                    return True if the node is successively created under the specified path.
        """
    
        result = False
        driver = self.driver
        try:
            # 1. wait 8 seconds
            time.sleep(8)
            # 2. examine and waiting for loading mask finish up
            ElementID = self.loadingMask.locator.get("value")
            errMessage = "Report doesn't finish generating within %s seconds"%TimeLimit
            WebDriverWait(driver, TimeLimit).until(EC.invisibility_of_element_located((By.ID, ElementID)), errMessage)
            # 3. examine the report logo
            errMessage = "Generated report is not as expected"
            elementid = self.generatedReportLogo.locator.get("value")
            flag = "//img[starts-with(@id, '" + elementid + "')]"    # locate the report logo
            elem = WebDriverWait(driver, 3).until(self._elem_available_cb(flag), errMessage)
            if elem:
                result = True
        except Exception, e:
            print "WaitForReport() get Exception: %s" %e
            result = False
        return result

    def _elem_available_cb(self, flag):
        """
        helper function for  WaitForReport()
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
        
    
            
            
class ConsumptionPageObj(EnergyReportPageObj):
    """ Consumption energy report page object module """
    
    year          = EditBoxWebElement("consumption.year")
    baseline_year = EditBoxWebElement("consumption.baseline_year")
    
    def __str__(self):
        return "Report: Consumption"
    
    def createReportInstance(self, report_param, workaround_dragndrop):
        """create consumption report instance using the given parameters"""
        
        accordion = AccordionPageObj()
        
        reportName   = report_param["reportName"]
        reportTitle  = report_param["reportTitle"]
        meterType    = report_param["meterType"]
        site         = report_param["site"]
        year         = report_param["year"]
        baselineYear = report_param["baselineYear"]
        meterList    = report_param["areaMeterList"]
        
        Macros.SelectReportInstance("Consumption")
        
        self.focus()
        self.reportName = reportName
        self.reportTitle = reportTitle
        self.site = site
        self.meterType = meterType
        self.year = year
        
        if baselineYear is not None:
            self.expandBaselineSetup()
            result = self.baseline_year.isDisplayed()
            assert result == True, "Verify Baseline Setup is displayed"
            self.baseline_year = baselineYear
            
        self.addNewItem.click()
        result = self.meterTree.isDisplayed()
        assert result == True, "Verify Area/Meter List pane is displayed"
        
        for DragAndDrop in meterList:
            if not self.selectedMeterTree.verifyTreeNodeDisplayed(DragAndDrop['DestPath']):
                # create group node on selected area meter list
                NewTreeNodeName = self.selectedMeterTree._getNodeNameFromPath(DragAndDrop['DestPath'])
                self.createMeterGroup(NewTreeNodeName)
                
            sourcePathName = DragAndDrop["SourcePath"]
            destPathName = DragAndDrop["DestPath"]
            self.dragAndDrop(sourcePathName, destPathName, workaround=workaround_dragndrop, reportName="Consumption\\%s"%reportName)
             
        self.saveChange()
        accordion.reportTree.WaitForUpdate()
        
        Macros.SelectReportInstance("Consumption\\%s"%reportName)
        result = accordion.reportTree.IsTreeNodeHighLighted("Consumption\\%s"%reportName)
        assert result == True, "Verify report node '%s' is highlighted"%reportName
        result = self.isLoaded()
        assert result == True, "Verify report UI for '%s' is loaded"%reportName
    
    
class ConsumptionByMeterPageObj(EnergyReportPageObj):
    """ Consumption by Meter energy report page object module """
    
    date_range = DropDownBoxWebElement("energyreport.date_range")
    date_from  = EditBoxWebElement("energyreport.date_from")
    date_to    = EditBoxWebElement("energyreport.date_to")
    
    occupancy_from = DropDownBoxWebElement("energyreport.occupancy_from")
    occupancy_to   = DropDownBoxWebElement("energyreport.occupancy_to")
    occupancy_days = DropDownBoxWebElement("energyreport.occupancy_days")
    occupancy_Sun  = CheckBoxWebElement("energyreport.occupancy_Sun")
    occupancy_Mon  = CheckBoxWebElement("energyreport.occupancy_Mon")
    occupancy_Tue  = CheckBoxWebElement("energyreport.occupancy_Tue")
    occupancy_Wed  = CheckBoxWebElement("energyreport.occupancy_Wed")
    occupancy_Thu  = CheckBoxWebElement("energyreport.occupancy_Thu")
    occupancy_Fri  = CheckBoxWebElement("energyreport.occupancy_Fri")
    occupancy_Sat  = CheckBoxWebElement("energyreport.occupancy_Sat")
    
    def __str__(self):
        return "Report: Consumption by Meter"
    
    
class ConsumptionByTimePageObj(EnergyReportPageObj):
    """ Consumption by Time energy report page object module """
    
    date_range   = DropDownBoxWebElement("energyreport.date_range")
    date_from    = EditBoxWebElement("energyreport.date_from")
    date_to      = EditBoxWebElement("energyreport.date_to")
    date_groupBy = DropDownBoxWebElement("energyreport.date_groupby")
    
    occupancy_from = DropDownBoxWebElement("energyreport.occupancy_from")
    occupancy_to   = DropDownBoxWebElement("energyreport.occupancy_to")
    occupancy_days = DropDownBoxWebElement("energyreport.occupancy_days")
    occupancy_Sun  = CheckBoxWebElement("energyreport.occupancy_Sun")
    occupancy_Mon  = CheckBoxWebElement("energyreport.occupancy_Mon")
    occupancy_Tue  = CheckBoxWebElement("energyreport.occupancy_Tue")
    occupancy_Wed  = CheckBoxWebElement("energyreport.occupancy_Wed")
    occupancy_Thu  = CheckBoxWebElement("energyreport.occupancy_Thu")
    occupancy_Fri  = CheckBoxWebElement("energyreport.occupancy_Fri")
    occupancy_Sat  = CheckBoxWebElement("energyreport.occupancy_Sat")
    
    def __str__(self):
        return "Report: Consumption by Time"
    
    
class ConsumptionComparisonPageObj(EnergyReportPageObj):
    """ Consumption Comparison energy report page object module """
    
    date_range   = DropDownBoxWebElement("energyreport.date_range")
    date_from    = EditBoxWebElement("energyreport.date_from")
    date_to      = EditBoxWebElement("energyreport.date_to")
    date_groupBy = DropDownBoxWebElement("energyreport.date_groupby")
    
    def __str__(self):
        return "Report: Consumption Comparison"
    
    
class ConsumptionTargetPageObj(EnergyReportPageObj):
    """ Consumption Target energy report page object module """
    
    date_range   = DropDownBoxWebElement("energyreport.date_range")
    date_from    = EditBoxWebElement("energyreport.date_from")
    date_to      = EditBoxWebElement("energyreport.date_to")
    date_groupBy = DropDownBoxWebElement("energyreport.date_groupby")
    
    def __str__(self):
        return "Report: Consumption Target"
    
    
class ContributionComparisonPageObj(EnergyReportPageObj):
    """ Contribution Comparison energy report page object module """
    
    date_range = DropDownBoxWebElement("energyreport.date_range")
    date_from  = EditBoxWebElement("energyreport.date_from")
    date_to    = EditBoxWebElement("energyreport.date_to")
    date_days  = DropDownBoxWebElement("energyreport.date_days")
    date_Sun   = CheckBoxWebElement("energyreport.date_Sun")
    date_Mon   = CheckBoxWebElement("energyreport.date_Mon")
    date_Tue   = CheckBoxWebElement("energyreport.date_Tue")
    date_Wed   = CheckBoxWebElement("energyreport.date_Wed")
    date_Thu   = CheckBoxWebElement("energyreport.date_Thu")
    date_Fri   = CheckBoxWebElement("energyreport.date_Fri")
    date_Sat   = CheckBoxWebElement("energyreport.date_Sat")
    
    def __str__(self):
        return "Report: Contribution Comparison"
    

class CostRankingPageObj(EnergyReportPageObj):
    """ Cost Ranking energy report page object module """
    
    date_range = DropDownBoxWebElement("energyreport.date_range")
    date_from  = EditBoxWebElement("energyreport.date_from")
    date_to    = EditBoxWebElement("energyreport.date_to")
    
    def __str__(self):
        return "Report: Cost Ranking"
    
    
class CumulativeConsumptionPageObj(EnergyReportPageObj):
    """ Cumulative Consumption energy report page object module """
    
    date_range   = DropDownBoxWebElement("energyreport.date_range")
    date_from    = EditBoxWebElement("energyreport.date_from")
    date_to      = EditBoxWebElement("energyreport.date_to")
    date_groupBy = DropDownBoxWebElement("energyreport.date_groupby")
    
    def __str__(self):
        return "Report: Cumulative Consumption"
    
    
class DailyAveragePageObj(EnergyReportPageObj):
    """ Daily Average energy report page object module """
    
    rollUp = EditBoxWebElement("daily_average.rollup") 
    
    date_range = DropDownBoxWebElement("energyreport.date_range")
    date_from  = EditBoxWebElement("energyreport.date_from")
    date_to    = EditBoxWebElement("energyreport.date_to")
    date_days  = DropDownBoxWebElement("energyreport.date_days")
    date_Sun   = CheckBoxWebElement("energyreport.date_Sun")
    date_Mon   = CheckBoxWebElement("energyreport.date_Mon")
    date_Tue   = CheckBoxWebElement("energyreport.date_Tue")
    date_Wed   = CheckBoxWebElement("energyreport.date_Wed")
    date_Thu   = CheckBoxWebElement("energyreport.date_Thu")
    date_Fri   = CheckBoxWebElement("energyreport.date_Fri")
    date_Sat   = CheckBoxWebElement("energyreport.date_Sat")
    
    baseline_offsetBy     = DropDownBoxWebElement("energyreport.baseline_offset_by")
    baseline_startingDate = EditBoxWebElement("energyreport.baseline_starting_date")
    
    def __str__(self):
        return "Report: Daily Average"
    
    
class DegreeDaysPageObj(EnergyReportPageObj):
    """ Degree Days energy report page object module """
    
    baseTemperature = EditBoxWebElement("degree_days.base_temperature") 
    
    date_range    = DropDownBoxWebElement("energyreport.date_range")
    date_from     = EditBoxWebElement("energyreport.date_from")
    date_to       = EditBoxWebElement("energyreport.date_to")
    date_groupBy  = DropDownBoxWebElement("energyreport.date_groupby")
    
    def __str__(self):
        return "Report: Degree Days"
    
    
class LoadDurationPageObj(EnergyReportPageObj):
    """ Load Duration energy report page object module """
    
    load_step = EditBoxWebElement("load_duration.load_step")
    load_mark = EditBoxWebElement("load_duration.load_mark")
    
    date_range = DropDownBoxWebElement("energyreport.date_range")
    date_from  = EditBoxWebElement("energyreport.date_from")
    date_to    = EditBoxWebElement("energyreport.date_to")
    date_days  = DropDownBoxWebElement("energyreport.date_days")
    date_Sun   = CheckBoxWebElement("energyreport.date_Sun")
    date_Mon   = CheckBoxWebElement("energyreport.date_Mon")
    date_Tue   = CheckBoxWebElement("energyreport.date_Tue")
    date_Wed   = CheckBoxWebElement("energyreport.date_Wed")
    date_Thu   = CheckBoxWebElement("energyreport.date_Thu")
    date_Fri   = CheckBoxWebElement("energyreport.date_Fri")
    date_Sat   = CheckBoxWebElement("energyreport.date_Sat")
    
    baseline_offsetBy     = DropDownBoxWebElement("energyreport.baseline_offset_by")
    baseline_startingDate = EditBoxWebElement("energyreport.baseline_starting_date")
    
    def __str__(self):
        return "Report: Load Duration"
    
    
class SingleMeterOccupancyPageObj(EnergyReportPageObj):
    """ Single Meter Occupancy energy report page object module """
    
    date_range   = DropDownBoxWebElement("energyreport.date_range")
    date_from    = EditBoxWebElement("energyreport.date_from")
    date_to      = EditBoxWebElement("energyreport.date_to")
    date_groupBy = DropDownBoxWebElement("energyreport.date_groupby")
    date_days    = DropDownBoxWebElement("energyreport.date_days")
    date_Sun     = CheckBoxWebElement("energyreport.date_Sun")
    date_Mon     = CheckBoxWebElement("energyreport.date_Mon")
    date_Tue     = CheckBoxWebElement("energyreport.date_Tue")
    date_Wed     = CheckBoxWebElement("energyreport.date_Wed")
    date_Thu     = CheckBoxWebElement("energyreport.date_Thu")
    date_Fri     = CheckBoxWebElement("energyreport.date_Fri")
    date_Sat     = CheckBoxWebElement("energyreport.date_Sat")
    
    
    occupancy_from = DropDownBoxWebElement("energyreport.occupancy_from")
    occupancy_to   = DropDownBoxWebElement("energyreport.occupancy_to")
    occupancy_days = DropDownBoxWebElement("energyreport.occupancy_days")
    occupancy_Sun  = CheckBoxWebElement("energyreport.occupancy_Sun")
    occupancy_Mon  = CheckBoxWebElement("energyreport.occupancy_Mon")
    occupancy_Tue  = CheckBoxWebElement("energyreport.occupancy_Tue")
    occupancy_Wed  = CheckBoxWebElement("energyreport.occupancy_Wed")
    occupancy_Thu  = CheckBoxWebElement("energyreport.occupancy_Thu")
    occupancy_Fri  = CheckBoxWebElement("energyreport.occupancy_Fri")
    occupancy_Sat  = CheckBoxWebElement("energyreport.occupancy_Sat")
    
    baseline_offsetBy     = DropDownBoxWebElement("energyreport.baseline_offset_by")
    baseline_startingDate = EditBoxWebElement("energyreport.baseline_starting_date")
    
    def __str__(self):
        return "Report: Single Meter Occupancy"



            
        