from libraries.PATS.Actions import WebdriverWrapper

webdriver_connection = WebdriverWrapper()

locators = {}

locators["login.username"] = {"by" : "id",   "value" : "username",  "parent" : None, "tag_name" : "input", "type" : "EditBox"}
locators["login.password"] = {"by" : "id",   "value" : "password",  "parent" : None, "tag_name" : "input", "type" : "EditBox"}
locators["login.submit"]   = {"by" : "name", "value" : "submit",       "parent" : None, "tag_name" : "input", "type" : "Button"}


locators["home.Headline"]        = {"by" : "tag_name", "value" : "h3",    "parent" : None, "tag_name" : "h3",  "type" : "Text"}
locators["home.enteliWEBLnk"]    = {"by" : "id",       "value" : "icon1", "parent" : None, "tag_name" : "div", "type" : "HyperLink"}
locators["home.enteliBRIDGELnk"] = {"by" : "id",       "value" : "icon2", "parent" : None, "tag_name" : "div", "type" : "HyperLink"}
locators["home.copperCubeLnk"]   = {"by" : "id",       "value" : "icon3", "parent" : None, "tag_name" : "div", "type" : "HyperLink"}


locators["pdConfig.wizHeader"]            = {"by" : "id",   "value" : "wizHeader",                                              "parent" : None, "tag_name" : "ul",     "type" : "TextBox"}
locators["pdConfig.confirmSubmit"]        = {"by" : "id",   "value" : "ctl00_MainContent_lblMessage",                           "parent" : None, "tag_name" : "span",   "type" : "TextBox"}

locators["pdConfig.Shipping.nickName"]    = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliWebConfig_ddlAddresscode",    "parent" : None, "tag_name" : "select", "type" : "DropDownBox"} 
locators["pdConfig.Shipping.contactName"] = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliWebConfig_txtContactName",    "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["pdConfig.Shipping.email"]       = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliWebConfig_txtEmail1",         "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["pdConfig.Shipping.address01"]   = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliWebConfig_txtAddress1",       "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["pdConfig.Shipping.city"]        = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliWebConfig_txtCity",           "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["pdConfig.Shipping.country"]     = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliWebConfig_ddlCountry",        "parent" : None, "tag_name" : "select", "type" : "DropDownBox"}
locators["pdConfig.Shipping.state"]       = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliWebConfig_ddlStateProvince",  "parent" : None, "tag_name" : "select", "type" : "DropDownBox"}
locators["pdConfig.Shipping.zipCode"]     = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliWebConfig_txtPostalCode",     "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["pdConfig.Shipping.phone"]       = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliWebConfig_txtPhone",          "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["pdConfig.Shipping.fax"]         = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliWebConfig_txtFax",            "parent" : None, "tag_name" : "input",  "type" : "EditBox"}

locators["ewebConfig.wizHeader"]                  = {"by" : "id",  "value" : "wizHeader",                                               "parent" : None, "tag_name" : "ul",     "type" : "TextBox"}
locators["ewebConfig.Partner ID"]                 = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_ddlPartnerID",       "parent" : None, "tag_name" : "select", "type" : "DropDownBox"}
locators["ewebConfig.PO Number"]                  = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_txtPoNumber",        "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["ewebConfig.Quantity"]                   = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_txtQuantity",        "parent" : None, "tag_name" : "select", "type" : "EditBox"}
locators["ewebConfig.IO Points"]                  = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_ddlEnteliWEBPoints", "parent" : None, "tag_name" : "select", "type" : "DropDownBox"}
locators["ewebConfig.Site Name"]                  = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_txtSiteName",        "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["ewebConfig.Site Address"]               = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_txtSiteAddress",     "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["ewebConfig.Additional Subscription"]    = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_ddlSubscription",    "parent" : None, "tag_name" : "select", "type" : "DropDownBox"}

locators["ewebConfig.Add-Ons.enteliVIZ"]               = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_tvProductsn1CheckBox", "parent" : None, "tag_name" : "input", "type" : "CheckBox"}
locators["ewebConfig.Add-Ons.enteliWEB API"]           = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_tvProductsn2CheckBox", "parent" : None, "tag_name" : "input", "type" : "CheckBox"}
locators["ewebConfig.Add-Ons.Virtual Machine"]         = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_tvProductsn3CheckBox", "parent" : None, "tag_name" : "input", "type" : "CheckBox"}
locators["ewebConfig.Add-Ons.Additional Subscription"] = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_tvProductsn4CheckBox", "parent" : None, "tag_name" : "input", "type" : "CheckBox"}
locators["ewebConfig.Add-Ons.Kaizen for enteliWEB"]    = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_tvProductsn6CheckBox", "parent" : None, "tag_name" : "input", "type" : "CheckBox"}
locators["ewebConfig.Add-Ons.Kaizen Cloud"]            = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_tvProductsn7CheckBox", "parent" : None, "tag_name" : "input", "type" : "CheckBox"}

