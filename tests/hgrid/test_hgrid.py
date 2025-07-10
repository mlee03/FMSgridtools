import os
from click.testing import CliRunner
import ctypes
import numpy
import xarray
from pathlib import Path
from FMSgridtools.make_hgrid.make_hgrid import make_hgrid
from FMSgridtools.make_hgrid.hgridobj import HGridObj

def test_lonlat_grid():
    runner = CliRunner()
    result = runner.invoke(make_hgrid, ['lonlat',
                                         '--xbnds', '0,30',
                                         '--ybnds', '50,50',
                                         '--nlon',  '60',
                                         '--nlat', '20',])
    assert result.exit_code == 0
    os.remove('horizontal_grid.nc')

def test_make_hgrid_info():

    hgrid_obj = HGridObj()

    hgrid_obj.make_grid_info(
        nxbnds=2,
        nybnds=2,
        nlon=numpy.array([60]),
        nlat=numpy.array([20]),
        conformal=False,
    )

    assert hgrid_obj.nxl.shape[0] == 1
    assert hgrid_obj.nxl.size == 1
    assert hgrid_obj.nxl[0] == 60
    assert hgrid_obj.nyl.shape[0] == 1
    assert hgrid_obj.nyl.size == 1
    assert hgrid_obj.nyl[0] == 20
    assert hgrid_obj.nx == hgrid_obj.nxl[0]
    assert hgrid_obj.ny == hgrid_obj.nyl[0]
    assert hgrid_obj.nxp == hgrid_obj.nx + 1
    assert hgrid_obj.nyp == hgrid_obj.ny + 1
    assert hgrid_obj.x.shape[0] == ctypes.c_ulong(hgrid_obj.nxp * hgrid_obj.nyp).value
    assert hgrid_obj.y.shape[0] == ctypes.c_ulong(hgrid_obj.nxp * hgrid_obj.nyp).value
    assert hgrid_obj.dx.shape[0] == ctypes.c_ulong(hgrid_obj.nx * hgrid_obj.nyp).value
    assert hgrid_obj.dy.shape[0] == ctypes.c_ulong(hgrid_obj.nxp * hgrid_obj.ny).value
    assert hgrid_obj.angle_dx.shape[0] == ctypes.c_ulong(hgrid_obj.nxp * hgrid_obj.nyp).value
    assert hgrid_obj.angle_dy.shape[0] == ctypes.c_ulong(hgrid_obj.nxp * hgrid_obj.nyp).value
    assert hgrid_obj.area.shape[0] == ctypes.c_ulong(hgrid_obj.nx * hgrid_obj.ny).value
    assert hgrid_obj.isc == 0
    assert hgrid_obj.iec == hgrid_obj.nx - 1
    assert hgrid_obj.jsc == 0
    assert hgrid_obj.jec == hgrid_obj.ny - 1




def test_write_out_hgrid():
    hgrid_obj = HGridObj()

    hgrid_obj.make_grid_info(
        nxbnds=2,
        nybnds=2,
        nlon=numpy.array([60]),
        nlat=numpy.array([20]),
        conformal=False,
    )

    grid_name = "test_hgrid"
    grid_file = grid_name + ".nc"

    hgrid_obj.write_out_hgrid(
        grid_name=grid_name,
    )

    assert Path(grid_file).exists()
    ds = xarray.open_dataset(grid_file)
    assert ds.data_vars['x'].dims == ('nyp','nxp')
    assert numpy.array_equal(ds.data_vars['x'].values.flatten(), hgrid_obj.x)
    grid_obj = hgrid_obj.make_gridobj()
    grid_obj.get_attributes()
    assert numpy.array_equal(grid_obj.x.flatten(), hgrid_obj.x)
    os.remove(Path(grid_file))

