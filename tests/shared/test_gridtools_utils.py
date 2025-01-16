import gridtools
import os
import pytest

def test_file_is_there_pass() :

    testfile = 'file_is_here'    
    with open(testfile, 'w') as myfile : pass
    gridtools.check_file_is_there(testfile)
    os.remove(testfile)

@pytest.mark.xfail
def test_file_is_there_fail() :
    
    testfile = 'file_is_not_here'
    gridtools.check_file_is_there(testfile)