locators["ewebConfig.Next01"]   = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_StartNavigationTemplateContainerID_btnNext1", "parent" : None, "tag_name" : "input", "type" : "Button"}
locators["ewebConfig.Previous"] = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_StepNavigationTemplateContainerID_btnPrevious", "parent" : None, "tag_name" : "input", "type" : "Button"}
locators["ewebConfig.Next02"]   = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_StepNavigationTemplateContainerID_btnNext", "parent" : None, "tag_name" : "input", "type" : "Button"}
locators["ewebConfig.Submit"]   = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_FinishNavigationTemplateContainerID_btnFinish", "parent" : None, "tag_name" : "input", "type" : "Button"}

locators["ewebConfig.Order Review"] = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliWebConfig_divCart", "parent" : None, "tag_name" : "div",  "type" : "TextBox"}

locators["ebridgeConfig.Partner ID"]         = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliBridgeConfig_ddlPartnerID",    "parent" : None, "tag_name" : "select", "type" : "DropDownBox"}
locators["ebridgeConfig.PO Number"]          = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliBridgeConfig_txtPoNumber",     "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["ebridgeConfig.Quantity"]           = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliBridgeConfig_txtQuantity",     "parent" : None, "tag_name" : "select", "type" : "EditBox"}
locators["ebridgeConfig.Power Supply"]       = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliBridgeConfig_ddlPowerSupply",  "parent" : None, "tag_name" : "select", "type" : "DropDownBox"}
locators["ebridgeConfig.Add-Ons.ModBUS TCP"] = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliBridgeConfig_chkModBusTcp",    "parent" : None, "tag_name" : "input",  "type" : "CheckBox"}
locators["ebridgeConfig.Counter.ModBUS TCP"] = {"by" : "id",  "value" : "ctl00_MainContent_wizEnteliBridgeConfig_txtModBusTcpQty", "parent" : None, "tag_name" : "select", "type" : "EditBox"}

locators["ebridgeConfig.Next01"]               = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliBridgeConfig_StartNavigationTemplateContainerID_btnNext1", "parent" : None, "tag_name" : "input", "type" : "Button"}
locators["ebridgeConfig.Previous"]             = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliBridgeConfig_StepNavigationTemplateContainerID_btnPrevious", "parent" : None, "tag_name" : "input", "type" : "Button"}
locators["ebridgeConfig.Next02"]               = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliBridgeConfig_StepNavigationTemplateContainerID_btnNext", "parent" : None, "tag_name" : "input", "type" : "Button"}
locators["ebridgeConfig.Submit"]               = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliBridgeConfig_FinishNavigationTemplateContainerID_btnFinish", "parent" : None, "tag_name" : "input", "type" : "Button"}

locators["ebridgeConfig.Shipping.nickName"]    = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliBridgeConfig_ddlAddresscode",    "parent" : None, "tag_name" : "select", "type" : "DropDownBox"} 
locators["ebridgeConfig.Shipping.contactName"] = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliBridgeConfig_txtContactName",    "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["ebridgeConfig.Shipping.email"]       = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliBridgeConfig_txtEmail1",         "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["ebridgeConfig.Shipping.address01"]   = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliBridgeConfig_txtAddress1",       "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["ebridgeConfig.Shipping.city"]        = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliBridgeConfig_txtCity",           "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["ebridgeConfig.Shipping.country"]     = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliBridgeConfig_ddlCountry",        "parent" : None, "tag_name" : "select", "type" : "DropDownBox"}
locators["ebridgeConfig.Shipping.state"]       = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliBridgeConfig_ddlStateProvince",  "parent" : None, "tag_name" : "select", "type" : "DropDownBox"}
locators["ebridgeConfig.Shipping.zipCode"]     = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliBridgeConfig_txtPostalCode",     "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["ebridgeConfig.Shipping.phone"]       = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliBridgeConfig_txtPhone",          "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["ebridgeConfig.Shipping.fax"]         = {"by" : "id",   "value" : "ctl00_MainContent_wizEnteliBridgeConfig_txtFax",            "parent" : None, "tag_name" : "input",  "type" : "EditBox"}


