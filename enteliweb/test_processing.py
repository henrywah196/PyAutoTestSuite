#--------------------------------------------------------------------------------------
# post_processing:    prepare and modify test report 
# 
#
#
# Author:        Henry Wang
# Created:       Aug 08, 2015
#--------------------------------------------------------------------------------------
import settings
import io, os, shutil, datetime, codecs, re, time
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
from libraries.sendmail import SendSMTPMail
    

#############################
# Report preparation related
#############################
def getReportTitle():
    """ return the predefined report title 
        which is stored in test_processing.ini file
    """
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_processing.ini"))
    return config.get("test_report", "title")


def getReportDescription():
    """ return the predefined report description 
        which is stored in test_processing.ini file
    """
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_processing.ini"))
    testBuild =  config.get("test_report", "build")
    #description = "Build under test: eweb %s<br>OS under test: %s"%(testBuild, testOS)
    description = "Test against %s on %s (host: %s)."%(testBuild, settings.PLATFORM, settings.HOST)
    return description


def getReportBuildInfo():
    """
    return the build number of the software under test
    """
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_processing.ini"))
    return config.get("test_report", "build")

def preProcessing(reportTitle=None):
    # obtain build number
    import requests
    r = requests.get("http://%s/enteliweb"%settings.HOST, verify=False)
    assert r.status_code == 200, "preProcessing(): get request returns incorrect code"
    m = re.search('<div>Version \d.\d.\d\d\d</div>', r.text)
    assert m is not None, "build_version is not found"
    build_number = m.group()
    build_number = "eweb%s"%build_number[13:-6]
    
    # update report title and build number in test_processing.ini file
    config = configparser.ConfigParser()
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_processing.ini")
    config.read(filePath)
    if reportTitle is not None:
        config.set('test_report', 'title', reportTitle)
    else:
        config.set('test_report', 'title', "enteliWEB Reporting Sanity Test Report")
    config.set('test_report', 'build', build_number)
    with open(filePath, 'w') as configfile:
        config.write(configfile)
        
    # prepare email subject
    config.read(filePath)
    send_result = config.get("email_notification", "send_result")
    if send_result == "True":
        config.set('email_notification', 'subject', "enteliWEB - # %s Test Result"%build_number)
        with open(filePath, 'w') as configfile:
            config.write(configfile)
    
    
def postProcessing(reportName=None):
    # create test_report folder if it's not exist
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests_report")
    if not os.path.exists(path):
        os.makedirs(path)
    if reportName is None:
        reportName = "test_report"
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), reportName + ".html")
    
        
    # email notification
    config = configparser.ConfigParser()
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_processing.ini")
    config.read(filePath)
    send_result = config.get("email_notification", "send_result")
    if send_result == "True":
        # generate the html message text
        HTMLMessage = None
        if (os.path.exists(src) == True):
            #hHTMLLogFile = open(src, 'r', encoding='utf-8')    # for python 3.x
            hHTMLLogFile = io.open(src, 'r', encoding='utf-8')    # for python 2.7
            HTMLMessage = ''
            for Line in hHTMLLogFile:
                HTMLMessage += Line
            hHTMLLogFile.close()
    
        # wait ten seconds to ensure the file processes are complete
        time.sleep (10)
    
        # set the subject
        Subject = config.get("email_notification", "subject")
        EMAIL_FROM_ADDRESS = config.get("email_notification", "sender")
        AddressList = config.get("email_notification", "recipients")
    
        # send the e-mail
        for ToAddress in re.split('\;',AddressList):
            SendSMTPMail(From=EMAIL_FROM_ADDRESS, 
                         To=ToAddress, 
                         Subject=Subject,
                         HTMLMessage=HTMLMessage)
    

    # update test report based on test_processing.ini
    now = datetime.datetime.now()
    file_name = "%s_%s.html"%(reportName, now.strftime("%Y%m%d%H%M"))
    dst = os.path.join(path, file_name)
    shutil.copy(src, dst)
    os.remove(src)
    
        
###########################
# Jenkins related function
###########################
def setBuildInfo(server, job, number, name, description):
    """ update server, job, buildnumber, buildname and 
        builddescription stored in test_processing.ini
    """
    config = configparser.ConfigParser()
    filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_processing.ini")
    config.read(filePath)
    config.set('jenkins', 'server', server)
    config.set('jenkins', 'job', job)
    config.set('jenkins', 'buildnumber', str(number))
    config.set('jenkins', 'buildname', name)
    config.set('jenkins', 'builddescription', description)
    with open(filePath, 'w') as configfile:
        config.write(configfile)
        

def editBuildInfo():
    """ obtain build information from test_processing.ini
        update associated job under jenkins server.
    """
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_processing.ini"))
    server = config.get("jenkins", "server")
    job = config.get("jenkins", "job")
    build_number = config.get("jenkins", "buildnumber")
    new_build_name = config.get("jenkins", "buildname")
    new_build_description = config.get("jenkins", "builddescription")
    
    
    # Edit Jenkins's build information
    p = {'json': '{"displayName":"%s", "description":"%s"}'%(new_build_name, new_build_description)}
    import requests
    r = requests.post("http://%s/job/%s/%s/configSubmit"%(server, job, build_number), data=p)
    
    
def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('edi', help='Edit Build Information', default=False)

    args = parser.parse_args()
    if args.edi:
        editBuildInfo()
        

if __name__ == "__main__":
    #post processing
    #editBuildInfo("localhost:8080", "PythonAutoTestSuites")
    main()






