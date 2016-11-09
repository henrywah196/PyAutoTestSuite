'''
search and return which trends have specified data type stored in coppercube
Created on May 11, 2015

@author: hwang
'''

import psycopg2
import sys
import pprint

HOSTNAME = "192.168.4.228"
VARTYPE = 3

def main():
    conn_string = "host='%s' dbname='artrends' user='postgres'"%HOSTNAME
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    
    # obtain all the table name
    cursor.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
    records = cursor.fetchall()
    #pprint.pprint(records)
    
    i = 0
    for item in records:
        table_name = item[0]
        cursor.execute('select distinct variant from "%s"'%table_name)
        variants = cursor.fetchall()
        result = []
        if VARTYPE:
            isFound = False
            for subItem in variants:
                if VARTYPE in subItem:
                    isFound = True
            if isFound:
                result.append(item)
                result.extend(variants)
                print result
                i = i + 1
                
        else:
            result.append(item)
            result.extend(variants)
            print result
            i = i + 1
    print "total %s tables"%i
        
    
    cursor.close()
    conn.close()
    del cursor
    del conn
    


if __name__ == "__main__":
    main()
