import logging
import numpy as np
from pathlib import Path
import pytest
from types import SimpleNamespace
import xarray as xr

import pyfms
import fmsgridtools
from fmsgridtools import GridObj

logger = logging.getLogger(__name__)

"""
Creating data to generate xarray dataset from
"""

nx = 10
ny = 10
nxp = nx + 1
nyp = ny + 1

answers = SimpleNamespace()
answers.tile = xr.DataArray(
    data="tile1",
    attrs=dict(
        standard_name="grid_tile_spec",
        geometry="spherical",
        north_pole="0.0 90.0",
        projection="cube_gnomonic",
        discretization="logically_rectangular",
        _FillValue=None,
    ),
)
answers.x = xr.DataArray(
    data=np.full(shape=(nyp, nxp), fill_value=0.5, dtype=np.float64),
    dims=["nyp", "nxp"],
    attrs=dict(
        units="degree_east", standard_name="geographic_longitude", _FillValue=None
    ),
)
answers.y = xr.DataArray(
    data=np.full(shape=(nyp, nxp), fill_value=1.0, dtype=np.float64),
    dims=["nyp", "nxp"],
    attrs=dict(
        units="degree_north", standard_name="geographic_latitude", _FillValue=None
    ),
)
answers.dx = xr.DataArray(
    data=np.full(shape=(nyp, nx), fill_value=1.5, dtype=np.float64),
    dims=["nyp", "nx"],
    attrs=dict(units="meters", standard_name="grid_edge_x_distance", _FillValue=None),
)
answers.dy = xr.DataArray(
    data=np.full(shape=(ny, nxp), fill_value=2.5, dtype=np.float64),
    dims=["ny", "nxp"],
    attrs=dict(units="meters", standard_name="grid_edge_y_distance", _FillValue=None),
)
answers.area = xr.DataArray(
    data=np.full(shape=(ny, nx), fill_value=4.0, dtype=np.float64),
    dims=["ny", "nx"],
    attrs=dict(units="m2", standard_name="grid_cell_area", _FillValue=None),
)
answers.angle_dx = xr.DataArray(
    data=np.full(shape=(nyp, nxp), fill_value=3.0, dtype=np.float64),
    dims=["nyp", "nxp"],
    attrs=dict(
        units="degrees_east",
        standard_name="grid_vertex_x_angle_WRT_geographic_east",
        _FillValue=None,
    ),
)
answers.angle_dy = xr.DataArray(
    data=np.full(shape=(nyp, nxp), fill_value=5.0, dtype=np.float64),
    dims=["nyp", "nxp"],
    attrs=dict(
        units="degrees_east",
        standard_name="grid_vertex_x_angle_WRT_geographic_east",
        _FillValue=None,
    ),
)
answers.arcx = xr.DataArray(
    "arcx",
    attrs=dict(
        standard_name="grid_edge_x_arc_type",
        north_pole="0.0 90.0",
        _FillValue=None,
    ),
)


@pytest.fixture(autouse=True)
def set_fms_files():

    inputnml = Path("input.nml")
    logfile = Path("logfile.000000.out")
    warnfile = Path("warnfile.000000.out")

    inputnml.touch()

    yield

    if inputnml.exists():
        inputnml.unlink()
    if logfile.exists():
        logfile.unlink()
    if warnfile.exists():
        warnfile.unlink()


