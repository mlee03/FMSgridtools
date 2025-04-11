import sys
import os
import xarray as xr
import ctypes
import numpy as np
import numpy.typing as npt
import click

from pyfms import pyFMS, pyFMS_mpp, pyFMS_mpp_domains

from FMSgridtools.make_hgrid.hgridobj import HGridObj
from FMSgridtools.shared.gridtools_utils import check_file_is_there, get_provenance_attrs
from FREnctools_lib.pyfrenctools.make_hgrid.make_hgrid_util import (
    create_regular_lonlat_grid,
    create_grid_from_file,
    create_simple_cartesian_grid,
    create_spectral_grid,
    create_conformal_cubic_grid,
    create_gnomonic_cubic_grid_GR,
    create_gnomonic_cubic_grid,
    create_f_plane_grid,
    fill_cubic_grid_halo,
)
# from FREnctools_lib.pyfrenctools.shared.tool_util import get_legacy_grid_size

"""
Usage of make_hgrid

fmsgridtools make_hgrid --grid_type (see types supported below) (string)
                        --my_grid_file file_name (string)
                        --nxbnds #
                        --nybnds #
                        --xbnds x(1),...,x(nxbnds)
                        --ybnds y(1),...,y(nybnds)
                        --nlon nlon(1),...nlon(nxbnds-1)
                        --nlat nlat(1),...nlat(nybnds-1)
                        --dlon dlon(1),...dlon(nxbnds)
                        --dlat dlat(1),...dlat(nybnds)
                        --lat_join #
                        --num_lon #
                        --nratio #
                        --simple_dx #
                        --simple_dy #
                        --grid_name (string)
                        --center (string)
                        --verbose (bool)
                        --shift_fac #
                        --do_schmidt (bool)
                        --stretch_fac #
                        --target_lon #
                        --target_lat #
                        --do_cube_transform (bool)
                        --nest_grids #
                        --parent_tile parent_tile(1),...parent_tile(nests-1)
                        --refine_ratio refine_ratio(1),...refine_ratio(nests-1)
                        --halo #
                        --istart_nest istart_nest(1),...istart_nest(nests-1)
                        --iend_nest iend_nest(1),...iend_nest(nests-1)
                        --jstart_nest jstart_nest(1),...jstart_nest(nests-1)
                        --jend_nest jend_nest(1),...jend_nest(nests-1)
                        --use_great_circle_algorithm (bool)
                        --out_halo #
                        --no_output_length_angle (bool)

The available options for grid_type are:
    1. 'from_file':
            --my_grid_file must be specified. The grid
            specified in my_grid_file should be super grid
            vertex.
    2. 'spectral_grid'
    3. 'regular_lonlat_grid':
            --nxbnds, --nybnds --xbnds, --ybnds, must be
            specified to define the grid bounds.
    4  'conformal_cubic_grid'
    5  'gnomonic_ed'
    6. 'simple_cartesian_grid':
            --xbnds, --ybnds must be specified to define
            the grid bounds location and grid size. number
            of bounds must be 2 in both and x and y-direction. 
            --simple_dx and --simple_dy must be specified to 
            specify uniform cell length.
    7. 'f_plane_grid':
            For setting geometric fractors according
            to f-plane. f_plane_latitude need to be specified.
    8.  'beta_plane_grid':
            For setting geometric fractors according
            to  beta plane. f_plane_latitude need to be
            specified

Example use:
                                                                               
    1.  generating regular lon-lat grid (supergrid size 60x20)
            fmsgridtools make_hgrid --grid_type regular_lonlat_grid 
                                    --nxbnds 2
                                    --nybnds 2 
                                    --xbnds 0,30 
                                    --ybnds 50,60
                                    --nlon 60
                                    --nlat 20                           

    2.  generating tripolar grid with various grid resolution and C-cell
        centered using monotonic bi-cub spline interpolation.
            fmsgridtools make_hgrid --grid_type tripolar_grid
                                    --nxbnds 2 
                                    --nybnds 7 
                                    --xbnds -280,80  
                                    --ybnds -82,-30,-10,0,10,30,90 
                                    --nlon 720                      
                                    --nlat 104,48,40,40,48,120 
                                    --grid_name om3_grid               
                                    --center c_cell                                                                        
                                                                                   
    3.  generating simple cartesian grid(supergrid size 20x20)                     
            fmsgridtools make_hgrid --grid_type simple_cartesian_grid 
                                    --xbnds 0,30 
                                    --ybnds 50,60    
                                    --nlon 20 
                                    --nlat 20  
                                    --simple_dx 1000 
                                    --simple_dy 1000        
                                                                                   
    4.  generating conformal cubic grid. (supergrid size 60x60 for each tile)      
            fmsgridtools make_hgrid --grid_type conformal_cubic_grid 
                                    --nlon 60 
                                    --nratio 2         
                                                                                   
    5. generating gnomonic cubic grid with equal_dist_face_edge(C48 grid)         
            fmsgridtools make_hgrid --grid_type gnomonic_ed 
                                    --nlon 96                             
                                                                                   
    6. generating gnomonic cubic stretched grid.                                  
            fmsgridtools make_hgrid --grid_type gnomonic_ed 
                                    --nlon 180 
                                    --do_schmidt               
                                    --stretch_factor 3 
                                    --target_lat 40. 
                                    --target_lon 20.          
                                                                                   
    7. generating gnomonic cubic stretched grid with two nests on tile 6.         
            fmsgridtools make_hgrid --grid_type gnomonic_ed 
                                    --nlon 192 
                                    --do_schmidt               
                                    --stretch_factor 3 
                                    --target_lat 10. 
                                    --target_lon 20.          
                                    --nest_grids 2 
                                    --parent_tile 6,6 
                                    --refine_ratio 2,2           
                                    --istart_nest 11,51 
                                    --jstart_nest 11,51                       
                                    --iend_nest 42,82 
                                    --jend_nest 42,82 
                                    --halo 3                  
                                                                                   
    8. generating spectral grid. (supergrid size 128x64)                          
            fmsgridtools make_hgrid --grid_type spectral_grid 
                                    --nlon 128 
                                    --nlat 64                
                                                                                   
    9. Through user-defined grids                                             
            fmsgridtools make_hgrid --grid_type from_file 
                                    --my_grid_file my_grid_file             
                                    --nlon 4 
                                    --nlat 4                                             
                                                                                   
        Contents of a sample my_grid_file:                                           
            The first line of my_grid_file will be text ( will be ignored)          
            followed by nlon+1 lines of real value of x-direction supergrid bound   
            location. Then another line of text ( will be ignored), followed by     
            nlat+1 lines of real value of y-direction supergrid bound location.     
                                                                                   
            For example:                                                            
                                                                                   
                x-grid                                                               
                  0.0                                                                  
                  5.0                                                                  
                  10.0                                                                 
                  15.0                                                                 
                  20.0                                                                 
                y-grid                                                               
                 -10                                                                  
                  10                                                                   
                  20                                                                   
                  30                                                                   
                  40                                                                   
                                                                                   
    10. generating f_plane_grids                                                  
            fmsgridtools make_hgrid --grid_type f_plane_grid 
                                    --f_plane_latitude 55 
                                    --nxbnd 2      
                                    --nybnd 2 
                                    --xbnd 0,30 
                                    --ybnd 50,60  
                                    --nlon 60 
                                    --nlat 20       
                                                                                   
A note on generating cyclic regular lon-lat grids when center = 'c_cell':-      
It is possible to have an improperly centered boundary unless care is taken to  
ensure local symmetry at the join.                                              
A correctly formed grid is only guaranteed if the first three values of the     
--xbnd argument mirror the last 3 and the first two 'nlon' arguments mirror the 
last 2.                                                                         
                                                                                   
For example for a global grid make_hgrid should be invoked as                   
            fmsgridtools make_hgrid --grid_type regular_lonlat_grid ...                          
                                    --xbnd 0,X1,X2,...,360-X2,360-X1,360                         
                                    --nlon N1,N2,...,N2,N1 
                                    --center c_cell                       
                                                                                   
As an example                                                                   
                                                                                   
            fmsgridtools make_hgrid --grid_type regular_lonlat_grid 
                                    --nxbnd 7 
                                    --nybnd 2          
                                    --xbnd 0,15,30,300,330,345,360 
                                    --ybnd 50,60                  
                                    --nlon 4,2,6,4,2,4 
                                    --nlat 2 
                                    --center c_cell                  
                                                                                   
                                                                                   
results in a valid cyclic grid whereas (note the second last value of nlon)     
                                                                                   
            fmsgridtools make_hgrid --grid_type regular_lonlat_grid
                                    --nxbnd 7 
                                    --nybnd 2          
                                    --xbnd 0,15,30,300,330,345,360 
                                    --ybnd 50,60                  
                                    --nlon 4,2,6,4,4,4 
                                    --nlat 2 
                                    --center c_cell                  
                                                                                   
                                                                                   
is not properly centered across 0,360                                           
                                                                                   
An informational message is issued if the leftmost and rightmost  resolutions   
differ  by more than 1 part in 10E6
"""

