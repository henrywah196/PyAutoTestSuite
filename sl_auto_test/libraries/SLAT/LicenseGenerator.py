#-------------------------------------------------------------------------------
# Name:        LicenseGenerator.py
# Purpose:     gui object to model Delta license generator application
#
# Author:      wah
# Created:     18/07/2014
#-------------------------------------------------------------------------------
import os, time
import _winreg
from pywinauto import application, findwindows


class Popup(object):
    """ class to model the small popup window in license generator """
    def __init__(self, parent):
        self.parent = parent    # reference to License generator object
        self.ref = None         # reference itself
            
    def isLoaded(self):
        """ verify if the popup is loaded """
        if not self.isClosed():
            return self.ref.IsVisible()
        else:
            return False
        
    def isClosed(self):
        """ verify if the popup is closed """
        if self.ref:
            return not self.ref.Exists()
        else:
            return True
        
    def click(self, buttonName):
        """ click the button in window """
        if self.ref:
            ctrl = self.ref[self.Controls[buttonName]]
            if ctrl.IsEnabled():
                ctrl.Click()
    #def isLoaded(self):
    #    """ verify if the error popup is loaded """
    #    self.update()
    #    return super(ErrorPopup, self).isLoaded()
            
    def Close(self):
        """ close the error popup window """
        if self.ref:
            ctrl = self.ref['OK']
            if ctrl.IsEnabled():
                ctrl.Click()
                time.sleep(5)
                
    def getPopupInfo(self):
        """ get the message in popup window """
        if self.ref:
            ctrl = self.ref['Static2']
            return (ctrl.Texts())[0] 
        else:
            return None
        

class Window(object):
    """ class to model main or sub window which belongs to License Generator """
    def __init__(self, parent):
        self.parent = parent    # reference to License Manager object
        self.ref = None         # reference itself

    def update(self, ref=None):
        """ update the internal control reference """
        if ref:
            self.ref = ref
        else:
            try:
                window = None
                w_handle = findwindows.find_windows(title=u'Delta Controls License Manager', class_name='#32770')[0]
                if w_handle != self.parent.ref.handle:
                    window = self.parent.app.window_(handle=w_handle)
                self.ref = window
            except: self.ref = None

    def isLoaded(self):
        """ verify if the window is loaded """
        if not self.isClosed():
            return self.ref.IsVisible()
        else:
            return False
        
    def isClosed(self):
        """ verify if the window is closed """
        if self.ref:
            return not self.ref.Exists()
        else:
            return True

    def Close(self):
        """ close window """
        if not self.isClosed():
            self.ref.Close()
            self.ref = None
            time.sleep(3)
            
    def isControlEnabled(self, controlName):
        """ verify if the control element in window is enabled """
        ctrl = self.ref[self.Controls[controlName]]
        return ctrl.IsEnabled()
            
    def click(self, buttonName):
        """ click the button in window """
        if self.ref:
            ctrl = self.ref[self.Controls[buttonName]]
            if ctrl.IsEnabled():
                ctrl.Click()
                
    def input(self, controlName, stringValue):
        """ input a string value to the editbox control in window"""
        if self.ref:
            ctrl = self.ref[self.Controls[controlName]]
            if ctrl.IsEnabled():
                ctrl.SetText(stringValue)
                
    def getValue(self, controlName):
        """ get a string value from the editbox control in window """
        if self.ref:
            ctrl = self.ref[self.Controls[controlName]]
            return (ctrl.Texts())[0]  
        
    def getDropdownList(self, controlName):
        """ get a list of available items in dropdown """ 
        result = None
        if self.ref:
            ctrl = self.ref[self.Controls[controlName]]
            if ctrl:
                items = ctrl.Texts()
                for item in items:
                    if not result:
                        result = []
                    if items.index(item) == 0:
                        continue
                    result.append(item)
        return result


