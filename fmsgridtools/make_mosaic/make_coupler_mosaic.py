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

    atmxocn = XGridObj(input_dir=input_dir, src_mosaic=atm_mosaic, tgt_mosaic=ocn_mosaic)
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
    #for itile in ocn_mask:
    #    print(np.sum(ocn_mask[itile]))
    #    ocn_mask[itile] = 1.0 - ocn_mask[itile]
    #    print(np.sum(ocn_mask[itile]))
        
    #lndxocn = XGridObj(input_dir=input_dir, src_mosaic=ocn_mosaic_file, tgt_mosaic=lnd_mosaic_file)
    #lndxocn.create_xgrid(src_mask = ocn_mask)
    #lndxocn.write('atmxlnd.nc')
    
    #atmxlnd = XGridObj(input_dir=input_dir, src_mosaic=atm_mosaic_file, tgt_mosaic=lnd_mosaic_file)
    #atmxlnd.create_xgrid()
    #atmxlnd.write('atmxlnd.nc')


    

