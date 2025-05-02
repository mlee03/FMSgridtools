import pytest
import os
import numpy as np
from click.testing import CliRunner
from FMSgridtools.shared.mosaicobj import MosaicObj
from FMSgridtools.make_mosaic.make_mosaic import make_mosaic

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
    assert os.path.exists(output) is True

def test_getntiles():
    mosaic = MosaicObj(mosaic_file=output)
    ntiles = mosaic.get_ntiles()
    assert ntiles == 6

def test_getgridfiles():
    mosaic2 = MosaicObj(mosaic_file=output)
    assert mosaic2.gridfiles == gridfiles
    os.remove(output)

def test_solo_mosaic():
    runner = CliRunner()
    result = runner.invoke(make_mosaic, ['solo', 
                                         '--num_tiles', '2',  
                                         '--tile_file', 'C192_grid.tile1.nc', 
                                         '--tile_file',  'C192_grid.tile2.nc'])
    assert result.exit_code == 0 
    assert 'NOTE: There are 1 contacts' in result.stdout


def test_regional_mosaic():
    runner = CliRunner()
    result = runner.invoke(make_mosaic, ['regional', 
                                         '--global_mosaic', 'C48_mosaic.nc', 
                                         '--regional_file', 'rregion_input_file.tile3.nc']) 
    assert result.exit_code == 0 
    assert 'Congratulations: You have successfully run regional mosaic' in result.stdout
