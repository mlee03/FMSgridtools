# unit test for Topog.py functionality

from gridtools_lib import TopogObj
import numpy as np
import pytest
from pathlib import Path

def test_write_one_tile():
    test_topog = TopogObj(output_name="test_topog_single_tile.nc",
                          ntiles = 1,
                          nx = 16,
                          ny = 16,
                          depth = np.zeros((16, 16)),
                          x_refine = 1,
                          y_refine = 1,
                          scale_factor = 1)
    test_topog.write_topog_file()
    assert Path("test_topog_single_tile.nc").exists()

def test_write_multi_tile():
    test_topog = TopogObj(output_name="test_topog_multi_tile.nc",
                          ntiles = 6,
                          nx = 16,
                          ny = 16,
                          depth = np.zeros((16, 16, 6)),
                          x_refine = 1,
                          y_refine = 1,
                          scale_factor = 1)
    test_topog.write_topog_file()
    assert Path("test_topog_multi_tile.nc").exists()

@pytest.mark.skip(reason="TODO")
def test_generate_realistic():
    pass

@pytest.mark.skip(reason="TODO")
def test_generate_rectangular_basin():
    pass

@pytest.mark.skip(reason="TODO")
def test_generate_gaussian():
    pass

@pytest.mark.skip(reason="TODO")
def test_generate_dome():
    pass

@pytest.mark.skip(reason="TODO")
def test_generate_bowl():
    pass

@pytest.mark.skip(reason="TODO")
def test_generate_idealized():
    pass

@pytest.mark.skip(reason="TODO")
def test_generate_idealized():
    pass