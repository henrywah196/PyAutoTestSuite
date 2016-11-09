#-------------------------------------------------------------------------------
# Name:        LicenseManager.py
# Purpose:     gui object to model windows license manger application
#
# Author:      wah
# Created:     09/04/2014
#-------------------------------------------------------------------------------
import os, time
from pywinauto import application, findwindows


class LoadingPopup(object):
    """ class to model the small loading popup window in license manager """
    def __init__(self, parent):
        self.parent = parent    # reference to License Manager object
        self.ref = None         # reference itself
        
    def update(self, ref=None):
        """ update the internal control reference """
        if ref:
            self.ref = ref
        else:
            try:
                w_handle = findwindows.find_windows(title=u'', class_name='#32770')[0]
                window = self.parent.app.window_(handle=w_handle)
                self.ref = window 
            except: self.ref = None
            
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
        

class ErrorPopup(LoadingPopup):
    """ class to model the ERROR popup window in license manager """
        
    def update(self, ref=None):
        """ update the internal control reference """
        if ref:
            self.ref = ref
        else:
            try:
                w_handle = findwindows.find_windows(title=u'ERROR', class_name='#32770')[0]
                window = self.parent.app.window_(handle=w_handle)
                self.ref = window 
            except: self.ref = None
            
    def isLoaded(self):
        """ verify if the error popup is loaded """
        self.update()
        return super(ErrorPopup, self).isLoaded()
            
    def Close(self):
        """ close the error popup window """
        if self.ref:
            ctrl = self.ref['OK']
            if ctrl.IsEnabled():
                ctrl.Click()
                time.sleep(5)
                
    def getErrorInfo(self):
        """ get the error message in error popup window """
        if self.ref:
            ctrl = self.ref['Static2']
            return (ctrl.Texts())[0] 
        else:
            return None


class Window(object):
    """ class to model main or sub window which belongs to License Manager """
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
            time.sleep(3)
            if self.isClosed():
                self.ref = None
            
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
        
    def select(self, controlName, itemName):
        """ select a item from the combobox control in window """
        if self.ref:
            ctrl = self.ref[self.Controls[controlName]]
            if ctrl:
                try: ctrl.Select(itemName)
                except Exception, e:
                    print "select(controlName='%s', itemName='%s') failed: %s" %(controlName, itemName, e)  


