import sys
import numpy as np 
from FMSgridtools.shared.gridobj import GridObj
from FMSgridtools.shared.mosaicobj import MosaicObj
import pyfrenctools

def make(num_tiles,
        dir_name,
        mosaic_name,
        tile_file,
        periodx,
        periody) -> None:
        """Generates mosaic information between tiles. The mosaic information includes:
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


        grid = MosaicObj(ntiles=num_tiles, gridfiles = tilefiles,
                        gridtiles = gridtiles).griddict()
        
        grid_data = {}
        for tile in gridtiles:
            grid_data[tile] = {}
            grid_data[tile]['x'] = grid[tile].x
            grid_data[tile]['y'] = grid[tile].y
            grid_data[tile]['nxp'] = grid[tile].nxp
            grid_data[tile]['nyp'] = grid[tile].nyp

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
                count, istart1, iend1, jstart1, jend1, istart2, iend2, jstart2, jend2  = contact.align_contact()

                if count > 0:
                    contacts.append(f"{mosaic_name}:tile{n}::{mosaic_name}:tile{m}")
                    ncontact+=1


                    contact_index.append(f"{istart1}:{iend1},{jstart1}:{jend1}::{istart2}:{iend2},{jstart2}:{jend2}")

        print("\nCongratulations: You have successfully run solo mosaic")
        print(f"NOTE: There are {ncontact} contacts\n")

        if ncontact > 0:
            grid = MosaicObj(mosaic_name=mosaic_name,
                               gridlocation=dir_name,
                               gridfiles=tilefiles,
                               gridtiles=gridtiles,
                               contacts=contacts,
                               contact_index=contact_index)
            grid.write_out_mosaic(f'{mosaic_name}.nc')
