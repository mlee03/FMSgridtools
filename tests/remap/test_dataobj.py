import numpy as np
from types import SimpleNamespace
import xarray as xr

import fmsgridtools

def write_files(outfile):
    grid_xt, grid_yt = 100, 50

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
        "variable1": variable1,
        "variable2": variable2
    }

    dataset = xr.Dataset(
        data_vars=data_vars,
        attrs={"associated_files": "pemberley_area: pemberley.nc"}
    )

    dataset.to_netcdf(outfile)
    return dataset


def test_dataobj():

    dataset = write_files("test.nc")

    variable1 = fmsgridtools.VariableObj(datafile="test")
    variable1.get_attributes(variable="variable1")

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
    assert variable1.attrs.missing == attributes.get("missing_value")
    assert variable1.attrs.fill_value == attributes.get("_FillValue")
    assert variable1.attrs.offset == attributes.get("add_offset")
    assert variable1.attrs.scale_factor == attributes.get("scale_factor")

    print(variable1.area)



if __name__ == "__main__":
    test_dataobj()