class LicenseManager(Window):
    """ class to model Delta License Manager (windows version) """
    def __init__(self, parent=None):
        super(LicenseManager, self).__init__(parent)
        self.Controls = {'ListView' : 'ListView',
                         'Activate' : 'Activate',
                         'Update'   : 'Update',
                         'Enable'   : 'Enable',
                         'Disable'  : 'Disable',
                         'View'     : 'View',
                         'Transfer' : 'Transfer',
                         'Add New'  : 'Add New',
                         'Remove'   : 'Remove',
                         'Exit'     : 'Exit',
                         'Start'    : 'Start',
                         'Stop'     : 'Stop'}
        self.app = application.Application()                                 # reference of application itself
        self.listView = None                                                 # reference of the product license list in main window
        self.LoadingPopup = LoadingPopup(self)                               # the small loading popup window
        self.ErrorPopup = ErrorPopup(self)                                   # the error popup window
        self.LicenseViewer = LicenseViewer(self)                                 # the License Viewer window
        self.TransferLicense = TransferLicense(self)                             # the Transfer License window 
        self.AddProduct = AddProduct(self)                                       # the Add Product window 
        self.SerialNumberAndActivationType = SerialNumberAndActivationType(self) # the Serial Number and Activation Type window
        self.DownloadLicense = DownloadLicense(self)                             # the Download License window
        self.LicenseActivation = LicenseActivation(self)                         # the License Activation window
        self.VmCallHome = VMCallHome(self)                                       # the Test Virtual Machine call home window
        
        self.LicensesFolder = "C:\ProgramData\Delta Controls\Licenses"    # location of license files

    def Launch(self, timeout, startApp=True):
        """ launch license manager """
        if startApp:
            self.app.start_(r"C:\Program Files (x86)\Delta Controls\License Management\LicenseManager.exe")
            time.sleep(15)
        
        self.LoadingPopup.update()
        while self.LoadingPopup.isLoaded():
            print "Debug: loading license..."
            time.sleep(15)
            if self.ErrorPopup.isLoaded():
                print "Debug Closing Error Popup..."
                self.ErrorPopup.Close()
            timeout = timeout - 15
            if timeout <= 0:
                if self.ErrorPopup.isLoaded():
                    self.ErrorPopup.Close()
                    self.Launch(timeout=60, startApp=False)
                raise Exception("License Manager: loading licenses timeout...")
        
        w_handle = findwindows.find_windows(title=u'Delta Controls License Manager', class_name='#32770')[0]
        self.update(self.app.window_(handle=w_handle))
        self.listView =self.ref[self.Controls['ListView']]
        
    def isLaunched(self):
        """ verify is the license manager is loaded """
        #return self.Main.Exist()
        return self.isLoaded()

    
    def Close(self):
        """ close license manager main window """
        super(LicenseManager, self).Close()
        time.sleep(3)
        if self.isClosed():
            self.app = None
    
    def Reset(self):
        """ reset license manager if exception occur """
        try:
            taskListObj = os.popen("tasklist")
            taskListStr = taskListObj.read()
            taskListObj.close()
            del taskListObj
            result = "LicenseManager.exe" in taskListStr
            if result:
                # kill the licensemanager process from windows
                os.system("taskkill /im LicenseManager.exe /f")
        except:
            pass
        time.sleep(5)
        try:
            # restart license server service
            import win32serviceutil
            serviceName = "DeltaLicense"
            win32serviceutil.RestartService(serviceName)
        except:
            pass
        self.ref = None
        self.app = None
            
        
        
    def getLicenseServerStatus(self):
        """ return the status of license server """
        ctrl = self.ref['Running']
        if ctrl.Exists():
            if ctrl.IsVisible():
                return 'Running'
            else:
                return None
        else:
            ctrl = self.ref['Stopped']
            if ctrl.Exists():
                if ctrl.IsVisible():
                    return 'Stopped'
                else:
                    return None
            else:
                return None
        
    def startLicenseServer(self):
        """ command to start license server by click the start button """
        ctrl = self.ref[self.Controls['Start']]
        if ctrl:
            ctrl.Click()
    
    def stopLicenseServer(self):
        """ command to stop license server by click the stop button """
        ctrl = self.ref[self.Controls['Stop']]
        if ctrl:
            ctrl.Click()

    def click(self, buttonName):
        """ click the button """
        ctrl = self.ref[self.Controls[buttonName]]
        if ctrl.IsEnabled():
            ctrl.Click()
            time.sleep(15)
            if buttonName == 'View': self.LicenseViewer.update()
            elif buttonName == 'Transfer': self.TransferLicense.update()
            elif buttonName == 'Add New': self.AddProduct.update()

    def getTotalLicenses(self):
        """ return total number of registered licenses in the list """
        return self.listView.ItemCount()

    def isLicenseListed(self, licenseNumber):
        """ verify if the specified licenseNumber in the list """
        items = self.listView.Items()
        if items:
            for item in items:
                if licenseNumber in item['text']:
                    return True
            return False
        else:
            return False

    def getLicenseInfo(self, licenseNumber):
        """ get the brief license information for the specified license number from the list """
        items = self.listView.Items()
        if items:
            target = None
            for item in items:
                if licenseNumber in item['text']:
                    target = item
                    break
            if target:
                info = {}
                idx = items.index(target)
                info['Product'] = items[idx]['text']
                idx = idx + 1
                info['Activation'] = items[idx]['text']
                idx = idx + 1
                info['Subscription'] = items[idx]['text']
                idx = idx + 1
                info['Enabled'] = items[idx]['text']
                return info
            else:
                return None
        else:
            return None

    def select(self, licenseNumber):
        """ select the specified license in the list """
        items = self.listView.Items()
        if items:
            target = None
            for item in items:
                if licenseNumber in item['text']:
                    target = item
                    break
            if target:
                idx = (items.index(target)) / 4
                self.listView.Select(idx)
            else:
                raise Exception("license number: %s doesn't in the list" %licenseNumber)
            
    def getLicFilesList(self):
        """ return a list of existing lic files """
        from os import listdir
        from os.path import isfile, join
        licFiles = [f for f in listdir(self.LicensesFolder) if isfile(join(self.LicensesFolder, f))]
        return licFiles
    
    def removeLicFile(self, fileName):
        """ delect a lic file from the specified lic folder """
        licFileFullName = os.path.join(self.LicensesFolder, fileName)
        os.remove(licFileFullName)


