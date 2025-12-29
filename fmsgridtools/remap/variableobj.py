from itertools import pairwise
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import xarray as xr

class DimObj():

    def __init__(self, axis: str, name: str = None, here: bool = False, size: int = None):
        self.axis = axis
        self.name = name
        self.size = size
        self.here = False


class DimsObj():

    def __init__(self):
        self.x = DimObj("X")
        self.y = DimObj("Y")
        self.z = DimObj("Z")
        self.time = DimObj("T")

    def get(self, da: xr.DataArray):

        """
        get dimensions
        """

        dims_dict = {dim.axis: dim for dim in [self.x, self.y, self.z, self.time]}

        for name, coord in da.coords.items():
            try:
                dim = dims_dict[coord.attrs.get("axis")]
                dim.name = name
                dim.size = coord.size
                dim.here = True
            except:
                print(f"{name} dim not found")

    def __repr__(self):

        repr_str ="\n"
        for obj in [self.x, self.y, self.z, self.time]:
            repr_str += f"axis={obj.axis}, name={obj.name}, here={obj.here}, size={obj.size}\n"
        return repr_str


class SrcFileObj():

    skip_variables = [
        "geolon_c", "geolat_c", "geolon_u", "geolat_u", "geolon_v", "geolat_v",
        "FA_X", "FA_Y", "FI_X", "FI_Y", "IX_TRANS", "IY_TRANS",
        "UI", "VI", "UO", "VO", "wet_c", "wet_v", "wet_u",
        "dxCu", "dyCu", "dxCv", "dyCv", "Coriolis",
        "areacello_cu", "areacello_cv", "areacello_bu",
        "average_T1", "average_T2", "average_DT", "time_bnds"
    ]


    def __init__(self, datafile: str, tiles: list = ["tile1"], input_dir: str = "./", variables: list = None):

        self.input_dir = str(input_dir)
        self.tiles = tiles
        self.src_datafiles = {tile: Path(input_dir)/Path(datafile + f".{tile}.nc") for tile in tiles}
        self.static_files = {}
        self.variables = variables

        self.src_datasets = {
            tile: xr.open_dataset(self.src_datafiles[tile], decode_cf=False) for tile in self.tiles
        }

        dataset = self.src_datasets[tiles[0]]
        # soil_area: 00010101.land_static.nc cell_area: 00010101.land_static_sg.nc
        associated_files = dataset.attrs.get("associated_files")
        if associated_files is not None:
            stringsplit = associated_files.replace(":", " ").split()
            for i in range(0, len(stringsplit), 2):
                self.static_files[stringsplit[i]] = {
                    tile: Path(input_dir)/stringsplit[i+1].replace(".nc", f".{tile}.nc") for tile in self.tiles
                }

        #get list of variables
        if self.variables is None:
            self.variables = []
            for variable in dataset:
                if variable in self.skip_variables:
                    print(f"skipping {variable}")
                else:
                    self.variables.append(variable)

    def __repr__(self):
        repr_str = "\n"
        repr_str += f"input_dir = {self.input_dir}\n"
        repr_str += f"tiles = {self.tiles}\n"
        repr_str += f"datafiles = {self.src_datafiles}\n"
        repr_str += f"static_files = {self.static_files}\n"
        return repr_str



class TgtFileObj():

    def __init__(self, datadict: dict = {}):
        self.dataarrays = datadict
        self.name = None
        self.dims = None

    def set_dataarray(self, variable: str = None, data_dict: dict = None, dataarray: xr.DataArray = None):

        if data_dict is not None:
            self.dataarrays["variable" ] = xr.DataArray.from_dict(data_dict)
        elif dataarray is not None:
            self.dataarrays["variable"] = dataarray
        else:
            raise RuntimeError("must provide something")

    def set_coords(self, grid):
        pass



class VariableObj():

    time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)

    def __init__(self, variable: str, fileobj: SrcFileObj = None):

        self.variable = variable
        self.fileobj = fileobj
        self.dims = DimsObj()

        self.dtype = None,
        self.missing_value = None,
        self.fill_value = None,
        self.offset = None,
        self.scale_factor = None

        self.static_files: {} = None
        self.src_data = None

        self.tgt_dict = {
            "data": npt.NDArray = None,
            "dims": list = None,
            "attrs": dict =  None
        }


    def get_attributes(self):

        tile = self.fileobj.tiles[0]
        dataset = self.fileobj.datasets[tile]

        if self.variable not in dataset:
            raise RuntimeError("variable not found")

        dataarray = dataset[self.variable]

        self.dims.get(dataarray)
        self.dtype=dataarray.dtype

        attributes = dataarray.attrs
        self.missing_value = attributes.get("missing_value")
        self.fill_value = attributes.get("_FillValue")
        self.offset = attributes.get("add_offset")
        self.scale_factor = attributes.get("scale_factor")

        if "area" in str(attributes.get("cell_method")):
            cell_measures = str(attributes.get("cell_measures"))
            if "area:" in cell_measures:
                self.static_files = self.fileobj.static_files[cell_measures.split()[1]]


    def slice(self, tile: str = "tile1", timepoint: int = None, klevel: int = None, prepare_data: bool = False):


        dataset = self.fileobj.datasets[tile]

        slice_dict = {}
        if klevel is not None and self.dims.z.here:
            slice_dict[self.dims.z.name] = klevel
        if timepoint is not None  and self.dims.time.here:
            slice_dict[self.dims.time.name] = timepoint

        self.src_data = dataset[self.variable].isel(slice_dict).values

        if prepare_data:
            self.prepare_data()
        return self.src_data


    def prepare_data(self):

        #missing value mask
        missing_value_mask = None
        if self.missing_value is not None:
            missing_value_mask = self.src_data == self.missing_value

        if self.offset is not None: self.src_data += self.offset
        if self.scale_factor is not None: self.src_data *= self.scale_factor

        #zero out missing values so it doens't contribute to remapping
        if missing_value_mask is not None:
            self.src_data = xr.where(missing_value_mask, 0.0, self.src_data)

        return self.src_data


    def init_tgt_dict(self, nx: int, ny: int, ntimes: int = None, nz: int = None):

        dims = []
        if self.dims.time.here:
            if ntimes is None: ntimes = self.dims.time.size
        dims.append(ntimes)

        if self.dims.z.here:
            if nz is None: nz = self.dims.z.size
        dims.append(nx)

        dims += [self.dims.y.size, self.dims.x.size]

        self.tgt_dict["dims"] = dims
        self.tgt_dict["attrs"]= self.src_datasets[self.fileobj.tiles[0]][self.variable].attrs
        self.tgt_dict["data"] = np.zeros((ntimes, nz, ny, nx), dtype=self.dtype)

        return self.tgt_dict


    def set_tgt_data(self, data: npt.NDArray, timepoint: int = None, klevel: int = None):

        if timepoint is None and klevel is None:
            self.tgt_dict["data"] = data
        elif timepoint is not None and klevel is not None:
            self.tgt_dict["data"][timepoint, klevel, :, :] = data
        elif timepoint is not None:
            self.tgt_dict["data"][timepoint, :, :] = data
        elif klevel is not None:
            self.tgt_dict["data"][klevel, :, :] = data

        return self.tgt_dict
