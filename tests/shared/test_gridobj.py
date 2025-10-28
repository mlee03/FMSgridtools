import numpy as np
from numpy.testing import assert_array_equal
from pathlib import Path
from types import SimpleNamespace
import xarray as xr

import pyfms
from fmsgridtools import GridObj


"""
Creating data to generate xarray dataset from
"""

nx = 10
ny = 10
nxp = nx + 1
nyp = ny + 1

ds = SimpleNamespace()
ds.tile = xr.DataArray(
    data='tile1',
    attrs=dict(
        standard_name="grid_tile_spec",
        geometry="spherical",
        north_pole="0.0 90.0",
        projection="cube_gnomonic",
        discretization="logically_rectangular",
    )
)
ds.x = xr.DataArray(
    data=np.full(shape=(nyp,nxp), fill_value=0.5, dtype=np.float64),
    dims=["nyp", "nxp"],
    attrs=dict(
        units="degree_east",
        standard_name="geographic_longitude",
    )
)
ds.y = xr.DataArray(
    data=np.full(shape=(nyp,nxp), fill_value=1.0, dtype=np.float64),
    dims=["nyp", "nxp"],
    attrs=dict(
        units="degree_north",
        standard_name="geographic_latitude",
    )
)
ds.dx = xr.DataArray(
    data=np.full(shape=(nyp,nxp), fill_value=1.5, dtype=np.float64),
    dims=["nyp", "nx"],
    attrs=dict(
        units="meters",
        standard_name="grid_edge_x_distance",
    )
)
ds.dy = xr.DataArray(
    data=np.full(shape=(nyp,nxp), fill_value=2.5, dtype=np.float64),
    dims=["ny", "nxp"],
    attrs=dict(
        units="meters",
        standard_name="grid_edge_y_distance",
    )
)
ds.area = xr.DataArray(
    data=np.full(shape=(ny,nx), fill_value=4.0, dtype=np.float64),
    dims=["ny", "nx"],
    attrs=dict(
        units="m2",
        standard_name="grid_cell_area",
    )
)
ds.angle_dx = xr.DataArray(
    data=np.full(shape=(nyp,nxp), fill_value=3.0, dtype=np.float64),
    dims=["nyp", "nxp"],
    attrs=dict(
        units="degrees_east",
        standard_name="grid_vertex_x_angle_WRT_geographic_east",
    )
)
ds.angle_dy = xr.DataArray(
    data=np.full(shape=(nyp,nxp), fill_value=5.0, dtype=np.float64),
    dims=["nyp", "nxp"],
    attrs=dict(
        units="degrees_east",
        standard_name="grid_vertex_x_angle_WRT_geographic_east",
    )
)
ds.arcx = xr.DataArray(
    [b'arcx'],
    attrs=dict(
        standard_name="grid_edge_x_arc_type",
        north_pole="0.0 90.0",
         _FillValue=False,
    )
)


def test_read_write(tmp_path):

    gridfile = Path("test.nc")

    testgrid = GridObj(gridtype="cubic")
    answers = [(ds.x, testgrid.x_obj),
               (ds.y, testgrid.y_obj),
               (ds.dx, testgrid.dx_obj),
               (ds.dy, testgrid.dy_obj),
               (ds.area, testgrid.area_obj),
               (ds.angle_dx, testgrid.angle_dx_obj),
               (ds.angle_dy, testgrid.angle_dy_obj),
               (ds.arcx, testgrid.arcx_obj),
               (ds.tile, testgrid.tile_obj)
    ]

    pyfms.fms.init()

    testgrid.x = ds.x.data
    testgrid.y = ds.y.data
    testgrid.dx = ds.dx.data
    testgrid.dy = ds.dy.data
    testgrid.area = ds.area.data
    testgrid.angle_dx = ds.angle_dx.data
    testgrid.angle_dy = ds.angle_dy.data
    testgrid.arcx = ds.arcx.data
    testgrid.tile = ds.tile.data

    testgrid.write(gridfile)

    assert gridfile.exists()

    del testgrid

    testgrid = GridObj(gridfile=gridfile).read_all()

    #test dims
    assert testgrid.nx == nx
    assert testgrid.ny == ny
    assert testgrid.nxp == nxp
    assert testgrid.nyp == nyp
    
    #test values
    for ds_coord, testgrid_coord in answers:
        assert_array_equal(ds_coord, testgrid_coord.data)

    gridfile.unlink()

    pyfms.fms.end()


def test_center_option():

    pyfms.fms.init()
    
    gridfile = "test_center.nc"
    nx2 = nx // 2
    ny2 = ny // 2
    nx2p = nx2 + 1
    ny2p = ny2 + 1

    # center points are value of 1
    x = np.array([[1,0]*nx2 + [1]]*nyp)
    y = np.array([[1]*nxp, [0]*nxp]*ny2 + [[1]*nxp])

    GridObj(gridfile=gridfile, x=x, y=y).write()

    grid = GridObj(gridfile=gridfile)
    xc, yc = grid.read_xy(center=True, radians=True)

    assert grid.nx == nx2
    assert grid.ny == ny2
    assert grid.nxp == nx2 + 1
    assert grid.nyp == ny2 + 1

    answer = np.radians(np.ones((ny2p,nx2p), dtype=np.float64))
    
    assert_array_equal(xc, answer)
    assert_array_equal(yc, answer)

    pyfms.fms.end()
    
    
def test_to_domain():

    nx, ny = 8, 8
    global_indices = [0, nx-1, 0, ny-1]
    
    pyfms.fms.init(ndomain=1)
    domain = pyfms.mpp_domains.define_domains(global_indices)

    x1 = np.arange(nx+1, dtype=np.float64)
    y1 = np.arange(ny+1, dtype=np.float64)
    x, y = np.meshgrid(x1, y1)

    area = np.ones((ny, nx), dtype=np.float64)
    
    grid = GridObj(x=x, y=y, area=area)
    grid.to_domain(domain)

    x1 = np.arange(domain.isc, domain.iec+2, dtype=np.float64)
    y1 = np.arange(domain.jsc, domain.jec+2, dtype=np.float64)
    xanswer, yanswer = np.meshgrid(x1, y1)
    area_answer = np.ones((domain.ysize_c, domain.xsize_c), dtype=np.float64)
    
    assert_array_equal(grid.x, xanswer)
    assert_array_equal(grid.y, yanswer)
    assert_array_equal(grid.area, area_answer)

    pyfms.fms.end()

    


