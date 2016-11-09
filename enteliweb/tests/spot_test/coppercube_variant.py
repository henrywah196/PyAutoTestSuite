'''
Created on Sep 23, 2015

@author: hwang
'''
import time
from libraries.eweb import Utilities
from settings import ArchiverDB


def TableInfo():
    cucubeDBConn = Utilities.DBConnect(ArchiverDB["CubeDBConn_cucube228"])
    cucubeDBConn.mkConnect()

    table_info_list = []
    
    try:
        cucubeDBConn.cursor.execute("select table_name from information_schema.tables where table_schema = 'public' and table_type='BASE TABLE'")
        rows = cucubeDBConn.cursor.fetchall()

        for row in rows:
            table_name = row.table_name
            cucubeDBConn.cursor.execute('select distinct variant from "%s"'%table_name)
            rows = cucubeDBConn.cursor.fetchall()
            variant_list = []
            for row in rows:
                variant_list.append(row.variant)
            table_info = {}
            table_info["table"] = table_name
            table_info["variant"] = variant_list
            table_info_list.append(table_info)
    finally:
        cucubeDBConn.disConnect()
        
    return table_info_list

def getTableInfo(variant_list):
    
    table_info_list = TableInfo()
    for item in table_info_list:
        variant = item["variant"]
        found = True
        for subitem in variant_list:
            if subitem not in variant:
                found = False
        if found:
            print item
            time.sleep(1)
            
            
if __name__ == "__main__":
    getTableInfo((5,))