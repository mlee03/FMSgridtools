import click
import sys
import xarray as xr
import numpy as np
from FMSgridtools.shared.gridobj import GridObj
from FMSgridtools.shared.mosaicobj import MosaicObj
from FMSgridtools.make_mosaic.regionalgridobj import RegionalGridObj

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




@click.option('--num_tiles',
              type=int,
              help="Number of tiles in the mosaic.")

@click.option('--dir',
              type=click.Path(exists=True, file_okay=False),
              help="the directory that contains all the tile grid files." )

@click.option('--global_mosaic',
              type=click.Path(exists=True),
              help="global_mosaic Specify the mosaic file for the global grid.")

@click.option('--regional_file',
              type=click.Path(exists=True),
              help="regional_file Specify the regional model output file.")

@click.option('--input_mosaic',
              type=click.Path(exists=True))

@click.option('--atmos_mosaic',
              type=click.Path(exists=True),
              help = ATMOS_MOSAIC_HELP)

@click.option('--ocean_mosaic',
              type=click.Path(exists=True))

@click.option('--ocean_topog',
              type=click.Path(exists=True))

@click.option('--mosaic_name', default='mosaic',
              help="mosaic name; The output file will be mosaic_name.nc.")

@click.option('--tile_file', '-f',
              multiple=True, type=click.Path(exists=True, file_okay=True),
              help = TILE_FILE_HELP)

@click.option('--periodx',
              default=0,
              help = "Specify the period in x-direction of mosaic. \
                Default value is 0 (not periodic)")

@click.option('--periody', default=0,
              help="Specify the period in y-direction of mosaic. \
                Default value is 0 (not periodic)")

@click.option('--sea_level', type=int, default=0)

@click.option('--land_mosaic', type=click.Path(exists=True))

@click.option('--wave_mosaic', type=click.Path(exists=True))

@click.option('--interp_order', default=2)

@click.option('--area_ratio_thresh', type=float, default=1e-6)

@click.option('--check')

@click.option('--print_memory')

@click.option('--rotate_poly')

@click.argument('type')

@click.command()
def main(
    num_tiles,
    dir,
    mosaic_name,
    tile_file,
    periodx,
    periody,
    global_mosaic,
    regional_file,
    input_mosaic,
    atmos_mosaic,
    ocean_mosaic,
    ocean_topog,
    land_mosaic,
    wave_mosaic,
    interp_order,
    area_ratio_thresh,
    check,
    sea_level,
    print_memory,
    rotate_poly,
    type) -> None:
    """main function"""

    if type == 'solo':
        make_solo_mosaic(
            num_tiles, dir, mosaic_name,
            tile_file, periodx,
            periody)
    elif type == 'regional':
        make_regional_mosaic(
            global_mosaic,
            regional_file)
    else:
        make_coupler_mosaic(
            atmos_mosaic,
            ocean_mosaic,
            ocean_topog,
            land_mosaic,
            wave_mosaic,
            interp_order,
            sea_level,
            mosaic_name,
            area_ratio_thresh,
            check,
            print_memory,
            rotate_poly)

