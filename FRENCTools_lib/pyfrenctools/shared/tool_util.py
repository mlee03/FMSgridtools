import numpy as np
import numpy.typing as npt
import ctypes

from pyfms.data_handling import (
    setscalar_Cint32,
    setarray_Cdouble,
)

lib = ctypes.CDLL("../../FRENCTools_lib/cfrenctools/c_build/clib.so")

def get_legacy_grid_size(
        nb: int,
        bnds: npt.NDArray[np.float64],
        dbnds: npt.NDArray[np.float64],
):
    _get_legacy_grid_size = lib.get_legacy_grid_size

    nb_c, nb_t = setscalar_Cint32(nb)
    bnds_p, bnds_t = setarray_Cdouble(bnds)
    dbnds_p, dbnds_t = setarray_Cdouble(dbnds)

    _get_legacy_grid_size.argtypes = [
        nb_t,
        bnds_t,
        dbnds_t,
    ]
    _get_legacy_grid_size.restype = ctypes.c_int

    _get_legacy_grid_size(
        nb_c,
        bnds_p,
        dbnds_p,
    )