import ctypes
import os
from .shared.create_xgrid import CreateXgrid

class cLIB():

    clib_path: str = os.path.dirname(__file__) + "/../cfrenctools/c_build/clib.so"
    clib: ctypes.CDLL = ctypes.CDLL(clib_path)
    __initialized = False
    
    @classmethod
    def init(cls):        
        if not cls.__initialized:
            CreateXgrid.init(clib=cls.clib)
            cls.__initialized = True

    @classmethod
    def change_lib(cls, clib_path: str):

        cls._clib_path = clib_path
        try: cls._clib = ctypes.CDLL(cls.clib_path)
        except: raise RuntimeError("ERROR LOADING LIBRARY")
            
        CreateXgrid.init(clib=cls.clib)
        cls.__initialized = True
