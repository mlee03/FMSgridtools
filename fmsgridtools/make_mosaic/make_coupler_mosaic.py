import ctypes
import numpy as np
from typing import List
import xarray as xr

import pyfrenctools

from fmsgridtools.shared.mosaicobj import MosaicObj
from fmsgridtools.shared.xgridobj import XGridObj

def make_coupler_mosaic(atm_mosaic_file: str, lnd_mosaic_file: str, ocn_mosaic_file: str, input_dir: str = './', topog_file: dict() = None):

    #read in mosaic files
    atm_mosaic = MosaicObj(input_dir=input_dir, mosaic_name=atm_mosaic_file).read()
    lnd_mosaic = MosaicObj(input_dir=input_dir, mosaic_name=lnd_mosaic_file).read()
    ocn_mosaic = MosaicObj(input_dir=input_dir, mosaic_name=ocn_mosaic_file).read()

    #read in grids
    atm_mosaic.get_grid(toradians=True, agrid=True, free_dataset=True)
    lnd_mosaic.get_grid(toradians=True, agrid=True, free_dataset=True)
    ocn_mosaic.get_grid(toradians=True, agrid=True, free_dataset=True)

    atmxlnd = XGridObj(input_dir=input_dir, src_mosaic=atm_mosaic_file, tgt_mosaic=lnd_mosaic_file)
    atmxlnd.create_xgrid()
    atmxlnd.write('atmxlnd.nc')

    topogfile_dict = {'tile1': input_dir + '/' + topog_file}

    pyfrenctools.mosaic_coupled_utils.extend_ocn_grid_south(ocn_mosaic)    
    ocn_mask = pyfrenctools.mosaic_coupled_utils.get_ocn_mask(ocn_mosaic=ocn_mosaic, topog_file=topogfile_dict)

    atmxocn = XGridObj(input_dir=input_dir, src_mosaic=ocn_mosaic_file, tgt_mosaic=atm_mosaic_file)
    atmxocn.create_xgrid(src_mask=ocn_mask)
    atmxocn.write('atmxocn.nc')

    #pyfrenctools.mosaic_coupled_utils.make_coupler_mosaic(atm_mosaic=atm_mosaic,
    #                                                      lnd_mosaic=lnd_mosaic,
    #                                                      ocn_mosaic=ocn_mosaic,
    #                                                      topogfile=input_dir+'/'+topog_file)
