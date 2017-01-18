'''
Created on Nov 9, 2016

@author: hwang
'''
from BAS_Report_Generic import BASReportPageObj
from selenium.common.exceptions import NoSuchElementException


class AdHocPageObj(BASReportPageObj):
    """ BAS Ad Hoc report page object module """
        
    def __repr__(self):
        super(AdHocPageObj, self).__repr__()
        
    def __str__(self):
        return "Report: AD HOC"
    
    
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
        spanElem = trElem.find_element_by_xpath("./td[1]/span[1]")
        deviceName = spanElem.text
        spanElem = trElem.find_element_by_xpath("./td[1]/span[2]")
        deviceNumber = spanElem.text
        return "%s %s"%(deviceName, deviceNumber)
    
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
                            divElem = tdElements[j].find_element_by_xpath("./div/div")
                            rowDic[columnHeaders[j]] = divElem.text
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
                        divElem = tdElements[i].find_element_by_xpath("./div/div")
                        rowDic[columnHeaders[i]] = divElem.text
                        i = i + 1
                    result.append(rowDic)
                return result
            
    
    