def make_solo_mosaic(
        num_tiles,
        dir,
        mosaic_name,
        tile_file,
        periodx,
        periody):
        """Generates mosaic information between tiles. The mosaic, information includes:
        list of tile files, list of contact region,
        specified by index, contact type."""

        contacts = []
        contact_index = []
        tilefiles = list(tile_file)
        nfiles = len(tilefiles)

        if nfiles == 0:
            if num_tiles == 1:
                tilefiles.append("horizontal_grid.tile1.nc")
            else:
                for n in range(num_tiles):
                    tilefiles.append(f"horizontal_grid.tile{n}.nc")
        else:
            if nfiles != num_tiles:
                sys.exit("Error: number tiles provided through --ntiles"
                     "does not match number of grid files passed through")

        gridtiles = [f'tile{i}' for i in range(1,nfiles+1)]


        mosaic = MosaicObj(ntiles=num_tiles, gridfiles = np.asarray(tilefiles),
                        gridtiles = np.asarray(gridtiles))
        
        mosaic.griddict()
        grid_data = {}
        for tile in gridtiles:
            grid_data[tile] = {}
            xvals = mosaic.grid_dict[tile].x
            grid_data[tile]['x'] = xvals
            yvals = mosaic.grid_dict[tile].y
            grid_data[tile]['y'] = yvals
            nxp = mosaic.grid_dict[tile].x.shape
            grid_data[tile]['nxp'] = nxp[1]
            nyp = mosaic.grid_dict[tile].y.shape
            grid_data[tile]['nyp'] = nyp[0]

        ncontact = 0
        #FIND CONTACT REGIONS
        for n in range(1,num_tiles):
            for m in range(n,num_tiles+1):
                contact = Contact(n, m, grid_data[f'tile{n}']['nxp'],
                        grid_data[f'tile{m}']['nxp'],
                        grid_data[f'tile{n}']['nyp'],
                        grid_data[f'tile{m}']['nyp'],
                        grid_data[f'tile{n}']['x'],
                        grid_data[f'tile{m}']['x'],
                        grid_data[f'tile{n}']['y'],
                        grid_data[f'tile{m}']['y'],
                        periodx, periody)
                count, istart1, iend1, jstart1, jend1, istart2, iend2, jstart2, jend2  = contact.align_contact(lib_file)

                if count > 0:
                    contacts.append(f"{mosaic_name}:tile{n}::{mosaic_name}:tile{m}")
                    ncontact+=1

                    tile1_istart = istart1
                    tile1_iend = iend1
                    tile1_jstart = jstart1
                    tile1_jend = jend1
                    tile2_istart = istart2
                    tile2_iend = iend2
                    tile2_jstart = jstart2
                    tile2_jend = jend2

                    contact_index.append(f"{tile1_istart}:{tile1_iend},{tile1_jstart}:{tile1_jend}::{tile2_istart}:{tile2_iend},{tile2_jstart}:{tile2_jend}")

        print("\nCongratulations: You have successfully run solo mosaic")
        print(f"NOTE: There are {ncontact} contacts\n")

        if ncontact > 0:
            mosaic = MosaicObj(mosaic_name,
                               gridlocation=dir,
                               gridfiles=tilefiles,
                               gridtiles=np.asarray(gridtiles),
                               contacts=np.asarray(contacts),
                               contact_index=np.asarray(contact_index))
            mosaic.write_out_mosaic(f'{mosaic_name}.nc')

def make_regional_mosaic(
        global_mosaic,
        regional_file):
        """ Generates a horizontal grid and solo mosaic for a regional output.
        The created grid and solo mosaic could be used to regrid regional
        output data onto regular lat-lon grid."""

        #get tile number from regional file
        tile = int(list(filter(str.isdigit, regional_file))[0])

        ds = xr.open_dataset(regional_file)
        nx = ds.sizes['grid_xt_sub01']
        ny = ds.sizes['grid_yt_sub01']

        indx = ds.grid_xt_sub01.values
        indy = ds.grid_yt_sub01.values

        i_min = np.min(indx)
        i_max = np.max(indx)
        j_min = np.min(indy)
        j_max = np.max(indy)

        if i_max-i_min+1 != nx:
            print("Error: make_regional_mosaic: i_max-i_min+1 != nx")
        if j_max-j_min+1 != ny:
            print("Error: make_regional_mosaic: j_max-j_min+1 != ny")

        global_m = MosaicObj(global_mosaic)
        global_m.griddict()
        xt = global_m.grid_dict[f'tile{tile}'].x
        xarr = xt[round(2*j_min - 2):round(2*j_min - 2 + 2*ny+1), round(2*i_min - 2):round(2*i_min - 2 + 2*nx+1)]
        yt = global_m.grid_dict[f'tile{tile}'].y
        yarr = yt[round(2*j_min - 2):round(2*j_min - 2 + 2*ny+1), round(2*i_min - 2):round(2*i_min - 2 + 2*nx+1)]

        regional_grid = RegionalGridObj(tile, xarr,
                                        yarr)
        regional_grid.write_out_regional_grid(f"regional_grid.tile{tile}.nc")

        print("\nCongratulations: You have successfully run make_regional_mosaic")

def make_coupler_mosaic(
        atmos_mosaic,
        ocean_mosaic,
        ocean_topog,
        land_mosaic,
        wave_mosaic,
        interp_order,
        sea_level,
        mosaic_name,
        area_ratio_thresh,
        check,
        print_memory,
        rotate_poly):


    pass


if __name__ == '__main__':
    main()
