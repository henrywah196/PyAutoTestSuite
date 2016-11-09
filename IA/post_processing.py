#--------------------------------------------------------------------------------------
# post_processing:    prepare and modify test report 
# 
#
#
# Author:        Henry Wang
# Created:       Aug 08, 2015
#--------------------------------------------------------------------------------------
import os, shutil, datetime
import ConfigParser, codecs

def processing(reportName=None):
    # create test_report folder if it's not exist
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests_report")
    if not os.path.exists(path):
        os.makedirs(path)

    # update test report based on post_processing.ini
    if reportName is None:
        reportName = "test_report"
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), reportName + ".html")
    now = datetime.datetime.now()
    file_name = "%s_%s.html"%(reportName, now.strftime("%Y%m%d%H%M"))
    dst = os.path.join(path, file_name)

    if os.path.isfile(src):
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "post_processing.ini"))
        heading_default = config.get("test_report", "heading_default")
        heading = config.get("test_report", "heading")
        description_default = config.get("test_report", "description_default")
        description = config.get("test_report", "description")
        report_r = codecs.open(src, 'r')
        report_w = codecs.open(dst, 'w')
        for line in report_r:
            if heading_default in line:
                report_w.write(line.replace(heading_default, heading))
            elif description_default in line:
                report_w.write(line.replace(description_default, description))
            else:
                report_w.write(line)

        report_r.close()
        report_w.close()


if __name__ == "__main__":
    #post processing
    processing()






