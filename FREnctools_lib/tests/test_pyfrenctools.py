import ctypes
import os
import pytest
import pyfrenctools

def test_loaded_library():
    assert(id(pyfrenctools.cLIB.clib) == id(pyfrenctools.CreateXgrid.clib))

@pytest.mark.xfail
def test_library_load_fail():
    pyfrenctools.cLIB.change_lib(clib_path="do_not_exist")