class VMCallHome(Window):
    """ class to model the Test Virtual Machine Call Home window in license manager """
    def __init__(self, parent):
        super(VMCallHome, self).__init__(parent)
        self.Controls = {'Test Call Home'   : 'Button',
                         'Close' : 'Close'}
        
    def isLoaded(self):
        """ verify if the window is loaded """
        self.update()
        if super(VMCallHome, self).isLoaded():
            ctrl = self.ref['Static']
            if (ctrl.Texts())[0] == 'Test Virtual Machine Call Home':
                return True
            else:
                return False
        else:
            return False


class LicenseActivation(Window):
    """ class to model the License Activation window in license manager """
    def __init__(self, parent):
        super(LicenseActivation, self).__init__(parent)
        self.Controls = {'Serial Key'    : 'Edit1',
                        'Company'       : 'Edit2',
                        'Site Name'     : 'Edit3',
                        'Salutation'    : 'Edit4',
                        'First Name'    : 'Edit5',
                        'Last Name'     : 'Edit6',
                        'Country'       : 'ComboBox',
                        'Email Address' : 'Edit7',
                        'Next'          : 'Next',
                        'Cancel'        : 'Cancel'}
        
    def isLoaded(self):
        """ verify if the License Activation window is loaded """
        self.update()
        if super(LicenseActivation, self).isLoaded():
            ctrl = self.ref['Static2']
            if (ctrl.Texts())[0] == 'License Activation':
                return True
            else:
                return False
        else:
            return False
        
    def click(self, buttonName):
        """ click the button in License Activation window """
        super(LicenseActivation, self).click(buttonName)
        if buttonName == 'Next':
            timeout = 60
            self.parent.LoadingPopup.update()
            while self.parent.LoadingPopup.isLoaded():
                print "Debug: Activating license..."
                time.sleep(15)
                timeout = timeout - 15
                if timeout <= 0:
                    raise Exception("License Manager: Activating licenses timeout...")
            self.parent.VmCallHome.update()


class DownloadLicense(Window):
    """ class to model the Download License window in license manager """
    def __init__(self, parent):
        super(DownloadLicense, self).__init__(parent)
        self.Controls = {'Next'   : 'Next',
                         'Cancel' : 'Cancel'}
        
    def isLoaded(self):
        """ verify if the Download License window is loaded """
        if super(DownloadLicense, self).isLoaded():
            ctrl = self.ref['Static4']
            if (ctrl.Texts())[0] == 'Download License':
                return True
            else:
                return False
        else:
            return False
        
    def click(self, buttonName):
        """ click the button in Download License window """
        super(DownloadLicense, self).click(buttonName)
        if buttonName == 'Next':
            timeout = 60
            self.parent.LoadingPopup.update()
            while self.parent.LoadingPopup.isLoaded():
                print "Debug: Downloading license..."
                time.sleep(15)
                timeout = timeout - 15
                if timeout <= 0:
                    raise Exception("License Manager: Downloading licenses timeout...")
            self.parent.LicenseActivation.update()


class SerialNumberAndActivationType(Window):
    """ class to model the Serial Number and Activation Type window in license manager """
    def __init__(self, parent):
        super(SerialNumberAndActivationType, self).__init__(parent)
        self.Controls = {'Serial Number' : 'Edit',
                         'Next'          : 'Next',
                         'Cancel'        : 'Cancel'}
        
    def isLoaded(self):
        """ verify if the Add Product window is loaded """
        if super(SerialNumberAndActivationType, self).isLoaded():
            ctrl = self.ref['Static2']
            if (ctrl.Texts())[0] == 'Serial Number and Activation Type':
                return True
            else:
                return False
        else:
            return False
        
    def click(self, buttonName):
        """ click the button in Serial Number and Activation Type window """
        super(SerialNumberAndActivationType, self).click(buttonName)
        if buttonName == 'Next':
            time.sleep(5)
            self.parent.DownloadLicense.update()


