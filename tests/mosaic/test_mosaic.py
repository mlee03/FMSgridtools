import os
import pytest
import random
import numpy as np
import xarray as xr
from click.testing import CliRunner
import fmsgridtools

grid_size = 48
tile_number = 1

gridfiles = [f'grid.tile{x}.nc' for x in range(6)]
gridtiles = [f'tile{x}' for x in range(6)]
ntiles = 6
output = 'test_mosaic.nc'


def make_grid(gridfile):

    xy = np.arange(0, grid_size+1, dtype=np.float64)

    x, y = np.meshgrid(xy, xy)
    area = xr.DataArray(np.ones((grid_size, grid_size), dtype=np.float64), dims=["ny", "nx"])
    x = xr.DataArray(x, dims=["nyp", "nxp"])
    y = xr.DataArray(y, dims=["nyp", "nxp"])
    
    xr.Dataset(data_vars = {"x": x, "y":y, "area":area}).to_netcdf(gridfile)

    
@pytest.mark.skip
def test_create_regional_input():

    nx = 1 + random.randint(1,100) % grid_size
    ny = 1 + random.randint(1,100) % grid_size

    nx_start = 1 + random.randint(1,100) % (grid_size - nx + 1)
    ny_start = 1 + random.randint(1,100) % (grid_size - nx + 1)

    xt = [nx_start+i for i in range(1, nx+1)]
    yt = [ny_start+i for i in range(1, ny+1)]

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

def test_write():
    mosaic = fmsgridtools.MosaicObj(ntiles=6,
                                    mosaic_name='test_mosaic',
                                    gridlocation='./',
                                    gridfiles=np.asarray(gridfiles),
                                    gridtiles=np.asarray(gridtiles),
                                    contacts=np.full(6, "", dtype=str),
                                    contact_index=np.full(6, "", dtype=str))
    mosaic.write(output)
    assert os.path.exists(output)
 
def test_ntiles():
    mosaic = fmsgridtools.MosaicObj(mosaic_name=output).read()
    assert mosaic.ntiles == 6

    
def test_gridfiles():
    mosaic2 = fmsgridtools.MosaicObj(mosaic_name=output).read()
    assert all([mosaic2.gridfiles[i] == gridfiles[i] for i in range(mosaic2.ntiles)])
    os.remove(output)

    
def test_getgrid():

    for ifile in gridfiles: make_grid(ifile)
    mosaic = fmsgridtools.MosaicObj(ntiles=ntiles, gridtiles=gridtiles, gridfiles=gridfiles)
    mosaic.get_grid(toradians=True)
    
    
def test_solo_mosaic():

    x1, y1 = np.meshgrid(np.arange(0,46,1, dtype=np.float64), np.arange(0,11,1, dtype=np.float64))
    xr.Dataset(data_vars=dict(x=xr.DataArray(x1, dims=["nyp","nxp"]),
                              y=xr.DataArray(y1, dims=["nyp", "nxp"]))
    ).to_netcdf('grid.tile1.nc')
    
    x2, y2 = np.meshgrid(np.arange(45,90,1, dtype=np.float64), np.arange(0,11,1, dtype=np.float64))
    xr.Dataset(data_vars=dict(x=xr.DataArray(x2, dims=["nyp","nxp"]),
                              y=xr.DataArray(y2, dims=["nyp", "nxp"]))
    ).to_netcdf('grid.tile2.nc')
                          
    runner = CliRunner()
    result = runner.invoke(fmsgridtools.make_mosaic.solo, ['--num_tiles', '2',
                                                           '--tile_file', 'grid.tile1.nc',
                                                           '--tile_file', 'grid.tile2.nc'])
    
    assert result.exit_code == 0
    print(result.stdout)
    assert 'NOTE: There are 1 contacts' in result.stdout
    os.remove('mosaic.nc')
    os.remove('grid.tile1.nc')
    os.remove('grid.tile2.nc')

@pytest.mark.skip
def test_regional_mosaic():
    runner = CliRunner()
    result = runner.invoke(fmsgridtools.make_mosaic, ['regional',
                                         '--global_mosaic',
                                         'C48_mosaic.nc',
                                         '--regional_file', 
                                         'regional_input_file.tile1.nc'])
    assert result.exit_code == 0
    assert 'Congratulations: You have successfully run regional mosaic' in result.stdout
    os.remove('regional_mosaic.nc')
    os.remove(f'regional_grid.tile{tile_number}.nc')
    os.remove(f'regional_input_file.tile{tile_number}.nc')
