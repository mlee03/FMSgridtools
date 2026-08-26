import copy
from itertools import pairwise
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import numpy.typing as npt
import xarray as xr

class DimObj():

    def __init__(self, axis: str, name: str = None, here: bool = False, size: int = None, attr: dict = None, coord_values: npt.NDArray = None):
        self.axis = axis
        self.name = name
        self.size = size
        self.attr = None
        self.coords = coord_values
        self.here = False


class FileDimsObj():

    def __init__(self):
        self.x = DimObj("X")
        self.y = DimObj("Y")
        self.z = DimObj("Z")
        self.time = DimObj("T")


    def init(self, dataset: xr.Dataset):

        """
        get dimensions
        """

        dims_dict = {dim.axis: dim for dim in [self.time, self.z, self.y, self.x]}

        for name, coord in dataset.coords.items():
            try:
                dim = dims_dict[coord.attrs.get("axis")]
                dim.name = name
                dim.attr = coord.attrs
                dim.size = coord.size
                dim.coords = coord.values
                dim.here = True
            except:
                print(f"{name} dim not found")

    def get_z(self, dims_list: list):
        if self.z.name in dims_list:
            return self.z
        else:
            return DimObj(axis="Z", name=self.z.name)

    def get_time(self, dims_list: list):
        if self.time.name in dims_list:
            return self.time
        else:
            return DimObj(axis="T", name=self.time.name)


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
        self.dims = FileDimsObj()
        self.datafiles = {tile: Path(input_dir)/Path(datafile + f".{tile}.nc") for tile in tiles}
        self.static_files = {}
        self.variables = variables

        self.datasets = {
            tile: xr.open_dataset(self.datafiles[tile], decode_cf=False) for tile in self.tiles
        }

        dataset = self.datasets[tiles[0]]

        # get dims
        self.dims.init(dataset)

        # soil_area: 00010101.land_static.nc cell_area: 00010101.land_static_sg.nc
        associated_files = dataset.attrs.get("associated_files")
        if associated_files is not None:
            stringsplit = associated_files.replace(":", " ").split()
            for i in range(0, len(stringsplit), 2):
                self.static_files[stringsplit[i]] = {
                    tile: Path(input_dir)/stringsplit[i+1].replace(".nc", f".{tile}.nc") for tile in self.tiles
                }

        #get list of variables if not specified
        if self.variables is None:
            for variable in dataset:
                if variable in self.skip_variables:
                    print(f"skipping {variable}")
                else:
                    self.variables.append(variable)

    def close_datasets(self):
        for tile in self.tiles:
            self.datasets[tile].close()

    def __repr__(self):
        repr_str = "\n"
        repr_str += f"input_dir = {self.input_dir}\n"
        repr_str += f"tiles = {self.tiles}\n"
        repr_str += f"datafiles = {self.datafiles}\n"
        repr_str += f"static_files = {self.static_files}\n"
        return repr_str


class TgtFileObj():

    def __init__(self, datafile: str|Path,  nx: int, ny: int, output_dir: str = "./"):

        self.output_dir = str(output_dir)
        self.datafile = datafile

        self.dims = FileDimsObj()
        self.dims.x.size = nx
        self.dims.y.size = ny


        self.datadict = {}


    def init_variable(self, variable: str, dtype, dims_list: list = None, attributes: dict = None, z_size: int = None, time_size: int = None):

        data_info = {}
        if dims_list is not None: data_info["dims"] = dims_list
        if attributes is not None: data_info["attrs"] = attributes

        shape = []
        if time_size is not None: shape.append(time_size)
        if z_size is not None: shape.append(z_size)
        shape += [self.dims.y.size, self.dims.x.size]

        data_info["data"] = np.zeros(shape, dtype=dtype)

        self.datadict[variable] = data_info

    def set_x_coords(self, grid):
        pass

    def set_y_coords(self, grid):
        pass

    def copy_coords(self, src_fileobj: SrcFileObj, axis: str):
        if axis == "T":
            self.dims.time = copy.deepcopy(src_fileobj.dims.time)
        elif axis == "Z":
            self.dims.z = copy.deepcopy(src_fileobj.dims.z)
        elif axis == "X":
            self.dims.x = copy.deepcopy(src_fileobj.dims.x)
        elif axis == "Y":
            self.dims.y = copy.deepcopy(src_fileobj.dims.y)


class VariableObj():

    time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)

    def __init__(self, variable: str, src_fileobj: SrcFileObj = None, tgt_fileobj: TgtFileObj = None):

        self.variable = variable

        self.src_fileobj = src_fileobj
        self.tgt_fileobj = tgt_fileobj

        self.z = None
        self.time = None
        self.zlist = [None]
        self.timelist = [None]

        self.dtype = None
        self.missing_value = None
        self.fill_value = None
        self.offset = None
        self.scale_factor = None

        self.static_files: {} = None

        tile = self.src_fileobj.tiles[0]
        dataarray = self.src_fileobj.datasets[tile][self.variable]

        dims_list = dataarray.dims
        self.z = self.src_fileobj.dims.get_z(dims_list)
        self.time = self.src_fileobj.dims.get_time(dims_list)
        if self.z.here: self.zlist = list(range(self.z.size))
        if self.time.here: self.timelist = list(range(self.time.size))

        self.dtype=dataarray.dtype

        attributes = dataarray.attrs
        self.missing_value = attributes.get("missing_value")
        self.fill_value = attributes.get("_FillValue")
        self.offset = attributes.get("add_offset")
        self.scale_factor = attributes.get("scale_factor")

        if "area" in str(attributes.get("cell_method")):
            cell_measures = str(attributes.get("cell_measures"))
            if "area:" in cell_measures:
                self.static_files = self.src_fileobj.static_files[cell_measures.split()[1]]

        self.tgt_fileobj.init_variable(self.variable, self.dtype, dims_list=dims_list, attributes=attributes, z_size=self.z.size, time_size=self.time.size)


    def slice(self, tile: str = "tile1", timepoint: int = None, klevel: int = None, prepare_data: bool = False):

        dataset = self.src_fileobj.datasets[tile]

        slice_dict = {}
        if klevel is not None:
            slice_dict[self.z.name] = klevel
        if timepoint is not None:
            slice_dict[self.time.name] = timepoint

        src_data = dataset[self.variable].isel(slice_dict).values

        if prepare_data:
            src_data = self.prepare_data(src_data)
        return src_data


    def prepare_data(self, src_data: npt.NDArray = None):

        #missing value mask
        missing_value_mask = None
        if self.missing_value is not None:
            missing_value_mask = src_data == self.missing_value

        if self.offset is not None: src_data += self.offset
        if self.scale_factor is not None: src_data *= self.scale_factor

        #zero out missing values so it doens't contribute to remapping
        if missing_value_mask is not None:
            src_data = xr.where(missing_value_mask, 0.0, src_data)

        return src_data


    def set_tgt_data(self, data: npt.NDArray, timepoint: int = None, klevel: int = None):

        tgt_data = self.tgt_fileobj.datadict[self.variable]["data"]

        if timepoint is None and klevel is None:
            tgt_data = data
        elif timepoint is not None and klevel is not None:
            tgt_data[timepoint, klevel, :, :] = data
        elif timepoint is not None:
            tgt_data[timepoint, :, :] = data
        elif klevel is not None:
            tgt_data[klevel, :, :] = data

        self.tgt_fileobj.datadict[self.variable]["data"] = tgt_data