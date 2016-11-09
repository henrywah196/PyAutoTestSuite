#-------------------------------------------------------------------------------
# Name:        TestData.py
# Purpose:     model software licensing test data
#
# Author:      wah
# Created:     18/07/2014
#-------------------------------------------------------------------------------
import json


class TestData(object):
    """ class to model the software licensing test data """
    def __init__(self, jsonFile):
        self.json_File_Location = jsonFile
        json_file = open(self.json_File_Location, "r")
        self.data = json.load(json_file)
        json_file.close()
        
            
    def getData(self, value=None, key="description"):
        """ return test Data Object """
        if value:
            result = None
            for item in self.data:
                target = None
                current = item[key]    # it could be either string or a list of string
                if type(value) == list:
                    if type(current) == list:
                        found = False
                        for valueItem in value:
                            if valueItem in current:
                                found = True
                            else:
                                found = False
                        if found:
                            target = item
                    else:
                        if current in value:
                            target = item
                else:
                    if type(current) == list:
                        if value in current:
                            target = item
                    else:
                        if value == current:
                            target = item
                if target:
                    if not result:
                        result = []
                    result.append(target)
            return result
                    
        else:
            return self.data
        
    def saveData(self):
        """ save any changes to test data """
        file_location = self.json_File_Location.replace(".json", "_Update.json")
        json_file = open(file_location, "w+")
        json_file.write(json.dumps(self.data, indent=4, separators=(', ', ' : ')))
        json_file.close()

