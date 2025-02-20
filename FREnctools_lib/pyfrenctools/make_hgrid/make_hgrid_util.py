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

def fill_cubic_grid_halo(
        nx: int, 
        ny: int, 
        halo: int, 
        data: npt.NDArray[np.float64], 
        data1_all: npt.NDArray[np.float64],
        data2_all: npt.NDArray[np.float64],
        tile: int,
        ioff: int,
        joff: int,
):
    nxp = nx + ioff
    nyp = ny + joff
    nxph = nx + ioff + 2*halo
    nyph = ny + joff + 2*halo

    for i in range(nxph*nyph):
        data[i] = -9999.

    # first copy computing domain data
    for j in range (nyp+1):
        for i in range(nxp+1):
            data[j*nxph+i] = data1_all[tile*nxp*nyp+(j-1)*nxp+(i-1)]

    ntiles = 6

    if tile%2 == 1:
        lw = (tile+ntiles-1)%ntiles
        le = (tile+ntiles+2)%ntiles
        ls = (tile+ntiles-2)%ntiles
        ln = (tile+ntiles+1)%ntiles
        for j in range(nyp+1):
            data[j*nxph] = data1_all[lw*nxp*nyp+(j-1)*nxp+nx-1]       # west halo
            data[j*nxph+nxp+1] = data2_all[le*nxp*nyp+ioff*nxp+nyp-j] # east halo

        for i in range(nxp+1):
            data[i] = data2_all[ls*nxp*nyp+(nxp-i)*nyp+(nx-1)]        # south halo
            data[(nyp+1)*nxph+i] = data1_all[ln*nxp*nyp+joff*nxp+i-1] # north halo
    else:
        lw = (tile+ntiles-2)%ntiles
        le = (tile+ntiles+1)%ntiles
        ls = (tile+ntiles-1)%ntiles
        ln = (tile+ntiles+2)%ntiles
        for j in range(nyp+1):
            data[j*nxph] = data2_all[lw*nxp*nyp+(ny-1)*nxp+nyp-j]     # west halo
            data[j*nxph+nxp+1] = data1_all[le*nxp*nyp+(j-1)*nxp+ioff] # east halo

        for i in range(nxp+1):
            data[i] = data1_all[ls*nxp*nyp+(ny-1)*nxp+i-1]                # south halo
            data[(nyp+1)*nxph+i] = data2_all[ln*nxp*nyp+(nxp-i)*nyp+joff] # north halo

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

def create_grid_from_file(
        file: str,
        nlon: npt.NDArray[np.int32],
        nlat: npt.NDArray[np.int32],
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        dx: npt.NDArray[np.float64],
        dy: npt.NDArray[np.float64],
        area: npt.NDArray[np.float64],
        angle_dx: npt.NDArray[np.float64],
        use_great_circle_algorithm: int,
        use_angular_midpoint: int
):
    _create_grid_from_file = lib.create_grid_from_file

    file_c, file_t = set_Cchar(file)
    nlon_p, nlon_t = setarray_Cint32(nlon)
    nlat_p, nlat_t = setarray_Cint32(nlat)
    x_p, x_t = setarray_Cdouble(x)
    y_p, y_t = setarray_Cdouble(y)
    dx_p, dx_t = setarray_Cdouble(dx)
    dy_p, dy_t = setarray_Cdouble(dy)
    area_p, area_t = setarray_Cdouble(area)
    angle_dx_p, angle_dx_t = setarray_Cdouble(angle_dx)
    use_great_circle_algorithm_c = ctypes.c_int(use_great_circle_algorithm)
    use_great_circle_algorithm_t = ctypes.c_int
    use_angular_midpoint_c = ctypes.c_int(use_angular_midpoint)
    use_angular_midpoint_t = ctypes.c_int

    _create_grid_from_file.argtypes = [
        file_t,
        nlon_t,
        nlat_t,
        x_t,
        y_t,
        dx_t,
        dy_t,
        area_t,
        angle_dx_t,
        use_great_circle_algorithm_t,
        use_angular_midpoint_t,
    ]
    _create_grid_from_file.restype = None

    _create_grid_from_file(
        file_c,
        nlon_p,
        nlat_p,
        x_p,
        y_p,
        dx_p,
        dy_p,
        area_p,
        angle_dx_p,
        use_great_circle_algorithm_c,
        use_angular_midpoint_c
    )

