#-------------------------------------------------------------------------------
# Test Case:     eweb14019.py
# Purpose:       Regression for EWEB-14019: Should restrict using GET on 
#                state-change requests
#
# Author:        Henry Wang
# Created:       Jul 03, 2015
#-------------------------------------------------------------------------------
try:
    import unittest, time, os
    import xlrd
    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from ddt import ddt, data
except ImportError, e:
    raise ImportError(str(e) + ". Install this module before run the script.")
import settings
from libraries.eweb import Macros
from libraries.PyAutoTestCase import *    # import test case template
from libraries.eweb.PageObjects.Accordion import AccordionPageObj


# Global settings
DATA_FILE_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), "eweb14019.xls"))    # filename containing testing data
KeyWords = "CSRF : You don`t have permission to do this operation"
Base_URL = "http://%s/enteliweb"%settings.HOST
WebGroupDBConn = {"driver"   : "MySQLdb Connector",
                  "server"   : settings.HOST,
                  "port"     : "49250",
                  "database" : "webgroup",
                  "user"     : "tester",
                  "password" : "demo"}


def getTestingData(fileName):
    """
    return a list of rows in te format of [sheetname, column01, column02, ...]
    """
    
    class TestData():
        def __init__(self):
            self.content = None
    
    rows = []
    book = xlrd.open_workbook(fileName)
    sheetNames = book.sheet_names()
    for item in sheetNames:
        sheet = book.sheet_by_name(item)
        for row_index in range(1, sheet.nrows):
            myTestData = TestData()
            myTestData.content = [item]
            myTestData.content.extend(list(sheet.row_values(row_index, 0, sheet.ncols)))
            rows.append(myTestData)
    return rows


