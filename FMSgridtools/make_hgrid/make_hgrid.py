import xarray as xr
import numpy as np
import click
from typing import Optional

from pyfms import pyFMS_mpp, pyFMS_mpp_domains
from FMSgridtools.shared.gridobj import GridObj

MAXBOUNDS = 100
REGULAR_LONLAT_GRID = 1
TRIPOLAR_GRID = 2
FROM_FILE = 3
SIMPLE_CARTESIAN_GRID = 4
SPECTRAL_GRID = 5
CONFORMAL_CUBIC_GRID = 6
GNOMONIC_ED = 7
F_PLANE_GRID = 8
BETA_PLANE_GRID = 9
MISSING_VALUE = -9999.

# TODO: Click stuff needed in here
@click.command()
@click.argument('args', nargs=-1)
@click.option("--grid_type", default="regular_lonlat_grid")
@click.option("--my_grid_file", default="")
@click.option("--nxbnds", default=2)
@click.option("--nybnds", default=2)
@click.option("--xbnds", type=str)
@click.option("--ybnds", type=str)
@click.option("--nlon", type=str)
@click.option("--nlat", type=str)
@click.option("--dlon", type=str)
@click.option("--dlat", type=str)
@click.option("--lat_join", default=65.)
@click.option("--nratio", default=1)
@click.option("--simple_dx", default=0.)
@click.option("--simple_dy", default=0.)
@click.option("--grid_name", default="horizontal_grid")
@click.option("--center", default="none")
@click.option("--shift_fac", default=18.0)
@click.option("--f_plane_latitude", default=100.)
@click.option("--do_schmidt", default=0)
@click.option("--do_cube_transform", default=0)
@click.option("--stretch_factor", type=float, default=0.0)
@click.option("--target_lon", type=float, default=0.0)
@click.option("--target_lat", type=float, default=0.0)
@click.option("--nest_grids", default=0)
@click.option("--parent_tile", type=str)
@click.option("--refine_ratio", type=str)
@click.option("--istart_nest", type=str)
@click.option("--iend_nest", type=str)
@click.option("--jstart_nest", type=str)
@click.option("--jend_nest", type=str)
@click.option("--halo", default=0)
@click.option("--great_circle_algorithm", default=False)
@click.option("--out_halo", default=0)
@click.option("--non_length_angle", default=False)
@click.option("--angular_midpoint", default=False)
@click.option("--rotate_poly", default=False)
@click.option("--verbose", default=False)
def main(
    args: str,
    grid_type: str,
    my_grid_file: Optional[str],
    nxbnds: int,
    nybnds: int,
    xbnds: str,
    ybnds: str,
    nlon: str,
    nlat: str,
    dlon: str,
    dlat: str,
    lat_join: float,
    nratio: int,
    simple_dx: float,
    simple_dy: float,
    grid_name: str,
    center: str,
    shift_fac: float,
    f_plane_latitude: float,
    do_schmidt: int,
    do_cube_transform: int,
    stretch_factor: float,
    target_lon: float,
    target_lat: float,
    nest_grids: int,
    parent_tile: str,
    refine_ratio: str,
    istart_nest: str,
    iend_nest: str,
    jstart_nest: str,
    jend_nest: str,
    halo: int,
    great_circle_algorithm: bool,
    out_halo: int,
    no_length_angle: bool,
    angular_midpoint: bool,
    rotate_poly: bool,
    verbose: bool,
):

    # start parallel
    # TODO: need to link to location of pyFMS shared library
    mpp = pyFMS_mpp(clib)
    mpp_domains = pyFMS_mpp_domains(clib)

    # TODO: Find what to use for error_type
    if(mpp.pyfms_npes() > 1):
        mpp.pyfms_error(error_type, "make_hgrid: make_hgrid must be run one processor, contact developer")


    print(f"==>NOTE: the grid type is {grid_type}")

    # TODO: Find where ntiles went
    if verbose:
        print(f"[INFO] make_hgrid.c Number of tiles (ntiles): {ntiles}")
        print(f"[INFO] make_hgrid.c Number of global tiles (ntiles_global): {ntiles_global}")


    # TODO: Methods to create types of grids to be passed instance of
    # GridStruct class

    if(my_grid_type==REGULAR_LONLAT_GRID):
        create_regular_lonlat_grid(
            &nxbnds, 
            &nybnds, 
            xbnds, 
            ybnds, 
            nlon, 
            nlat, 
            dx_bnds, 
            dy_bnds,
            use_legacy, 
            &isc, 
            &iec, 
            &jsc, 
            &jec, 
            x, 
            y, 
            dx, 
            dy, 
            area,
            angle_dx, 
            center,
            use_great_circle_algorithm,
        )
    elif(my_grid_type==TRIPOLAR_GRID):
        create_tripolar_grid(
            &nxbnds, 
            &nybnds, 
            xbnds, 
            ybnds, 
            nlon, 
            nlat, 
            dx_bnds, 
            dy_bnds,
            use_legacy, 
            &lat_join, 
            &isc, 
            &iec, 
            &jsc, 
            &jec, 
            x, 
            y, 
            dx, 
            dy,
            area, 
            angle_dx, 
            center, 
            verbose, 
            use_great_circle_algorithm,
        )
    elif(my_grid_type==FROM_FILE):
        for n in range(ntiles):
            n1 = n * nxp * nyp
            n2 = n * nx * nyp
            n3 = n * nxp * ny
            n4 = n * nx * ny
            create_grid_from_file(
                my_grid_file[n], 
                &nx, 
                &ny, 
                x+n1, 
                y+n1, 
                dx+n2, 
                dy+n3, 
                area+n4, 
                angle_dx+n1, 
                use_great_circle_algorithm, 
                use_angular_midpoint,
            )
    elif(my_grid_type==SIMPLE_CARTESIAN_GRID):
        create_simple_cartesian_grid(
            xbnds, 
            ybnds, 
            &nx, 
            &ny, 
            &simple_dx, 
            &simple_dy, 
            &isc, 
            &iec, 
            &jsc, 
            &jec,
            x, 
            y, 
            dx, 
            dy, 
            area, 
            angle_dx,
        )
    elif(my_grid_type==SPECTRAL_GRID):
        create_spectral_grid(
            &nx, 
            &ny, 
            &isc, 
            &iec, 
            &jsc, 
            &jec, 
            x, 
            y, 
            dx, 
            dy, 
            area, 
            angle_dx, 
            use_great_circle_algorithm,
        )
    elif(my_grid_type==CONFORMAL_CUBIC_GRID):
        create_conformal_cubic_grid(
            &nx, 
            &nratio, 
            method, 
            orientation, 
            x, 
            y, 
            dx, 
            dy, 
            area, 
            angle_dx, 
            angle_dy,
        )
    elif(my_grid_type==GNOMONIC_ED):
        if(nest_grids == 1 and parent_tile_list[0] == 0):
            create_gnomonic_cubic_grid_GR(
                grid_type, 
                nxl, 
                nyl, 
                x, 
                y, 
                dx, 
                dy, 
                area, 
                angle_dx, 
                angle_dy,
                shift_fac, 
                do_schmidt, 
                do_cube_transform, 
                stretch_factor, 
                target_lon, 
                target_lat,
                nest_grids, 
                parent_tile[0], 
                refine_ratio[0],
                istart_nest[0], 
                iend_nest[0], 
                jstart_nest[0], 
                jend_nest[0],
                halo, 
                output_length_angle,
            )
        else:
            create_gnomonic_cubic_grid(
                grid_type, 
                nxl, 
                nyl, 
                x, 
                y, 
                dx, 
                dy, 
                area, 
                angle_dx, 
                angle_dy,
                shift_fac, 
                do_schmidt, 
                do_cube_transform, 
                stretch_factor, 
                target_lon, 
                target_lat,
                nest_grids, 
                parent_tile, 
                refine_ratio,
                istart_nest, 
                iend_nest, 
                jstart_nest, 
                jend_nest,
                halo, 
                output_length_angle,
            )
    elif(my_grid_type==F_PLANE_GRID or my_grid_type==BETA_PLANE_GRID):
        create_f_plane_grid(
            &nxbnds, 
            &nybnds, 
            xbnds, 
            ybnds, 
            nlon, 
            nlat, 
            dx_bnds, 
            dy_bnds,
            use_legacy, 
            f_plane_latitude, 
            &isc, 
            &iec, 
            &jsc, 
            &jec, 
            x, 
            y, 
            dx, 
            dy, 
            area, 
            angle_dx, 
            center,
        )

    grid_data.write_data()

    if(mpp_pe() == mpp_root_pe() and verbose):
        print("generate_grid is run successfully")
    
    mpp_end()

    # End of main