class LicenseGenerator(Window):
    """ class to model Delta License Generator Utility """
    
    @classmethod
    def changeMode(cls, modeName):
        """ change the mode of license generator before you loading it """
        baseReg = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Wow6432Node\\Delta Controls\\License Generator", 0, _winreg.KEY_ALL_ACCESS)
        time.sleep(3)
        
        if modeName == "RMA":
            _winreg.SetValueEx(baseReg, "RMA", 0, 1, "delta")
            _winreg.SetValueEx(baseReg, "Testing", 0, 1, "no")
        if modeName == "Testing":
            _winreg.SetValueEx(baseReg, "RMA", 0, 1, "no")
            _winreg.SetValueEx(baseReg, "Testing", 0, 1, "delta")
        
        baseReg.Close()
        del baseReg
    
    def __init__(self, parent=None):
        super(LicenseGenerator, self).__init__(parent)
        self.Controls = {'Items List'                : 'ListView2',
                         'Selected Item List'        : 'ListView1',
                         'Components DropDown'       : 'ComboBox2',
                         'Count'                     : 'CountEdit',
                         'Add'                       : 'Add',
                         'Update'                    : 'Update',
                         'Remove'                    : 'Remove',
                         'Clear All'                 : 'Clear All',
                         'View Log File'             : 'SysLink',
                         'Generate License'          : 'Button',
                         'Customer Name'             : 'Edit',
                         'Sales Order'               : 'Edit2',
                         'Original Serial'           : 'Original Serial:Edit',
                         'Hardware Serial'           : 'Hardware Serial:Edit',
                         'Query'                     : 'Query',
                         'Installation Site Name'    : 'Installation Site Name:Edit',
                         'Installation Partner'      : 'Installing Partner:Edit',
                         'Installation Site Address' : 'Installation Site Address:Edit',
                         'Upgrade License'           : 'Button',
                         'Clone License'             : 'Button7',
                         'Unassign Hardware'         : 'Button6',}
        self.app = application.Application()                             # reference of application itself
        self.ItemsListView = None                                        # reference to Items list view pane
        self.SelectedItemListView = None                                 # reference to selected item list view pane
        self.ContinuePopup = ContinuePopup(self)                         # the small Continue popup window after generating a license successfully
        self.ErrorPopup = ErrorPopup(self)                               # the error popup window after failed generating a license
        self.LGPopup = LicenseGeneratorPopup(self)
        self.Log = LicenseGeneratorLog(self)                             # the License License Generator Log window
        self.AALGPopup = AALGPopup(self)
        self.EmailPopup = EmailPopup(self)

    def Launch(self, timeout, startApp=True):
        """ launch license manager """
        if startApp:
            self.app.start_(r"C:\Program Files (x86)\Delta Controls\License Generator\LicenseGenerator.exe")
            time.sleep(timeout)
        
        w_handle = findwindows.find_windows(title=u'Delta Controls License Generator', class_name='#32770')[0]
        self.update(self.app.window_(handle=w_handle))
        self.ItemsListView =self.ref[self.Controls['Items List']]
        self.SelectedItemListView = self.ref[self.Controls['Selected Item List']]
        
    def isLaunched(self):
        """ verify if the license generator is loaded """
        #return self.Main.Exist()
        return self.isLoaded()

    def Close(self):
        """ close license generator utility """
        super(LicenseGenerator, self).Close()
        time.sleep(3)
        #self.app = None
        
    def Reset(self):
        """ reset license generator if exception occur """
        taskListObj = os.popen("tasklist")
        taskListStr = taskListObj.read()
        taskListObj.close()
        del taskListObj
        try:
            if "AutoLicGenerator410.exe" in taskListStr:
                os.system("taskkill /im AutoLicGenerator410.exe /f")
        except:
            pass
        try:
            if "LicenseGenerator.exe" in taskListStr:
                # kill the licensemanager process from windows
                os.system("taskkill /im LicenseGenerator.exe /f")
        except:
            pass
        time.sleep(5)
        self.ref = None
        self.app = None
        
    def getMode(self):
        """ get the current mode of license generator either RMA or Testing """
        result = "Unknown"
        ctrl = self.ref['Button']
        label = ctrl.Texts()
        if "Generate License" in label:
            result = "Testing"
        if "Upgrade License" in label:
            result = "RMA"
        return result

    def click(self, buttonName):
        """ click the button """
        ctrl = self.ref[self.Controls[buttonName]]
        if ctrl.IsEnabled():
            ctrl.Click()
            time.sleep(15)
            if buttonName == 'View': self.LicenseViewer.update()
            elif buttonName == 'Transfer': self.TransferLicense.update()
            elif buttonName == 'Add New': self.AddProduct.update()

    def getProductList(self):
        """ get the available product list from license generator """
        result = None
        items = self.ItemsListView.Items()
        if items:
            total = len(items)
            i = 0
            while i < total:
                if not result:
                    result = {}
                value = items[i]['text']
                key = items[i + 1]['text']
                result[key] = value
                i = i + 2
        return result
            

    def selectProduct(self, itemName):
        """ command to select the client software name from list """
        items = self.ItemsListView.Items()
        if items:
            target = None
            for item in items:
                if itemName == item['text']:
                    #work around for enteliBRIDGE
                    #print "itemName: %s" %itemName
                    #print "item['text']: %s" %item['text']
                    target = item
                    break
            if target:
                idx = (items.index(target) - 1) / 2
                #print "idx: %s" %idx
                self.ItemsListView.Select(idx)
            else:
                raise Exception("product: '%s' doesn't in the list" %itemName)
            
    def getAddedComponents(self):
        """ return a list of added components from the components list pane """
        result = None
        items = self.SelectedItemListView.Items()
        if items:
            result = []
            i = 0
            while i < len(items):
                component = []
                component.append(items[i + 1]['text'])
                component.append(items[i]['text'])
                result.append(component)
                i = i + 2
        return result
    
    def isComponentExist(self, compoName):
        """ return true if the specified component is in the added component list """
        result = False
        targetList = self.getAddedComponents()
        if targetList:
            for item in targetList:
                if item[0] == compoName:
                    result = True
                    break
        return result
                     
    def addComponent(self, compoName, count=None):
        """ command to add a component to the components list pane """
        ctrl = self.ref[self.Controls['Components DropDown']]
        if ctrl.IsEnabled():
            items = ctrl.Texts()
            if items:
                target = None
                for item in items:
                    if compoName in item:
                        target = item
                        break
                if target:
                    ctrl.Select(target)
                    if count:
                        ctrl =  self.ref[self.Controls['Count']]
                        if ctrl.IsEnabled():
                            ctrl.SetText(count)
                    ctrl = self.ref[self.Controls['Add']]
                    if ctrl.IsEnabled():
                        ctrl.Click()
        
    def removeComponent(self, compoName):
        """ command to remove a component from the components list """
        items = self.SelectedItemListView.Items()
        if items:
            target = None
            for item in items:
                if compoName in item['text']:
                    target = item
                    break
            if target:
                idx = (items.index(target) - 1) / 2
                self.SelectedItemListView.Select(idx)
                ctrl =  self.ref[self.Controls['Remove']]
                if ctrl.IsEnabled():
                    ctrl.Click()
            else:
                raise Exception("Component '%s' doesn't in the list" %compoName)
            
    def updateComponent(self, compoName, count):
        """ command to update the counter of a component from the components list """
        if count:
            items = self.SelectedItemListView.Items()
            if items:
                target = None
                for item in items:
                    if compoName in item['text']:
                        target = item
                        break
                if target:
                    idx = (items.index(target) - 1) / 2
                    self.SelectedItemListView.Select(idx)
                    time.sleep(2)
                    ctrl =  self.ref[self.Controls['Count']]
                    if ctrl.IsEnabled():
                        ctrl.SetText(count)
                    time.sleep(2)
                    ctrl =  self.ref[self.Controls['Update']]
                    if ctrl.IsEnabled():
                        ctrl.Click()
                else:
                    raise Exception("Component '%s' doesn't in the list" %compoName)
            
            
    def viewLogFile(self):
        "command to load license generator log window"
        ctrl = self.ref[self.Controls['View Log File']]
        ctrl.Click()
        time.sleep(3)
        try:
            w_handle = findwindows.find_windows(title=u'License Generator Log', class_name='#32770')[0]
            self.Log.update(self.app.window_(handle=w_handle))
        except:
            pass


