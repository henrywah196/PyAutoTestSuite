'''
Created on Jan 28, 2016

@author: hwang
'''
import time, datetime
import settings
from libraries.eweb.DataObjects.WebGroup import WebGroupDBObj
from libraries.PyAutoTestCase import *


class CrawlerTest(TestCaseTemplate):
    
    def setUp(self):
        super(CrawlerTest, self).setUp()
        self.webgroup = WebGroupDBObj()
        
        # define test parameters
        self.limitation = 12      # limit execution time, default 5 hours
        self.interval   = 60      # interval of check the status, default 60 seconds
        self.baseline   = 5    # baseline information for how long to finish crawler by hours
        
    def tearDown(self):
        super(CrawlerTest, self).tearDown()
        del self.webgroup
    
    def test01(self):
        self._testMethodDoc = "crawler speed test using QA test network"
        
        myDBConn = self.webgroup
        
        cursor = myDBConn.cursor.execute("select count(*) as total from device")    
        row = cursor.fetchone()
        totalDevices = row.total
        
        cursor = myDBConn.cursor.execute("select count(*) as total from ref")    
        row = cursor.fetchone()
        totalReferences = row.total
        
        # update test method doc string
        self._testMethodDoc = self._testMethodDoc + "(%s devices, %s object references)"%(totalDevices, totalReferences)
        print self._testMethodDoc
        
        # clear cachetime for all device
        cursor = myDBConn.cursor.execute("update device set Cachetime = NULL")
        cursor.commit()
        print "reset devices cache time to NULL"
        
        startTime = datetime.datetime.now()
        
        isFinished = False
        limitation = self.limitation * 3600 / self.interval
        total = None
        while not isFinished:
            time.sleep(self.interval)
            limitation = limitation - 1
            myDBConn.cursor.commit()
            cursor = myDBConn.cursor.execute("select count(*) as total from device where Cachetime is NULL")
            row = cursor.fetchone()
            total = row.total
            print "crawlering, current: %s (expected: 0)"%total
            if (total == 0) or (limitation == 0):
                isFinished = True
        
        if total == 0:
            finishTime = datetime.datetime.now()
            diff = (finishTime - startTime).total_seconds()
            diffInHours = diff / 3600
            if (self.baseline is not None) and ((diff - self.baseline * 3600) > 0):
                result = (diff - self.baseline * 3600) / (self.baseline * 3600)
                if result > 0.5:
                    self.fail("crawler was finish using around %s hours which is 50% large than baseline (%s hours)"%(diffInHours, self.baseline))
                else:
                    print "crawler was finish using around %s hours"%diffInHours
            else:
                print "crawler was finish using around %s hours"%diffInHours
        else:
            self.fail("crawler was not finish within %s hours"%self.limitation)
            
            

if __name__ == "__main__":
    unittest.main()
            
                
