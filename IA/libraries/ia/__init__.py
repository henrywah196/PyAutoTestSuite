locators = {}

locators["welcome.title"]           = "Delta Controls | Interactive Architecture"
locators["welcome.welcome_heading"] = {"by":"class_name", "value":"content-welcome-heading", "parent":None, "tag_name":"h2", "type":"TextBox"}
locators["welcome.online_version"]  = {"by":"class_name", "value":"selection__link--left",   "parent":None, "tag_name":"a", "type":"Button"}


locators["login.title"]    = "Delta Controls Passport Login"
locators["login.username"] = {"by":"name", "value":"username", "parent":None, "tag_name":"input", "type":"EditBox"}
locators["login.password"] = {"by":"name", "value":"password", "parent":None, "tag_name":"input", "type":"EditBox"}
locators["login.submit"]   = {"by":"name", "value":"submit",   "parent":None, "tag_name":"input", "type":"EditBox"}


locators["main.title"]           = "Delta City | Sales tool"
locators["main.navigator"]       = {"by":"class_name", "value":"nav-controls-1",       "parent":None, "tag_name":"nav", "type":"NavigationBar"}
locators["main.nav_healthcare"]  = {"by":"class_name", "value":"nav-item-healthcare",  "parent":None, "tag_name":"a",   "type":"Button"}
locators["main.nav_hospitality"] = {"by":"class_name", "value":"nav-item-hospitality", "parent":None, "tag_name":"a",   "type":"Button"}
locators["main.nav_education"]   = {"by":"class_name", "value":"nav-item-education",   "parent":None, "tag_name":"a",   "type":"Button"}
locators["main.nav_commercial"]  = {"by":"class_name", "value":"nav-item-commercial",  "parent":None, "tag_name":"a",   "type":"Button"}
locators["main.nav_datacentre"]  = {"by":"class_name", "value":"nav-item-data-centre", "parent":None, "tag_name":"a",   "type":"Button"}

# Generic elements locator for HotSpot Building
locators["building.title"]        = locators["main.title"]
locators["building.backtocity"]   = {"by":"class_name", "value":"back-button",    "parent":None, "tag_name":"span", "type":"Button"}
locators["building.navigator"]    = {"by":"class_name", "value":"nav-controls-2", "parent":None, "tag_name":"nav",  "type":"NavigationBar"}
locators["building.nav_previous"] = {"by":"class_name", "value":"bx-prev",        "parent":None, "tag_name":"a",    "type":"Button"}
locators["building.nav_next"]     = {"by":"class_name", "value":"bx-next",        "parent":None, "tag_name":"a",    "type":"Button"}
locators["building.image"]        = {"by":"class_name", "value":"video_image",    "parent":None, "tag_name":"div",  "type":"Image"}

