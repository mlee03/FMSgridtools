import ctypes
import numpy as np
from typing import List
import xarray as xr

import pyfrenctools
from fmsgridtools.shared.mosaicobj import MosaicObj
from fmsgridtools.shared.xgridobj import XGridObj

def extend_ocn_grid_south(ocn_mosaic: MosaicObj):

    tiny_value = np.float64(1.e-7)
    min_atm_lat = np.radians(-90.0, dtype=np.float64)
    
    if ocn_mosaic.grid['tile1'].y[0][0] > min_atm_lat + tiny_value:
        #extend
        for itile in ocn_mosaic.gridtiles:
            nxp = ocn_mosaic.grid[itile].nxp

            x = ocn_mosaic.grid[itile].x
            ocn_mosaic.grid[itile].x = np.concatenate(([x[0]], x))   

            y = ocn_mosaic.grid[itile].y            
            ocn_mosaic.grid[itile].y = np.concatenate((np.full((1,nxp), min_atm_lat, dtype=np.float64), y))

            ocn_mosaic.grid[itile].ny = ocn_mosaic.grid[itile].ny + 1
        ocn_mosaic.extended_south = 1
    else:
        ocn_mosaic.extended_south = 0


def get_ocn_mask(ocn_mosaic: type(MosaicObj), topog_file: dict() = None, sea_level: np.float64 = np.float64(0.0)):

    nx = ocn_mosaic.grid['tile1'].nx 
    ny = ocn_mosaic.grid['tile1'].ny

    ocn_mask = {}
    if topog_file is None:
        for itile in ocn_mosaic.gridtiles:
            ocn_mask[itile] = np.ones((ny,nx), dtype=np.float64)
        return mask    

    for itile in ocn_mosaic.gridtiles:
        topog = xr.load_dataset(topog_file[itile])['depth'].values

        one, zero = np.float64(1.0), np.float64(0.0)
        imask = np.where(topog>sea_level, one, zero)
            
        if ocn_mosaic.extended_south > 0 :
            ocn_mask[itile] = np.concatenate(([np.zeros(nx, dtype=np.float64)], imask))
        else:
            ocn_mask[itile] = imask

    return ocn_mask


def get_atmxlnd(atmxocn_landpart: type[XGridObj], atm_mosaic: type[MosaicObj] = None, atm_area = None):
    
    for otile in atmxocn_landpart.datadict:

        atmxlnd = {}

        for atmtile in atmxocn_landpart.datadict[otile]:

            #get atm area
            nx = atm_mosaic.grid[atmtile].nx
            atm_area = pyfrenctools.grid_utils.get_grid_area(atm_mosaic.grid[atmtile].x, atm_mosaic.grid[atmtile].y)

            datadict = atmxocn_landpart.datadict[otile][atmtile]            

            i_before, j_before = -99, -99
            atm_i, atm_j, xarea = [], [], []

            for ij in range(datadict["nxcells"]):
            
                this_i = datadict["i_src"][ij]
                this_j = datadict["j_src"][ij]
                this_xarea = datadict["xarea"][ij]
                this_atm_area = atm_area[(this_j*nx + this_i)]

                if this_xarea/this_atm_area > np.float64(1.e-6):  
                    if this_i == i_before and this_j == j_before:                    
                        xarea[-1] += this_xarea
                    else:
                        i_before, j_before = this_i, this_j
                        xarea.append(this_xarea)
                        atm_i.append(this_i)
                        atm_j.append(this_j)
            atmxlnd[atmtile] = dict(nxcells = len(atm_i),
                                    i_src = np.array(atm_i),
                                    j_src = np.array(atm_j),
                                    i_tgt = np.array(atm_i),
                                    j_tgt = np.array(atm_j),
                                    xarea = np.array(xarea, dtype=np.float64))
    return atmxlnd
    
    

def make_coupler_mosaic(atm_mosaic_file: str, lnd_mosaic_file: str, ocn_mosaic_file: str,
                        input_dir: str = './', topog_file: dict() = None):

    #read in mosaic files
    atm_mosaic = MosaicObj(input_dir=input_dir, mosaic_name=atm_mosaic_file).read()
    lnd_mosaic = MosaicObj(input_dir=input_dir, mosaic_name=lnd_mosaic_file).read()
    ocn_mosaic = MosaicObj(input_dir=input_dir, mosaic_name=ocn_mosaic_file).read()

    #read in grids
    atm_mosaic.get_grid(toradians=True, agrid=True, free_dataset=True)
    lnd_mosaic.get_grid(toradians=True, agrid=True, free_dataset=True)
    ocn_mosaic.get_grid(toradians=True, agrid=True, free_dataset=True)

    #get ocean mask
    topogfile_dict = {'tile1': input_dir + '/' + topog_file}
    extend_ocn_grid_south(ocn_mosaic)    
    ocn_mask = get_ocn_mask(ocn_mosaic=ocn_mosaic, topog_file=topogfile_dict)

    #atmxocn
    atmxocn = XGridObj(src_mosaic=atm_mosaic, tgt_mosaic=ocn_mosaic)
    atmxocn.create_xgrid(tgt_mask=ocn_mask)

    #undo extra ocn dimension and write
    for ocntile in atmxocn.datadict:
        for atmtile in atmxocn.datadict[ocntile]:
            atmxocn.datadict[ocntile][atmtile]['j_tgt'] = atmxocn.datadict[ocntile][atmtile]['j_tgt'] - ocn_mosaic.extended_south
            atmxocn.write(datadict=atmxocn.datadict[ocntile][atmtile], 
                          outfile=f"{atm_mosaic.mosaic_name[:-3]}_{atmtile}X{ocn_mosaic.mosaic_name[:-3]}_{ocntile}.nc")


    #ocn mask for lnd    
    for itile in ocn_mask: ocn_mask[itile] = 1.0 - ocn_mask[itile]

    #atmxlnd
    atmxocn_landpart = XGridObj(src_mosaic=atm_mosaic, tgt_mosaic=ocn_mosaic)
    atmxocn_landpart.create_xgrid(tgt_mask=ocn_mask)
    atmxlnd = get_atmxlnd(atmxocn_landpart, atm_mosaic=atm_mosaic)
    for atmtile in atmxlnd:
        atmxocn.write(datadict=atmxlnd[atmtile], 
                      outfile=f"{atm_mosaic.mosaic_name[:-3]}_{atmtile}X{atm_mosaic.mosaic_name[:-3]}_{atmtile}.nc")