def test_read_write(set_fms_files):

    pyfms.fms.init()

    gridfile = Path("test_read_write.nc")

    # write gridobj
    testgrid = GridObj(gridtype="cubic")
    testgrid.x = answers.x.data
    testgrid.y = answers.y.data
    testgrid.dx = answers.dx.data
    testgrid.dy = answers.dy.data
    testgrid.area = answers.area.data
    testgrid.angle_dx = answers.angle_dx.data
    testgrid.angle_dy = answers.angle_dy.data
    testgrid.arcx = str(answers.arcx.data)
    testgrid.tile = str(answers.tile.data)

    testgrid.write(gridfile)
    assert gridfile.exists()

    del testgrid

    # read gridobj
    testgrid = GridObj(gridfile=gridfile).read()

    # test dims
    assert testgrid.nx == nx
    assert testgrid.ny == ny
    assert testgrid.nxp == nxp
    assert testgrid.nyp == nyp

    # test values
    np.testing.assert_array_equal(testgrid.x, answers.x.data)
    np.testing.assert_array_equal(testgrid.y, answers.y.data)
    np.testing.assert_array_equal(testgrid.dx, answers.dx.data)
    np.testing.assert_array_equal(testgrid.dy, answers.dy.data)
    np.testing.assert_array_equal(testgrid.area, answers.area.data)
    np.testing.assert_array_equal(testgrid.angle_dx, answers.angle_dx.data)
    np.testing.assert_array_equal(testgrid.angle_dy, answers.angle_dy.data)
    assert testgrid.arcx == str(answers.arcx.data)
    assert testgrid.tile == str(answers.tile.data)

    gridfile.unlink()
    pyfms.fms.end()


def test_minigrids_option(set_fms_files):

    pyfms.fms.init()

    gridfile = Path("test_center.nc")
    nx2 = nx // 2
    ny2 = ny // 2
    nx2p = nx2 + 1
    ny2p = ny2 + 1

    # center points are value of 1
    x = np.array([[1, 0] * nx2 + [1]] * nyp)
    y = np.array([[1] * nxp, [0] * nxp] * ny2 + [[1] * nxp])

    GridObj(gridfile=gridfile, x=x, y=y).write()

    #test gridc
    grid = GridObj(gridfile=gridfile).read(radians=True, xy_only=True)
    gridc = grid.get_gridc()

    assert gridc.xsize == nx2p
    assert gridc.ysize == ny2p

    answer = np.radians(np.ones((ny2p, nx2p), dtype=np.float64))
    np.testing.assert_array_equal(gridc.x, answer)
    np.testing.assert_array_equal(gridc.y, answer)

    grid.free_gridc()
    assert grid.gridc is None

    #test gridt
    gridt = grid.get_gridt()

    assert gridt.xsize == nx2
    assert gridt.ysize == ny2

    answer = np.zeros((ny2, nx2), dtype=np.float64)
    np.testing.assert_array_equal(gridt.x, answer)
    np.testing.assert_array_equal(gridt.y, answer)

    grid.free_gridt()
    assert grid.gridt is None

    grid.free_supergrid()
    assert grid.x is grid.y is None

    gridfile.unlink()
    pyfms.fms.end()

#@pytest.mark.skip("error in pyFMS")
def test_to_domain(set_fms_files):

    nx, ny = 8, 8
    global_indices = [0, nx - 1, 0, ny - 1]

    Path("input.nml").touch()

    pyfms.fms.init()
    domain = pyfms.mpp_domains.define_domains(global_indices)

    x1 = np.arange(nx + 1, dtype=np.float64)
    y1 = np.arange(ny + 1, dtype=np.float64)
    x, y = np.meshgrid(x1, y1)
    area = np.ones((ny, nx), dtype=np.float64)

    grid = GridObj(x=x, y=y, area=area, domain=domain)
    grid.to_domain(domain)

    x1_answer = np.arange(domain.isc, domain.iec + 2, dtype=np.float64)
    y1_answer = np.arange(domain.jsc, domain.jec + 2, dtype=np.float64)
    xanswer, yanswer = np.meshgrid(x1_answer, y1_answer)
    area_answer = np.ones((domain.ysize_c, domain.xsize_c), dtype=np.float64)

    np.testing.assert_array_equal(grid.x, xanswer)
    np.testing.assert_array_equal(grid.y, yanswer)
    np.testing.assert_array_equal(grid.area, area_answer)

    pyfms.fms.end()
