import numpy as np
import numpy.typing as npt
import ctypes

from pyfms.data_handling import (
    setscalar_Cint32,
    setscalar_Cdouble,
    setarray_Cdouble,
    setarray_Cint32,
    set_Cchar,
)

lib = ctypes.CDLL("../../FRENCTools_lib/cfrenctools/c_build/clib.so")

def create_regular_lonlat_grid(
        nxbnds: int,
        nybnds: int,
        xbnds: npt.NDArray[np.float64],
        ybnds: npt.NDArray[np.float64],
        nlon: npt.NDArray[np.int32],
        nlat: npt.NDArray[np.int32],
        dlon: npt.NDArray[np.float64],
        dlat: npt.NDArray[np.float64],
        use_legacy: int,
        isc: int,
        iec: int,
        jsc: int,
        jec: int,
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        dx: npt.NDArray[np.float64],
        dy: npt.NDArray[np.float64],
        area: npt.NDArray[np.float64],
        angle_dx: npt.NDArray[np.float64],
        center: str,
        use_great_circle_algorithm: int
):
    _create_regular_lonlat_grid = lib.create_regular_lonlat_grid

    nxbnds_c, nxbnds_t = setscalar_Cint32(nxbnds)
    nybnds_c, nybnds_t = setscalar_Cint32(nybnds)
    xbnds_p, xbnds_t = setarray_Cdouble(xbnds)
    ybnds_p, ybnds_t = setarray_Cdouble(ybnds)
    nlon_p, nlon_t = setarray_Cint32(nlon)
    nlat_p, nlat_t = setarray_Cint32(nlat)
    dlon_p, dlon_t = setarray_Cdouble(dlon)
    dlat_p, dlat_t = setarray_Cdouble(dlat)
    use_legacy_c = ctypes.c_int(use_legacy)
    use_legacy_t = ctypes.POINTER(ctypes.c_int)
    isc_c, isc_t = setscalar_Cint32(isc)
    iec_c, iec_t = setscalar_Cint32(iec)
    jsc_c, jsc_t = setscalar_Cint32(jsc)
    jec_c, jec_t = setscalar_Cint32(jec)
    x_p, x_t = setarray_Cdouble(x)
    y_p, y_t = setarray_Cdouble(y)
    dx_p, dx_t = setarray_Cdouble(dx)
    dy_p, dy_t = setarray_Cdouble(dy)
    area_p, area_t = setarray_Cdouble(area)
    angle_dx_p, angle_dx_t = setarray_Cdouble(angle_dx)
    center_c, center_t = set_Cchar(center)
    use_great_circle_algorithm_c = ctypes.c_int(use_great_circle_algorithm)
    use_great_circle_algorithm_t = ctypes.POINTER(ctypes.c_int)

    _create_regular_lonlat_grid.argtypes = [
        nxbnds_t,
        nybnds_t,
        xbnds_t,
        ybnds_t,
        nlon_t,
        nlat_t,
        dlon_t,
        dlat_t,
        use_legacy_t,
        isc_t,
        iec_t,
        jsc_t,
        jec_t,
        x_t,
        y_t,
        dx_t,
        dy_t,
        area_t,
        angle_dx_t,
        center_t,
        use_great_circle_algorithm_t,
    ]
    _create_regular_lonlat_grid.restype = None

    _create_regular_lonlat_grid(
        nxbnds_c,
        nybnds_c,
        xbnds_p,
        ybnds_p,
        nlon_p,
        nlat_p,
        dlon_p,
        dlat_p,
        use_legacy_c,
        isc_c,
        iec_c,
        jsc_c,
        jec_c,
        x_p,
        y_p,
        dx_p,
        dy_p,
        area_p,
        angle_dx_p,
        center_c,
        use_great_circle_algorithm_c,
    )

