'''
Created on May 11, 2013

@author: WAH
'''
import os, nose
# import test cases
from nosesamples import NoseSamples
from nosesamples02 import NoseSamples02


if __name__ == "__main__":
    #execute test suite
    log_file_name = "nosesuite_result"
    argv = ["fake", "--verbosity=2", "--logging-clear-handlers", "--with-html", "--html-file=%s.html"%os.path.join(os.path.dirname(os.path.abspath(__file__)), log_file_name)]
    nose.main(defaultTest=__name__, argv=argv, exit=False)






