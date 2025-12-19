import numpy as np
from pathlib import Path
import pytest
import xarray as xr

import pyfms
import fmsgridtools

ntiles = 6
ncontacts = 12

answers = {}
answers["mosaic"] = xr.DataArray(
    data="test_mosaic",
    attrs=dict(
        standard_name="grid_mosaic_spec",
        children="gridtiles",
        contact_regions="contacts",
        grid_descriptor="",
    ),
)
answers["gridlocation"] = xr.DataArray(
    data="./", attrs=dict(standard_name="grid_file_location")
)
answers["gridfiles"] = xr.DataArray(
    data=[f"C96.tile{i}.nc" for i in range(1, ntiles + 1)], dims=["ntiles"]
)
answers["gridtiles"] = xr.DataArray(
    data=[f"tile{i}" for i in range(1, ntiles + 1)], dims=["ntiles"]
)
answers["contacts"] = xr.DataArray(
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
answers["contact_index"] = xr.DataArray(
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
answers_ds = xr.Dataset(data_vars=answers)


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

    # write mosaic file
    mosaic = fmsgridtools.MosaicObj(mosaicfile=mosaicfile)
    mosaic.mosaic = answers_ds.mosaic.data
    mosaic.gridlocation = answers_ds.gridlocation.data
    mosaic.gridfiles = answers_ds.gridfiles.data
    mosaic.gridtiles = answers_ds.gridtiles.data
    mosaic.contacts = answers_ds.contacts.data
    mosaic.contact_index = answers_ds.contact_index.data

    mosaic.write()
    assert mosaicfile.exists()

    # delete object in order to read
    del mosaic

    # read mosaic file
    mosaic = fmsgridtools.MosaicObj(mosaicfile=mosaicfile).read()

    # check answers
    assert mosaic.mosaic == answers_ds.mosaic.data
    assert mosaic.gridlocation == answers_ds.gridlocation.data
    assert mosaic.gridfiles == list(answers_ds.gridfiles.data)
    assert mosaic.gridtiles == list(answers_ds.gridtiles.data)
    assert mosaic.contacts == list(answers_ds.contacts.data)
    assert mosaic.contact_index == list(answers_ds.contact_index.data)


def test_get_grid(set_fms_files):

    pyfms.fms.init()

    mosaicfile = "test_get_grid.nc"

    # write mosaic file for testing
    answers_ds.to_netcdf(mosaicfile)

    # write grid for testing
    xy = np.arange(0, 96, dtype=np.float64)
    x, y = np.meshgrid(xy, xy)
    for gridfile in mosaic.gridfiles:
        fmsgridtools.GridObj(x=x, y=y).write(gridfile)

    # read mosaic file, get grid
    mosaic = fmsgridtools.MosaicObj(mosaicfile=mosaicfile).read()
    grids = mosaic.get_grid()

    # test grids have been read in correctly
    for tile in mosaic.gridtiles:
        np.testing.assert_array_equal(grids[tile].x, x)
        np.testing.assert_array_equal(grids[tile].y, y)

    # test get grids have been converted to radians correctly
    grids_radians = mosaic.get_grid(radians=True)
    for tile in mosaic.gridtiles:
        np.testing.assert_array_equal(grids_radians[tile].x, np.radians(x))
        np.testing.assert_array_equal(grids_radians[tile].y, np.radians(y))

    pyfms.fms.end()
