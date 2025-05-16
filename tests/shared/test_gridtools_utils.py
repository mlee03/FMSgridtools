from fmsgridtools import check_file_is_there
from fmsgridtools import get_provenance_attrs
import os
import pytest

def test_check_file_is_there() :

    testfile = 'file_is_here'    
    with open(testfile, 'w') as myfile : pass
    check_file_is_there(testfile)
    os.remove(testfile)

@pytest.mark.xfail
def test_check_file_is_not_there() :
    
    testfile = 'file_is_not_here'
    check_file_is_there(testfile)

def test_provenance_attrs():
    p_attrs = gridtools.get_provenance_attrs(True, "0.2")
    print("attribute values:\n")
    print(p_attrs)
