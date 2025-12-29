import numpy as np
from types import SimpleNamespace

import xarray as xr
import fmsgridtools

src = SimpleNamespace(
    ntiles=6,
    nx=12,
    ny=24,
    nk=3,
    ntimes=4,
    dxy=1.0,
    mosaicfile="src_mosaic.nc",
    gridfile="src_grid"
)
tgt = SimpleNamespace(
    ntiles=1,
    nx=src.nx, #* 2,
    ny=src.ny, #* 2,
    nk=3,
    ntimes=4,
    dxy=src.dxy, # / 2.0,
    mosaicfile="tgt_mosaic.nc",
    gridfile="tgt_grid"
)

nxgrid_per_tile = tgt.nx//2 * tgt.ny//2
nxgrid = nxgrid_per_tile * 6

ntimes, nk, ny, nx = src.ntimes, src.nk, src.ny//2, src.nx//2

missing_value = -np.float64(-99.)
missing_ijkl = [(1,1,1,1), (2,2,2,2)]

data_list = []
for itile in range(1, src.ntiles+1):
    data = np.zeros((ntimes, nk, ny, nx), dtype=np.float64)
    for itime in range(ntimes):
        for k in range(nk):
            for j in range(ny):
                start = itile*10000 + itime*1000+k*100+j*10
                data[itime, k, j, :] = np.arange(start, start+nx, dtype=np.float64)
    for (itime, k, j, i) in missing_ijkl:
        data[itime,k,j,i] = missing_value
    data_list.append(data)


def write_mosaics():

    """
    make mosaic and grid files for testing
    """

    # write mosaic
    for parent in [src, tgt]:
        fmsgridtools.MosaicObj(
            gridtiles=[f"tile{i}" for i in range(1, parent.ntiles+1)],
            gridfiles=[f"{parent.gridfile}.tile{i}.nc" for i in range(1, parent.ntiles+1)]
        ).write(parent.mosaicfile)

    # write grid
    for parent in [src, tgt]:
        for itile in range(1, parent.ntiles+1):
            x1 = np.array([i*parent.dxy for i in range(parent.nx+1)], dtype=np.float64)
            y1 = np.array([j*parent.dxy for j in range(parent.ny+1)], dtype=np.float64)
            x, y = np.meshgrid(x1, y1)
            fmsgridtools.GridObj(x=x, y=y).write(parent.gridfile + f".tile{itile}.nc")


def write_data(outfile):

    for itile in range(src.ntiles):

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
            data_list[itile],
            dims = ["time", "pfull", "grid_yt", "grid_xt"],
            attrs = {
                "_FillValue": -np.float64(-100),
                "long_name": "test variable 1",
                "units": "kg m-2",
                "missing_value": missing_value,
                "add_offset": np.float64(0.0),
                "scale_factor": np.float64(1.0),
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

        dataset.to_netcdf(outfile+f".tile{itile+1}.nc", unlimited_dims="time")
    return dataset
