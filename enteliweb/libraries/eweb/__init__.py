'''
Description: web elements locator wrapper
Created on Jan 31, 2013
@author: WAH
'''
import os, json


class Locators(object):
    """ class to wrap web element locator """
    def __init__(self):
        self.data = {}
        self.jsonFiles = ["administration.json", "energy_report.json", "bas_report.json", "access_activity_report.json"]
        self.json_File_Location = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)), "locators")
        for item in self.jsonFiles:
            jsonFilePath = os.path.join(self.json_File_Location, item)
            with open(jsonFilePath, "r") as json_file:
                tempData = json.load(json_file)
                self.data.update(tempData)
                json_file.close()
        
            
    def get(self, locatorString=None):
        """ return test Data Object """
        if locatorString:
            return self.data[locatorString]
                    
        else:
            return self.data


if __name__ == "__main__":
    locators = Locators()
    print len(locators.get())