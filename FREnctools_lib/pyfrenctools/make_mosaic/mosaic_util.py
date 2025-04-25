import ctypes
from ctypes import create_string_buffer
from typing import Optional
import numpy as np
import numpy.typing as npt
from cfrenctools import LIB
import pathlib
from numpy.ctypeslib import ndpointer

class Contact:
    def __init__(self,
                 tile1: int,
                 tile2: int,
                 nxp1: int, 
                 nxp2: int,
                 nyp1: int, 
                 nyp2: int, 
                 x1: npt.NDArray, 
                 x2: npt.NDArray,
                 y1: npt.NDArray,
                 y2: npt.NDArray,
                 periodx: int = None,
                 periody: int = None):
        
        self.tile1 = tile1
        self.tile2 = tile2
        self.nxp1 = nxp1 
        self.nxp2 = nxp2
        self.nyp1 = nyp1 
        self.nyp2 = nyp2
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.periodx = periodx
        self.periody = periody

    def align_contact(self) -> int:

        clibrary = pyfrenctools.cfrenctools.LIB().lib
        #acquire function signature
        find_align = clibrary.get_align_contact

        #represent parameters needed
        find_align.argtypes = [ctypes.c_int, ctypes.c_int,
                               ctypes.c_int, ctypes.c_int,
                               ctypes.c_int, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_double),
                               ctypes.POINTER(ctypes.c_double),
                               ctypes.POINTER(ctypes.c_double),
                               ctypes.POINTER(ctypes.c_double),
                               ctypes.c_double,
                               ctypes.c_double,
                               ctypes.POINTER(ctypes.c_int),
                               ctypes.POINTER(ctypes.c_int),
                               ctypes.POINTER(ctypes.c_int),
                               ctypes.POINTER(ctypes.c_int),
                               ctypes.POINTER(ctypes.c_int),
                               ctypes.POINTER(ctypes.c_int),
                               ctypes.POINTER(ctypes.c_int),
                               ctypes.POINTER(ctypes.c_int)]

        c_double_p = ctypes.POINTER(ctypes.c_double)

        istart1, iend1, jstart1, jend1, \
        istart2, iend2, jstart2, jend2 = [ctypes.c_int() for i in range(8)]
        count = find_align(
            ctypes.c_int(self.tile1),
            ctypes.c_int(self.tile2),
            ctypes.c_int(self.nxp1),
            ctypes.c_int(self.nyp1),
            ctypes.c_int(self.nxp2),
            ctypes.c_int(self.nyp2),
            self.x1.ctypes.data_as(c_double_p),
            self.y1.ctypes.data_as(c_double_p),
            self.x2.ctypes.data_as(c_double_p),
            self.y2.ctypes.data_as(c_double_p),
            ctypes.c_double(self.periodx),
            ctypes.c_double(self.periody),
            ctypes.byref(istart1),
            ctypes.byref(iend1),
            ctypes.byref(jstart1),
            ctypes.byref(jend1),
            ctypes.byref(istart2),
            ctypes.byref(iend2),
            ctypes.byref(jstart2),
            ctypes.byref(jend2))

        return (count, istart1.value, iend1.value, jstart1.value,
    jend1.value, istart2.value, iend2.value, jstart2.value, jend2.value)


    def overlap_contact_call(self):
        pass

