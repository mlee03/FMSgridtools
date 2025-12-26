import numpy as np
from types import SimpleNamespace
import xarray as xr

import fmsgridtools

def write_files(outfile):

    grid_xt, grid_yt, nk, ntimes = 100, 50, 10, 4

    variable_xt = xr.DataArray(
        np.arange(grid_xt, dtype=np.float64),
        dims = ["grid_xt"],
        attrs={
            "units": "degrees_E",
            "long_name": "made up T-cell longitude",
            "axis": "X"
        }
    )

    variable_yt = xr.DataArray(
        np.arange(grid_yt, dtype=np.float64),
        dims = ["grid_yt"],
        attrs={
            "units": "degrees_N",
            "long_name": "made up T-cell latitude",
            "axis": "Y"
        }
    )

    variable_yt = xr.DataArray(
        np.arange(grid_yt, dtype=np.float64),
        dims = ["grid_yt"],
        attrs={
            "units": "degrees_N",
            "long_name": "made up T-cell latitude",
            "axis": "Y"
        }
    )

    variable_pfull = xr.DataArray(
        np.arange(nk, dtype=np.float64),
        dims = ["pfull"],
        attrs = {
            "units": "mb",
            "long_name": "ref full pressure level",
            "axis": "Z",
            "positive": "down"
        }
    )

    variable_time = xr.DataArray(
        np.arange(ntimes, dtype=np.float64),
        dims = ["time"],
        attrs= {
            "units": "days since 0001-01-01 00:00:00",
            "long_name": "time",
            "axis": "T",
            "calendar_type": "NOLEAP",
            "calendar": "noleap"
        }
    )

    variable1 = xr.DataArray(
        np.ones((grid_yt, grid_xt), dtype=np.float64),
        dims = ["grid_yt", "grid_xt"],
        attrs = {
            "_FillValue": -np.float64(-100),
            "long_name": "test variable 1",
            "units": "kg m-2",
            "missing": np.float64(45.12),
            "add_offset": np.float64(-24.326),
            "scale_factor": np.float64(-55),
            "cell_method": "area:mean time:mean",
            "cell_measures": "area: pemberley_area",
            "standard_name": "Mr. Darcy"
        }
    )

    variable2 = xr.DataArray(
        np.zeros((grid_yt, grid_xt), dtype=np.float32),
        dims = ["grid_yt", "grid_xt"],
        attrs = {
            "_FillValue": False,
            "long_name": "test variable 2",
            "cell_method": "area:mean",
            "standard_name": "Missing cell_measures, expected to fail",
            "missing_value": -np.float32(-1.0),
            "scale_factor": -np.float32(-0.05),
            "offset": np.float32(0.0)
        }
    )

    data_vars = {
        "grid_xt": variable_xt,
        "grid_yt": variable_yt,
        "pfull": variable_pfull,
        "time": variable_time,
        "variable1": variable1,
        "variable2": variable2
    }

    dataset = xr.Dataset(
        data_vars=data_vars,
        attrs={"associated_files": "pemberley_area: pemberley.nc longbourn_area: longbourn.nc"}
    )

    dataset.to_netcdf(outfile)
    return dataset


def test_dataobj():

    dataset = write_files("test.tile1.nc")

    fileobj = fmsgridtools.FileObj("test")

    variable1 = fmsgridtools.VariableObj(fileobj=fileobj)
    variable1.get_attributes(variable="variable1")
    print(variable1.dims)

    #check dimensions
    for (name, dim) in [("grid_xt", variable1.dims.x), ("grid_yt", variable1.dims.y)]:
        assert dim.name == name
        assert dim.here
        assert dim.size == dataset[name].size
    for dim in [variable1.dims.time, variable1.dims.z]:
        assert dim.name is None
        assert not dim.here
        assert dim.size is None

    attributes = dataset["variable1"].attrs
    assert variable1.missing == attributes.get("missing_value")
    assert variable1.fill_value == attributes.get("_FillValue")
    assert variable1.offset == attributes.get("add_offset")
    assert variable1.scale_factor == attributes.get("scale_factor")


if __name__ == "__main__":
    test_dataobj()
