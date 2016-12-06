'''
Created on Nov 9, 2016

@author: hwang
'''
from BAS_Report_Generic import BASReportPageObj


class CommissioningSheetsPageObj(BASReportPageObj):
    """ BAS Commissioning Sheet report page object module """
        
    def __repr__(self):
        super(CommissioningSheetsPageObj, self).__repr__()
        
    def __str__(self):
        return "Report: Commissioning Sheets"
    
    
    ##################################
    # generated report related method
    ##################################
    def generatedReportGetData(self):
        """ return data from generated report
        """
        result = []
        driver = self.driver
        driver.switch_to_default_content()
        driver.switch_to_frame("mainFrame")
        driver.switch_to_frame("resultReport")
        tocElements = self._generateReportGetKeyTOCElements()
        for tocElem in tocElements:
            deviceInfo = self._generatedReportGetDeviceInfo(tocElem)
            result.append(deviceInfo)
        driver.switch_to_default_content()
        driver.switch_to_frame("mainFrame")
        return result
        
    
    def _generateReportGetKeyTOCElements(self):
        """ helper to return a list of __TOC_X_0 elements """
        driver = self.driver
        target = []
        elements = driver.find_elements_by_xpath("//tr[starts-with(@id, '__TOC_') and '_0' = substring(@id, string-length(@id)- string-length('_0') +1)]")
        for elem in elements:
            idString = elem.get_attribute("id")
            subString = idString[6:-2]
            if not "_" in subString:
                target.append(elem)
        return target
    
    def _generatedReportGetDeviceInfo(self, keyTOCElement):
        """ helper to return the device information based on __TOC_X_0 element """
        result = {}
        preSiblingElements = keyTOCElement.find_elements_by_xpath("./preceding-sibling::tr")
        # obtain device label
        target = preSiblingElements[len(preSiblingElements) - 2]
        elem = target.find_element_by_xpath("./td[1]/div/div")
        result["header"] = elem.text
        # obtain device info
        target = preSiblingElements[len(preSiblingElements) - 1]
        tableElem = target.find_element_by_xpath("./td[1]/table")
        trElements = tableElem.find_elements_by_tag_name("tr")
        for elem in trElements:
            tdNameElem = elem.find_element_by_xpath("./td[1]/div")
            tdValueElem = elem.find_element_by_xpath("./td[2]/div")
            if "Location" in tdNameElem.text:
                result["location"] = tdValueElem.text
            elif "Model" in tdNameElem.text:
                result["model"] = tdValueElem.text
            elif "IP" in tdNameElem.text:
                result["ip"] = tdValueElem.text
        return result
        
            
            
            
        
