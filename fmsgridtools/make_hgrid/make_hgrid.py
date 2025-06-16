import click

import fmsgridtools.make_hgrid.lonlat_grid as lonlat_grid
import fmsgridtools.make_hgrid.gnomonic_grid as gnomonic_grid


@click.group()
def make_hgrid():
    """Make H-Grid CLI"""

@make_hgrid.command()
@click.option(
    "--nlon", 
    type=str, 
    default=None,
    help="Comma separated list of model grid points(supergrid) for each zonal regions of varying resolution.",
)
@click.option(
    "--nlat", 
    type=str, 
    default=None,
    help="Comma separated of model grid points(supergid) for each meridinal regions of varying resolution.",
)
@click.option(
    "--xbnds",
    type=str,
    default=None,
    help="Specify boundaries for defining zonal regions of varying resolution."
)
@click.option(
    "--ybnds", 
    type=str, 
    default=None,
    help="Specify boundaries for defining meridional regions of varying resolution",
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
    "--use_great_circle_algorithm", 
    is_flag=True, 
    default=False,
    help="When specified, great_circle_algorithm will be used to compute grid cell area.",
)
@click.option(
    "--grid_name",
    type=str,
    default="horizontal_grid",
    help="""
    Specify the grid name. The output grid file name will be grid_name.nc if there is one tile and 
    grid_name.tile#.nc if there is more than one tile. The default value will be 'horizontal_grid'.
    """,
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
)
def lonlat(
    nlon: str, 
    nlat: str, 
    xbnds: str, 
    ybnds: str, 
    dlon: str, 
    dlat: str, 
    use_great_circle_algorithm: bool,
    grid_name: str,
    verbose: bool,
):
    lonlat_grid.make(
        nlon=nlon,
        nlat=nlat,
        xbnds=xbnds,
        ybnds=ybnds,
        dlon=dlon,
        dlat=dlat,
        use_great_circle_algorithm=use_great_circle_algorithm,
        grid_name=grid_name,
        verbose=verbose,
    )

@make_hgrid.command()
@click.option(
    "--nlon", 
    type=str, 
    default=None,
    help="Model grid points(supergrid) for each zonal regions of varying resolution.",
)
@click.option(
    "--shift_fac",
    type=float,
    default=18.0,
    help="shift west by 180/shift_fac. Default value is 18."
)
@click.option(
    "--stretch_factor",
    type=float,
    default=0.0,
    help="Stretching factor for the grid"
)
@click.option(
    "--target_lon",
    type=float,
    default=0.0,
    help="center longitude of the highest resolution tile"
)
@click.option(
    "--target_lat",
    type=float,
    default=0.0,
    help="center latitude of the highest resolution tile"
)
@click.option(
    "--nest_grids",
    type=int,
    default=0,
    help="""
    set to create this # nested grids as well as the global grid.
    When it is set, besides 6 tile grid files created, there are #
    more nest grids with file name = grid_name.tile${parent_tile}.nest.nc
    """,
)
@click.option(
    "--parent_tile",
    type=str,
    default=None,
    help="Specify the comma-separated list of the parent tile number(s) of nest grid(s)."
)
@click.option(
    "--refine_ratio",
    type=str,
    default=None,
    help="Specify the comma-separated list of refinement ratio(s) for nest grid(s)."
)
@click.option(
    "--istart_nest",
    type=str,
    default=None,
    help="Specify the comma-separated list of starting i-direction index(es) of nest grid(s) in parent tile supergrid(Fortran index)."
)
@click.option(
    "--iend_nest",
    type=str,
    default=None,
    help="Specify the comma-separated list of ending i-direction index(es) of nest grid(s) in parent tile supergrid(Fortran index)."
)
@click.option(
    "--jstart_nest",
    type=str,
    default=None,
    help="Specify the comma-separated list of starting j-direction index(es) of nest grid(s) in parent tile supergrid(Fortran index)."
)
@click.option(
    "--jend_nest",
    type=str,
    default=None,
    help="Specify the comma-separated list of ending j-direction index(es) of nest grid(s) in parent tile supergrid(Fortran index)."
)
@click.option(
    "--halo",
    type=int,
    default=0,
    help="""
    halo size is used in the atmosphere cubic sphere
    model. Its purpose is to make sure the nest,
    including the halo region, is fully contained
    within a single parent (coarse) tile.
    """,
)
@click.option(
    "--out_halo",
    type=int,
    default=0,
    help="extra halo size data to be written out."
)
@click.option(
    "--grid_name",
    type=str,
    default="horizontal_grid",
    help="""
    Specify the grid name. The output grid file name
    will be grid_name.nc if there is one tile and
    grid_name.tile#.nc if there is more than one tile.
    The default value will be horizontal_grid.
    """,
)
@click.option(
    "--grid_type",
    type=str,
    default="gnomonic_ed",
    help="Specify the grid type. Options are 'gnomonic_ed', 'gnomonic_dist', or 'gnomonic_angl'.",
)
@click.option(
    "--output_length_angle",
    is_flag=True,
    default=True,
    help="Default to true, set to false to not output length angle"

)
@click.option(
    "--do_schmidt",
    is_flag=True,
    default=False,
    help="""
    Set to do Schmidt transformation to create
    stretched grid. When do_schmidt is set, the
    following must be set: --stretch_factor
    --target_lon and --target_lat.
    """,
)
@click.option(
    "--do_cube_transform",
    is_flag=True,
    default=False,
    help="""
    re-orient the rotated cubed sphere so that tile 6
    has 'north' facing upward, which would make
    analysis and explaining nest placement much easier.
    When do_cube_transform is set, the following must
    be set: --stretch_factor, --target_lon, and --target_lat.
    """,
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
)
def gnomonic(
    nlon: str,
    shift_fac: float,
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
    out_halo: int,
    grid_name: str,
    grid_type: str, 
    output_length_angle: bool,
    do_schmidt: bool,
    do_cube_transform: bool,
    verbose: bool
):
    gnomonic_grid.make(
        nlon=nlon,
        shift_fac=shift_fac,
        stretch_factor=stretch_factor,
        target_lon=target_lon,
        target_lat=target_lat,
        nest_grids=nest_grids,
        parent_tile=parent_tile,
        refine_ratio=refine_ratio,
        istart_nest=istart_nest,
        iend_nest=iend_nest,
        jstart_nest=jstart_nest,
        jend_nest=jend_nest,
        halo=halo,
        out_halo=out_halo,
        grid_name=grid_name,
        grid_type=grid_type,
        output_length_angle=output_length_angle,
        do_schmidt=do_schmidt,
        do_cube_transform=do_cube_transform,
        verbose=verbose,
    )
