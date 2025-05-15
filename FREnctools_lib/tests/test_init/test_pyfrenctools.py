import ctypes
import os
import pytest
import pyfrenctools
import module1

def test_loaded_library():
    assert(id(pyfrenctools.cfrenctools.lib) == id(pyfrenctools.create_xgrid.lib))

def test_load_library_once():
    myclass = module1.Module1Class()
    assert id(pyfrenctools.cfrenctools.lib) == myclass.module1_lib_id

@pytest.mark.xfail
def test_library_load_fail():
    pyfrenctools.cfrenctools.changelib(libpath="do_not_exist")



