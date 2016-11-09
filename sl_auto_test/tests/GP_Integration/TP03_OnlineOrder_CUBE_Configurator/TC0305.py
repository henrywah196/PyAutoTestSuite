'''
Created on Jan 14, 2015

@author: hwang
'''
from libraries.SLAT.TC_Template_GPI import *
from ddt import ddt, file_data


@ddt
class TC0305(TC_Template_GPI):
    
    def setUp(self):
        super(TC0305, self).setUp()
        print "\nTest: %s" %self.currentTest
        

    def tearDown(self):
        super(TC0305, self).tearDown()
    
    
    @file_data('TC0305.json')
    def test01_Place_Order(self, test_data):
        """ Examine online place order for enteliBRIDGE """
        #order = test_data
        order = test_data
        username = order["Login"]
        password = loginAccount[username]
        success = self.command_Load_OnlineConfigurator(username, password)
        self.verify_IsTrue(success, "Load Online Order Config page")
        time.sleep(10)
        
        success = self.command_OC_Place_Order(order)
        print "Order %s has been submitted: %s" %(order["PO"], success)
        self.verify_IsTrue(success, "Verify Place order: %s" %order["PO"]) 
            
        self.command_Close_OnlineConfigurator()
                    
        
if __name__ == "__main__":
    TC0305.execute()
        