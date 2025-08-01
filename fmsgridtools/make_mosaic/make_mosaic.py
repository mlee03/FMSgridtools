import click
import numpy as np

import fmsgridtools.make_mosaic.solo_mosaic as solo_mosaic
import fmsgridtools.make_mosaic.regional_mosaic as regional_mosaic
import fmsgridtools.make_mosaic.coupled_mosaic as coupled_mosaic

ATMOS_MOSAIC_HELP = "specify the atmosphere mosaic information \
    This file contains list of tile files which specify \
    the grid information for each tile. Each grid is \
    required to be logically rectangular grid. The \
    file name cannot be 'mosaic.nc'"

TILE_FILE_HELP = "Grid file name of all tiles in the mosaic. \
    The file name should be the \
    relative path (exclude the absolute file path) \
    The absolute file path will be dir/tile_file. \
    the default for tile_file will be'horizontal_grid.tile#.nc'"


mosaic_name = click.option('--mosaic_name',
              default='mosaic',
              help="mosaic name; The output file will be mosaic_name.nc.")

sea_level = click.option('--sea_level', type=np.float64, default=np.float64(0.0))

ocean_topog = click.option('--ocean_topog',
                           type=click.Path(exists=True),
                           required=True)


@click.command()
@mosaic_name
@click.option("--num_tiles",
              type=int,
              required=True,
              help="Number of tiles in the mosaic.")

@click.option('--dir_name',
              type=click.Path(exists=True, file_okay=False),
              help="the directory that contains all the tile grid files." )

@click.option('--tile_file', '-f',
              multiple=True, type=click.Path(exists=True, file_okay=True),
              help=TILE_FILE_HELP)

@click.option('--periodx',
              default=0,
              help = "Specify the period in x-direction of mosaic. \
                Default value is 0 (not periodic)")

@click.option('--periody', default=0,
              help="Specify the period in y-direction of mosaic. \
                Default value is 0 (not periodic)")

def solo(num_tiles,
         dir_name,
         mosaic_name,
         tile_file,
         periodx,
         periody):
    
    solo_mosaic.make(num_tiles,
                     mosaic_name,
                     list(tile_file),
                     dir_name,
                     periodx,
                     periody)


@click.command()
@click.option('--global_mosaic',
              type=click.Path(exists=True),
              help="global_mosaic Specify the mosaic file for the global grid.")

@click.option('--regional_file',
              type=click.Path(exists=True),
              help="regional_file Specify the regional model output file.")

def regional(global_mosaic, 
             regional_file):
    
    regional_mosaic.make(global_mosaic, 
                         regional_file)


@click.command()
@mosaic_name
@sea_level
@ocean_topog
@click.option('--input_mosaic',
              type=click.Path(exists=True))

def quick(input_mosaic,
          mosaic_name,
          ocean_topog,
          sea_level,
          land_frac_file,
          land_frac_field):
    pass


@click.command()
@sea_level
@ocean_topog
@click.option('--input_dir',
              type=click.Path(exists=True),
              default="./",
              help = "input directory")

@click.option('--atmos_mosaic',
              type=click.Path(exists=True),
              required=True,
              help = ATMOS_MOSAIC_HELP)

@click.option('--ocean_mosaic',
              required=True,
              type=click.Path(exists=True))

@click.option('--land_mosaic', type=click.Path(exists=True), required=True)

@click.option('--interp_order', type=str, default="conserve_order1")

@click.option('--area_ratio_thresh', type=np.float64, default=np.float64(1e-6))

@click.option('--check')

@click.option('--rotate_poly')

def coupled(input_dir,
            atmos_mosaic,
            ocean_mosaic,
            land_mosaic,
            ocean_topog,
            sea_level,
            interp_order,
            area_ratio_thresh,
            check,
            rotate_poly):

    coupled_mosaic.set_parameters(sea_level,
                                  area_ratio_thresh,
                                  interp_order,
                                  rotate_poly)
    
    coupled_mosaic.make(atm_mosaic_file=atmos_mosaic,
                        lnd_mosaic_file=land_mosaic,
                        ocn_mosaic_file=ocean_mosaic,
                        topog_file=ocean_topog,
                        input_dir=input_dir)
