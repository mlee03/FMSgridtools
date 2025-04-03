import ctypes
import os
from .shared.create_xgrid import CreateXgrid

class cLIB():

    clib_path: str = os.path.dirname(__file__) + "/../cfrenctools/c_build/clib.so"
    clib: ctypes.CDLL = ctypes.CDLL(clib_path)
    
    @classmethod
    def init(cls):        
        CreateXgrid.init(clib=cls.clib)

    @classmethod
    def change_lib(cls, clib_path: str = None):
        if clib_path is not None:
            cls._clib_path = clib_path
            try:
                cls._clib = ctypes.CDLL(cls.clib_path)
            except:
                raise RuntimeError("ERROR LOADING LIBRARY")
        CreateXgrid.init(clib=cls.clib)
        
