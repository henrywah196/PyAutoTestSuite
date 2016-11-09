'''
Created on Jan 14, 2015

@author: hwang
'''
from libraries.SLAT.TC_Template_GPI import *
from ddt import ddt, file_data


oldorder = {"Login"              : "quoteuser@deltacontrols.com",
            "Partner"            : "R-004 (Regulvar Inc.)",
            "Product"            : "enteliBRIDGE",
            "PO"                 : "WAH201501231600",
            "Add-Ons"            : ["ModBUS TCP"],
            "Counter_ModBUS_TCP" : "220",
            "Power Supply"       : "110VAC to 12VDC (North America)",
            "Quantity"           : "3",
            "Shipping"           : "Shipping Info 02"
           }

neworder = {"Login"              : "quoteuser@deltacontrols.com",
            "Partner"            : "R-004 (Regulvar Inc.)",
            "Product"            : "CopperCube",
            "PO"                 : "WAH201501231600",
            "Trend Logs"         : "5000 TLs - Extra Large",
            "SQL Connector"      : "Yes",
            "Power Supply"       : "110VAC to 12VDC (North America)",
            "Quantity"           : "3",
            "Shipping"           : "Shipping Info 02"
           }



@ddt
class TC0105(TC_Template_GPI):
    
    def setUp(self):
        super(TC0105, self).setUp()
        print "\nTest: %s" %self.currentTest
        

    def tearDown(self):
        super(TC0105, self).tearDown()
    
    
    @file_data('TC0105.json')
    def test01_Place_Order(self, test_data):
        """ Examine online place order for enteliWEB """
        #order = test_data
        order = test_data
        username = order["Login"]
        password = loginAccount[username]
        success = self.command_Load_OnlineConfigurator(username, password)
        time.sleep(10)
        
        if success:
            result = self.command_OC_Place_Order(order, submit=False)
            time.sleep(2)
            itemNumbers = self.ooconfigurator.ewebConfig.orderReview.getItemNumbers()
            if itemNumbers:
                print itemNumbers
                for item in itemNumbers:
                    counter = self.ooconfigurator.ewebConfig.orderReview.getItemCounter(item)
                    price = self.ooconfigurator.ewebConfig.orderReview.getItemPrice(item)
                    print "%s: %s x %s" %(item, price, counter)
                    
            print self.ooconfigurator.ewebConfig.orderReview.getConfigurationPrice()
            print self.ooconfigurator.ewebConfig.orderReview.getTotalPrice()
            print self.ooconfigurator.ewebConfig.orderReview.getCurrencyType()
            print self.ooconfigurator.ewebConfig.orderReview.isListPrice()
                    
            
        self.command_Close_OnlineConfigurator()
                    
        
if __name__ == "__main__":
    TC0105.execute()
        