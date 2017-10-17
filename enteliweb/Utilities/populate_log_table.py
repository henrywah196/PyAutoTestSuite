# coding: utf-8
################################################################################################
#
# Description :  populate log table to make it over 1 million records
#
################################################################################################
import settings
from libraries.eweb.DataObjects.WebGroup import WebGroupDBObj
import os, time


def populate_log_table(total=1000000):
    
    webgroup = WebGroupDBObj()
    sql_string = """insert into log (Timestamp, LogType, User, Action, Object, Property, OldValue, NewValue, Result, Comment)
                    values(str_to_date('2017-01-05 21:30:09', '%Y-%m-%d %H:%i:%s'), 'ADMIN', '231b1eb6-f579-11e6-92dc-080027f18e75', 
                    'LOGIN', '231b1eb6-f579-11e6-92dc-080027f18e75', 'User', '', '', 
                    'OK', 'faked testing log record');"""
    i = 1
    while i <= total:
        webgroup.cursor.execute(sql_string)
        i = i + 1
        if (i % 10000) == 0:
            webgroup.cnxn.commit()
            time.sleep(1)
            print "%s records added"%i
    webgroup.cnxn.commit()
    del webgroup
        

if __name__ == "__main__":
    populate_log_table(200000)