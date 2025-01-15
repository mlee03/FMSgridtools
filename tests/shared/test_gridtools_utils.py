import gridtools
from gridtools import file_is_there
import os
import pytest

def test_file_is_there_pass() :

    testfile = 'file_is_here'    
    with open(testfile, 'w') as myfile : pass
    gridtools.file_is_there(testfile)
    os.remove(testfile)

@pytest.mark.xfail
def test_file_is_there_fail() :
    
    testfile = 'file_is_not_here'
    gridtools.file_is_there(testfile)