class AddProduct(Window):
    """ class to model the Add Product window in license manager """
    def __init__(self, parent):
        super(AddProduct, self).__init__(parent)
        self.Controls = {'Select Product' : 'ComboBox',
                         'OK'             : 'OK',
                         'Cancel'         : 'Cancel'}
        if self.ref:
            self.comboBox = self.ref[self.Controls['Select Product']]
        else:
            self.comboBox = None
        
    def isLoaded(self):
        """ verify if the Add Product window is loaded """
        if super(AddProduct, self).isLoaded():
            ctrl = self.ref['Static']
            if (ctrl.Texts())[0] == 'Add Product':
                return True
            else:
                return False
        else:
            return False
        
    def update(self, ref=None):
        """ update the internal control reference """
        super(AddProduct, self).update(ref)
        if self.ref:
            self.comboBox = self.ref['ComboBox']
        else:
            self.comboBox = None
        
    def select(self, productName):
        """ select a product from the combo box in Add Product window """
        if self.comboBox:
            try: self.comboBox.Select(productName)
            except Exception, e:
                print "LicenseManager.AddProduct.select(productName='%s') failed: %s" %(productName, e)
            
    def isSelected(self, productName):
        """ verify if the specified product is selected in combo box in Add Product window """
        if self.comboBox:
            current = (self.comboBox.Texts())[0]
            return current == productName
        else:
            return False
        
    def click(self, buttonName):
        """ click the button in Add Product window """
        super(AddProduct, self).click(buttonName)
        if buttonName == 'OK':
            time.sleep(15)
            self.parent.SerialNumberAndActivationType.update()


class TransferLicense(Window):
    """ class to model the Transfer License window in license manager """
    def __init__(self, parent):
        super(TransferLicense, self).__init__(parent)
        self.Controls = {'Yes' : 'Yes',
                         'No'  : 'No'}
        
    def isLoaded(self):
        """ verify if the Transfer License window is loaded """
        self.update()
        if super(TransferLicense, self).isLoaded():
            ctrl = self.ref['Static']
            if (ctrl.Texts())[0] == 'Transfer License':
                return True
            else:
                return False
        else:
            return False
        
    def click(self, buttonName):
        """ click the button in Transfer license window """
        super(TransferLicense, self).click(buttonName)
        if buttonName == 'Yes':
            timeout = 60
            while not self.isClosed():
                time.sleep(15)
                timeout = timeout - 15
                if timeout <=0:
                    raise Exception("License Manager: transferring license timeout...")


class LicenseViewer(Window):
    """ class to model the license viewer window in license manager """
    def __init__(self, parent):
        super(LicenseViewer, self).__init__(parent)
        self.Controls = {'TreeView' : 'TreeView',
                         'Close'    : 'Close'}
        if self.ref:
            self.treeView = self.ref[self.Controls['TreeView']]
        else:
            self.treeView = None
            
    def update(self, ref=None):
        """ update the internal control reference """
        super(LicenseViewer, self).update(ref)
        if self.ref:
            self.treeView = self.ref['TreeView']
        else:
            self.treeView = None
            
    def isLoaded(self):
        """ verify if the license viewer window is loaded """
        if super(LicenseViewer, self).isLoaded():
            ctrl = self.ref['Static']
            if (ctrl.Texts())[0] == 'License Viewer':
                return True
            else:
                return False
        else:
            return False
            
    def getLicenseInfo(self):
        """ get license information from license viewer window
            return a dictionary of license information """
        if self.treeView:
            node = self.treeView.Root()    # get root node from tree view
            result = None
            while node:
                nodeName = node.Text()
                if 'Modules' in nodeName:    # the Modules node
                    childNodes = node.Children()
                    if childNodes:
                        moduleList = []
                        for childNode in childNodes:
                            moduleList.append(childNode.Text())
                        result['Modules'] = moduleList
                    else:
                        result['Modules'] = None
                            
                elif 'Installation Codes' in nodeName:    # the Installation Codes node
                    childNodes = node.Children()
                    if childNodes:
                        codeList = {}
                        for childNode in childNodes:
                            childNodeName = childNode.Text()
                            childList = childNodeName.split(':')
                            codeList[(childList[0]).strip()] = (childList[1]).strip()
                        result['Installation Codes'] = codeList
                    else:
                        result['Installation Codes'] = None
                elif ':' in nodeName:
                    nodeList = nodeName.split(':')
                    if not result:
                        result = {} 
                    result[(nodeList[0]).strip()] = (nodeList[1]).strip()
                node = node.Next()    # get next node from tree view
            return result      
        else: 
            return None


