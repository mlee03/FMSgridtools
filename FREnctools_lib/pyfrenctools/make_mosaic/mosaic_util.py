import ctypes
import dataclasses
import numpy as np
import numpy.typing as npt
from typing import Optional

@dataclasses.dataclass
class Contact:
    tile1: Optional[int] = None
    tile2: Optional[int] = None
    nxp1: Optional[int] = None
    nxp2: Optional[int] = None
    nyp1: Optional[int] = None
    nyp2: Optional[int] = None
    x1: Optional[npt.NDArray] = None
    x2: Optional[npt.NDArray] = None
    y1: Optional[npt.NDArray] = None
    y2: Optional[npt.NDArray] = None
    periodx: Optional[int] = None
    periody: Optional[int] = None

    def align_contact(self, lib_file:str) -> int:

        clibrary = ctypes.CDLL(lib_file)

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
