import click
import sys


#from gridtools import MosaicStruct

@click.command()

@click.option('--num_tiles', type=int, help="number of tiles")
@click.option('--grid_dir')
@click.option('--global_mosaic')
@click.option('--regional_mosaic')
@click.option('--input_mosaic')
@click.option('--atmos_mosaic')
@click.option('--ocean_mosaic')
@click.option('--ocean_topog')
@click.option('--mosaic_name')
@click.option('--tile_file', '-f', multiple=True, type=click.Path(exists=True))
@click.option('--periodx')
@click.option('--periody')
@click.option('--ocean_topog')
@click.option('--sea_level')
@click.option('--land_frac_file')
@click.option('--land_frac_field')
@click.option('--land_mosaic')
@click.option('--wave_mosaic')
@click.option('--interp_order')
@click.option('--area_ratio_thresh')
@click.option('--check')
@click.option('--print_memory')
@click.option('--rotate_poly')
@click.argument('type')

def main(num_tiles, grid_dir, global_mosaic, regional_mosaic, input_mosaic, atmos_mosaic, ocean_mosaic, mosaic_name, tile_file, periodx, periody, ocean_topog, sea_level, land_frac_file, land_frac_field, land_mosaic, wave_mosaic, interp_order, area_ratio_thresh, check, print_memory, rotate_poly, type):

    if type == 'solo':
        make_solo_mosaic(num_tiles, grid_dir, mosaic_name, tile_file, periodx, periody)
    elif type == 'regional':
        make_regional_mosaic(global_mosaic, regional_mosaic)
    else:
        make_coupler_moasic(atmos_mosaic, ocean_mosaic, ocean_topog, land_mosaic, wave_mosaic, interp_order, sea_level, mosaic_name, area_ratio_thresh, check, print_memory, rotate_poly)




def make_solo_mosaic(num_tiles, grid_dir, mosaic_name, tile_file, periodx, periody):
    tilefiles = list(tile_file)
    nfiles = len(tilefiles)
    #if file name is not specified
    if nfiles == 0:
        if num_tiles == 1:
            tilefiles = "horizontal_grid.nc"
        else:
            for n in range(num_tiles):
                    tilefiles.append("horizontal_grid.tile{}.nc".format(n))
    else:
        #ensure that the number of tiles matches the number of grid files provided
        if nfiles != num_tiles:
            sys.exit("Error: number tiles provided through --ntiles does not match number of grid files passed through")
    print(tilesfiles)
    #gather grid data from grid files...

    #find contact regions

    #define dimension

    #define variable


def make_regional_mosaic(global_mosaic, regional_mosaic):
    pass

def make_coupler_mosaic(atmos_mosaic, ocean_mosaic, ocean_topog, land_mosaic, wave_mosaic, interp_order, sea_level, mosaic_name, area_ratio_thresh, check, print_memory, rotate_poly):
    pass



if __name__ == '__main__':
    main()