MAXBOUNDS = 100
MAX_NESTS = 128
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


@click.command()
@click.option(
    "--grid_type", 
    type=str, 
    default="regular_lonlat_grid",
    help="specify type of topography. See above for grid type option.",
)
@click.option(
    "--my_grid_file", 
    type=str, 
    default=None,
    help="when this flag is present, the program will read grid information\
          from 'my_grid_file'. The file format can be ascii file or netcdf\
          file. Multiple file entry are allowed but the number should be\
          less than MAXBOUNDS.",
)
@click.option(
    "--nxbnds", 
    type=int, 
    default=2,
    help="Specify number of zonal regions for varying resolution.",
)
@click.option(
    "--nybnds", 
    type=int, 
    default=2,
    help="Specify number of meridinal regions for varying resolution.",
)
@click.option(
    "--xbnds",
    type=str,
    default=None,
    help="Specify boundaries for defining zonal regions of varying resolution.\
          When --tripolar is present, x also defines the longitude of the two\
          new poles. nxbnds must be 2 and lon_start = x(1), lon_end = x(nxbnds)\
          are longitude of the two new poles.",
)
@click.option(
    "--ybnds", 
    type=str, 
    default=None,
    help="Specify boundaries for defining meridional regions of varying\
          resolution",
)
@click.option(
    "--nlon", 
    type=str, 
    default=None,
    help="Number of model grid points(supergrid) for each zonal regions of\
          varying resolution.",
)
@click.option(
    "--nlat", 
    type=str, 
    default=None,
    help="Number of model grid points(supergid) for each meridinal regions of\
          varying resolution.",
)
@click.option(
    "--dlon", 
    type=str, 
    default=None,
    help="nominal resolution of zonal regions",
)
@click.option(
    "--dlat", 
    type=str, 
    default=None,
    help="nominal resolution of meridional regions",
)
@click.option(
    "--lat_join", 
    type=float, 
    default=65.,
    help="Specify latitude for joining spherical and rotated bipolar grid.\
          Default value is 65 degree.",
)
@click.option(
    "--nratio", 
    type=int, 
    default=1,
    help="Speicify the refinement ratio when calculating cell length and area\
          of supergrid.",
)
@click.option(
    "--simple_dx", 
    type=float, 
    default=0.,
    help="Specify the uniform cell length in x-direction for simple cartesian\
          grid.",
)
@click.option(
    "--simple_dy", 
    type=float, 
    default=0.,
    help="Specify the uniform cell length in y-direction for simple cartesian\
          grid.",
)
@click.option(
    "--grid_name", 
    type=str, 
    default="horizontal_grid",
    help=("Specify the grid name. The output grid file name will be" 
          "grid_name.nc if there is one tile and grid_name.tile#.nc if there is"
          "more than one tile. The default value will be horizontal_grid."),
)
@click.option(
    "--center", 
    type=str, 
    default="none",
    help="""Specify the center location of grid. Valid entries will be 'none'"
          ", 't_cell' or 'c_cell' with default value 'none'. The grid "
          "refinement is assumed to be 2 in x and y-direction when center is "
          "not 'none'. 'c_cell' should be used for the grid used in MOM.""",
)
@click.option(
    "--shift_fac", 
    type=float, 
    default=18.0, 
    help="shift west by 180/shift_fac. Default value is 18.",
)
@click.option(
    "--f_plane_latitude", 
    type=float, 
    default=100.,
    help=""
)
@click.option(
    "--do_schmidt", 
    is_flag=True, 
    default=False, 
    help=("Set to do Schmidt transformation to create stretched grid. When "
          "do_schmidt is set, the following must be set: --stretch_factor, "
          " --target_lon and --target_lat."),
)
@click.option(
    "--do_cube_transform", 
    is_flag=True, 
    default=False,
    help=("re-orient the rotated cubed sphere so that tile 6 has 'north' "
          "facing upward, which would make analysis and explaining nest "
          "placement much easier. When do_cube_transform is set, the "
          "following must be set: --stretch_factor, --latget_lon, and "
          " --target_lat."),
)
@click.option(
    "--stretch_factor", 
    type=float, 
    default=0.0,
    help="Stretching factor for the grid",
)
@click.option(
    "--target_lon", 
    type=float, 
    default=0.0,
    help="center longitude of the highest resolution tile",
)
@click.option(
    "--target_lat", 
    type=float, 
    default=0.0,
    help="center latitude of the highest resolution tile",
)
@click.option(
    "--nest_grids", 
    type=int, 
    default=0,
    help="""set to create this # nested grids as well as the global grid. This 
          replaces the option --nest_grid. This option could only be set when  
          grid_type is 'gnomonic_ed'. When it is set, besides 6 tile grid ,
          files created, there are # more nest grids with 
          file name = grid_name.tile.nest.nc""",
)
@click.option(
    "--parent_tile", 
    type=str, 
    default=None, 
    help="Specify the comma-separated list of the parent tile number(s) of \
        nest grid(s).",
)
@click.option(
    "--refine_ratio", 
    type=str, 
    default=None, 
    help="Specify the comma-separated list of refinement ratio(s) for nest\
          grid(s).",
)
@click.option(
    "--istart_nest", 
    type=str, 
    default=None,
    help="Specify the comma-separated list of starting i-direction index(es)\
          of nest grid(s) in parent tile supergrid(Fortran index).",
)
@click.option(
    "--iend_nest", 
    type=str, 
    default=None, 
    help="Specify the comma-separated list of ending i-direction index(es) of \
        nest grids in parent tile supergrid( Fortran index).",
)
@click.option(
    "--jstart_nest", 
    type=str, 
    default=None,
    help="Specify the comma-separated list of starting j-direction index(es) of \
        nest grids in parent tile supergrid(Fortran index).",
)
@click.option(
    "--jend_nest", 
    type=str, 
    default=None,
    help="Specify the comma-separated list of ending j-direction index(es) of \
        nest grids in parent tile supergrid (Fortran index).",
)
@click.option(
    "--halo", 
    type=int, 
    default=0, 
    help=("halo size is used in the atmosphere cubic sphere model. Its purpose "
          "is to make sure the nest, including the halo region, is fully "
          "contained within a single parent (coarse) tile. The option may "
          "be obsolete and removed in future development. It only needs to "
          "be specified when --nest_grid(s) is set."),
)
@click.option(
    "--use_great_circle_algorithm", 
    is_flag=True, 
    default=False,
    help="When specified, great_circle_algorithm will be used to compute grid \
         cell area.",
)
@click.option(
    "--out_halo", 
    type=int, 
    default=0,
    help="extra halo size data to be written out. This is only works for \
         gnomonic_ed.",
)
@click.option(
    "--no_output_length_angle",
    is_flag=True, 
    default=False,
    help="When specified, will not output length(dx,dy) and angle \
         (angle_dx, angle_dy)"
)
@click.option(
    "--angular_midpoint", 
    is_flag=True,
    default=False,
    help=""
)
@click.option(
    "--rotate_poly",
    is_flag=True, 
    default=False,
    help=("Set to calculate polar polygon areas by calculating the area of a "
          "copy of the polygon, with the copy being rotated far away from the" 
          "pole.")
)
@click.option(
    "--verbose", 
    is_flag=True, 
    default=False,
    help=("Will print out running time message when this option is set. "
          "Otherwise the run will be silent when there is no error.")
)
def make_hgrid(
    grid_type: str,
    my_grid_file: str,
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
    do_schmidt: bool,
    do_cube_transform: bool,
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
    use_great_circle_algorithm: bool,
    out_halo: int,
    no_output_length_angle: bool,
    angular_midpoint: bool,
    rotate_poly: bool,
    verbose: bool,
):
    nratio = 1
    method = "conformal"
    orientation = "center_pole"
    nxbnds0 = nxbnds
    nybnds0 = nybnds
    nxbnds1 = 0
    nybnds1 = 0
    nxbnds2 = 0
    nybnds2 = 0
    nxbnds3 = 0
    nybnds3 = 0

    num_nest_args = 0
    nn = 0

    present_stretch_factor = 0
    present_target_lon = 0
    present_target_lat = 0
    output_length_angle = 1
    ntiles = 1
    ntiles_global = 1
    ntiles_file = 0
    grid_obj = HGridObj()

    center = "none"
    geometry = "spherical"
    projection = "none"
    arcx = "small_circle"
    north_pole_tile = "0.0 90.0"
    north_pole_arcx = "0.0 90.0"
    discretization = "logically_rectangular"
    conformal = "true"

    fms_file = "input.nml"
    with open(fms_file, "x") as file:
        file.write("")

    #TODO: Will change after pyFMS refactor
    pyfms = pyFMS(cFMS_path="./pyFMS/cFMS/libcFMS/.libs/libcFMS.so")
    mpp = pyFMS_mpp(cFMS=pyfms.cFMS)
    mpp_domains = pyFMS_mpp_domains(cFMS=pyfms.cFMS)

    if(mpp.npes() > 1):
        mpp.pyfms_error(errortype=2, errormsg="make_hgrid: make_hgrid must be run one processor, contact developer")

    if xbnds is not None:
        xbnds = np.fromstring(xbnds, dtype=np.float64, sep=',')
        nxbnds1 = xbnds.size
    else:
        xbnds = np.empty(shape=100, dtype=np.float64, order="C")

    if ybnds is not None:
        ybnds = np.fromstring(ybnds, dtype=np.float64, sep=',')
        nybnds1 = ybnds.size
    else:
        ybnds = np.empty(shape=100, dtype=np.float64, order="C")
    
    if nlon is not None:
        nlon = np.fromstring(nlon, dtype=np.int32, sep=',')
        nxbnds2 = nlon.size

    if nlat is not None:
        nlat = np.fromstring(nlat, dtype=np.int32, sep=',')
        nybnds2 = nlat.size

    if dlon is not None:
        dx_bnds = np.fromstring(dlon, dtype=np.float64, sep=',')
        nxbnds3 = dx_bnds.size
    else:
        dx_bnds = np.zeros(shape=100, dtype=np.float64, order="C")
        
    if dlat is not None:
        dy_bnds = np.fromstring(dlat, dtype=np.float64, sep=',')
        nybnds3 = dy_bnds.size
    else:
        dy_bnds = np.zeros(shape=100, dtype=np.float64, order="C")

    if stretch_factor != 0.0:
        present_stretch_factor = 1

    if target_lon != 0.0:
        present_target_lon = 1

    if target_lat != 0.0:
        present_target_lat = 1

    if refine_ratio is not None:
        refine_ratio = np.fromstring(refine_ratio, dtype=np.int32, sep=',')
        num_nest_args = refine_ratio.size

    if parent_tile is not None:
        parent_tile = np.fromstring(refine_ratio, dtype=np.int32, sep=',')
        num_nest_args = parent_tile.size

    if istart_nest is not None:
        istart_nest = np.fromstring(istart_nest, dtype=np.int32, sep=',')
        num_nest_args = istart_nest.size

    if iend_nest is not None:
        iend_nest = np.fromstring(iend_nest, dtype=np.int32, sep=',')
        num_nest_args = iend_nest.size

    if jstart_nest is not None:
        jstart_nest = np.fromstring(jstart_nest, dtype=np.int32, sep=',')
        num_nest_args = jstart_nest.size

    if jend_nest is not None:
        jend_nest = np.fromstring(jend_nest, dtype=np.int32, sep=',')
        num_nest_args = jend_nest.size

    if no_output_length_angle:
        output_length_angle = 0

    if angular_midpoint:
        use_angular_midpoint = 1

    if my_grid_file is not None:
        my_grid_file = np.array(my_grid_file.split(','))
        ntiles_file = my_grid_file.size

    # TODO: rotate_poly?

    if mpp.pe() == 0 and verbose:
        print(f"==>NOTE: the grid type is {grid_type}")

    if grid_type == "regular_lonlat_grid":
        my_grid_type = REGULAR_LONLAT_GRID
    elif grid_type == "from_file":
        my_grid_type = FROM_FILE
    elif grid_type == "simple_cartesian_grid":
        my_grid_type = SIMPLE_CARTESIAN_GRID
    elif grid_type == "spectral_grid":
        my_grid_type = SPECTRAL_GRID
    elif grid_type == "conformal_cubic_grid":
        my_grid_type = CONFORMAL_CUBIC_GRID
    elif grid_type == "gnomonic_ed":
        my_grid_type = GNOMONIC_ED
    elif grid_type == "f_plane_grid":
        my_grid_type = F_PLANE_GRID
    elif grid_type == "beta_plane_grid":
        my_grid_type = BETA_PLANE_GRID
    else:
        mpp.pyfms_error(errotype=2, errormsg="make_hgrid: only grid_type = 'regular_lonlat_grid', 'tripolar_grid', 'from_file', 'gnomonic_ed', 'conformal_cubic_grid', 'simple_cartesian_grid', 'spectral_grid', 'f_plane_grid' and 'beta_plane_grid' is implemented")
        
    if my_grid_type != GNOMONIC_ED and out_halo != 0:
        mpp.pyfms_error(errortype=2, errormsg="make_hgrid: out_halo should not be set when grid_type = gnomonic_ed")
    if out_halo != 0 and out_halo != 1:
        mpp.pyfms_error(errortype=2, errormsg="make_hgrid: out_halo should be 0 or 1")

    if my_grid_type != GNOMONIC_ED and do_schmidt:
        mpp.pyfms_error(errortype=2, errormsg="make_hgrid: --do_schmidt should not be set when grid_type is not 'gnomonic_ed'")

    if my_grid_type != GNOMONIC_ED and do_cube_transform:
        mpp.pyfms_error(errortype=2, errormsg="make_hgrid: --do_cube_transform should not be set when grid_type is not 'gnomonic_ed'")

    if do_cube_transform and do_schmidt:
        mpp.pyfms_error(errortype=2, errormsg="make_hgrid: both --do_cube_transform and --do_schmidt are set")
    
    use_legacy = 0

    """
    Command line argument check
    """

    if my_grid_type == REGULAR_LONLAT_GRID or my_grid_type == F_PLANE_GRID or my_grid_type == BETA_PLANE_GRID:
        nxbnds = nxbnds0
        nybnds = nybnds0
        if nxbnds < 2 or nybnds < 2:
            mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'regular_lonlat_grid', 'tripolar_grid', 'f_plane_grid' or 'beta_plane_grid', both nxbnds and nybnds should be no less than 2")
        if nxbnds != nxbnds1:
            mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'regular_lonlat_grid, 'tripolar_grid', 'f_plane_grid' or 'beta_plane_grid', nxbnds does not match number of entry in xbnds")
        if nybnds != nybnds1:
            mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'regular_lonlat_grid, 'tripolar_grid', 'f_plane_grid' or 'beta_plane_grid', nybnds does not match number of entry in ybnds")
        
        num_specify = 0
        if nxbnds2 > 0 and nybnds2 > 0:
            num_specify += 1
        if nxbnds3 > 0 and nybnds3 > 0:
            num_specify += 1
            use_legacy = 1
        
        if num_specify == 0:
            mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'regular_lonlat_grid', 'tripolar_grid', 'f_plane_grid' or 'beta_plane_grid', need to specify one of the pair --nlon --nlat or --dlon --dlat")
        if num_specify == 2:
            mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'regular_lonlat_grid', 'tripolar_grid', 'f_plane_grid' or 'beta_plane_grid', can not specify both --nlon --nlat and --dlon --dlat")
        if use_legacy:
            if nxbnds != nxbnds3:
                mpp.pfms_error(errortype=2, errormsg="make_hgrid: grid type is 'tripolar_grid', 'tripolar_grid', 'f_plane_grid' or 'beta_plane_grid', nxbnds does not match number of entry in dlon")
            if nybnds != nybnds3:
                mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'tripolar_grid', 'tripolar_grid', 'f_plane_grid' or 'beta_plane_grid', nybnds does not match number of entry in dlat")
        else:
            if nxbnds != nxbnds2+1:
                mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'tripolar_grid', 'tripolar_grid', 'f_plane_grid' or 'beta_plane_grid', nxbnds does not match number of entry in nlon")
            if nybnds != nybnds2+1:
                mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'tripolar_grid', 'tripolar_grid', 'f_plane_grid' or 'beta_plane_grid', nybnds does not match number of entry in nlat")

    # if my_grid_type == CONFORMAL_CUBIC_GRID or my_grid_type == GNOMONIC_ED:
    #     ntiles = 6
    #     ntiles_global = 6

    # if my_grid_type != GNOMONIC_ED and nest_grids:
    #     mpp.pyfms_error(errortype=2, errormsg="make_hgrid: --nest_grids can be set only when grid_type = 'gnomonic_ed'")

    # elif my_grid_type == FROM_FILE:
    #     if ntiles_file == 0:
    #         mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid_type is 'from_file', but my_grid_file is not specified")
    #     ntiles = ntiles_file
    #     ntiles_global = ntiles_file
    #     for n in range(ntiles):
    #         if ".nc" in my_grid_file[n]:
    #             file_path = my_grid_file[n] + ".nc"
    #             check_file_is_there(file_path)
    #             with xr.open_dataset(file_path) as ds:
    #                 if "grid_xt" in ds.sizes:
    #                     if "grid_yt" not in ds.sizes:
    #                         mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid_yt should be a dimension when grid_xt is a dimension")
    #                     nlon[n] = ds.sizes["grid_xt"]*2
    #                     nlat[n] = ds.sizes["grid_yt"]*2
    #                 elif "rlon" in ds.sizes:
    #                     if "rlat" not in ds.sizes:
    #                         mpp.pyfms_error(errortype=2, errormsg="make_hgrid: rlat should be a dimension when rlon is a dimension")
    #                     nlon[n] = ds.sizes["rlon"]*2
    #                     nlat[n] = ds.sizes["rlat"]*2
    #                 elif "lon" in ds.sizes:
    #                     if "lat" not in ds.sizes:
    #                         mpp.pyfms_error(errortype=2, errormsg="make_hgrid: lat should be a dimension when lon is a dimension")
    #                     nlon[n] = ds.sizes["lon"]*2
    #                     nlat[n] = ds.sizes["lat"]*2
    #                 elif "i" in ds.sizes:
    #                     if "j" not in ds.sizes:
    #                         mpp.pyfms_error(errortype=2, errormsg="make_hgrid: j should be a dimension when i is a dimension")
    #                     nlon[n] = ds.sizes["i"]*2
    #                     nlat[n] = ds.sizes["j"]*2
    #                 elif "x" in ds.sizes:
    #                     if "y" not in ds.sizes:
    #                         mpp.pyfms_error(errortype=2, errormsg="make_hgrid: y should be a dimension when x is a dimension")
    #                     nlon[n] = ds.sizes["x"]*2
    #                     nlat[n] = ds.sizes["y"]*2
    #                 else:
    #                     mpp.pyfms_error(errortype=2, errormsg="make_hgrid: none of grid_xt, rlon, lon, x, and i is a dimension in input file")
    #         else:
    #             if nxbnds2 != ntiles or nybnds2 != ntiles:
    #                 mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'from_file', number entry entered through --nlon and --nlat should be equal to number of files specified through --my_grid_file")
    #     """
    #     For simplification purposes, it is assumed at this point that all tiles will have the same grid size
    #     """
    #     for n in range(1, ntiles):
    #         if nlon[n] != nlon[0] or nlat[n] != nlat[0]:
    #             mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid_type is from_file, all the tiles should have same grid size, contact developer")
    # elif my_grid_type == SIMPLE_CARTESIAN_GRID:
    #     geometry = "planar"
    #     north_pole_tile = "none"
    #     if nxbnds1 != 2 or nybnds1 != 2:
    #         mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'simple_cartesian_grid', number entry entered through --xbnds and --ybnds should be 2")
    #     if nxbnds2 != 1 or nybnds2 != 1:
    #         mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'simple_cartesian_grid', number entry entered through --nlon and --nlat should be 1")
    #     if simple_dx == 0 or simple_dy == 0:
    #         mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid_type is 'simple_cartesian_grid', both simple_dx and simple_dy both should be specified")
    # elif my_grid_type == SPECTRAL_GRID:
    #     if nxbnds2 != 1 or nybnds2 != 1:
    #         mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'spectral_grid', number entry entered through --nlon and --nlat should be 1")
    # elif my_grid_type == CONFORMAL_CUBIC_GRID:
    #     projection = "cube_gnomonic"
    #     conformal = "FALSE"
    #     if nxbnds2 != 1:
    #         mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'conformal_cubic_grid', number entry entered through --nlon should be 1")
    #     if nratio < 1:
    #         mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'conformal_cubic_grid', nratio should be a positive integer")
    # elif my_grid_type == GNOMONIC_ED:
    #     projection = "cube_gnomonic"
    #     conformal = "FALSE"
    #     if do_schmidt or do_cube_transform:
    #         if present_stretch_factor == 0 or present_target_lon == 0 or present_target_lat == 0:
    #             mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'gnomonic_ed, --stretch_factor, --target_lon and --target_lat must be set when --do_schmidt or --do_cube_transform is set")
    #     for n in range(nest_grids):
    #         if refine_ratio[n] == 0:
    #             mpp.pyfms_error(errortype=2, errormsg="make_hgrid: --refine_ratio must be set when --nest_grids is set")
    #         if parent_tile[n] == 0 and mpp.pe() == 0:
    #             print("NOTE from make_hgrid: parent_tile is 0, the output grid will have resolution refine_ration*nlon", file=sys.stderr)
    #         else:
    #             if istart_nest[n] == 0:
    #                 mpp.pyfms_error(errortype=2, errormsg="make_hgrid: --istart_nest must be set when --nest_grids is set")
    #             if iend_nest[n] == 0:
    #                 mpp.pyfms_error(errortype=2, errormsg="make_hgrid: --iend_nest must be set when --nest_grids is set")
    #             if jstart_nest[n] == 0:
    #                 mpp.pyfms_error(errortype=2, errormsg="make_hgrid: --jstart_nest must be set when --nest_grids is set")
    #             if jend_nest[n] == 0:
    #                 mpp.pyfms_error(errortype=2, errormsg="make_hgrid: --jend_nest must be set when --nest_grids is set")
    #             if halo == 0:
    #                 mpp.pyfms_error(errortype=2, errormsg="make_hgrid: --halo must be set when --nest_grids is set")
    #             ntiles += 1
    #             if verbose:
    #                 print(f"Configuration for nest {ntiles} validated.", file=sys.stderr)
    #     if verbose:
    #         print(f"Updated number of tiles, including nests (ntiles): {ntiles}", file=sys.stderr)
    #     if nxbnds2 != 1:
    #         mpp.pyfms_error(errortype=2, errormsg="make_hgrid: grid type is 'gnomonic_cubic_grid', number entry entered through --nlon should be 1")
    # elif my_grid_type == F_PLANE_GRID or my_grid_type == BETA_PLANE_GRID:
    #     if f_plane_latitude > 90 or f_plane_latitude < -90:
    #         mpp.pyfms_error(errortype=2, errormsg="make_hgrid: f_plane_latitude should be between -90 and 90.")
    #     if f_plane_latitude > ybnds[nybnds-1] or f_plane_latitude < ybnds[0]:
    #         if mpp.pe() == 0:
    #             print("Warning from make_hgrid: f_plane_latitude is not inside the latitude range of the grid", file=sys.stderr)
    #     if mpp.pe() == 0:
    #         print(f"make_hgrid: setting geometric factor according to f-plane with f_plane_latitude = {f_plane_latitude}", file=sys.stderr)
    # else:
    #     mpp.pyfms_error(errortype=2, errormsg="make_hgrid: passed grid type is not implemented")

    if verbose:
        print(f"[INFO] make_hgrid: Number of tiles (ntiles): {ntiles}", file=sys.stderr)
        print(f"[INFO] make_hgrid: Number of global tiles (ntiles_global): {ntiles_global}", file=sys.stderr)

    nxl = np.empty(shape=ntiles, dtype=np.int32)
    nyl = np.empty(shape=ntiles, dtype=np.int32)

    """
    Get super grid size
    """
    if my_grid_type == GNOMONIC_ED or my_grid_file == CONFORMAL_CUBIC_GRID:
        for n in range(ntiles_global):
            nxl[n] = nlon[0]
            nyl[n] = nxl[n]
            if nest_grids and parent_tile[0] == 0:
                nxl[n] *= refine_ratio[0]
                nyl[n] *= refine_ratio[0]

        for n in range(ntiles_global, ntiles):
            nn = n - ntiles_global
            nxl[n] = (iend_nest[nn] - istart_nest[nn] + 1) * refine_ratio[nn]
            nyl[n] = (jend_nest[nn] - jstart_nest[nn] + 1) * refine_ratio[nn]
    elif my_grid_type == FROM_FILE:
        for n in range(ntiles_global):
            nxl[n] = nlon[n]
            nyl[n] = nlat[n]
    else:
        nxl[0] = 0
        nyl[0] = 0
        for n in range(nxbnds - 1):
            nxl[0] += nlon[n]
        for n in range(nybnds - 1):
            nyl[0] += nlat[n]

    nx = nxl[0]
    ny = nyl[0]
    nxp = nx + 1
    nyp = ny + 1

    if center == "none" and center == "c_cell" and center == "t_cell":
        mpp.pyfms_error(errortype=2, errormsg="make_hgrid: center should be 'none', 'c_cell' or 't_cell' ")

    # --non_length_angle should only be set when grid_type == GNOMONIC_ED
    if not output_length_angle and my_grid_type != GNOMONIC_ED:
        mpp.pyfms_error(errortype=2, errormsg="make_hgrid: --no_length_angle is set but grid_type is not 'gnomonic_ed'")

    """
    Create grid information
    """

    for n_nest in range(ntiles):
        print(f"[INFO] tile: {n_nest}, nxl[{nxl[n_nest]}], nyl[{nyl[n_nest]}], ntiles: {ntiles}", file=sys.stderr)

    size1 = ctypes.c_ulong(0)
    size2 = ctypes.c_ulong(0)
    size3 = ctypes.c_ulong(0)
    size4 = ctypes.c_long(0)

    if my_grid_type == FROM_FILE:
        for n in range(ntiles_global):
            size1.value += (nlon[n] + 1) * (nlat[n] + 1)
            size2.value += (nlon[n] + 1) * (nlat[n] + 1 + 1)
            size3.value += (nlon[n] + 1 +1) * (nlat[n] + 1)
            size4.value += (nlon[n] + 1) * (nlat[n] + 1)
    else:
        size1 = ctypes.c_ulong(nxp * nyp * ntiles_global)
        size2 = ctypes.c_ulong(nxp * (nyp + 1) * ntiles_global)
        size3 = ctypes.c_ulong((nxp + 1) * nyp * ntiles_global)
        size4 = ctypes.c_ulong(nxp * nyp * ntiles_global)

    if not (nest_grids == 1 and parent_tile[0] == 0):
        for n_nest  in range(ntiles_global, ntiles_global+nest_grids):
            if verbose:
                print(f"[INFO] Adding memory size for nest {n_nest}, nest_grids: {nest_grids}", file=sys.stderr)
            size1.value += (nxl[n_nest]+1) * (nyl[n_nest]+1)
            size2.value += (nxl[n_nest]+1) * (nyl[n_nest]+2)
            size3.value += (nxl[n_nest]+2) * (nyl[n_nest]+1)
            size4.value += (nxl[n_nest]+1) * (nyl[n_nest]+1)

    if verbose:
        print(f"[INFO] Allocating arrays of size {size1.value} for x, y based on nxp: {nxp} nyp: {nyp} ntiles: {ntiles}", file=sys.stderr)
    grid_obj.x = np.empty(shape=size1.value, dtype=np.float64)
    grid_obj.y = np.empty(shape=size1.value, dtype=np.float64)
    grid_obj.area = np.empty(shape=size4.value, dtype=np.float64)
    grid_obj.arcx = arcx
    if output_length_angle:
        grid_obj.dx = np.empty(shape=size2.value, dtype=np.float64)
        grid_obj.dy = np.empty(shape=size3.value, dtype=np.float64)
        grid_obj.angle_dx = np.empty(shape=size1.value, dtype=np.float64)
        if conformal != "true":
            grid_obj.angle_dy = np.empty(shape=size1.value, dtype=np.float64)

    isc = 0
    iec = nx - 1
    jsc = 0
    jec = ny - 1

    if(my_grid_type==REGULAR_LONLAT_GRID):
        create_regular_lonlat_grid(
            nxbnds, 
            nybnds, 
            xbnds, 
            ybnds, 
            nlon, 
            nlat, 
            dx_bnds, 
            dy_bnds,
            use_legacy, 
            isc, 
            iec, 
            jsc, 
            jec, 
            grid_obj.x, 
            grid_obj.y, 
            grid_obj.dx, 
            grid_obj.dy, 
            grid_obj.area,
            grid_obj.angle_dx, 
            center,
            use_great_circle_algorithm,
        )
    # elif(my_grid_type==FROM_FILE):
    #     for n in range(ntiles):
    #         n1 = n * nxp * nyp
    #         n2 = n * nx * nyp
    #         n3 = n * nxp * ny
    #         n4 = n * nx * ny
    #         create_grid_from_file(
    #             my_grid_file[n], 
    #             nx, 
    #             ny, 
    #             grid_obj.x[n1:], 
    #             grid_obj.y[n1:], 
    #             grid_obj.dx[n2:], 
    #             grid_obj.dy[n3:], 
    #             grid_obj.area[n4:], 
    #             grid_obj.angle_dx[n1:], 
    #             use_great_circle_algorithm, 
    #             use_angular_midpoint,
    #         )
    # elif(my_grid_type==SIMPLE_CARTESIAN_GRID):
    #     create_simple_cartesian_grid(
    #         xbnds, 
    #         ybnds, 
    #         nx, 
    #         ny, 
    #         simple_dx, 
    #         simple_dy, 
    #         isc, 
    #         iec, 
    #         jsc, 
    #         jec,
    #         grid_obj.x, 
    #         grid_obj.y, 
    #         grid_obj.dx, 
    #         grid_obj.dy, 
    #         grid_obj.area, 
    #         grid_obj.angle_dx,
    #     )
    # elif(my_grid_type==SPECTRAL_GRID):
    #     create_spectral_grid(
    #         nx, 
    #         ny, 
    #         isc, 
    #         iec, 
    #         jsc, 
    #         jec, 
    #         grid_obj.x, 
    #         grid_obj.y, 
    #         grid_obj.dx, 
    #         grid_obj.dy, 
    #         grid_obj.area, 
    #         grid_obj.angle_dx, 
    #         use_great_circle_algorithm,
    #     )
    # elif(my_grid_type==CONFORMAL_CUBIC_GRID):
    #     create_conformal_cubic_grid(
    #         nx, 
    #         nratio, 
    #         method, 
    #         orientation, 
    #         grid_obj.x, 
    #         grid_obj.y, 
    #         grid_obj.dx, 
    #         grid_obj.dy, 
    #         grid_obj.area, 
    #         grid_obj.angle_dx, 
    #         grid_obj.angle_dy,
    #     )
    # elif(my_grid_type==GNOMONIC_ED):
    #     if(nest_grids == 1 and parent_tile[0] == 0):
    #         create_gnomonic_cubic_grid_GR(
    #             grid_type, 
    #             nxl, 
    #             nyl, 
    #             grid_obj.x, 
    #             grid_obj.y, 
    #             grid_obj.dx, 
    #             grid_obj.dy, 
    #             grid_obj.area, 
    #             grid_obj.angle_dx, 
    #             grid_obj.angle_dy,
    #             shift_fac, 
    #             do_schmidt, 
    #             do_cube_transform, 
    #             stretch_factor, 
    #             target_lon, 
    #             target_lat,
    #             nest_grids, 
    #             parent_tile[0], 
    #             refine_ratio[0],
    #             istart_nest[0], 
    #             iend_nest[0], 
    #             jstart_nest[0], 
    #             jend_nest[0],
    #             halo, 
    #             output_length_angle,
    #         )
    #     else:
    #         create_gnomonic_cubic_grid(
    #             grid_type, 
    #             nxl, 
    #             nyl, 
    #             grid_obj.x, 
    #             grid_obj.y, 
    #             grid_obj.dx, 
    #             grid_obj.dy, 
    #             grid_obj.area, 
    #             grid_obj.angle_dx, 
    #             grid_obj.angle_dy,
    #             shift_fac, 
    #             do_schmidt, 
    #             do_cube_transform, 
    #             stretch_factor, 
    #             target_lon, 
    #             target_lat,
    #             nest_grids, 
    #             parent_tile, 
    #             refine_ratio,
    #             istart_nest, 
    #             iend_nest, 
    #             jstart_nest, 
    #             jend_nest,
    #             halo, 
    #             output_length_angle,
    #         )
    # elif(my_grid_type==F_PLANE_GRID or my_grid_type==BETA_PLANE_GRID):
    #     create_f_plane_grid(
    #         nxbnds, 
    #         nybnds, 
    #         xbnds, 
    #         ybnds, 
    #         nlon, 
    #         nlat, 
    #         dx_bnds, 
    #         dy_bnds,
    #         use_legacy, 
    #         f_plane_latitude, 
    #         isc, 
    #         iec, 
    #         jsc, 
    #         jec, 
    #         grid_obj.x, 
    #         grid_obj.y, 
    #         grid_obj.dx, 
    #         grid_obj.dy, 
    #         grid_obj.area, 
    #         grid_obj.angle_dx, 
    #         center,
    #     )
    else:
        mpp.pyfms_error(errortype=2, errormsg="make_hgrid: passed grid type is not implemented")


    """
    Write out data
    """
    pos_c = 0
    pos_e = 0
    pos_t = 0
    pos_n = 0
    for n in range(ntiles):
        grid_obj.tile = "tile" + str(n+1)
        if ntiles > 1:
            outfile = grid_name + ".tile" + ".nc" + str(n+1)
        else:
            outfile = grid_name + ".nc"
        
        if verbose:
            print(f"Writing out {outfile}", file=sys.stderr)
        
        nx = nxl[n]
        ny = nyl[n]
        if verbose:
            print(f"[INFO] Outputting arrays of size nx: {nx} and ny: {ny} for tile: {n}", file=sys.stderr)
        nxp = nx + 1
        nyp = ny + 1

        if out_halo == 0:
            if verbose:
                print(f"[INFO] START NC XARRAY write out_halo=0 tile number = n: {n} offset = pos_c: {pos_c}", file=sys.stderr)
                print(f"[INFO] XARRAY: n: {n} x[0]: {grid_obj.x[pos_c]} x[1]: {grid_obj.x[pos_c+1]} x[2]: {grid_obj.x[pos_c+2]} x[3]: {grid_obj.x[pos_c+3]} x[4]: {grid_obj.x[pos_c+4]} x[5]: {grid_obj.x[pos_c+5]} x[10]: {grid_obj.x[pos_c+10]}", file=sys.stderr)
                if n > 0:
                    print(f"[INFO] XARRAY: n: {n} x[0]: {grid_obj.x[pos_c]} x[-1]: {grid_obj.x[pos_c-1]} x[-2]: {grid_obj.x[pos_c-2]} x[-3]: {grid_obj.x[pos_c-3]} x[-4]: {grid_obj.x[pos_c-4]} x[-5]: {grid_obj.x[pos_c-5]} x[-10]: {grid_obj.x[pos_c-10]}", file=sys.stderr)
            grid_obj.x = grid_obj.x[pos_c:]
            grid_obj.y = grid_obj.y[pos_c:]
            if output_length_angle:
                grid_obj.dx = grid_obj.dx[pos_n:]
                grid_obj.dy = grid_obj.dy[pos_e:]
                grid_obj.angle_dx = grid_obj.angle_dx[pos_c:]
                if conformal != "true":
                    grid_obj.angle_dy = grid_obj.angle_dy[pos_c:]
            grid_obj.area = grid_obj.area[pos_t:]
        else:
            tmp = np.empty(shape=(nxp+2*out_halo)*(nyp+2*out_halo), dtype=np.float64)
            if verbose:
                print(f"[INFO] INDEX NC write with halo tile number = n: {n}", file=sys.stderr)
            fill_cubic_grid_halo(nx, ny, out_halo, tmp, grid_obj.x, grid_obj.x, n, 1, 1)
            grid_obj.x = tmp.copy()
            fill_cubic_grid_halo(nx, ny, out_halo, tmp, grid_obj.y, grid_obj.y, n, 1, 1)
            grid_obj.y = tmp.copy()
            if output_length_angle:
                fill_cubic_grid_halo(nx, ny, out_halo, tmp, grid_obj.angle_dx, grid_obj.angle_dx, n, 1, 1)
                grid_obj.angle_dx = tmp.copy()
                if conformal != "true":
                    fill_cubic_grid_halo(nx, ny, out_halo, tmp, grid_obj.angle_dy, grid_obj.angle_dy, n, 1, 1)
                    grid_obj.angle_dy = tmp.copy()
                fill_cubic_grid_halo(nx, ny, out_halo, tmp, grid_obj.dx, grid_obj.dy, n, 0, 1)
                grid_obj.dx = tmp.copy()
                fill_cubic_grid_halo(nx, ny, out_halo, tmp, grid_obj.dy, grid_obj.dx, n, 1, 0)
                grid_obj.dy = tmp.copy()
            fill_cubic_grid_halo(nx, ny, out_halo, tmp, grid_obj.area, grid_obj.area, n, 0, 0)
            grid_obj.area = tmp.copy()

        if verbose:
            print(f"About to close {outfile}")

        nx = nxl[n]
        ny = nyl[n]
        nxp = nx + 1
        nyp = ny + 1

        if verbose:
            print(f"[INFO] INDEX Before increment n: {n} pos_c {pos_c} nxp {nxp} nyp {nyp} nxp*nyp {nxp*nyp}", file=sys.stderr)
        pos_c += nxp*nyp
        if verbose:
            print(f"[INFO] INDEX After increment n: {n} pos_c {pos_c}.", file=sys.stderr)
        pos_e += nxp*ny
        pos_n += nx*nyp
        pos_t += nx*ny

    prov_attrs = get_provenance_attrs(great_circle_algorithm=use_great_circle_algorithm)
    grid_obj.write_out_hgrid(
        outfile=outfile,
        nx=nx,
        ny=ny,
        nxp=nxp,
        nyp=nyp,
        global_attrs=prov_attrs,
        north_pole_tile=north_pole_tile,
        north_pole_arcx=north_pole_arcx,
        projection=projection,
        geometry=geometry,
        discretization=discretization,
        conformal=conformal,
        out_halo=out_halo,
        output_length_angle=output_length_angle,
    )

    if(mpp.pe() == 0 and verbose):
        print("generate_grid is run successfully")

    pyfms.pyfms_end()

    os.remove(fms_file)
    

    # End of main

    if __name__ == "__main__":
        make_hgrid()