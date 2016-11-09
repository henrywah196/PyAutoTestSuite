'''
Created on Jan 14, 2014

@author: hwang
'''
from libraries.SLAT.OnlineConfigurator import locators
from ConfigProdPageObj import ConfigProduct
from basewebelement import TextBox, EditBox, CheckBox, DropDownBox, Button
import time
#from msilib.schema import CheckBox


class ConfigenteliBRIDGE(ConfigProduct):
    
    partnerID = DropDownBox("ebridgeConfig.Partner ID")
    poNumber = EditBox("ebridgeConfig.PO Number")
    quantity = EditBox("ebridgeConfig.Quantity")
    powerSupply = DropDownBox("ebridgeConfig.Power Supply")
    addON_ModBUS_TCP = CheckBox("ebridgeConfig.Add-Ons.ModBUS TCP")
    counter_ModBUS_TCP = EditBox("ebridgeConfig.Counter.ModBUS TCP")
    
    btnNext01 = Button("ebridgeConfig.Next01")
    btnPrevious = Button("ebridgeConfig.Previous")
    btnNext02 = Button("ebridgeConfig.Next02")
    btnSubmit = Button("ebridgeConfig.Submit")
    
    #Shipping Info
    nickName = DropDownBox("ebridgeConfig.Shipping.nickName")
    contactName = EditBox("ebridgeConfig.Shipping.contactName")
    email = EditBox("ebridgeConfig.Shipping.email")
    address01 = EditBox("ebridgeConfig.Shipping.address01")
    city = EditBox("ebridgeConfig.Shipping.city")
    country = DropDownBox("ebridgeConfig.Shipping.country")
    state = DropDownBox("ebridgeConfig.Shipping.state")
    zipCode = EditBox("ebridgeConfig.Shipping.zipCode")
    phone = EditBox("ebridgeConfig.Shipping.phone")
    fax = EditBox("ebridgeConfig.Shipping.fax")
    
    
    def __init__(self):
        self.driver = None
        
    def __repr__(self):
        super(ConfigenteliBRIDGE, self).__repr__()
        
        