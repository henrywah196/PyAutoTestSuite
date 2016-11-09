#-------------------------------------------------------------------------------
# Test Case:     Regression for SL-855 (Regression_SL855.py)
# Purpose:       Regression for Memory leak in License Server - port temporary 
#                fix for 2.1 into 2.0
#
# Test description:
#                run this script, each test round it will return and display 
#                the memory usage of DeltaLicense service. during script running
#                try kill the LicenseServer.exe process and make sure it will 
#                going back automatically. verify when the memory usage is reach
#                around 200MB, the service will auto restart.
#                 
#                this test need WMI and Delta SL test module to be preinstalled.  
#                 
#
# Author:        Henry Wang
# Created:       Mar. 04, 2015
#-------------------------------------------------------------------------------
import time
import sltest
import wmi


def TestRound(totalRounds=200, privateWorkingSet=False):
    
    print "Before start: memory usage %s bytes"%getMemoryInfo(privateWorkingSet=True)
    
    i = 0
    while i < totalRounds:
        try:
            sl = sltest.sl(sltest.SL_CLIENT_WEBSERVER_V2)
            time.sleep(2)
            trial = sl.auxopentrial()
            time.sleep(2)
            sl.auxmodulecreate(trial, sltest.SL_MODULE_WEB_POINTS, sltest.SL_MODULE_TYPE_COUNTER, 50000)
            time.sleep(2)
            sl.auxmodulecreate(trial, sltest.SL_MODULE_ENTELIVIZ, sltest.SL_MODULE_TYPE_BOOLEAN, 1)
            time.sleep(2)
            sl.auxmodulecreate(trial, sltest.SL_MODULE_WEB_APPS, sltest.SL_MODULE_TYPE_BOOLEAN, 1)
            time.sleep(5)
            sl.auxmoduledelete(trial, sltest.SL_MODULE_WEB_POINTS)
            time.sleep(2)
            sl.auxmoduledelete(trial, sltest.SL_MODULE_ENTELIVIZ)
            time.sleep(2)
            sl.auxmoduledelete(trial, sltest.SL_MODULE_WEB_APPS)
            
            if privateWorkingSet:
                print "test round %s: memory usage %s bytes"%(i, getMemoryInfo(privateWorkingSet=True))
            else:
                print "test round %s: memory usage %s bytes"%(i, getMemoryInfo())
            
            sl.auxclose(trial)
            time.sleep(2)
            del sl
            time.sleep(2)
            
        except Exception, e:
            print "test round %s: %s"%(i, str(e))
            try: 
                sl.auxclose(trial) 
            except: pass
            del sl
            time.sleep(2)
        i = i + 1
        
    time.sleep(60)
    
    print "After finish: memory usage %s bytes"%getMemoryInfo(privateWorkingSet=True)

def getMemoryInfo(privateWorkingSet=False):
    ''' return the memory usage info of DeltaLicense service '''
    result = None
    c = wmi.WMI()
    if privateWorkingSet:
        targetProcess = (c.Win32_PerfRawData_PerfProc_Process(Name="LicenseServer"))[0]
        result = targetProcess.WorkingSetPrivate
        del targetProcess
        del c
    else:
        targetService = (c.Win32_Service(Name="DeltaLicense"))[0]
        targetProcess = (c.Win32_Process(ProcessId=targetService.ProcessId))[0]
        result = targetProcess.WorkingSetSize
        del targetProcess
        del targetService
        del c
    return result
    

if __name__ == "__main__":
    TestRound(privateWorkingSet=True)


