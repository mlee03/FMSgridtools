import ctypes
import os
import pyfrenctools

def test_load_library_default():
    cfrenctools = pyfrenctools.cfrenctools.LIB().lib

def test_load_library_explicit():
    frenctoolslib = os.path.dirname(__file__) + "/../cfrenctools/c_build/clib.so"
    cfrenctools = pyfrenctools.cfrenctools.LIB(frenctoolslib).lib



