import os

import pytest
import xarray as xr
import numpy as np

from gridtools import GridStruct

def test_read_and_write_gridstruct(tmp_path):
    nx = 3
    ny = 3
    nxp = nx + 1
    nyp = ny + 1

    out_gridstruct = GridStruct(
        tile="test_tile",
        x = np.full(shape=(nyp,nxp), fill_value=1.0, dtype=np.float64),
        y = np.full(shape=(nyp,nxp), fill_value=2.0, dtype=np.float64),
        dx = np.full(shape=(nyp,nx), fill_value=1.5, dtype=np.float64),
        dy = np.full(shape=(ny,nxp), fill_value=2.5, dtype=np.float64),
        area = np.full(shape=(ny,nx), fill_value=4.0, dtype=np.float64),
        angle_dx = np.full(shape=(nyp,nxp), fill_value=3.0, dtype=np.float64),
        angle_dy = np.full(shape=(nyp,nxp), fill_value=5.0, dtype=np.float64),
        arcx = "test_arcx",
    )

    file_path = tmp_path / "test_grid.nc"

    out_gridstruct.write_out_grid(file_path=file_path)

    assert file_path.exists()

    in_gridstruct = GridStruct.grid_from_file(file_path=file_path)

    assert in_gridstruct.tile == out_gridstruct.tile
    np.testing.assert_array_equal(in_gridstruct.x, out_gridstruct.x)
    np.testing.assert_array_equal(in_gridstruct.y, out_gridstruct.y)
    np.testing.assert_array_equal(in_gridstruct.dx, out_gridstruct.dx)
    np.testing.assert_array_equal(in_gridstruct.dy, out_gridstruct.dy)
    np.testing.assert_array_equal(in_gridstruct.area, out_gridstruct.area)
    np.testing.assert_array_equal(in_gridstruct.angle_dx, out_gridstruct.angle_dx)
    np.testing.assert_array_equal(in_gridstruct.angle_dy, out_gridstruct.angle_dy)
    assert in_gridstruct.arcx == out_gridstruct.arcx

    file_path.unlink()

    assert not file_path.exists()
