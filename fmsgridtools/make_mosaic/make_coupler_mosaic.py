import ctypes
import numpy as np
from typing import List
import xarray as xr

import pyfrenctools

from fmsgridtools.shared.mosaicobj import MosaicObj

def make_coupler_mosaic(atm_mosaic_file: str, lnd_mosaic_file: str, ocn_mosaic_file: str, input_dir: str = './', topog_file: str = None):

    #read in mosaic files
    atm_mosaic = MosaicObj(input_dir=input_dir, mosaic_name=atm_mosaic_file).read()
    lnd_mosaic = MosaicObj(input_dir=input_dir, mosaic_name=lnd_mosaic_file).read()
    ocn_mosaic = MosaicObj(input_dir=input_dir, mosaic_name=ocn_mosaic_file).read()

    #read in grids
    atm_mosaic.get_grid(toradians=True, agrid=True, free_dataset=True)
    lnd_mosaic.get_grid(toradians=True, agrid=True, free_dataset=True)
    ocn_mosaic.get_grid(toradians=True, agrid=True, free_dataset=True)
        
    pyfrenctools.mosaic_coupled_utils.make_coupler_mosaic(atm=atm_mosaic,
                                                          lnd=lnd_mosaic,
                                                          ocn=ocn_mosaic,
                                                          topogfile=input_dir+'/'+topog_file)
