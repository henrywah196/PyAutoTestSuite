#--------------------------------------------------------------------------------------
# Setup:    setup test project environment, install required modules 
# 
#
#
# Author:        Henry Wang
# Created:       Aug 08, 2015
#--------------------------------------------------------------------------------------
import os, shutil, site, pip
from setuptools.command import easy_install

def setup():
    print "\nSetup pyAutoTest '%s' ...\n"%(os.path.dirname(os.path.abspath(__file__)))
    easy_install.main(['nose', 'nose-html', 'ddt', 'selenium', 'pywinauto', 'requests', 'pil'])
    # there's issue install pyodbc using easy_install using pip instead
    pip.main(['install', 'pyodbc'])

    print "\nModify ddt module ...\n"
    reload(site)
    import ddt
    dst = os.path.join(os.path.dirname(ddt.__file__), "ddt.py")
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup", "ddt.py")
    print "replace: %s"%dst
    print "with: %s"%src
    shutil.copyfile(src, dst)

    print "\nPrepare .pth file ...\n"
    fileName = os.path.basename(os.path.normpath(os.path.dirname(os.path.abspath(__file__)))) + ".pth"
    fileFullName = os.path.join(site.getsitepackages()[1], fileName)
    print "create %s"%fileFullName
    file = open(fileFullName, 'w')
    file.write(os.path.dirname(os.path.abspath(__file__)))
    file.close()


if __name__ == "__main__":
    setup()