locators["cubeConfig.Partner ID"]         = {"by" : "id",  "value" : "ctl00_MainContent_wizCopperCubeConfig_ddlPartnerID",    "parent" : None, "tag_name" : "select", "type" : "DropDownBox"}
locators["cubeConfig.PO Number"]          = {"by" : "id",  "value" : "ctl00_MainContent_wizCopperCubeConfig_txtPoNumber",     "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["cubeConfig.Quantity"]           = {"by" : "id",  "value" : "ctl00_MainContent_wizCopperCubeConfig_txtQuantity",     "parent" : None, "tag_name" : "select", "type" : "EditBox"}
locators["cubeConfig.Power Supply"]       = {"by" : "id",  "value" : "ctl00_MainContent_wizCopperCubeConfig_ddlPowerSupply",  "parent" : None, "tag_name" : "select", "type" : "DropDownBox"}
locators["cubeConfig.Trend Logs"]         = {"by" : "id",  "value" : "ctl00_MainContent_wizCopperCubeConfig_ddlSize",         "parent" : None, "tag_name" : "select", "type" : "DropDownBox"}
locators["cubeConfig.SQL Connector"]      = {"by" : "id",  "value" : "ctl00_MainContent_wizCopperCubeConfig_chkSQLOption",    "parent" : None, "tag_name" : "input",  "type" : "CheckBox"}
    
locators["cubeConfig.Next01"]               = {"by" : "id",   "value" : "ctl00_MainContent_wizCopperCubeConfig_StartNavigationTemplateContainerID_btnNext1", "parent" : None, "tag_name" : "input", "type" : "Button"}
locators["cubeConfig.Previous"]             = {"by" : "id",   "value" : "ctl00_MainContent_wizCopperCubeConfig_StepNavigationTemplateContainerID_btnPrevious", "parent" : None, "tag_name" : "input", "type" : "Button"}
locators["cubeConfig.Next02"]               = {"by" : "id",   "value" : "ctl00_MainContent_wizCopperCubeConfig_StepNavigationTemplateContainerID_btnNext", "parent" : None, "tag_name" : "input", "type" : "Button"}
locators["cubeConfig.Submit"]               = {"by" : "id",   "value" : "ctl00_MainContent_wizCopperCubeConfig_FinishNavigationTemplateContainerID_btnFinish", "parent" : None, "tag_name" : "input", "type" : "Button"}
    
locators["cubeConfig.Shipping.nickName"]    = {"by" : "id",   "value" : "ctl00_MainContent_wizCopperCubeConfig_ddlAddresscode",    "parent" : None, "tag_name" : "select", "type" : "DropDownBox"} 
locators["cubeConfig.Shipping.contactName"] = {"by" : "id",   "value" : "ctl00_MainContent_wizCopperCubeConfig_txtContactName",    "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["cubeConfig.Shipping.email"]       = {"by" : "id",   "value" : "ctl00_MainContent_wizCopperCubeConfig_txtEmail1",         "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["cubeConfig.Shipping.address01"]   = {"by" : "id",   "value" : "ctl00_MainContent_wizCopperCubeConfig_txtAddress1",       "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["cubeConfig.Shipping.city"]        = {"by" : "id",   "value" : "ctl00_MainContent_wizCopperCubeConfig_txtCity",           "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["cubeConfig.Shipping.country"]     = {"by" : "id",   "value" : "ctl00_MainContent_wizCopperCubeConfig_ddlCountry",        "parent" : None, "tag_name" : "select", "type" : "DropDownBox"}
locators["cubeConfig.Shipping.state"]       = {"by" : "id",   "value" : "ctl00_MainContent_wizCopperCubeConfig_ddlStateProvince",  "parent" : None, "tag_name" : "select", "type" : "DropDownBox"}
locators["cubeConfig.Shipping.zipCode"]     = {"by" : "id",   "value" : "ctl00_MainContent_wizCopperCubeConfig_txtPostalCode",     "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["cubeConfig.Shipping.phone"]       = {"by" : "id",   "value" : "ctl00_MainContent_wizCopperCubeConfig_txtPhone",          "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["cubeConfig.Shipping.fax"]         = {"by" : "id",   "value" : "ctl00_MainContent_wizCopperCubeConfig_txtFax",            "parent" : None, "tag_name" : "input",  "type" : "EditBox"}



