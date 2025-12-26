import numpy as np
from types import SimpleNamespace
import xarray as xr

import fmsgridtools

nx, ny, nk, ntimes = 10, 8, 3, 4

answers = np.zeros((ntimes, nk, ny, nx), dtype=np.float64)
for itime in range(ntimes):
    for k in range(nk):
        for j in range(ny):
            start = itime*1000+k*100+j*10
            answers[itime, k, j, :] = np.arange(start, start+nx, dtype=np.float64)

missing_ijkl = [(1,1,1,1), (2,2,2,2)]
for (itime, k, j, i) in missing_ijkl:
    answers[itime,k,j,i] = missing_value


def write_files(outfile):



    variable_xt = xr.DataArray(
        np.arange(nx, dtype=np.float64),
        dims = ["grid_xt"],
        attrs={
            "units": "degrees_E",
            "long_name": "made up T-cell longitude",
            "axis": "X"
        }
    )

    variable_yt = xr.DataArray(
        np.arange(ny, dtype=np.float64),
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
        answers,
        dims = ["time", "pfull", "grid_yt", "grid_xt"],
        attrs = {
            "_FillValue": -np.float64(-100),
            "long_name": "test variable 1",
            "units": "kg m-2",
            "missing_value": missing_value,
            "add_offset": np.float64(0.0),
            "scale_factor": np.float64(0.0),
            "cell_method": "area:mean time:mean",
            "cell_measures": "area: pemberley_area",
            "standard_name": "Mr. Darcy"
        }
    )

    variable2 = xr.DataArray(
        np.zeros((ny, nx), dtype=np.float32),
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

    dataset.to_netcdf(outfile, unlimited_dims="time")
    return dataset


def test_dataobj():

    dataset = write_files("test.tile1.nc")

    fileobj = fmsgridtools.FileObj("test")

    variable1 = fmsgridtools.VariableObj(variable="variable1", fileobj=fileobj)

    #check dimensions
    variable1.get_attributes()
    dims = [
        ("grid_xt", variable1.dims.x),
        ("grid_yt", variable1.dims.y),
        ("time", variable1.dims.time),
        ("pfull", variable1.dims.z)
    ]
    for (name, dim) in dims:
        assert dim.name == name
        assert dim.here
        assert dim.size == dataset[name].size

    attributes = dataset["variable1"].attrs
    assert variable1.missing_value == attributes.get("missing_value")
    assert variable1.fill_value == attributes.get("_FillValue")
    assert variable1.offset == attributes.get("add_offset")
    assert variable1.scale_factor == attributes.get("scale_factor")

    #slice
    reconstruct_data = np.zeros((ntimes, nk, ny, nx), dtype=np.float64)
    for itime in range(ntimes):
        for k in range(nk):
            sliced_data = variable1.slice(timepoint=itime, klevel=k)
            np.testing.assert_equal(sliced_data, answers[itime, k, :, :])
            reconstruct_data[itime, k, :, :] = variable1.prepare_data()

    #check missing values
    for (itime, k, j, i) in missing_ijkl:
        assert reconstruct_data[itime,k,j,i] ==  np.float64(0.0)




if __name__ == "__main__":
    test_dataobj()
