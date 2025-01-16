from gridtools import check_file_is_there
import os
import pytest

def test_check_file_is_there() :

    testfile = 'file_is_here'    
    with open(testfile, 'w') as myfile : pass
    gridtools.check_file_is_there(testfile)
    os.remove(testfile)

@pytest.mark.xfail
def test_check_file_is_not_there() :
>>>>>>> origin/main
    
    testfile = 'file_is_not_here'
    gridtools.check_file_is_there(testfile)


