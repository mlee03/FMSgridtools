import numpy as np
import xarray as xr

import fmsgridtools

def test_make_coupler_mosaic():

    fmsgridtools.make_coupler_mosaic(atm_mosaic_file='C48_mosaic.nc',
                                     lnd_mosaic_file='C48_mosaic.nc',
                                     ocn_mosaic_file='ocean_mosaic.nc',
                                     input_dir='/home/Mikyung.Lee/fmsgridtools/agridfix/tests/mosaic/input',
                                     topog_file='ocean_topog.nc')


if __name__ == "__main__":
    test_make_coupler_mosaic()

