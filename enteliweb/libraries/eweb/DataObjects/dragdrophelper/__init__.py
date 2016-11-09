import os

def html5DragDropHelper(seleniumDriver, strSourceID, strDestinationID):
    """
    A suggested workaround to simulate HTML5 drag and drop via JavaScript
    reference:
    http://stackoverflow.com/questions/29381233/how-to-simulate-html5-drag-and-drop-in-selenium-webdriver
    """
    jquery_url = "http://code.jquery.com/jquery-1.11.2.min.js"
    
    seleniumDriver.set_script_timeout(30)
    
    js_File_Location = os.path.dirname(__file__)
    
    # load jQuery helper
    jsFilePath = os.path.join(js_File_Location, "jquery_load_helper.js")
    with open(jsFilePath) as f:
        load_jquery_js = f.read()
            
    # load drag and drop helper
    jsFilePath = os.path.join(js_File_Location, "drag_and_drop_helper.js")
    with open(jsFilePath) as f:
        drag_and_drop_js = f.read()
            
    # load jQuery
    seleniumDriver.execute_async_script(load_jquery_js, jquery_url)
    
    # perform drag and drop
    seleniumDriver.execute_script(drag_and_drop_js + "$('#%s').simulateDragDrop({dropTarget: '#%s'});"%(strSourceID, strDestinationID))
    
    
def pyautoguiDragDropHelper(seleniumDriver, elemFrom, elemTo):
    """
    A workaround for tree node drag and drop using pyautogui model
    the helper assume it working in iframe 'mainFrame'
    """
    import pyautogui    # input pyautogui model
        
    elemFromX = (elemFrom.rect)["x"]
    elemFromY = (elemFrom.rect)["y"]
    elemFromW = (elemFrom.rect)["width"]
    elemFromH = (elemFrom.rect)["height"]
        
    elemToX = (elemTo.rect)["x"]
    elemToY = (elemTo.rect)["y"]
    elemToW = (elemTo.rect)["width"]
    elemToH = (elemTo.rect)["height"]
        
    # switch to default doc to get it's origin
    seleniumDriver.switch_to_default_content()
    docX, docY = _getDocOrigin(seleniumDriver)
        
    # get the iframe origin
    iframe = seleniumDriver.find_element_by_id("mainFrame")
    iframeX = (iframe.rect)["x"]
    iframeY = (iframe.rect)["y"]
        
    #switch back to iframe
    seleniumDriver.switch_to_frame("mainFrame")
      
    movetoX = docX + iframeX + elemFromX + elemFromW / 2
    movetoY = docY + iframeY + elemFromY + elemFromH / 2
        
    dragtoX = docX + iframeX + elemToX + elemToW / 2
    dragtoY = docY + iframeY + elemToY + elemToH / 2
        
    # mouse drag and drop
    pyautogui.moveTo(movetoX, movetoY, 0.3)
    pyautogui.dragTo(dragtoX, dragtoY, 0.3, button="left")    
        
    
def _getDocOrigin(seleniumDriver):
    """
    helper to get absolute coordinates of document with js
    """
      
    # this is the border width of the OS window
    border = seleniumDriver.execute_script("return (window.outerWidth - window.innerWidth)/2;")
    
    # Assuming the window border is homogeneous and there is nothing in
    # the bottom of the window (firebug or something like that)
    menuHeight = seleniumDriver.execute_script("return (window.outerHeight-window.innerHeight) - %s*2;"%border)
    
    absX = seleniumDriver.execute_script("return window.screenX + %s;"%border)
    absY = seleniumDriver.execute_script("return window.screenY + %s + %s;"%(border, menuHeight))
    
    return absX, absY
    
        