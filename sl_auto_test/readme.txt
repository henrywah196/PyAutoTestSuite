1. test automation using python nose test runner (or call it framework). so download and install python nose first.
    Install nose using setuptools: easy_install nose
    or pip: pip install nose

2. test automation using Data Driven Test. so download and install python ddt module.
    Install ddt using setuptools: easy_install ddt
    or pip: pip install ddt

3. to make the ddt test method name more simple, the default function mk_test_name need to be replaced by following one:

def mk_test_name(name, value, index=0):
    """
    overwrite the default function
    Generate a new name for a test case.
    It will take the original test name and append an ordinal index in the 
    format of three digit with leading zero.
    """
    test_name = "{0}_{1}".format(name, "%03d"%(index + 1))
    return re.sub('\W|^(?=\d)', '_', test_name)
    
4. to let nose generate html test report, download and install HTML report generation plugin for nose.
    Install nose-html 1.1 using setuptools: easy_install nose-html
    or pip: pip install nose-html

5. modify windows User Account Control (UAC)

Change UAC from "Default - Notify me only when programs try to make changes to my computer" to "Never notify me when..."
Reboot the PC. 