import ctypes
import os
import pytest
import pyfrenctools
import module1

def test_loaded_library():
    assert(id(pyfrenctools.cLIB.clib) == id(pyfrenctools.CreateXgrid.clib))

def test_load_library_once():
    myclass = module1.Module1Class()
    assert(id(pyfrenctools.cLIB.clib) == myclass.module1_clib_id)

@pytest.mark.xfail
def test_library_load_fail():
    pyfrenctools.cLIB.change_lib(clib_path="do_not_exist")



