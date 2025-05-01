import ctypes
import os
from .shared.create_xgrid import create_xgrid

class cfrenctools():

    __libpath: str = os.path.dirname(__file__) + "/../cfrenctools/c_build/clib.so"
    __lib: ctypes.CDLL = ctypes.cdll.LoadLibrary(__libpath)

    @classmethod
    def printme(cls):
        print(cls.lib)
    
    @classmethod
    def init(cls):
        create_xgrid.init(cls.libpath, cls.lib)

    @classmethod
    def changelib(cls, libpath):
        cls.__libpath = libpath
        cls.__lib = ctypes.CDLL(cls.__libpath)
        cls.init()
        
    @classmethod
    @property
    def lib(cls):
        return cls.__lib

    @classmethod
    @property
    def libpath(cls):
        return cls.__libpath
