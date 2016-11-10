from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from libraries.eweb.PageObjects.BasePageObject import BaseFrameObject
from libraries.eweb.PageObjects.BaseWebElement import BaseWebElement, TextBoxWebElement, EditBoxWebElement, ButtonWebElement, DropDownBoxWebElement, CheckBoxWebElement
import time, datetime


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


class BASReportPageObj(BaseFrameObject):
    """ generic BAS report page object module """
    
    configPanel           =  BaseWebElement("BASReportPageObj.configPanel")
    configPanel_Collapsed =  BaseWebElement("BASReportPageObj.configPanel_Collapsed")
    configPanel_Header    =  BaseWebElement("BASReportPageObj.configPanel_Header")
    
    reportHistory = ReportHistoryDropDown()  
    
    save     = ButtonWebElement("BASReportPageObj.save")
    run      = ButtonWebElement("BASReportPageObj.run")
    delete   = ButtonWebElement("BASReportPageObj.delete")
    copy     = ButtonWebElement("BASReportPageObj.copy")
    schedule = ButtonWebElement("BASReportPageObj.schedule")
    email    = ButtonWebElement("BASReportPageObj.email")
    
    reportName  = EditBoxWebElement("BASReportPageObj.reportName")
    reportTitle = EditBoxWebElement("BASReportPageObj.reportTitle")
    site        = EditBoxWebElement("BASReportPageObj.site") 
    
    loadingMask = TextBoxWebElement("BASReportPageObj.loadingMask")
    
    
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