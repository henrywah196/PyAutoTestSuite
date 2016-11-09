from libraries.Actions import WebdriverWrapper

webdriver_connection = WebdriverWrapper()

locators = {}

locators["login.username"] = {"by" : "id", "value" : "tbUsername",  "parent" : None, "tag_name" : "input", "type" : "EditBox"}
locators["login.password"] = {"by" : "id", "value" : "tbPassword",  "parent" : None, "tag_name" : "input", "type" : "EditBox"}
locators["login.submit"]   = {"by" : "id", "value" : "Login",       "parent" : None, "tag_name" : "input", "type" : "Button"}

locators["home.Headline"]     = {"by" : "id",    "value" : "ctl00_cphMainPage_lblInformation", "parent" : None, "tag_name" : "span",   "type" : "Text"}
locators["home.SearchValue"]  = {"by" : "id",    "value" : "ctl00_cphMainPage_tbSearchValue",  "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["home.SearchButton"] = {"by" : "xpath", "value" : "//button[@type='submit']",         "parent" : None, "tag_name" : "button", "type" : "Button"}
locators["home.NoResult"]     = {"by" : "id",    "value" : "ctl00_cphMainPage_lblNoResult",    "parent" : None, "tag_name" : "span",   "type" : "Text"}

locators["home.KeyListTable"]  = {"by" : "id",    "value" : "ctl00_cphMainPage_gvActivations",    "parent" : None, "tag_name" : "table",   "type" : "Table"}
locators["home.LicFilesTable"] = {"by" : "id",    "value" : "ctl00_cphMainPage_gvLicenseFiles",   "parent" : None, "tag_name" : "table",   "type" : "Table"}

locators["licfile.Headline"]      = {"by" : "id",  "value" : "ctl00_cphMainPage_lblInformation",                        "parent" : None, "tag_name" : "span",   "type" : "Text"}
locators["licfile.Modules"]       = {"by" : "id",  "value" : "ctl00_cphMainPage_accPnlModules_header_lblHeaderModules", "parent" : None, "tag_name" : "span",   "type" : "Text"}
locators["licfile.ModulesTable"]  = {"by" : "id",  "value" : "ctl00_cphMainPage_accPnlModules_content_gvModules",       "parent" : None, "tag_name" : "table",  "type" : "Table"}
locators["licfile.DataArea"]      = {"by" : "id",  "value" : "ctl00_cphMainPage_accPnlData_header_lblHeaderData",       "parent" : None, "tag_name" : "span",   "type" : "Text"}
locators["licfile.DataAreaTable"] = {"by" : "id",  "value" : "ctl00_cphMainPage_accPnlData_content_gvData",             "parent" : None, "tag_name" : "table",  "type" : "Table"}

locators["module.Headline"]          = {"by" : "id",    "value" : "ctl00_cphMainPage_lblInformation",  "parent" : None, "tag_name" : "span",   "type" : "Text"}
locators["module.ModuleNumber"]      = {"by" : "id",    "value" : "ctl00_cphMainPage_ddlModuleId",     "parent" : None, "tag_name" : "select", "type" : "EditBox"}
locators["module.ValidUntilDay"]     = {"by" : "id",    "value" : "ctl00_cphMainPage_tbValidUntilDay", "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["module.ValidNumberOfDays"] = {"by" : "id",    "value" : "ctl00_cphMainPage_tbValidUntil",    "parent" : None, "tag_name" : "input",  "type" : "EditBox"}
locators["module.Save"]              = {"by" : "id",    "value" : "ctl00_cphMainPage_lblSave",         "parent" : None, "tag_name" : "span",   "type" : "Button"}
locators["module.Cancel"]            = {"by" : "id",    "value" : "ctl00_cphMainPage_lblCancel",       "parent" : None, "tag_name" : "span",   "type" : "Button"}