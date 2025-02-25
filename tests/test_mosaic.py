import pytest
import os
import numpy as np
from click.testing import CliRunner
from FMSgridtools.shared.mosaicobj import MosaicObj

gridfiles = [f'grid.tile{x}.nc' for x in range(6)]
gridtiles = [f'tile{x}' for x in range(6)]
output = 'test_mosaic.nc'

def test_write_function():
    mosaic = MosaicObj(ntiles=6,
                    mosaic_name='test_mosaic',
                    gridlocation='./',
                    gridfiles=np.asarray(gridfiles),
                    gridtiles=np.asarray(gridtiles),
                    contacts=np.full(6, "", dtype=str),
                    contact_index=np.full(6, "", dtype=str))
    mosaic.write_out_mosaic(output)
    assert os.path.exists(output) == True

def test_getntiles():
    mosaic = MosaicObj(mosaic_file=output)
    ntiles = mosaic.get_ntiles()
    assert ntiles == 6

def test_getgridfiles():
    mosaic2 = MosaicObj(mosaic_file=output)
    assert mosaic2.gridfiles == gridfiles
    os.remove(output)

def test_solo_mosaic():
    #will attempt to utilize CliRunner() to test make_mosaic.py
    pass

def test_regional_mosaic():
    pass



