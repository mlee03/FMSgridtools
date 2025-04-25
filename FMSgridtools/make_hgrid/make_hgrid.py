import click

from FMSgridtools.make_hgrid.make_lonlat_grid import make_lonlat_grid


@click.group()
def make_hgrid():
    pass

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
    help="When specified, great_circle_algorithm will be used to compute grid \
         cell area.",
)
def lonlat(
    nlon, 
    nlat, 
    xbnds, 
    ybnds, 
    dlon, 
    dlat, 
    use_great_circle_algorithm
):
    make_lonlat_grid(
        nlon=nlon,
        nlat=nlat,
        xbnds=xbnds,
        ybnds=ybnds,
        dlon=dlon,
        dlat=dlat,
        use_great_circle_algorithm=use_great_circle_algorithm,
    )