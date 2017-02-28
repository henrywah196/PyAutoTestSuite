'''
Created on Nov 9, 2016

@author: hwang
'''
from BAS_Report_Generic import BASReportPageObj
from selenium.common.exceptions import NoSuchElementException


class CommissioningSheetsPageObj(BASReportPageObj):
    """ BAS Commissioning Sheet report page object module """
        
    def __repr__(self):
        super(CommissioningSheetsPageObj, self).__repr__()
        
    def __str__(self):
        return "Report: Commissioning Sheets"
    
    
    ##################################
    # generated report related method
    ##################################
    def generatedReportGetData(self, strKeyWord=None):
        """ return data from generated report
        """
        result = []
        driver = self.driver
        driver.switch_to_default_content()
        driver.switch_to_frame("mainFrame")
        driver.switch_to_frame("resultReport")
        tocElements = self._generateReportGetKeyTOCElements()
        for tocElem in tocElements:
            deviceInfo = self._generatedReportGetDeviceInfo(tocElem[0])
            if strKeyWord != "device info only":
                ioInfo = self._generatedReportGetIOInfo(tocElem)
                deviceInfo.update(ioInfo)
            result.append(deviceInfo)
        driver.switch_to_default_content()
        driver.switch_to_frame("mainFrame")
        return result
        
    
    def _generateReportGetKeyTOCElements(self):
        """ helper to return a list of [__TOC_X_0, __TOC_X_1] elements
            which represent the start point of Inputs and Outputs table
        """
        result = []
        driver = self.driver
        target = []
        elements = driver.find_elements_by_xpath("//tr[starts-with(@id, '__TOC_') and '_0' = substring(@id, string-length(@id)- string-length('_0') +1)] | //tr[starts-with(@id, '__TOC_') and '_1' = substring(@id, string-length(@id)- string-length('_1') +1)]")
        for elem in elements:
            idString = elem.get_attribute("id")
            subString = idString[6:-2]
            if not "_" in subString:
                target.append(elem)
        numList = []
        for elem in target:
            numString = (elem.get_attribute("id"))[6:-2]
            if numString not in numList:
                numList.append(numString)
        for numString in numList:
            grpList = []
            for elem in target:
                if "_%s_"%numString in elem.get_attribute("id"):
                    grpList.append(elem)
            result.append(grpList)
        i = 0
        while i < len(result):
            if i != len(result) - 1:
                result[i].append(result[i + 1][0])
            i = i + 1 
        if len(result[len(result) - 1]) != 1:
            result[len(result) - 1].append(None)  
        return result
            
    
    def _generatedReportGetDeviceInfo(self, keyTOCElement):
        """ helper to return the device information based on __TOC_X_0 element """
        result = {}
        preSiblingElements = keyTOCElement.find_elements_by_xpath("./preceding-sibling::tr")
        
        # obtain device label from its tr element
        target = preSiblingElements[len(preSiblingElements) - 4]
        #elem = target.find_element_by_xpath("./td[1]/div/div")
        result["header"] = target.text
        
        # obtain device info
        '''
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
        '''
        target = preSiblingElements[len(preSiblingElements) - 3]    # Location info
        tdValueElem = target.find_element_by_xpath("./td[2]/div")
        result["location"] = tdValueElem.text
        target = preSiblingElements[len(preSiblingElements) - 2]    # Model info
        tdValueElem = target.find_element_by_xpath("./td[2]/div")
        result["model"] = tdValueElem.text
        target = preSiblingElements[len(preSiblingElements) - 1]    # IP info
        tdValueElem = target.find_element_by_xpath("./td[2]/div")
        result["ip"] = tdValueElem.text
                
        return result
    
    def _generatedReportGetRowElems(self, startElem, endElem=None):
        """ helper to return a list of tr elements between tartElem and endElem """
        if endElem is not None:
            result = []
            #nextSiblingElements = startElem.find_elements_by_xpath("./following-sibling::tr")
            flag = endElem.get_attribute("id")
            nextSiblingElements = startElem.find_elements_by_xpath("./following-sibling::tr[@class='style_70'] | ./following-sibling::tr[@id='%s']"%flag)
            for elem in nextSiblingElements:
                if elem == endElem:
                    break
                else:
                    result.append(elem)
            return result
        else:
            nextSiblingElements = startElem.find_elements_by_xpath("./following-sibling::tr[@class='style_70']")
            return nextSiblingElements
        
    def _generatedReportGetIOInfo(self, keyTOCElement):
        """ helper to return the inputs and outputs information based on __TOC_X_X element """
        try:
            self.driver.implicitly_wait(2)
            if len(keyTOCElement) == 3:
                result = {}
                inputsElems = self._generatedReportGetRowElems(keyTOCElement[0], keyTOCElement[1])
                outputsElems = self._generatedReportGetRowElems(keyTOCElement[1], keyTOCElement[2])
                elemsList = [inputsElems, outputsElems]
                i = 0
                while i < len(elemsList):
                    tmpList = []
                    elems = elemsList[i]
                    for elem in elems:
                        objDic = {}
                        objDic["id"] = elem.find_element_by_xpath("./td[1]/div").text
                        objDic["name"] = elem.find_element_by_xpath("./td[2]/div/div").text
                        try: objDic["scale"] = elem.find_element_by_xpath("./td[7]/div/div").text
                        except NoSuchElementException: objDic["scale"] = ""
                        tmpList.append(objDic)
                    if i == 0:    
                        result["inputs"] = tmpList
                    else:
                        result["outputs"] = tmpList
                    i = i + 1
                
                return result
            else:
                result = {}
                elems = None
                if len(keyTOCElement) == 2:
                    elems = self._generatedReportGetRowElems(keyTOCElement[0], keyTOCElement[1])
                else:
                    elems = self._generatedReportGetRowElems(keyTOCElement[0], None)
                tmpList = []
                for elem in elems:
                    objDic = {}
                    objDic["id"] = elem.find_element_by_xpath("./td[1]/div").text
                    objDic["name"] = elem.find_element_by_xpath("./td[2]/div/div").text
                    try: objDic["scale"] = elem.find_element_by_xpath("./td[7]/div/div").text
                    except NoSuchElementException: objDic["scale"] = ""
                    tmpList.append(objDic)
                if keyTOCElement[0].find_element_by_xpath("./td[1]/div").text == "Inputs":
                    result["inputs"] = tmpList
                if keyTOCElement[0].find_element_by_xpath("./td[1]/div").text == "Outputs":
                    result["outputs"] = tmpList
                return result
            
        finally:
            self.driver.implicitly_wait(30)
    
    