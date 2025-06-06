import os
import pytest
import random
import numpy as np
import xarray as xr
from click.testing import CliRunner
from FMSgridtools.shared.mosaicobj import MosaicObj 
from FMSgridtools.make_mosaic.make_mosaic import make_mosaic

DEFAULT_GRID_SIZE = 48
DEFAULT_TILE_NUMBER = 1

gridfiles = [f'grid.tile{x}.nc' for x in range(6)]
gridtiles = [f'tile{x}' for x in range(6)]
tile_number = DEFAULT_TILE_NUMBER
output = 'test_mosaic.nc'
tilefile = 'tile1.nc'


def test_create_tile():
    xstart, xend = 0, 360
    ystart, yend = -90, 90

    x = np.arange(xstart, xend, dtype=np.float64)
    y = np.arange(ystart, yend, dtype=np.float64)
    x, y = np.meshgrid(x, y)

    xarr = xr.DataArray(
            data = x,
            dims = ["nyp", "nxp"])

    yarr = xr.DataArray(
            data = y,
            dims = ["nyp", "nxp"])

    tile = xr.Dataset(
        data_vars={"x": xarr,
                   "y": yarr}).to_netcdf(tilefile)

def test_create_regional_input():
    grid_size = DEFAULT_GRID_SIZE

    nx = 1 + random.randint(1,100) % grid_size
    ny = 1 + random.randint(1,100) % grid_size

    nx_start = 1 + random.randint(1,100) % (grid_size - nx + 1)
    ny_start = 1 + random.randint(1,100) % (grid_size - nx + 1)

    xt = []
    yt= []

    for i in range(1,nx+1):
        xt.append(nx_start+i)

    for i in range(1,ny+1):
        yt.append(ny_start+i)

    xt_data = xr.DataArray(
            data = xt,
            dims = ["grid_xt_sub01"]).astype(np.float64)

    yt_data = xr.DataArray(
        data = yt,
        dims = ["grid_yt_sub01"]).astype(np.float64)

    xr.Dataset(
        data_vars={
            "grid_xt_sub01": xt_data,
            "grid_yt_sub01": yt_data}).to_netcdf(
            f"regional_input_file.tile{tile_number}.nc")


def test_write_function():
    mosaic = MosaicObj(ntiles=6,
                    mosaic_name='test_mosaic',
                    gridlocation='./',
                    gridfiles=np.asarray(gridfiles),
                    gridtiles=np.asarray(gridtiles),
                    contacts=np.full(6, "", dtype=str),
                    contact_index=np.full(6, "", dtype=str))
    mosaic.write_out_mosaic(output)
    assert os.path.exists(output)

def test_getntiles():
    mosaic = MosaicObj(mosaic_file=output).read()
    assert mosaic.ntiles == 6

def test_getgridfiles():
    mosaic = MosaicObj(mosaic_file=output).read()
    assert set(mosaic.gridfiles) == set(gridfiles)
    os.remove(output)

def test_solo_mosaic():
    runner = CliRunner()
    result = runner.invoke(make_mosaic, ['solo',
                                         '--num_tiles', '2',
                                         '--tile_file', 'C192_grid.tile1.nc',
                                         '--tile_file',  'C192_grid.tile2.nc'])
    assert result.exit_code == 0
    assert 'NOTE: There are 1 contacts' in result.stdout
    os.remove('mosaic.nc')
    os.remove(tilefile)

def test_regional_mosaic():
    runner = CliRunner()
    result = runner.invoke(make_mosaic, ['regional',
                                         '--global_mosaic',
                                         'C48_mosaic.nc',
                                         '--regional_file', 
                                         'regional_input_file.tile1.nc'])
    assert result.exit_code == 0
    assert 'Congratulations: You have successfully run regional mosaic' in result.stdout
    os.remove('regional_mosaic.nc')
    os.remove(f'regional_grid.tile{tile_number}.nc')
    os.remove(f'regional_input_file.tile{tile_number}.nc')
