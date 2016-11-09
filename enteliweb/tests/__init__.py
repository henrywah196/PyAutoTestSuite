locators = {}

locators["login.username"]                             = {"by":"id",    "value":"username", "parent":None, "tag_name":"input", "type":"EditBox"}
locators["login.password"]                             = {"by":"id",    "value":"password", "parent":None, "tag_name":"input", "type":"EditBox"}
locators["login.submit"]                               = {"by":"id",    "value":"btn_login", "parent":None, "tag_name":"input", "type": "Button"}

locators["main.settings"]                              = {"by":"id",    "value":"loggedin_user", "parent":None, "tag_name":"a", "type":"HyperLink"}
locators["main.logout"]                                = {"by":"id",    "value":"link_logout", "parent":None, "tag_name":"a", "type":"HyperLink"}
locators["main.administration"]                        = {"by":"id",    "value":"link_admin", "parent":None, "tag_name":"a", "type":"HyperLink"}
locators["main.help"]                                  = {"by":"id",    "value":"link_help", "parent":None, "tag_name":"img", "type":"HyperLink"}

locators["admin.title"]                                = {"by":"id",    "value":"headertitle", "parent":None, "tag_name":"span", "type":"TextBox"}
locators["admin.meters"]                               = {"by":"id",    "value":"link_listMeters", "parent":None, "tag_name":"a", "type":"HyperLink"}
locators["admin.base_unit_configuration"]              = {"by":"id",    "value":"link_reportbaseunits", "parent":None, "tag_name":"a", "type":"HyperLink"}

locators["units.title"]                                = {"by":"id",    "value":"headertitle", "parent":None, "tag_name":"span", "type":"TextBox"}
locators["units.alert_message"]                        = {"by":"xpath", "value":"//div[@class='errorDiv']/span[1]", "parent":None, "tag_name":"span", "type":"TextBox"}
locators["units.setdefaultmetric"]                     = {"by":"id",    "value":"baseUnitSetMetric-btnInnerEl", "parent":None, "tag_name":"span", "type":"Button"}
locators["units.setdefaultimperial"]                   = {"by":"id",    "value":"baseUnitSetImperial-btnInnerEl", "parent":None, "tag_name":"span", "type":"Button"}
locators["units.outdoor_temp"]                         = {"by":"id",    "value":"Temperature-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.outdoor_temp.invalid_icon"]            = {"by":"id",    "value":"Temperature-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.electricity_consumption"]              = {"by":"id",    "value":"Energy_Electric-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.electricity_consumption.invalid_icon"] = {"by":"id",    "value":"Energy_Electric-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.electricity_demand"]                   = {"by":"id",    "value":"Power_Electric-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.electricity_demand.invalid_icon"]      = {"by":"id",    "value":"Power_Electric-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.apparent_consumption"]                 = {"by":"id",    "value":"Apparent_Energy_Electric-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.apparent_consumption.invalid_icon"]    = {"by":"id",    "value":"Apparent_Energy_Electric-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.apparent_demand"]                      = {"by":"id",    "value":"Apparent_Power_Electric-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.apparent_demand.invalid_icon"]         = {"by":"id",    "value":"Apparent_Power_Electric-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.gas_consumption"]                      = {"by":"id",    "value":"Volume_Gas-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.gas_consumption.invalid_icon"]         = {"by":"id",    "value":"Volume_Gas-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.gas_demand"]                           = {"by":"id",    "value":"Flow_Volume_Gas-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.gas_demand.invalid_icon"]              = {"by":"id",    "value":"Flow_Volume_Gas-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.energy_consumption"]                   = {"by":"id",    "value":"Energy_Gas-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.energy_consumption.invalid_icon"]      = {"by":"id",    "value":"Energy_Gas-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.energy_demand"]                        = {"by":"id",    "value":"Power_Gas-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.energy_demand.invalid_icon"]           = {"by":"id",    "value":"Power_Gas-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.fuel_consumption"]                     = {"by":"id",    "value":"Volume_Fuel-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.fuel_consumption.invalid_icon"]        = {"by":"id",    "value":"Volume_Fuel-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.fuel_demand"]                          = {"by":"id",    "value":"Flow_Volume_Fuel-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.fuel_demand.invalid_icon"]             = {"by":"id",    "value":"Flow_Volume_Fuel-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.water_consumption"]                    = {"by":"id",    "value":"Volume_Water-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.water_consumption.invalid_icon"]       = {"by":"id",    "value":"Volume_Water-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.water_demand"]                         = {"by":"id",    "value":"Flow_Volume_Water-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.water_demand.invalid_icon"]            = {"by":"id",    "value":"Flow_Volume_Water-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.thermal_consumption"]                  = {"by":"id",    "value":"Energy_Thermal-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.thermal_consumption.invalid_icon"]     = {"by":"id",    "value":"Energy_Thermal-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.thermal_demand"]                       = {"by":"id",    "value":"Power_Thermal-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.thermal_demand.invalid_icon"]          = {"by":"id",    "value":"Power_Thermal-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.steam_consumption"]                    = {"by":"id",    "value":"Weight_Steam-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.steam_consumption.invalid_icon"]       = {"by":"id",    "value":"Weight_Steam-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.steam_demand"]                         = {"by":"id",    "value":"Flow_Mass_Steam-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.steam_demand.invalid_icon"]            = {"by":"id",    "value":"Flow_Mass_Steam-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.carbon_emission"]                      = {"by":"id",    "value":"Weight_Carbon-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.carbon_emission.invalid_icon"]         = {"by":"id",    "value":"Weight_Carbon-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.currency"]                             = {"by":"id",    "value":"Currency-inputEl", "parent":None, "tag_name":"input", "type":"DropDownBox"}
locators["units.currency.invalid_icon"]                = {"by":"id",    "value":"Currency-errorEl", "parent":None, "tag_name":"div", "type":"icon"}
locators["units.save"]                                 = {"by":"id",    "value":"baseUnitSaveBtn-btnInnerEl", "parent":None, "tag_name":"span", "type":"Button"}