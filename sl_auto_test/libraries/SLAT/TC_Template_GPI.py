#-------------------------------------------------------------------------------
# File Name:     TC_Template_GPI.py
# Description:   Test Case Template for GP Integration Test
#
# Author:        Henry Wang
# Created:       Jan 29, 2015
#-------------------------------------------------------------------------------
import settings
from libraries.PyAutoTestCase import *
from libraries.SLAT.OnlineConfigurator.OnlineConfiguratorObj import OnlineConfigurator
from libraries.SLAT.TestData import *
import os, time, datetime


loginAccount = {"hwang@deltacontrols.com"     : "passwahpass",
                "purchaser@escautomation.com" : "access",
                "quoteuser@deltacontrols.com" : "access"
                }

shippings = {"Shipping Info 01" : {"NickName"     : "MAIN",
                                   "Contact Name" : "Mutual Tech",
                                   "Email"        : "hwang@deltacontrols.com",
                                   "Address 1"    : "388-13988 Cambie Road",
                                   "City"         : "Richmond",
                                   "Country"      : "Canada",
                                   "State"        : "British Columbia",
                                   "ZipCode"      : "V6V2K4",
                                   "Phone"        : "6042958888",
                                   "Fax"          : "6042958889"
                                   },
             "Shipping Info 02" : {"NickName"     : "MAIN",
                                   "Contact Name" : "Surrey City Hall",
                                   "Email"        : "hwang@deltacontrols.com",
                                   "Address 1"    : "14245 56th Avenue",
                                   "City"         : "Surrey",
                                   "Country"      : "Canada",
                                   "State"        : "British Columbia",
                                   "ZipCode"      : "V3X 3A2",
                                   "Phone"        : "604 591-4011",
                                   "Fax"          : "604 591-4012"
                                   },
             "Shipping Info 03" : {"NickName"     : "MAIN",
                                   "Contact Name" : "Markham Civic Centre",
                                   "Email"        : "hwang@deltacontrols.com",
                                   "Address 1"    : "101 Town Centre Boulevard",
                                   "City"         : "Markham",
                                   "Country"      : "Canada",
                                   "State"        : "Ontario",
                                   "ZipCode"      : "L3R 9W3",
                                   "Phone"        : "(905) 477-5530",
                                   "Fax"          : "(905) 477-5531"
                                   },
             "Shipping Info 04" : {"NickName"     : "MAIN",
                                   "Contact Name" : "Disneyland Park",
                                   "Email"        : "hwang@deltacontrols.com",
                                   "Address 1"    : "1313 Disneyland Drive",
                                   "City"         : "Anaheim",
                                   "Country"      : "United States",
                                   "State"        : "California",
                                   "ZipCode"      : "92802",
                                   "Phone"        : "+1 714-781-4636",
                                   "Fax"          : "+1 714-781-4637"
                                   },
             "Shipping Info 05" : {"NickName"     : "MAIN",
                                   "Contact Name" : "Office of Admissions",
                                   "Email"        : "hwang@deltacontrols.com",
                                   "Address 1"    : "370 Lighty Student Services Bldg",
                                   "Address 2"    : "Washington State University PO Box 641067",
                                   "City"         : "Pullman",
                                   "Country"      : "United States",
                                   "State"        : "Washington",
                                   "ZipCode"      : "99164-1067",
                                   "Phone"        : "888-GO-TO-WSU",
                                   "Fax"          : "509-335-4902"
                                   },
             "Shipping Info 06" : {"NickName"     : "MAIN",
                                   "Contact Name" : "Shanghai Oriental Pearl",
                                   "Email"        : "slsqatester@yahoo.com.hk",
                                   "Address 1"    : "No. 1 Pudong Century Avenue",
                                   "City"         : "Shanghai",
                                   "Country"      : "China",
                                   "State"        : "",
                                   "ZipCode"      : "200120",
                                   "Phone"        : "8621 58791888",
                                   "Fax"          : "8621 58828222"
                                   }
             }