def create_simple_cartesian_grid(
        xbnds: npt.NDArray[np.float64],
        ybnds: npt.NDArray[np.float64],
        nlon: npt.NDArray[np.int32],
        nlat: npt.NDArray[np.int32],
        simple_dx: float,
        simple_dy: float,
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
):
    _create_simple_cartesian_grid = lib.create_simple_cartesian_grid

    xbnds_p, xbnds_t = setarray_Cdouble(xbnds)
    ybnds_p, ybnds_t = setarray_Cdouble(ybnds)
    nlon_p, nlon_t = setarray_Cint32(nlon)
    nlat_p, nlat_t = setarray_Cint32(nlat)
    simple_dx_c, simple_dx_t = setscalar_Cdouble(simple_dx)
    simple_dy_c, simple_dy_t = setarray_Cdouble(simple_dy)
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

    _create_simple_cartesian_grid.argtypes = [
        xbnds_t,
        ybnds_t,
        nlon_t,
        nlat_t,
        simple_dx_t,
        simple_dy_t,
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
    ]
    _create_simple_cartesian_grid.restype = None

    _create_simple_cartesian_grid(
        xbnds_p,
        ybnds_p,
        nlon_p,
        nlat_p,
        simple_dx_c,
        simple_dy_c,
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
    )


def create_spectral_grid(
        nlon: npt.NDArray[np.int32],
        nlat: npt.NDArray[np.int32],
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
        use_great_circle_algorithm: int,
):
    _create_spectral_grid = lib.create_spectral_grid

    nlon_p, nlon_t = setarray_Cint32(nlon)
    nlat_p, nlat_t = setarray_Cint32(nlat)
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
    use_great_circle_algorithm_c = ctypes.c_int(use_great_circle_algorithm)
    use_great_circle_algorithm_t = ctypes.c_int

    _create_spectral_grid.argtypes = [
        nlon_t,
        nlat_t,
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
        use_great_circle_algorithm_t,
    ]
    _create_spectral_grid.restype = None

    _create_spectral_grid(
        nlon_p,
        nlat_p,
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
        angle_dx_p,
        use_great_circle_algorithm_c,
    )

def create_conformal_cubic_grid(
        npts: int,
        nratio: int,
        method: str,
        orientation: str,
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        dx: npt.NDArray[np.float64],
        dy: npt.NDArray[np.float64],
        area: npt.NDArray[np.float64],
        angle_dx: npt.NDArray[np.float64],
        angle_dy: npt.NDArray[np.float64],
):
    _create_conformal_cubic_grid = lib.create_conformal_cubic_grid

    npts_c, npts_t = setscalar_Cint32(npts)
    nratio_c, nratio_t = setscalar_Cint32(nratio)
    method_c, method_t = set_Cchar(method)
    orientation_c, orientation_t = set_Cchar(orientation)
    x_p, x_t = setarray_Cdouble(x)
    y_p, y_t = setarray_Cdouble(y)
    dx_p, dx_t = setarray_Cdouble(dx)
    dy_p, dy_t = setarray_Cdouble(dy)
    area_p, area_t = setarray_Cdouble(area)
    angle_dx_p, angle_dx_t = setarray_Cdouble(angle_dx)
    angle_dy_p, angle_dy_t = setarray_Cdouble(angle_dy)

    _create_conformal_cubic_grid.argtypes = [
        npts_t,
        nratio_t,
        method_t,
        orientation_t,
        x_t,
        y_t,
        dx_t,
        dy_t,
        area_t,
        angle_dx_t,
        angle_dy_t,
    ]
    _create_conformal_cubic_grid.restype = None

    _create_conformal_cubic_grid(
        npts_c,
        nratio_c,
        method_c,
        orientation_c,
        x_p,
        y_p,
        dx_p,
        dy_p,
        area_p,
        angle_dx_p,
        angle_dy_p,
    )