def main():
    lm = LicenseManager()
    lm.Launch(timeout=120)

    result = lm.ErrorPopup.isLoaded()
    print " verify if the error window popup: %s" %result
    
    if result:
        lm.ErrorPopup.Close()
        print "close error popup"

    result = lm.isControlEnabled('Activate')
    print "Is button 'Activate' enabled: %s" %result

    result = lm.isControlEnabled('Add New')
    print "Is button 'Add New' enabled: %s" %result

    result = lm.getTotalLicenses()
    print "Total license in the list: %s" %result

    result = lm.isLicenseListed('8K8Vf-65dF6-QzGaM-4WFEa-xb5MO-0p5zt')
    print "Is license 8K8Vf-65dF6-QzGaM-4WFEa-xb5MO-0p5zt in the list: %s" %result

    result = lm.getLicenseInfo('8K8Vf-65dF6-QzGaM-4WFEa-xb5MO-0p5zt')
    print "License info for 8K8Vf-65dF6-QzGaM-4WFEa-xb5MO-0p5zt:\n%s" %result
    
    lm.select('8K8Vf-65dF6-QzGaM-4WFEa-xb5MO-0p5zt')
    print "select 8K8Vf-65dF6-QzGaM-4WFEa-xb5MO-0p5zt in the list"
    
    result = lm.isControlEnabled('Enable')
    print "verify if the enable button is enabled: %s" %result
    
    if result:
        lm.click('Enable')
        print "click the enable button"
        time.sleep(5)
        result = lm.ErrorPopup.isLoaded()
        print "verify if the error window is popup: %s" %result
        if result:
            result = lm.ErrorPopup.getErrorInfo()
            print "error message: %s" %result
            lm.ErrorPopup.Close()
            time.sleep(5)
            result = lm.ErrorPopup.isClosed()
            print "verify error window is closed: %s" %result    
    

    result = lm.isLicenseListed('BE8Vt-65dF6-QzGah-4WFEa-1b5MO-0r5zh')
    print "Is license BE8Vt-65dF6-QzGah-4WFEa-1b5MO-0r5zh in the list: %s" %result

    result = lm.getLicenseInfo('BE8Vt-65dF6-QzGah-4WFEa-1b5MO-0r5zh')
    print "License info for BE8Vt-65dF6-QzGah-4WFEa-1b5MO-0r5zh:\n%s" %result

    result = lm.isControlEnabled('View')
    print "Is Button 'View' enabled: %s" %result

    lm.select('Bq8VM-65dF6-QzGaV-4WFEa-xb5MO-0j5zf')
    print "select Bq8VM-65dF6-QzGaV-4WFEa-xb5MO-0j5zf in the list"

    result = lm.isControlEnabled('View')
    print "Is button 'View' enabled: %s" %result

    if result:
        lm.click('View')
        print "click 'View' button"

    result = lm.LicenseViewer.isLoaded()
    print "Is License Viewer window loaded: %s" %result
    
    result = lm.LicenseViewer.getLicenseInfo()
    print "get license info from license viewer:\n%s" %result

    lm.LicenseViewer.Close()
    time.sleep(5)
    
    result = lm.getLicenseServerStatus()
    print "License Server Status: %s" %result
   
    ''' 
    if result == "Running":
        lm.stopLicenseServer()
        time.sleep(10)
        
    result = lm.getLicenseServerStatus()
    print result
    
    if result == "Stopped":
        lm.startLicenseServer()
        time.sleep(20)
    
    result = lm.getLicenseServerStatus()
    print result
    '''
    
    result = lm.isControlEnabled('Transfer')
    print "Is Button 'Transfer' enabled: %s" %result
    
    lm.click('Transfer')
    time.sleep(5)
    print "click button 'Transfer'"
    
    result = lm.TransferLicense.isLoaded()
    print "Is Transfer License window loaded: %s" %result
    
    lm.TransferLicense.click('No')
    print "click button 'No' in Transfer License window"
    
    result = lm.TransferLicense.isClosed()
    print "Is Transfer License window closed: %s" %result
    
    lm.select('BE8Vt-65dF6-QzGah-4WFEa-1b5MO-0r5zh')
    print "select BE8Vt-65dF6-QzGah-4WFEa-1b5MO-0r5zh in the list"
    result = lm.isControlEnabled('Transfer')
    print "Is Button 'Transfer' enabled: %s" %result
    lm.click('Transfer')
    time.sleep(5)
    print "click button 'Transfer'"
    result = lm.TransferLicense.isLoaded()
    print "Is Transfer License window loaded: %s" %result
    lm.TransferLicense.click('Yes')
    print "click button 'Yes' in Transfer License window"
    result = lm.isLicenseListed('BE8Vt-65dF6-QzGah-4WFEa-1b5MO-0r5zh')
    print "Is license BE8Vt-65dF6-QzGah-4WFEa-1b5MO-0r5zh in the list: %s" %result
    
    
    result = lm.isControlEnabled('Add New')
    print "Is Button 'Add New' enabled: %s" %result
    
    lm.click('Add New')
    print "click button 'Add New'"
    
    result = lm.AddProduct.isLoaded()
    print "Is Add Product window loaded: %s" %result
    
    lm.AddProduct.select('orcaView')
    print "select 'orcaView' from combobox in Add Product window"
    
    result = lm.AddProduct.isSelected('orcaView')
    print "is 'orcaView' selected in combobox in Add Product window: %s" %result
    
    lm.AddProduct.select('enteliWEB')
    print "select 'enteliWEB' from combobox in Add Product window"
    
    result = lm.AddProduct.isSelected('enteliWEB')
    print "is 'enteliWEB' selected in combobox in Add Product window: %s" %result
    
    lm.AddProduct.select('Earthright Energy Dashboard')
    print "select 'Earthright Energy Dashboard' from combobox in Add Product window"
    
    lm.AddProduct.click('OK')
    print "click OK button"
    
    result = lm.AddProduct.isClosed()
    print "verify if Add Product windows is closed: %s" %result
    
    result = lm.SerialNumberAndActivationType.isLoaded()
    print "verify if Serial Number window is loaded: %s" %result
    
    result = lm.SerialNumberAndActivationType.isControlEnabled('Next')
    print "verify if the Next button is enabled: %s" %result
    
    lm.SerialNumberAndActivationType.input('Serial Number', 'BE8Vt-65dF6-QzGah-4WFEa-1b5MO-0r5zh')
    print "input serial number: BE8Vt-65dF6-QzGah-4WFEa-1b5MO-0r5zh"
    
    result = lm.SerialNumberAndActivationType.isControlEnabled('Next')
    print "verify if the Next button is enabled: %s" %result
    
    lm.SerialNumberAndActivationType.click('Next')
    print "click Next button on Serial Number and Activation window"
    
    result = lm.SerialNumberAndActivationType.isClosed()
    print "verify if the serial number and activation type window is closed: %s" %result
    
    result = lm.DownloadLicense.isLoaded()
    print "verify if the download license window is loaded: %s" %result
    
    lm.DownloadLicense.click('Next')
    print "click Next button on Download License window"
    
    result = lm.DownloadLicense.isClosed()
    print "verify if download license windows is closed: %s" %result
    
    result = lm.LicenseActivation.isLoaded()
    print "verify if license activation window is loaded: %s" %result
    
    result = lm.LicenseActivation.isControlEnabled('Serial Key')
    print "verify if the serial key edit box is enabled: %s" %result
    
    result = lm.LicenseActivation.getValue('Serial Key')
    print "value in serial key edit box: %s" %result
    
    result = lm.LicenseActivation.isControlEnabled('Company')
    print "verify if the company edit box is enabled: %s" %result
    
    result = lm.LicenseActivation.getValue('Company')
    print "value in company edit box: %s" %result
    
    lm.LicenseActivation.input('Company', '')
    print "clear company edit box"
    
    result = lm.LicenseActivation.isControlEnabled('Next')
    print "verify if Next button is enabled: %s" %result
    
    lm.LicenseActivation.input('Company', 'ACME Testing Ltd.')
    print "input 'ACME Testing Ltd.' in company edit box"
    
    result = lm.LicenseActivation.getValue('Company')
    print "value in company edit box: %s" %result
    
    result = lm.LicenseActivation.isControlEnabled('Next')
    print "verify if Next button is enabled: %s" %result
    
    lm.LicenseActivation.click('Next')
    print "click Next button in License Activation window"
    
    result = lm.LicenseActivation.isClosed()
    print "verify if the License activation windows is closed: %s" %result
    
    result = lm.isLicenseListed('BE8Vt-65dF6-QzGah-4WFEa-1b5MO-0r5zh')
    print "Is license BE8Vt-65dF6-QzGah-4WFEa-1b5MO-0r5zh in the list: %s" %result
    
    
    
    lm.click('Exit')
    time.sleep(3)
    print "click button 'Exist'"
    
    result = lm.isClosed()
    print "Is License Manager closed: %s" %result
    

if __name__ == '__main__':
    #main()
    lm = LicenseManager()
    lm.Launch(timeout=10)
    lm.Close()
    if not lm.isClosed():
        lm.Reset()
    
