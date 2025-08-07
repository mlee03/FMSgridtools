import sys
import numpy as np
from typing import List
from fmsgridtools.shared.gridobj import GridObj
from fmsgridtools.shared.mosaicobj import MosaicObj
import pyfrenctools

#authorship got overwritten somehow.
#original developer - halle.derry 

def make(num_tiles,
         mosaic_name,
         tilefiles: List[str],
         dir_name: str = "./",
         periodx: int = 0,
         periody: int = 0) -> None:

    """
    Generates mosaic information between tiles. The mosaic information includes:
    list of tile files, list of contact region,
    specified by index, contact type.
    """
    
    if not tilefiles: sys.exit("Error, must supply grid files")        
    if len(tilefiles) != num_tiles:
        sys.exit("Error: number tiles provided through --ntiles"
                 "does not match number of grid files passed through")

    # expects files to be named gridfile.tile#.nc"    
    gridtiles = []
    for ifile in tilefiles:
        for istring in ifile.split("."):
            if "tile" in istring:
                gridtiles.append(istring)
                break

    if len(gridtiles) != num_tiles: sys.exit("Error, number of gridtiles does not equal num_tiles")

    grid = MosaicObj(ntiles=num_tiles, gridfiles = tilefiles, gridtiles = gridtiles).get_grid(toradians=True)
                
    ncontact, contacts, contact_index = 0, [], []
    #FIND CONTACT REGIONS
    for n in range(num_tiles):
        tilen = gridtiles[n]
        for m in range(n+1,num_tiles):
            tilem = gridtiles[m]
            contact = pyfrenctools.mosaic_util.Contact(n, m, grid[tilen].nxp,
                                                       grid[tilem].nxp,
                                                       grid[tilen].nyp,
                                                       grid[tilem].nyp,
                                                       grid[tilen].x,
                                                       grid[tilem].x,
                                                       grid[tilen].y,
                                                       grid[tilem].y,
                                                       periodx, periody)
            count, istart1, iend1, jstart1, jend1, istart2, iend2, jstart2, jend2  = contact.align_contact()
            
            if count > 0:
                contacts.append(f"{mosaic_name}:tile{n}::{mosaic_name}:tile{m}")
                contact_index.append(f"{istart1}:{iend1},{jstart1}:{jend1}::{istart2}:{iend2},{jstart2}:{jend2}")

        ncontact = len(contacts)
        print("\nCongratulations: You have successfully run solo mosaic")
        print(f"NOTE: There are {ncontact} contacts\n")
        
        if ncontact > 0:
            mosaic = MosaicObj(name=mosaic_name,
                               gridlocation=dir_name,
                               gridfiles=tilefiles,
                               gridtiles=gridtiles,
                               contacts=contacts,
                               contact_index=contact_index)
            mosaic.write(f'{mosaic_name}.nc')
