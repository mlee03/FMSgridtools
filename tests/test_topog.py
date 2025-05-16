# unit test for Topog.py functionality

from os import remove
from pathlib import Path

import numpy as np
import pytest
import xarray

from FMSgridtools import TopogObj, get_provenance_attrs


def test_generate_rectangular_basin_single_tile():
    out_file = "test_topog_rectangular_basin_single_tile.nc"
    test_topog = TopogObj(output_name=out_file,
                          ntiles = 1,
                          global_attrs = get_provenance_attrs(),
                          x_vals_tile = {'tile1': 16},
                          y_vals_tile = {'tile1': 16},
                          x_refine = 1,
                          y_refine = 1,
                          scale_factor = 1)
    test_topog.make_rectangular_basin(bottom_depth=128)
    test_topog.write_topog_file()
    assert Path(out_file).exists()
    ds = xarray.open_dataset(out_file)
    assert ds.data_vars['depth'].dims == ('ny', 'nx')
    assert all(val == 128.0 for val in ds.data_vars['depth'].values.flatten())
    remove(Path(out_file))

def test_generate_rectangular_basin_multi_tile():
    out_file = "test_topog_rectangular_basin_multi_tile.nc"
    test_topog = TopogObj(output_name=out_file,
                          ntiles = 6,
                          global_attrs = get_provenance_attrs(),
                          x_vals_tile = {'tile1': 16,
                                'tile2': 16,
                                'tile3': 16,
                                'tile4': 16,
                                'tile5': 16,
                                'tile6': 16},
                          y_vals_tile = {'tile1': 16,
                                'tile2': 16,
                                'tile3': 16,
                                'tile4': 16,
                                'tile5': 16,
                                'tile6': 16},
                          x_refine = 1,
                          y_refine = 1,
                          scale_factor = 1)
    test_topog.make_rectangular_basin(bottom_depth=128.0)
    test_topog.write_topog_file()
    assert Path(out_file).exists()
    ds = xarray.open_dataset(out_file)
    for i in range(6):
        assert ds.data_vars[f'depth_tile{i+1}'].dims == (f'ny_tile{i+1}', f'nx_tile{i+1}')
        assert all( val == 128.0 for val in ds.data_vars[f'depth_tile{i+1}'].values.flatten())
    remove(Path(out_file))

# needs input files generated, will be much easier once make_hgrid and make_mosaic are done
@pytest.mark.skip(reason="TODO")
def test_generate_realistic():
    pass
