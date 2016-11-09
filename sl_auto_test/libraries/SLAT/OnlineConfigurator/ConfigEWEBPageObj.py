'''
Created on Jan 14, 2014

@author: hwang
'''
from libraries.SLAT.OnlineConfigurator import locators
from basepageobject import BasePageObject
from basewebelement import TextBox, EditBox, CheckBox, DropDownBox, Button
import time
#from msilib.schema import CheckBox


class OrderReview(TextBox):
    
    def getItemNumbers(self):
        itemNumbers = None
        elem = self.getElement(self.locator)
        elem.location_once_scrolled_into_view
        if elem:
            itemNumbers = []
            orString = elem.text
            result = orString.splitlines()
            for item in result:
                if "Item #:" in item:
                    item = item.split("Item #:",1)[1]
                    item = item.split("Price:",1)[0]
                    item = item.split(",",1)[0]
                    itemNumbers.append(item.strip())
        return itemNumbers
    
    def getItemCounter(self, itemNumber):
        target = None
        elem = self.getElement(self.locator)
        elem.location_once_scrolled_into_view
        if elem:
            orString = elem.text
            result = orString.splitlines()
            for item in result:
                if itemNumber in item:
                    target = item
                    break
            if target:
                target = target.split("x",1)[0]
                target = target.strip()
                
        return target
    
    def getItemPrice(self, itemNumber):
        target = None
        elem = self.getElement(self.locator)
        elem.location_once_scrolled_into_view
        if elem:
            orString = elem.text
            result = orString.splitlines()
            for item in result:
                if itemNumber in item:
                    target = item
                    break
            if target:
                target = target.split("Price: $",1)[1]
                target = target.split(")",1)[0]
                target = target.strip()
                
        return target
    
    def getConfigurationPrice(self):
        target = None
        elem = self.getElement(self.locator)
        elem.location_once_scrolled_into_view
        if elem:
            orString = elem.text
            result = orString.splitlines()
            for item in result:
                if "Configuration Price:" in item:
                    target = item
                    break
            if target:
                target = target.split("$",1)[1]
                target = target.strip()
                
        return target
    
    def getTotalPrice(self):
        target = None
        elem = self.getElement(self.locator)
        elem.location_once_scrolled_into_view
        if elem:
            orString = elem.text
            result = orString.splitlines()
            for item in result:
                if "Total" in item:
                    target = item
                    break
            if target:
                target = target.split("$",1)[1]
                target = target.strip()
                
        return target
    
    def getCurrencyType(self):
        target = None
        elem = self.getElement(self.locator)
        elem.location_once_scrolled_into_view
        if elem:
            orString = elem.text
            result = orString.splitlines()
            for item in result:
                if "Total" in item:
                    target = item
                    break
            if target:
                if "CAD" in target:
                    target = "C$"
                else:
                    target = "US$"
                
        return target
    
    def isListPrice(self):
        target = None
        elem = self.getElement(self.locator)
        elem.location_once_scrolled_into_view
        if elem:
            orString = elem.text
            result = orString.splitlines()
            for item in result:
                if "Total" in item:
                    target = item
                    break
            if target:
                if "List" in target:
                    target = True
                else:
                    target = False
                    
        return target
        
        

class ConfigenteliWEB(BasePageObject):
    
    wizHeader = TextBox("ewebConfig.wizHeader")
    partnerID = DropDownBox("ewebConfig.Partner ID")
    poNumber = EditBox("ewebConfig.PO Number")
    ioPoints = DropDownBox("ewebConfig.IO Points")
    quantity = EditBox("ewebConfig.Quantity")
    siteName = EditBox("ewebConfig.Site Name")
    siteAddress = EditBox("ewebConfig.Site Address")
    additionalSUB = DropDownBox("ewebConfig.Additional Subscription")
    addON_enteliVIZ = CheckBox("ewebConfig.Add-Ons.enteliVIZ")
    addON_eWEBAPI = CheckBox("ewebConfig.Add-Ons.enteliWEB API")
    addON_eWEBVM = CheckBox("ewebConfig.Add-Ons.Virtual Machine")
    addON_eWEBSUB = CheckBox("ewebConfig.Add-Ons.Additional Subscription")
    addON_KEE = CheckBox("ewebConfig.Add-Ons.Kaizen for enteliWEB")
    addON_KEC = CheckBox("ewebConfig.Add-Ons.Kaizen Cloud")
    btnNext01 = Button("ewebConfig.Next01")
    btnPrevious = Button("ewebConfig.Previous")
    btnNext02 = Button("ewebConfig.Next02")
    btnSubmit = Button("ewebConfig.Submit")
    confirmSubmit = TextBox("pdConfig.confirmSubmit")
    
    orderReview = OrderReview("ewebConfig.Order Review")
    
    #Shipping Info
    nickName = DropDownBox("pdConfig.Shipping.nickName")
    contactName = EditBox("pdConfig.Shipping.contactName")
    email = EditBox("pdConfig.Shipping.email")
    address01 = EditBox("pdConfig.Shipping.address01")
    city = EditBox("pdConfig.Shipping.city")
    country = DropDownBox("pdConfig.Shipping.country")
    state = DropDownBox("pdConfig.Shipping.state")
    zipCode = EditBox("pdConfig.Shipping.zipCode")
    phone = EditBox("pdConfig.Shipping.phone")
    fax = EditBox("pdConfig.Shipping.fax")
    
    
    def __init__(self):
        self.driver = None
        
    def __repr__(self):
        super(ConfigenteliWEB, self).__repr__()
        
    def isLoaded(self):
        """
        verify the page is loaded in web browser successfully
        """
        return self.wizHeader.isDisplayed()
    
    def scroll_to_bottom(self):
        """
        scroll to page bottom
        """
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def isSubmitted(self):
        """
        verify if the order has been submitted successfully
        """
        pass
    
        