def create_gnomonic_cubic_grid_GR(
        grid_type: str,
        nlon: npt.NDArray[np.int32],
        nlat: npt.NDArray[np.int32],
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        dx: npt.NDArray[np.float64],
        dy: npt.NDArray[np.float64],
        area: npt.NDArray[np.float64],
        angle_dx: npt.NDArray[np.float64],
        angle_dy: npt.NDArray[np.float64],
        shift_fac: float,
        do_schmidt: int,
        do_cube_transform: int,
        stretch_factor: float,
        target_lon: float,
        target_lat: float,
        nest_grid: int,
        parent_tile: int,
        refine_ratio: int,
        istart_nest: int,
        iend_nest: int,
        jstart_nest: int,
        jend_nest: int, 
        halo: int, 
        output_length_angle: int,
):
    _create_gnomonic_cubic_grid_GR = lib.create_gnomonic_cubic_gridGR

    grid_type_c, grid_type_t = set_Cchar(grid_type)
    nlon_p, nlon_t = setarray_Cint32(nlon)
    nlat_p, nlat_t = setarray_Cint32(nlat)
    x_p, x_t = setarray_Cdouble(x)
    y_p, y_t = setarray_Cdouble(y)
    dx_p, dx_t = setarray_Cdouble(dx)
    dy_p, dy_t = setarray_Cdouble(dy)
    area_p, area_t = setarray_Cdouble(area)
    angle_dx_p, angle_dx_t = setarray_Cdouble(angle_dx)
    angle_dy_p, angle_dy_t = setarray_Cdouble(angle_dy)
    shift_fac_c, shift_fac_t = setscalar_Cdouble(shift_fac)
    do_schmidt_c, do_schmidt_t = setscalar_Cint32(do_schmidt)
    do_cube_transform_c, do_cube_transform_t = setscalar_Cint32(do_cube_transform)
    stretch_factor_c, stretch_factor_t = setscalar_Cdouble(stretch_factor)
    target_lon_c, target_lon_t = setscalar_Cint32(target_lon)
    target_lat_c, target_lat_t = setscalar_Cint32(target_lat)
    nest_grid_c, nest_grid_t = setscalar_Cint32(nest_grid)
    parent_tile_c, parent_tile_t = setscalar_Cint32(parent_tile)
    refine_ratio_c, refine_ratio_t = setscalar_Cint32(refine_ratio)
    istart_nest_c, istart_nest_t = setscalar_Cint32(istart_nest)
    iend_nest_c, iend_nest_t = setscalar_Cint32(iend_nest)
    jstart_nest_c, jstart_nest_t = setscalar_Cint32(jstart_nest)
    jend_nest_c, jend_nest_t = setscalar_Cint32(jend_nest)
    halo_c, halo_t = setscalar_Cint32(halo)
    output_length_angle_c, output_length_angle_t = setscalar_Cint32(output_length_angle)

    _create_gnomonic_cubic_grid_GR.argtypes = [
        grid_type_t,
        nlon_t,
        nlat_t,
        x_t,
        y_t,
        dx_t,
        dy_t,
        area_t,
        angle_dx_t,
        angle_dy_t,
        shift_fac_t,
        do_schmidt_t,
        do_cube_transform_t,
        stretch_factor_t,
        target_lon_t,
        target_lat_t,
        nest_grid_t,
        parent_tile_t,
        refine_ratio_t,
        istart_nest_t,
        iend_nest_t,
        jstart_nest_t,
        jend_nest_t,
        halo_t,
        output_length_angle_t,
    ]
    _create_gnomonic_cubic_grid_GR.restype = None

    _create_gnomonic_cubic_grid_GR(
        grid_type_c,
        nlon_p,
        nlat_p,
        x_p,
        y_p,
        dx_p,
        dy_p,
        area_p,
        angle_dx_p,
        angle_dy_p,
        shift_fac_c,
        do_schmidt_c,
        do_cube_transform_c,
        stretch_factor_c,
        target_lon_c,
        target_lat_c,
        nest_grid_c,
        parent_tile_c,
        refine_ratio_c,
        istart_nest_c,
        iend_nest_c,
        jstart_nest_c,
        jend_nest_c,
        halo_c,
        output_length_angle_c,
    )

