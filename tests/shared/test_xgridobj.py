from gridtools import XGridObj, GridObj
import numpy as np
import os
import pytest
import xarray as xr


def generate_remap_file(filename) :
    string = 255
    ncells = 10
    two = 2

    tile1 = xr.DataArray( data = np.array([1]*ncells),
                          dims = ('ncells'),
                          attrs = dict(tile1_standard_name = "tile_number_in_mosaic1") )
    tile1_cell = xr.DataArray( data = np.array([[4,2]]*ncells),
                               dims = ('ncells', 'two'),
                               attrs = dict(tile1_cell_standard_name = "parent_cell_indices_in_mosaic1"))
    tile2_cell = xr.DataArray( data = np.array([[2,3]]*ncells),
                               dims = ('ncells', 'two'),
                               attrs = dict(tile2_cell_standard_name = "parent_cell_indices_in_mosaic2"))
    xgrid_area = xr.DataArray( data = np.random.rand(ncells),
                               dims = ('ncells'),
                               attrs = dict(xgrid_area_units = "m2"))
    xgrid = xr.Dataset( data_vars = dict(tile1 = tile1,
                                         tile1_cell = tile1_cell,
                                         tile2_cell = tile2_cell,
                                         xgrid_area = xgrid_area))
    xgrid.to_netcdf(filename, mode='w')
    return xgrid


def test_in_development_create_xgridobj() :

    # create xgrid from mosaic files
    with open('src_mosaic.nc', 'w') as myfile : pass
    with open('tgt_mosaic.nc', 'w') as myfile : pass    
    xgrid = XGridObj(src_mosaic='src_mosaic.nc', tgt_mosaic='tgt_mosaic.nc')
    del(xgrid)
    os.remove('src_mosaic.nc')
    os.remove('tgt_mosaic.nc')

    # create xgrid from gridobjs
    src_grid = GridObj(gridfile='file')
    tgt_grid = GridObj(gridfile='file')    
    xgrid = XGridObj( src_grid=src_grid, tgt_grid=tgt_grid )
    del(src_grid, tgt_grid, xgrid)

    
def test_create_xgridobj_from_restart_file() :

    remap_file = 'remap.nc'

    answer = generate_remap_file(remap_file)
    xgrid = XGridObj(restart_remap_file=remap_file)

    assert( answer.equals(xgrid.dataset) )
    del(xgrid, answer)
    os.remove(remap_file)