def create_tripolar_grid(
        nxbnds: int,
        nybnds: int,
        xbnds: npt.NDArray[np.float64],
        ybnds: npt.NDArray[np.float64],
        nlon: npt.NDArray[np.int32],
        nlat: npt.NDArray[np.int32],
        dlon: npt.NDArray[np.float64],
        dlat: npt.NDArray[np.float64],
        use_legacy: int,
        lat_join_in: float,
        isc: int,
        iec: int,
        jsc: int,
        jec: int,
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        dx: npt.NDArray[np.float64],
        dy: npt.NDArray[np.float64],
        area: npt.NDArray[np.float64],
        angle_dx: npt.NDArray[np.float64],
        center: str,
        verbose: int,
        use_great_circle_algorithm: int
):
    _create_tripolar_grid = lib.create_tripolar_grid

    nxbnds_c, nxbnds_t = setscalar_Cint32(nxbnds)
    nybnds_c, nybnds_t = setscalar_Cint32(nybnds)
    xbnds_p, xbnds_t = setarray_Cdouble(xbnds)
    ybnds_p, ybnds_t = setarray_Cdouble(ybnds)
    nlon_p, nlon_t = setarray_Cint32(nlon)
    nlat_p, nlat_t = setarray_Cint32(nlat)
    dlon_p, dlon_t = setarray_Cdouble(dlon)
    dlat_p, dlat_t = setarray_Cdouble(dlat)
    use_legacy_c = ctypes.c_int(use_legacy)
    use_legacy_t = ctypes.POINTER(ctypes.c_int)
    lat_join_in_c, lat_join_in_t = setscalar_Cdouble(lat_join_in)
    isc_c, isc_t = setscalar_Cint32(isc)
    iec_c, iec_t = setscalar_Cint32(iec)
    jsc_c, jsc_t = setscalar_Cint32(jsc)
    jec_c, jec_t = setscalar_Cint32(jec)
    x_p, x_t = setarray_Cdouble(x)
    y_p, y_t = setarray_Cdouble(y)
    dx_p, dx_t = setarray_Cdouble(dx)
    dy_p, dy_t = setarray_Cdouble(dy)
    area_p, area_t = setarray_Cdouble(area)
    angle_dx_p, angle_dx_t = setarray_Cdouble(angle_dx)
    center_c, center_t = set_Cchar(center)
    verbose_c = ctypes.c_int(verbose)
    verbose_t = ctypes.POINTER(ctypes.c_int)
    use_great_circle_algorithm_c = ctypes.c_int(use_great_circle_algorithm)
    use_great_circle_algorithm_t = ctypes.POINTER(ctypes.c_int)

    _create_tripolar_grid.argtypes = [
        nxbnds_t,
        nybnds_t,
        xbnds_t,
        ybnds_t,
        nlon_t,
        nlat_t,
        dlon_t,
        dlat_t,
        use_legacy_t,
        lat_join_in_t,
        isc_t,
        iec_t,
        jsc_t,
        jec_t,
        x_t,
        y_t,
        dx_t,
        dy_t,
        area_t,
        angle_dx_t,
        center_t,
        verbose_t,
        use_great_circle_algorithm_t,
    ]
    _create_tripolar_grid.restype = None

    _create_tripolar_grid(
        nxbnds_c,
        nybnds_c,
        xbnds_p,
        ybnds_p,
        nlon_p,
        nlat_p,
        dlon_p,
        dlat_p,
        use_legacy_c,
        lat_join_in_c,
        isc_c,
        iec_c,
        jsc_c,
        jec_c,
        x_p,
        y_p,
        dx_p,
        dy_p,
        area_p,
        angle_dx_p,
        center_c,
        verbose_c,
        use_great_circle_algorithm_c,
    )

def create_grid_from_file():

def create_simple_cartesian_grid():

def create_spectral_grid():

def create_conformal_cubic_grid():

def create_gnomonic_cubic_grid_GR():

def create_gnomonic_cubic_grid():

def create_f_plane_grid():