def create_gnomonic_cubic_grid(
        grid_type: str,
        nlon: npt.NDArray[np.int32],
        nlat: npt.NDArray[np.int32],
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        dx: npt.NDArray[np.float64],
        dy: npt.NDArray[np.float64],
        area: npt.NDArray[np.float64],
        angle_dx: npt.NDArray[np.float64],
        angle_dy: npt.NDArray[np.float64],
        shift_fac: float,
        do_schmidt: int,
        do_cube_transform: int,
        stretch_factor: float,
        target_lon: float,
        target_lat: float,
        num_nest_grids: int,
        parent_tile: npt.NDArray[np.int32],
        refine_ratio: npt.NDArray[np.int32],
        istart_nest: npt.NDArray[np.int32],
        iend_nest: npt.NDArray[np.int32],
        jstart_nest: npt.NDArray[np.int32],
        jend_nest: npt.NDArray[np.int32],
        halo: int,
        output_length_angle: int,
):
    _create_gnomonic_cubic_grid = lib.create_gnomonic_cubic_grid

    grid_type_c, grid_type_t = set_Cchar(grid_type)
    nlon_p, nlon_t = setarray_Cint32(nlon)
    nlat_p, nlat_t = setarray_Cint32(nlat)
    x_p, x_t = setarray_Cdouble(x)
    y_p, y_t = setarray_Cdouble(y)
    dx_p, dx_t = setarray_Cdouble(dx)
    dy_p, dy_t = setarray_Cdouble(dy)
    area_p, area_t = setarray_Cdouble(area)
    angle_dx_p, angle_dx_t = setarray_Cdouble(angle_dx)
    angle_dy_p, angle_dy_t = setarray_Cdouble(angle_dy)
    shift_fac_c, shift_fac_t = setscalar_Cdouble(shift_fac)
    do_schmidt_c, do_schmidt_t = setscalar_Cint32(do_schmidt)
    do_cube_transform_c, do_cube_transform_t = setscalar_Cint32(do_cube_transform)
    stretch_factor_c, stretch_factor_t = setscalar_Cdouble(stretch_factor)
    target_lon_c, target_lon_t = setscalar_Cdouble(target_lon)
    target_lat_c, target_lat_t = setscalar_Cdouble(target_lat)
    num_nest_grids_c, num_nest_grids_t = setscalar_Cint32(num_nest_grids)
    parent_tile_p, parent_tile_t = setarray_Cint32(parent_tile)
    refine_ratio_p, refine_ratio_t = setarray_Cint32(refine_ratio)
    istart_nest_p, istart_nest_t = setarray_Cint32(istart_nest)
    iend_nest_p, iend_nest_t = setarray_Cint32(iend_nest)
    jstart_nest_p, jstart_nest_t = setarray_Cint32(jstart_nest)
    jend_nest_p, jend_nest_t = setarray_Cint32(jend_nest)
    halo_c, halo_t = setscalar_Cint32(halo)
    output_length_angle_c, output_length_angle_t = setscalar_Cint32(output_length_angle)

    _create_gnomonic_cubic_grid.argtypes = [
        grid_type_t,
        nlon_t,
        nlat_t,
        x_t,
        y_t,
        dx_t,
        dy_t,
        area_t,
        angle_dx_t,
        angle_dy_t,
        shift_fac_t,
        do_schmidt_t,
        do_cube_transform_t,
        stretch_factor_t,
        target_lon_t,
        target_lat_t,
        num_nest_grids_t,
        parent_tile_t,
        refine_ratio_t,
        istart_nest_t,
        iend_nest_t,
        jstart_nest_t,
        jend_nest_t,
        halo_t,
        output_length_angle_t,
    ]
    _create_gnomonic_cubic_grid.restype = None

    _create_gnomonic_cubic_grid(
        grid_type_c,
        nlon_p,
        nlat_p,
        x_p,
        y_p,
        dx_p,
        dy_p,
        area_p,
        angle_dx_p,
        angle_dy_p,
        shift_fac_c,
        do_schmidt_c,
        do_cube_transform_c,
        stretch_factor_c,
        target_lon_c,
        target_lat_c,
        num_nest_grids_c,
        parent_tile_p,
        refine_ratio_p,
        istart_nest_p,
        iend_nest_p,
        jstart_nest_p,
        jend_nest_p,
        halo_c,
        output_length_angle_c,
    )

def create_f_plane_grid(
        nxbnds: int,
        nybnds: int,
        xbnds: npt.NDArray[np.float64],
        ybnds: npt.NDArray[np.float64],
        nlon: npt.NDArray[np.int32],
        nlat: npt.NDArray[np.int32],
        dlon: npt.NDArray[np.float64],
        dlat: npt.NDArray[np.float64],
        use_legacy: int,
        f_plane_latitude: float,
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
        center: str
):
    _create_f_plane_grid = lib.create_f_plane_grid

    nxbnds_c, nxbnds_t = setscalar_Cint32(nxbnds)
    nybnds_c, nybnds_t = setscalar_Cint32(nybnds)
    xbnds_p, xbnds_t = setarray_Cdouble(xbnds)
    ybnds_p, ybnds_t = setarray_Cdouble(ybnds)
    nlon_p, nlon_t = setarray_Cint32(nlon)
    nlat_p, nlat_t = setarray_Cint32(nlat)
    dlon_p, dlon_t = setarray_Cdouble(dlon)
    dlat_p, dlat_t = setarray_Cdouble(dlat)
    use_legacy_c, use_legacy_t = setscalar_Cint32(use_legacy)
    f_plane_latitude_c, f_plane_latitude_t = setscalar_Cdouble(f_plane_latitude)
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

    _create_f_plane_grid.argtypes = [
        nxbnds_t,
        nybnds_t,
        xbnds_t,
        ybnds_t,
        nlon_t,
        nlat_t,
        dlon_t,
        dlat_t,
        use_legacy_t,
        f_plane_latitude_t,
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
    ]
    _create_f_plane_grid.restype = None

    _create_f_plane_grid(
        nxbnds_c,
        nybnds_c,
        xbnds_p,
        ybnds_p,
        nlon_p,
        nlat_p,
        dlon_p,
        dlat_p,
        use_legacy_c,
        f_plane_latitude_c,
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
    )