class TC_Template_GPI(TestCaseTemplate):
    
    def setUp(self):
        super(TC_Template_GPI, self).setUp()
        self.currentTest = self.id().split('.')[-1]
        self.ooconfigurator = OnlineConfigurator()    # define Online Order Configurator web interface
        

    def tearDown(self):
        super(TC_Template_GPI, self).tearDown()
        self.command_Close_OnlineConfigurator()
        self.ooconfigurator = None
    
    
    def command_Load_OnlineConfigurator(self, userName, password, logHeader=None):  
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Load Online Order Configurator Web Interface"
        success = True 
        self.ooconfigurator.launch()
        time.sleep(10)
        success = self.ooconfigurator.loginPage.isLoaded()
        self.verify_IsTrue(success, "%s\nVerify login page is loaded"%self.messageHeader, HaltOnErr=False)
        if success:
            self.ooconfigurator.loginPage.username = userName
            self.ooconfigurator.loginPage.password = password
            self.ooconfigurator.loginPage.submit()
            time.sleep(10)
            success = self.ooconfigurator.homePage.isLoaded()
            self.verify_IsTrue(success, "%s\nVerify home page is loaded"%self.messageHeader, HaltOnErr=False)
        return success 
    
    
    def command_Close_OnlineConfigurator(self, logHeader=None):    
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Close Online Order Configurator Web Interface"
        self.ooconfigurator.close()
        
        
    def command_OC_Place_Order(self, order, submit=True, logHeader=None):
        if logHeader:
            self.messageHeader = logHeader
        else:
            self.messageHeader = "Place an Order for '%s'" %order["Product"]
        success = True
        if order["Product"] == "enteliWEB":
            self.ooconfigurator.homePage.enteliWEBLnk.click()
            time.sleep(10)
            success = self.ooconfigurator.ewebConfig.isLoaded()
            if success:
                if self.ooconfigurator.ewebConfig.partnerID.isDisplayed():
                    self.ooconfigurator.ewebConfig.partnerID = order["Partner"]
                    time.sleep(2)
                self.ooconfigurator.ewebConfig.poNumber = order["PO"]
                self.ooconfigurator.ewebConfig.ioPoints = order["IO_Points"]
                time.sleep(5)
                self.ooconfigurator.ewebConfig.quantity = order["Quantity"]
                self.ooconfigurator.ewebConfig.poNumber.click()
                time.sleep(1)
                if "enteliVIZ" in order["Add-Ons"]:
                    self.ooconfigurator.ewebConfig.addON_enteliVIZ.select()
                if "enteliWEB API" in order["Add-Ons"]:
                    self.ooconfigurator.ewebConfig.addON_eWEBAPI.select()
                if "Offline Virtual Machine" in order["Add-Ons"]:
                    self.ooconfigurator.ewebConfig.addON_eWEBVM.select()
                if "Kaizen for enteliWEB" in order["Add-Ons"]:
                    self.ooconfigurator.ewebConfig.addON_KEE.select()
                if "Kaizen Cloud" in order["Add-Ons"]:
                    self.ooconfigurator.ewebConfig.addON_KEC.select()
                if "Additional Subscription" in order["Add-Ons"]:
                    self.ooconfigurator.ewebConfig.addON_eWEBSUB.select()
                # workaround for Firefox issue
                if ("Offline Virtual Machine" in order["Add-Ons"]) or ("Additional Subscription" in order["Add-Ons"]):
                    self.ooconfigurator.ewebConfig.scroll_to_bottom()
                    self.ooconfigurator.ewebConfig.btnNext01.click()
                    time.sleep(2)
                    self.ooconfigurator.ewebConfig.btnPrevious.click()
                    time.sleep(2)
                # end of workaround for firefox issue
                if "Offline Virtual Machine" in order["Add-Ons"]:
                    self.ooconfigurator.ewebConfig.siteName = order["Site Name"]
                    self.ooconfigurator.ewebConfig.siteAddress = order["Site Address"]
                    self.ooconfigurator.ewebConfig.poNumber.click()
                    time.sleep(1)
                if "Additional Subscription" in order["Add-Ons"]:
                    self.ooconfigurator.ewebConfig.additionalSUB = order["Subscription"]
                    self.ooconfigurator.ewebConfig.poNumber.click()
                    time.sleep(1)
                    
                if submit:
                    self.ooconfigurator.ewebConfig.scroll_to_bottom()
                    time.sleep(1)
                    self.ooconfigurator.ewebConfig.btnNext01.click()
                    time.sleep(2)
                
                    success = self.ooconfigurator.ewebConfig.btnNext02.isDisplayed()
                    if success:
                        self.ooconfigurator.ewebConfig.btnNext02.click()
                        time.sleep(2)
            
                    success = self.ooconfigurator.ewebConfig.btnSubmit.isDisplayed()
                    if success:
                        self.ooconfigurator.ewebConfig.nickName = shippings[order["Shipping"]]["NickName"]
                        self.ooconfigurator.ewebConfig.contactName = shippings[order["Shipping"]]["Contact Name"]
                        self.ooconfigurator.ewebConfig.email = shippings[order["Shipping"]]["Email"]
                        self.ooconfigurator.ewebConfig.address01 = shippings[order["Shipping"]]["Address 1"]
                        self.ooconfigurator.ewebConfig.city = shippings[order["Shipping"]]["City"]
                        self.ooconfigurator.ewebConfig.country = shippings[order["Shipping"]]["Country"]
                        self.ooconfigurator.ewebConfig.state = shippings[order["Shipping"]]["State"]
                        self.ooconfigurator.ewebConfig.zipCode = shippings[order["Shipping"]]["ZipCode"]
                        self.ooconfigurator.ewebConfig.phone = shippings[order["Shipping"]]["Phone"]
                        self.ooconfigurator.ewebConfig.fax = shippings[order["Shipping"]]["Fax"]
            
                    self.ooconfigurator.ewebConfig.btnSubmit.click()
                    time.sleep(15)
                    success = self.ooconfigurator.ewebConfig.confirmSubmit.isDisplayed()
                
        if order["Product"] == "enteliBRIDGE":
            self.ooconfigurator.homePage.enteliBRIDGELnk.click()
            time.sleep(10)
            success = self.ooconfigurator.ebridgeConfig.isLoaded()
            if success:
                if self.ooconfigurator.ebridgeConfig.partnerID.isDisplayed():
                    self.ooconfigurator.ebridgeConfig.partnerID = order["Partner"]
                    time.sleep(2)
                self.ooconfigurator.ebridgeConfig.poNumber = order["PO"]
                self.ooconfigurator.ebridgeConfig.quantity = order["Quantity"]
                self.ooconfigurator.ebridgeConfig.poNumber.click()
                time.sleep(1)
                if "ModBUS TCP" in order["Add-Ons"]:
                    self.ooconfigurator.ebridgeConfig.addON_ModBUS_TCP.select()
                    self.ooconfigurator.ebridgeConfig.counter_ModBUS_TCP = order["Counter_ModBUS_TCP"]
                self.ooconfigurator.ebridgeConfig.powerSupply = order["Power Supply"]
                
                if submit:
                    self.ooconfigurator.ebridgeConfig.scroll_to_bottom()
                    time.sleep(1)
                    self.ooconfigurator.ebridgeConfig.btnNext01.click()
                    time.sleep(2)
                
                    success = self.ooconfigurator.ebridgeConfig.btnNext02.isDisplayed()
                    if success:
                        self.ooconfigurator.ebridgeConfig.btnNext02.click()
                        time.sleep(2)
            
                    success = self.ooconfigurator.ebridgeConfig.btnSubmit.isDisplayed()
                    if success:
                        self.ooconfigurator.ebridgeConfig.nickName = shippings[order["Shipping"]]["NickName"]
                        self.ooconfigurator.ebridgeConfig.contactName = shippings[order["Shipping"]]["Contact Name"]
                        self.ooconfigurator.ebridgeConfig.email = shippings[order["Shipping"]]["Email"]
                        self.ooconfigurator.ebridgeConfig.address01 = shippings[order["Shipping"]]["Address 1"]
                        self.ooconfigurator.ebridgeConfig.city = shippings[order["Shipping"]]["City"]
                        self.ooconfigurator.ebridgeConfig.country = shippings[order["Shipping"]]["Country"]
                        self.ooconfigurator.ebridgeConfig.state = shippings[order["Shipping"]]["State"]
                        self.ooconfigurator.ebridgeConfig.zipCode = shippings[order["Shipping"]]["ZipCode"]
                        self.ooconfigurator.ebridgeConfig.phone = shippings[order["Shipping"]]["Phone"]
                        self.ooconfigurator.ebridgeConfig.fax = shippings[order["Shipping"]]["Fax"]
            
                    self.ooconfigurator.ebridgeConfig.btnSubmit.click()
                    time.sleep(15)
                    success = self.ooconfigurator.ebridgeConfig.confirmSubmit.isDisplayed()
            
        if order["Product"] == "CopperCube":
            self.ooconfigurator.homePage.copperCubeLnk.click()
            time.sleep(10)
            success = self.ooconfigurator.cucubeConfig.isLoaded()
            if success:
                if self.ooconfigurator.cucubeConfig.partnerID.isDisplayed():
                    self.ooconfigurator.cucubeConfig.partnerID = order["Partner"]
                    time.sleep(2)
                self.ooconfigurator.cucubeConfig.poNumber = order["PO"]
                self.ooconfigurator.cucubeConfig.quantity = order["Quantity"]
                self.ooconfigurator.cucubeConfig.poNumber.click()
                time.sleep(1)
                self.ooconfigurator.cucubeConfig.trendLogs = order["Trend Logs"]
                time.sleep(1)
                if order["SQL Connector"]:
                    self.ooconfigurator.cucubeConfig.sqlConnector.select()
                    time.sleep(1)
                self.ooconfigurator.cucubeConfig.powerSupply = order["Power Supply"]
                
                if submit:
                    self.ooconfigurator.cucubeConfig.scroll_to_bottom()
                    time.sleep(1)
                    self.ooconfigurator.cucubeConfig.btnNext01.click()
                    time.sleep(2)
                
                    success = self.ooconfigurator.cucubeConfig.btnNext02.isDisplayed()
                    if success:
                        self.ooconfigurator.cucubeConfig.btnNext02.click()
                        time.sleep(2)
            
                    success = self.ooconfigurator.cucubeConfig.btnSubmit.isDisplayed()
                    if success:
                        self.ooconfigurator.cucubeConfig.nickName = shippings[order["Shipping"]]["NickName"]
                        self.ooconfigurator.cucubeConfig.contactName = shippings[order["Shipping"]]["Contact Name"]
                        self.ooconfigurator.cucubeConfig.email = shippings[order["Shipping"]]["Email"]
                        self.ooconfigurator.cucubeConfig.address01 = shippings[order["Shipping"]]["Address 1"]
                        self.ooconfigurator.cucubeConfig.city = shippings[order["Shipping"]]["City"]
                        self.ooconfigurator.cucubeConfig.country = shippings[order["Shipping"]]["Country"]
                        self.ooconfigurator.cucubeConfig.state = shippings[order["Shipping"]]["State"]
                        self.ooconfigurator.cucubeConfig.zipCode = shippings[order["Shipping"]]["ZipCode"]
                        self.ooconfigurator.cucubeConfig.phone = shippings[order["Shipping"]]["Phone"]
                        self.ooconfigurator.cucubeConfig.fax = shippings[order["Shipping"]]["Fax"]
            
                    self.ooconfigurator.cucubeConfig.btnSubmit.click()
                    time.sleep(15)
                    success = self.ooconfigurator.cucubeConfig.confirmSubmit.isDisplayed()
                
               
        return success
                
                    