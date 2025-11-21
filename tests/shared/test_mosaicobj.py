import numpy as np
from pathlib import Path
import pytest
import xarray as xr

import pyfms
import fmsgridtools

ntiles = 6
ncontacts = 12

ds = {}
ds["mosaic"] = xr.DataArray(
    data="test_mosaic",
    attrs=dict(
        standard_name="grid_mosaic_spec",
        children="gridtiles",
        contact_regions="contacts",
        grid_descriptor="",
    ),
)
ds["gridlocation"] = xr.DataArray(
    data="./", attrs=dict(standard_name="grid_file_location")
)
ds["gridfiles"] = xr.DataArray(
    data=[f"C96.tile{i}.nc" for i in range(1, ntiles + 1)], dims=["ntiles"]
)
ds["gridtiles"] = xr.DataArray(
    data=[f"tile{i}" for i in range(1, ntiles + 1)], dims=["ntiles"]
)
ds["contacts"] = xr.DataArray(
    data=[
        "C384_mosaic:tile1::C384_mosaic:tile2",
        "C384_mosaic:tile1::C384_mosaic:tile3",
        "C384_mosaic:tile1::C384_mosaic:tile5",
        "C384_mosaic:tile1::C384_mosaic:tile6",
        "C384_mosaic:tile2::C384_mosaic:tile3",
        "C384_mosaic:tile2::C384_mosaic:tile4",
        "C384_mosaic:tile2::C384_mosaic:tile6",
        "C384_mosaic:tile3::C384_mosaic:tile4",
        "C384_mosaic:tile3::C384_mosaic:tile5",
        "C384_mosaic:tile4::C384_mosaic:tile5",
        "C384_mosaic:tile4::C384_mosaic:tile6",
        "C384_mosaic:tile5::C384_mosaic:tile6",
    ],
    attrs=dict(
        standard_name="grid_contact_spec",
        contact_type="boundary",
        alignment="true",
        contact_index="contact_index",
        orientation="orient",
    ),
    dims=["ncontacts"],
)
ds["contact_index"] = xr.DataArray(
    data=[
        "768:768,1:768::1:1,1:768",
        "1:768,768:768::1:1,768:1",
        "1:1,1:768::768:1,768:768",
        "1:768,1:1::1:768,768:768",
        "1:768,768:768::1:768,1:1",
        "768:768,1:768::768:1,1:1",
        "1:768,1:1::768:768,768:1",
        "768:768,1:768::1:1,1:768",
        "1:768,768:768::1:1,768:1",
        "1:768,768:768::1:768,1:1",
        "768:768,1:768::768:1,1:1",
        "768:768,1:768::1:1,1:768",
    ],
    dims=["ncontacts"],
    attrs=dict(standard_name="starting_ending_point_index_of_contact"),
)
example_ds = xr.Dataset(data_vars=ds)


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


def test_read_and_write(set_fms_files):

    mosaicfile = "test_mosaic.nc"

    mosaic = fmsgridtools.MosaicObj(mosaicfile=mosaicfile)
    mosaic.mosaic = example_ds.mosaic.data
    mosaic.gridlocation = example_ds.gridlocation.data
    mosaic.gridfiles = example_ds.gridfiles.data
    mosaic.gridtiles = example_ds.gridtiles.data
    mosaic.contacts = example_ds.contacts.data
    mosaic.contact_index = example_ds.contact_index.data

    mosaic.write()

    del mosaic

    mosaic = fmsgridtools.MosaicObj(mosaicfile=mosaicfile).read()

    assert mosaic.mosaic == example_ds.mosaic.data
    assert mosaic.gridlocation == example_ds.gridlocation.data
    assert mosaic.gridfiles == list(example_ds.gridfiles.data)
    assert mosaic.gridtiles == list(example_ds.gridtiles.data)
    assert mosaic.contacts == list(example_ds.contacts.data)
    assert mosaic.contact_index == list(example_ds.contact_index.data)


def test_get_grid(set_fms_files):

    pyfms.fms.init()

    mosaicfile = "test_get_grid.nc"
    example_ds.to_netcdf(mosaicfile)

    mosaic = fmsgridtools.MosaicObj(mosaicfile=mosaicfile).read()

    # write grid
    xy = np.arange(0, 96, dtype=np.float64)
    x, y = np.meshgrid(xy, xy)
    for gridfile in mosaic.gridfiles:
        fmsgridtools.GridObj(x=x, y=y).write(gridfile)

    # test get grid
    grids = mosaic.get_grid()
    for tile in mosaic.gridtiles:
        np.testing.assert_array_equal(grids[tile].x, x)
        np.testing.assert_array_equal(grids[tile].y, y)

    # test get grid in radians
    grids_radians = mosaic.get_grid(radians=True)
    for tile in mosaic.gridtiles:
        np.testing.assert_array_equal(grids_radians[tile].x, np.radians(x))
        np.testing.assert_array_equal(grids_radians[tile].y, np.radians(y))

    pyfms.fms.end()
