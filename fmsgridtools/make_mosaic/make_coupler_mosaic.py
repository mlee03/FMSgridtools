import ctypes
import numpy as np
from typing import List
import xarray as xr

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


def get_ocn_mask(ocn_mosaic: type(MosaicObj), topog_file: dict() = None, sea_level: np.float64 = 0.0):

    nx = ocn_mosaic.grid['tile1'].nx 
    ny = ocn_mosaic.grid['tile1'].ny

    ocn_mask = {}
    if topog_file is None:
        for itile in ocn_mosaic.gridtiles:
            ocn_mask[itile] = np.ones((ny,nx), dtype=np.float64)
        return mask    
    else:
        for itile in ocn_mosaic.gridtiles:
            topog = xr.load_dataset(topog_file[itile])['depth'].values

            one, zero = np.float64(1.0), np.float64(0.0)
            imask = np.where(topog>sea_level, one, zero)
            
            if ocn_mosaic.extended_south > 0 :
                ocn_mask[itile] = np.concatenate(([np.zeros(nx, dtype=np.float64)], imask))
            else:
                ocn_mask[itile] = imask

        return ocn_mask
    

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
    for tgt_tile in atmxocn.dataset:
      for src_tile in atmxocn.dataset[tgt_tile]:
        tgt_ij = atmxocn.dataset[tgt_tile][src_tile]['tgt_ij'].values 
        for i in range(len(tgt_ij)):
          tgt_ij[i][1] = tgt_ij[i][1]-1     
          atmxocn.dataset[tgt_tile][src_tile]['tgt_ij'].data = tgt_ij
    for ocn_tile in atmxocn.dataset:
        for atm_tile in atmxocn.dataset[ocn_tile]:
            atmxocn.dataset[ocn_tile][atm_tile].to_netcdf(f'atm_mosaic_{atm_tile}Xocn_mosaic_{ocn_tile}.nc')

    #ocn mask for lnd    
    for itile in ocn_mask: ocn_mask[itile] = 1.0 - ocn_mask[itile]
        
    #atmxlnd
    atmxlnd = XGridObj(src_mosaic=atm_mosaic, tgt_mosaic=ocn_mosaic)
    atmxlnd.create_xgrid(tgt_mask=ocn_mask)
    for otile in atmxlnd.dataset:
        for atmtile in atmxlnd.dataset[otile]:

            dataset = atmxlnd.dataset[otile][atmtile]
            
            atm_ij, area = [], []
            newcount, ij_before = -1, np.array([-99,-99], dtype=np.int32)

            for this_ij, this_area in zip(dataset.src_ij.values, dataset.xarea.values):
                if np.all(this_ij == ij_before):
                    area[newcount] += this_area
                else:
                    newcount, ij_before = newcount+1, this_ij
                    area.append(this_area)
                    atm_ij.append(this_ij)
            #print
            src_ij = xr.DataArray(np.array(atm_ij), dims=["nxcells", "two"], attrs=dataset["src_ij"].attrs)
            tgt_ij = xr.DataArray(np.array(atm_ij), dims=["nxcells", "two"], attrs=dataset["tgt_ij"].attrs)
            xarea = xr.DataArray(np.array(area), dims=["nxcells"], attrs=dataset["xarea"].attrs)
            xr.Dataset(data_vars={"src_ij": src_ij,
                                  "tgt_ij": tgt_ij,
                                  "xarea": xarea}).to_netcdf(f"atm_mosaic_{atmtile}Xlnd_mosaic_{atmtile}.nc")

