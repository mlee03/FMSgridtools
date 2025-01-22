import os

import pytest
import xarray as xr
import numpy as np

from gridtools import GridObj

def test_read_and_write_gridstruct(tmp_path):
    """
    Creating data to generate xarray dataset from
    """
    nx = 3
    ny = 3
    nxp = nx + 1
    nyp = ny + 1

    tile = xr.DataArray(
        ["tile1"],
        attrs=dict(
            standard_name="grid_tile_spec",
            geometry="spherical",
            north_pole="0.0 90.0",
            projection="cube_gnomonic",
            discretization="logically_rectangular",
        )
    )
    x = xr.DataArray(
        data=np.full(shape=(nyp,nxp), fill_value=1.0, dtype=np.float64),
        dims=["nyp", "nxp"],
        attrs=dict(
            units="degree_east", 
            standard_name="geographic_longitude",
        )
    )
    y = xr.DataArray(
        data=np.full(shape=(nyp,nxp), fill_value=2.0, dtype=np.float64),
        dims=["nyp", "nxp"],
        attrs=dict(
            units="degree_north", 
            standard_name="geographic_latitude",
        )
    )
    dx = xr.DataArray(
        data=np.full(shape=(nyp,nx), fill_value=1.5, dtype=np.float64),
        dims=["nyp", "nx"],
        attrs=dict(
            units="meters", 
            standard_name="grid_edge_x_distance",
        )
    )
    dy = xr.DataArray(
        data=np.full(shape=(ny,nxp), fill_value=2.5, dtype=np.float64),
        dims=["ny", "nxp"],
        attrs=dict(
            units="meters", 
            standard_name="grid_edge_y_distance",
        )
    )
    area = xr.DataArray(
        data=np.full(shape=(ny,nx), fill_value=4.0, dtype=np.float64),
        dims=["ny", "nx"],
        attrs=dict(
            units="m2", 
            standard_name="grid_cell_area",
        )
    )
    angle_dx = xr.DataArray(
        data=np.full(shape=(nyp,nxp), fill_value=3.0, dtype=np.float64),
        dims=["nyp", "nxp"],
        attrs=dict(
            units="degrees_east", 
            standard_name="grid_vertex_x_angle_WRT_geographic_east",
        )
    )
    angle_dy = xr.DataArray(
        data=np.full(shape=(nyp,nxp), fill_value=5.0, dtype=np.float64),
        dims=["nyp", "nxp"],
        attrs=dict(
            units="degrees_east", 
            standard_name="grid_vertex_x_angle_WRT_geographic_east",
        )
    )
    arcx = xr.DataArray(
        ["arcx"],
        attrs=dict(
            standard_name="grid_edge_x_arc_type",
            north_pole="0.0 90.0",
            _FillValue=False,
        )
    )

    out_grid_dataset = xr.Dataset(
        data_vars={
            "tile": tile,
            "x": x,
            "y": y,
            "dx": dx,
            "dy": dy,
            "area": area,
            "angle_dx": angle_dx,
            "angle_dy": angle_dy,
            "arcx": arcx,
        }
    )

    file_path = tmp_path / "test_grid.nc"

    empty_grid_obj = GridObj()

    assert isinstance(empty_grid_obj, GridObj)

    from_dataset_grid_obj = GridObj(grid_data=out_grid_dataset)
    assert from_dataset_grid_obj.grid_data is not None
    assert from_dataset_grid_obj.grid_file is None

    from_dataset_grid_obj.write_out_grid(filepath=file_path)

    assert file_path.exists()

    from_file_grid_obj = GridObj(grid_file=file_path)
    assert from_file_grid_obj.grid_data is None
    assert from_file_grid_obj.grid_file is not None

    assert isinstance(from_file_grid_obj, GridObj)

    from_file_meth_grid_obj = GridObj.from_file(filepath=file_path)

    """
    Checking if from_file class method generates instance of GridObj,
    and compares contents to file contents
    """
    assert isinstance(from_file_meth_grid_obj, GridObj)
    np.testing.assert_array_equal(from_file_meth_grid_obj.x, from_dataset_grid_obj.x)
    np.testing.assert_array_equal(from_file_meth_grid_obj.y, from_dataset_grid_obj.y)
    np.testing.assert_array_equal(from_file_meth_grid_obj.dx, from_dataset_grid_obj.dx)
    np.testing.assert_array_equal(from_file_meth_grid_obj.dy, from_dataset_grid_obj.dy)
    np.testing.assert_array_equal(from_file_meth_grid_obj.area, from_dataset_grid_obj.area)
    np.testing.assert_array_equal(from_file_meth_grid_obj.angle_dx, from_dataset_grid_obj.angle_dx)
    np.testing.assert_array_equal(from_file_meth_grid_obj.angle_dy, from_dataset_grid_obj.angle_dy)

    file_path.unlink()

    assert not file_path.exists()
