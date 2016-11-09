'''
Created on Jan 14, 2014

@author: hwang
'''
from libraries.SLAT.OnlineConfigurator import locators
from ConfigProdPageObj import ConfigProduct
from basewebelement import TextBox, EditBox, CheckBox, DropDownBox, Button
import time
#from msilib.schema import CheckBox


class ConfigCopperCube(ConfigProduct):
    
    partnerID = DropDownBox("cubeConfig.Partner ID")
    poNumber = EditBox("cubeConfig.PO Number")
    quantity = EditBox("cubeConfig.Quantity")
    powerSupply = DropDownBox("cubeConfig.Power Supply")
    trendLogs = DropDownBox("cubeConfig.Trend Logs")
    sqlConnector = CheckBox("cubeConfig.SQL Connector")
    
    btnNext01 = Button("cubeConfig.Next01")
    btnPrevious = Button("cubeConfig.Previous")
    btnNext02 = Button("cubeConfig.Next02")
    btnSubmit = Button("cubeConfig.Submit")
    
    #Shipping Info
    nickName = DropDownBox("cubeConfig.Shipping.nickName")
    contactName = EditBox("cubeConfig.Shipping.contactName")
    email = EditBox("cubeConfig.Shipping.email")
    address01 = EditBox("cubeConfig.Shipping.address01")
    city = EditBox("cubeConfig.Shipping.city")
    country = DropDownBox("cubeConfig.Shipping.country")
    state = DropDownBox("cubeConfig.Shipping.state")
    zipCode = EditBox("cubeConfig.Shipping.zipCode")
    phone = EditBox("cubeConfig.Shipping.phone")
    fax = EditBox("cubeConfig.Shipping.fax")
    
    
    def __init__(self):
        self.driver = None
        
    def __repr__(self):
        super(ConfigCopperCube, self).__repr__()
        
        