class LicenseGeneratorLog(Window):
    """ class to model the License Generator Log window """
    def __init__(self, parent):
        super(LicenseGeneratorLog, self).__init__(parent)
        self.Controls = {'Log List' : 'ListView',
                         'Close'    : 'Close'}
        self.ListView = None
        
    def update(self, ref):
        """ update the internal control reference """
        super(LicenseGeneratorLog, self).update(ref)
        if self.ref:
            self.ListView = self.ref[self.Controls['Log List']]
        
    def getLastEntry(self):
        """ return the last log entry """
        result = None
        if self.ListView:
            logList = self.ListView.Texts()
            listLen = len(logList)
            if listLen >= 6:
                result = []
                result.append(logList[listLen - 6])
                result.append(logList[listLen - 5])
                result.append(logList[listLen - 4])
                result.append(logList[listLen - 3])
                result.append(logList[listLen - 2])
                result.append(logList[listLen - 1])
        return result
    
        
class ContinuePopup(Popup):
    """ class to model the Continue Popup window """
    def __init__(self, parent):
        super(ContinuePopup, self).__init__(parent)
        self.Controls = {'Yes' : '&Yes',
                         'No'  : '&No'}
    
    def isLoaded(self):
        """ verify if the popup is loaded """
        self.update()
        return super(ContinuePopup, self).isLoaded()
        
    def update(self):
        """ update the internal control reference """
        try:
            w_handle = findwindows.find_windows(title=u'Continue', class_name='#32770')[0]
            window = self.parent.app.window_(handle=w_handle)
            self.ref = window
        except: self.ref = None
        
        
