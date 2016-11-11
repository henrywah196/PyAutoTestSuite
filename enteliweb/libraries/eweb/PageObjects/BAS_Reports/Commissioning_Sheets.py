'''
Created on Nov 9, 2016

@author: hwang
'''
from BAS_Report_Generic import BASReportPageObj


class CommissioningSheetsPageObj(BASReportPageObj):
    """ BAS Commissioning Sheet report page object module """
        
    def __repr__(self):
        super(CommissioningSheetsPageObj, self).__repr__()
        
    def __str__(self):
        return "Report: Commissioning Sheets"
