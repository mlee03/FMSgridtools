import numpy as np
import xarray as xr

import fmsgridtools

def test_make_coupler_mosaic():

    fmsgridtools.coupler_mosaic.make(atm_mosaic_file='C48_mosaic.nc',
                                     lnd_mosaic_file='C48_mosaic.nc',
                                     ocn_mosaic_file='ocean_mosaic.nc',
                                     input_dir='/home/Mikyung.Lee/fmsgridtools/agridfix/tests/mosaic/input',
                                     topog_file='ocean_topog.nc')

    #number of cells differs by 2 for C48_mosaic_tile3Xocean_mosaic_tile1.nc
    #might be due to precision error
    fmsgridtools.coupler_mosaic.make(atm_mosaic_file='C48_mosaic.nc',
                                     lnd_mosaic_file='C48_mosaic.nc',
                                     ocn_mosaic_file='ocean_mosaic.nc',
                                     input_dir='/home/Mikyung.Lee/fmsgridtools/agridfix/tests/mosaic/input',
                                     topog_file='ocean_topog.nc',
                                     on_gpu=True)


if __name__ == "__main__":
    test_make_coupler_mosaic()

