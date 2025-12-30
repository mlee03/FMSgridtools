import numpy as np
from types import SimpleNamespace
import xarray as xr

import fmsgridtools
import write_files

def test_dataobj():

    dataset = write_files.write_data("test")

    srcfileobj = fmsgridtools.SrcFileObj("test", tiles=["tile1"])
    tgtfileobj = fmsgridtools.TgtFileObj("test", nx=10, ny=14)
    
    variable1 = fmsgridtools.VariableObj(variable="variable1", src_fileobj=srcfileobj, tgt_fileobj=tgtfileobj)

    #check dimensions
    dims = [
        ("grid_xt", variable1.src_fileobj.dims.x),
        ("grid_yt", variable1.src_fileobj.dims.y),
        ("time", variable1.time),
        ("pfull", variable1.z)
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
    src = write_files.src
    reconstruct_data = np.zeros((src.ntimes, src.nk, src.ny//2, src.nx//2), dtype=np.float64)
    for itime in range(src.ntimes):
        for k in range(src.nk):
            sliced_data = variable1.slice(tile="tile1", timepoint=itime, klevel=k)
            np.testing.assert_equal(sliced_data, write_files.data_list[0][itime, k, :, :])
            reconstruct_data[itime, k, :, :] = variable1.prepare_data(sliced_data)

    #check missing values
    for (itime, k, j, i) in write_files.missing_ijkl:
        assert reconstruct_data[itime,k,j,i] ==  np.float64(0.0)

def test_remap():

    write_files.write_mosaics()
    dataset = write_files.write_data("test")

    src_mosaic = write_files.src.mosaicfile
    tgt_mosaic = write_files.tgt.mosaicfile

    fmsgridtools.remap.conservative.remap(src_mosaicfile=src_mosaic, tgt_mosaicfile=tgt_mosaic, input_file="test")


if __name__ == "__main__":
    test_dataobj()
