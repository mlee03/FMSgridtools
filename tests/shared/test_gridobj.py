import os

import numpy as np
import xarray as xr
from gridtools import GridObj


"""
Creating data to generate xarray dataset from
"""

nx = 3
ny = 3
nxp = nx + 1
nyp = ny + 1

tile = xr.DataArray(
    [b'tile1'],
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
    [b'arcx'],
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

def test_empty_grid_obj():

    empty_grid_obj = GridObj()
    assert isinstance(empty_grid_obj, GridObj)

def test_gridobj_from_dataset():

    from_dataset_grid_obj = GridObj(grid_data=out_grid_dataset)
    assert isinstance(from_dataset_grid_obj, GridObj)
    assert from_dataset_grid_obj.grid_data is not None
    assert from_dataset_grid_obj.grid_file is None

    np.testing.assert_array_equal(from_dataset_grid_obj.x, out_grid_dataset.x.values)
    np.testing.assert_array_equal(from_dataset_grid_obj.y, out_grid_dataset.y.values)
    np.testing.assert_array_equal(from_dataset_grid_obj.dx, out_grid_dataset.dx.values)
    np.testing.assert_array_equal(from_dataset_grid_obj.dy, out_grid_dataset.dy.values)
    np.testing.assert_array_equal(from_dataset_grid_obj.area, out_grid_dataset.area.values)
    np.testing.assert_array_equal(from_dataset_grid_obj.angle_dx, out_grid_dataset.angle_dx.values)
    np.testing.assert_array_equal(from_dataset_grid_obj.angle_dy, out_grid_dataset.angle_dy)

def test_write_out_grid_griddata(tmp_path):

    from_dataset_grid_obj = GridObj(grid_data=out_grid_dataset)

    file_path = tmp_path / "test_grid.nc"

    from_dataset_grid_obj.write_out_grid(filepath=file_path)

    assert file_path.exists()

    file_path.unlink()

    assert not file_path.exists()

def test_gridobj_from_gridfile_init(tmp_path):

    from_dataset_grid_obj = GridObj(grid_data=out_grid_dataset)

    file_path = tmp_path / "test_grid.nc"

    from_dataset_grid_obj.write_out_grid(filepath=file_path)

    from_file_init_grid_obj = GridObj(grid_file=file_path)
    assert isinstance(from_file_init_grid_obj, GridObj)
    assert from_file_init_grid_obj.grid_file is not None

    # print(from_file_init_grid_obj.x)

    np.testing.assert_array_equal(from_file_init_grid_obj.x, out_grid_dataset.x.values)
    np.testing.assert_array_equal(from_file_init_grid_obj.y, out_grid_dataset.y.values)
    np.testing.assert_array_equal(from_file_init_grid_obj.dx, out_grid_dataset.dx.values)
    np.testing.assert_array_equal(from_file_init_grid_obj.dy, out_grid_dataset.dy.values)
    np.testing.assert_array_equal(from_file_init_grid_obj.area, out_grid_dataset.area.values)
    np.testing.assert_array_equal(from_file_init_grid_obj.angle_dx, out_grid_dataset.angle_dx.values)
    np.testing.assert_array_equal(from_file_init_grid_obj.angle_dy, out_grid_dataset.angle_dy)

    file_path.unlink()

    assert not file_path.exists()

def test_gridobj_from_file(tmp_path):

    from_dataset_grid_obj = GridObj(grid_data=out_grid_dataset)

    file_path = tmp_path / "test_grid.nc"

    from_dataset_grid_obj.write_out_grid(filepath=file_path)

    from_file_grid_obj = GridObj.from_file(filepath=file_path)

    assert isinstance(from_file_grid_obj, GridObj)

    file_path.unlink()

    assert not file_path.exists()

    np.testing.assert_array_equal(from_file_grid_obj.x, out_grid_dataset.x.values)
    np.testing.assert_array_equal(from_file_grid_obj.y, out_grid_dataset.y.values)
    np.testing.assert_array_equal(from_file_grid_obj.dx, out_grid_dataset.dx.values)
    np.testing.assert_array_equal(from_file_grid_obj.dy, out_grid_dataset.dy.values)
    np.testing.assert_array_equal(from_file_grid_obj.area, out_grid_dataset.area.values)
    np.testing.assert_array_equal(from_file_grid_obj.angle_dx, out_grid_dataset.angle_dx.values)
    np.testing.assert_array_equal(from_file_grid_obj.angle_dy, out_grid_dataset.angle_dy)