class LicenseGeneratorPopup(Popup):
    """ class to model the small license generator Popup window after click the query button """
    def __init__(self, parent):
        super(LicenseGeneratorPopup, self).__init__(parent)
        self.Controls = {'OK'  : 'OK',
                         'Yes' : '&Yes',
                         'No'  : '&No'}
        
    def isLoaded(self):
        """ verify if the popup is loaded """
        self.update()
        return super(LicenseGeneratorPopup, self).isLoaded()
        
    def update(self):
        """ update the internal control reference """
        try:
            w_handle = findwindows.find_windows(title=u'LicenseGenerator', class_name='#32770')[0]
            window = self.parent.app.window_(handle=w_handle)
            self.ref = window
        except: self.ref = None
        
        
class ErrorPopup(Popup):
    """ class to model the Error Popup window """
    def __init__(self, parent):
        super(ErrorPopup, self).__init__(parent)
        self.Controls = {'OK' : 'OK'}
    
    def isLoaded(self):
        """ verify if the popup is loaded """
        self.update()
        return super(ErrorPopup, self).isLoaded()
        
    def update(self):
        """ update the internal control reference """
        try:
            w_handle = findwindows.find_windows(title=u'ERROR', class_name='#32770')[0]
            window = self.parent.app.window_(handle=w_handle)
            self.ref = window
        except: self.ref = None


class AALGPopup(Popup):
    """ class to model the Exception of Activation of Automatic License Generator 4 Popup """
    def __init__(self, parent):
        super(AALGPopup, self).__init__(parent)
    
    def isLoaded(self):
        """ verify if the popup is loaded """
        self.update()
        return super(AALGPopup, self).isLoaded()
        
    def update(self):
        """ update the internal control reference """
        try:
            w_handle = findwindows.find_windows(title=u'Activation of Automatic License Generator 4', class_name='TFormEasyGo2')[0]
            window = self.parent.app.window_(handle=w_handle)
            self.ref = window
        except: self.ref = None
    
    def Close(self):
        """ close the error popup window """
        if self.ref:
            self.ref.Close()
            time.sleep(5)
            
            
class EmailPopup(Popup):
    """ class to model the Exception of Email warning Popup """
    def __init__(self, parent):
        super(EmailPopup, self).__init__(parent)
    
    def isLoaded(self):
        """ verify if the popup is loaded """
        self.update()
        return super(EmailPopup, self).isLoaded()
        
    def update(self):
        """ update the internal control reference """
        try:
            w_handle = findwindows.find_windows(title=u'Email', class_name='#32770')[0]
            window = self.parent.app.window_(handle=w_handle)
            self.ref = window
        except: self.ref = None
    
    def Close(self):
        """ close the error popup window """
        if self.ref:
            self.ref.Close()
            time.sleep(5)
        

def main():
    LicenseGenerator.changeMode("RMA")
    lg = LicenseGenerator()
    lg.Launch(timeout=10)
    result = lg.getMode()
    print "current mode is %s" %result
    lg.Close()
    
    LicenseGenerator.changeMode("RMA")
    lg = LicenseGenerator()
    lg.Launch(timeout=10)
    result = lg.getMode()
    print "current mode is %s" %result
    lg.Close()
    
    LicenseGenerator.changeMode("Testing")
    lg = LicenseGenerator()
    lg.Launch(timeout=10)
    result = lg.getMode()
    print "current mode is %s" %result
    
    result = lg.isLaunched()
    print "verify if license generator is loaded: %s" %result
    
    if result:
        result = lg.Log.isLoaded()
        print "verify is License generator log window is loaded: %s" %result
        lg.viewLogFile()
        print "click View Log File link"
        result = lg.Log.isLoaded()
        print "verify if license generator log windows is loaded: %s" %result
        print lg.Log.getLastEntry()
        lg.Log.Close()    # close log window
        result = lg.Log.isClosed()
        print "verify if license generator log window is closed: %s" %result
        
        lg.selectProduct('CuCube-M')
        print lg.getAddedComponents()
        lg.selectProduct('enteliBRIDGE')
        print lg.getAddedComponents()
        lg.addComponent('enteliBRIDGE-N2', '10')
        print lg.getAddedComponents()
        lg.selectProduct('enteliWEB-Ent')
        print lg.getAddedComponents()
        lg.addComponent('enteliWEB-Ent-2500IO-AddOn', '5')
        print lg.getAddedComponents()
        lg.selectProduct('enteliWEB-KEL-ExpSub')
        print lg.getAddedComponents()
        
        lg.Close()
        
    

if __name__ == '__main__':
    main()