@ddt
class TestCase(TestCaseTemplate):
    @classmethod
    def setUpClass(cls):
        super(TestCase, cls).setUpClass()
        cls.Browser = settings.BROWSER
        cls.Host = settings.HOST
        cls.Username = settings.USERNAME
        cls.Password = settings.PASSWORD

        # define a place holder for test data
        cls.testData = None

        # setup webgroup db connection
        try: import MySQLdb
        except ImportError as e:
            raise Exception("Exception: %s. Please install MySQLdb module first." %e)

        try:
            cls.connection = MySQLdb.connect(host=WebGroupDBConn["server"], port=int(WebGroupDBConn["port"]), user=WebGroupDBConn["user"], passwd=WebGroupDBConn["password"], db=WebGroupDBConn["database"])
        except Exception as e:
            raise Exception("Exception: %s" %e)


        # load enteliWEB
        cls.setupClassFlag = [True, ""]
        try:
            profile = webdriver.FirefoxProfile()
            profile.set_preference('webdriver_enable_native_events', True)
            Macros.LoadEnteliWEB(cls.Host, cls.Browser, cls.Username, cls.Password, ff_profile=profile)
            cls.accordion = AccordionPageObj()
        except:
            cls.setupClassFlag[0] = False
            cls.setupClassFlag[1] = "verify user logged in: failed"
            
        
        
    @classmethod
    def tearDownClass(cls):
        super(TestCase, cls).tearDownClass()
        Macros.CloseEnteliWEB()
        cls.connection.close()


    def setUp(self):
        super(TestCase, self).setUp()
        
        if not self.setupClassFlag[0]:
            self.fail(self.setupClassFlag[1])
            
            
    def tearDown(self):
        super(TestCase, self).tearDown()
            
        
    @data(*getTestingData(DATA_FILE_LOCATION))
    def testMain(self, testData):
        # Update doc string based on test data
        self._testMethodDoc = "Verify Request: %s"%testData.content[1]
        self.testData = testData.content
        self.driver = self.accordion.driver
    
        step = self._testMethodDoc
        #print "\n" + step

        # prepare request url
        if self.testData[0] == "Kaizen Energy" and self.testData[1] == "Modify Virtual Datapoint":
            self._prepareModifyVirtualDatapoint()
        elif self.testData[0] == "Energy Reports" and self.testData[1] in ("Update Consumption Report", "Run Consumption Report", "Schedule Consumption Report", "Delete Consumption Report"):
            self._prepareEnergyReports()
        elif self.testData[0] == "Kaizen Energy" and self.testData[1] == "Modify Report Schedule":
            self._prepareModifyReportSchedule()
            
        url = Base_URL + self.testData[2]
        self.driver.get(url)
        keyWordsXpath = "//*[contains(text(),'" + KeyWords + "')]"
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, keyWordsXpath)))
        except TimeoutException:
            if self.testData[0] == "Kaizen Energy" and self.testData[1] == "BaseUnit Setup":
                self._verifyBaseUnitSetup()
            elif self.testData[0] == "Kaizen Energy" and self.testData[1] == "Modify Virtual Datapoint":
                self._verifyModifyVirutalDatapoint()
            elif self.testData[0] == "Kaizen Energy" and self.testData[1] == "Modify Report Schedule":
                self._verifyModifyReportSchedule()
            elif self.testData[0] == "Energy Reports" and self.testData[1] == "Schedule Consumption Report":
                self._verifyScheduleConsumpReport()
            else:
                self.fail("%s: CSRF Warning is not returned"%step)
    

    def _verifyBaseUnitSetup(self):
        """
        Special case dealing:
        After a GET request for BaseUnit setup, it will load BaseUnit setup page
        with no changes on base units instead of returning CSRF warning.

        This test will send a request to change Outdoor Temp. unit to FAHRENHEIT and
        this helper function will verify the base unit for Outdoor Temp is still CELSIUS
        """

        cursor = self.connection.cursor()
        cursor.execute("SELECT Value FROM settings_global where Type = 'BaseUnit' and Name = 'Temperature'")
        row = cursor.fetchone()
        expected = "CELSIUS"
        current = None
        if row:
            current = row[0]
        self.assertEqual(expected, current, "Verify Outdoor Temp unit hasn't been updated by This GET request.")


    def _prepareModifyVirtualDatapoint(self):
        """
        helper function to update test data, to replace the place holder <datapoint_formula_id> in url
        to a real datapoint formula id 
        """
        url = self.testData[2]
        datapoint_formula_id = ""
        cursor = self.connection.cursor()
        cursor.execute("SELECT ID FROM datapoint_formula")
        row = cursor.fetchone()
        if row:
            datapoint_formula_id = row[0]

        # append datapoint formula Id to current test data
        self.testData.append(datapoint_formula_id)

        # replace place holer in url with datapoint formula id
        url = url.replace("<datapoint_formula_id>", datapoint_formula_id)
        self.testData[2] = url
        

    def _verifyModifyVirutalDatapoint(self):
        """
        Special case dealing:
        After a GET request for modify virtual datapoint, it will load virtual datapoint edit page
        with no changes on the virtual datapoint instead of returning CSRF warning.

        This test will send a request to update virutal datapoint name and formula
        this helper function will verify the target virtual datapoint has not been updated.
        """

        cursor = self.connection.cursor()
        cursor.execute("SELECT Name, Expression FROM datapoint_formula where ID = '%s'"%self.testData[3])
        row = cursor.fetchone()
        expected01 = "security"
        expected02 = "111"
        current01 = None
        current02 = None
        if row:
            current01 = row[0]
            current02 = row[1]
        self.assertNotEqual(expected01, current01, "Verify virtual datapoint name hasn't been updated by This GET request.")
        self.assertNotEqual(expected02, current02, "Verify virtual datapoint formula hasn't been updated by This GET request.")


    def _prepareEnergyReports(self):
        """
        helper function to update test data, to replace the place holder <report_id> in url
        to a real consumption report instance id
        """
        url = self.testData[2]
        report_id = ""
        cursor = self.connection.cursor()
        cursor.execute("SELECT ID FROM report WHERE FilePath = 'Consumption'")
        row = cursor.fetchone()
        if row:
            report_id = row[0]

        # append datapoint formula Id to current test data
        self.testData.append(report_id)

        # replace place holer in url with datapoint formula id
        url = url.replace("<report_id>", report_id)
        self.testData[2] = url


    def _prepareModifyReportSchedule(self):
        """
        helper function to update test data, to replace the place holder <report_schedule_id> and <report_id> in url
        to a real id string
        """
        url = self.testData[2]
        report_schedule_id = ""
        report_id = ""
        cursor = self.connection.cursor()
        cursor.execute("SELECT ID, Report FROM report_schedule")
        row = cursor.fetchone()
        if row:
            report_schedule_id = row[0]
            report_id = row[1]

        # append datapoint formula Id to current test data
        self.testData.append(report_schedule_id)
        self.testData.append(report_id)

        # replace place holer in url with datapoint formula id
        url = url.replace("<report_schedule_id>", report_schedule_id)
        url = url.replace("<report_id>", report_id)
        self.testData[2] = url


    def _verifyModifyReportSchedule(self):
        """
        Special case dealing:
        After a GET request for modify a report schedule, it will report schedule edit page
        with no changes on the virtual datapoint instead of returning CSRF warning.

        This test will send a request to update a report schedule's Language to de
        this helper function will verify the target report schedule has not been updated.
        """

        cursor = self.connection.cursor()
        cursor.execute("SELECT Locale FROM report_schedule where ID = '%s' and Report = '%s'"%(self.testData[3], self.testData[4]))
        row = cursor.fetchone()
        expected = "de"
        current = None
        if row:
            current = row[0]
        self.assertNotEqual(expected, current, "Verify the language of the report schedule hasn't been dated by This GET request.")
        
        
    def _verifyScheduleConsumpReport(self):
        """
        special case dealing:
        after a get request for schedule a report, it will got to schedule a report page instead of return
        CSRF warning.
        this fuction will verify after request send, the schedule a report page is loaded.
        """
        self.driver.switch_to.default_content()
        target = self.driver.find_element_by_id("headertitle")
        current = target.text.strip()
        expected = "Schedule a Report"
        self.assertEqual(current, expected, "verify schedule a report doesn't get through failed")
    

if __name__ == "__main__":
    unittest.main()
        
    