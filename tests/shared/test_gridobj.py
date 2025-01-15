import os

import pytest
import xarray as xr
import numpy as np

from gridtools import GridObj

def test_read_and_write_gridstruct(tmp_path):
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

    out_grid_obj = GridObj(grid=out_grid_dataset, gridfile=file_path)

    out_grid_obj.write_out_grid(filepath=file_path)

    assert file_path.exists()

    in_grid_obj = GridObj.from_file(filepath=file_path)

    assert in_grid_obj.grid.tile == out_grid_obj.grid.tile
    np.testing.assert_array_equal(in_grid_obj.grid.x, out_grid_obj.grid.x)
    np.testing.assert_array_equal(in_grid_obj.grid.y, out_grid_obj.grid.y)
    np.testing.assert_array_equal(in_grid_obj.grid.dx, out_grid_obj.grid.dx)
    np.testing.assert_array_equal(in_grid_obj.grid.dy, out_grid_obj.grid.dy)
    np.testing.assert_array_equal(in_grid_obj.grid.area, out_grid_obj.grid.area)
    np.testing.assert_array_equal(in_grid_obj.grid.angle_dx, out_grid_obj.grid.angle_dx)
    np.testing.assert_array_equal(in_grid_obj.grid.angle_dy, out_grid_obj.grid.angle_dy)
    assert in_grid_obj.grid.arcx == out_grid_obj.grid.arcx

    file_path.unlink()

    assert not file_path.exists()
