from itertools import pairwise
from pathlib import Path
from types import SimpleNamespace

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


class FileObj():

    def __init__(self, datafile: str, tiles: list = ["tile1"], input_dir: str = "./"):

        self.input_dir = str(input_dir)
        self.tiles = tiles
        self.datafiles = {tile: Path(input_dir)/Path(datafile + f".{tile}.nc") for tile in tiles}
        self.static_files = {}

        with xr.open_dataset(self.datafiles[self.tiles[0]], decode_cf=False) as dataset:
            # soil_area: 00010101.land_static.nc cell_area: 00010101.land_static_sg.nc
            associated_files = dataset.attrs.get("associated_files")
            if associated_files is not None:
                stringsplit = associated_files.replace(":", " ").split()
                for i in range(0, len(stringsplit), 2):
                    self.static_files[stringsplit[i]] = {
                        tile: Path(input_dir)/stringsplit[i+1].replace(".nc", f".{tile}.nc") for tile in self.tiles
                    }

    def __repr__(self):
        repr_str = "\n"
        repr_str += f"input_dir = {self.input_dir}\n"
        repr_str += f"tiles = {self.tiles}\n"
        repr_str += f"datafiles = {self.datafiles}\n"
        repr_str += f"static_files = {self.static_files}\n"
        return repr_str


class VariableObj():

    time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)

    def __init__(self, variable: str, fileobj: FileObj = None):

        self.variable = variable
        self.fileobj = fileobj        
        self.dims = DimsObj()

        self.missing_value = None,
        self.fill_value = None,
        self.offset = None,
        self.scale_factor = None

        self.static_files: {} = None
        self.data = None


    def get_attributes(self):

        tile = self.fileobj.tiles[0]
        infile = self.fileobj.datafiles[tile]

        if not infile.exists:
            raise RuntimeError("file does not exist")

        with xr.open_dataset(infile, decode_cf=False) as dataset:

            if self.variable not in dataset:
                raise RuntimeError("variable not found")
            dataarray = dataset[self.variable]

            self.dims.get(dataarray)

            attributes = dataarray.attrs
            self.missing_value = attributes.get("missing_value")
            self.fill_value = attributes.get("_FillValue")
            self.offset = attributes.get("add_offset")
            self.scale_factor = attributes.get("scale_factor")

            if "area" in str(attributes.get("cell_method")):
                cell_measures = str(attributes.get("cell_measures"))
                if "area:" in cell_measures:
                    self.static_files = self.fileobj.static_files[cell_measures.split()[1]]


    def slice(self, tile: str = "tile1", timepoint: int = -99, klevel: int = -99):

        #python, values above 0 are true...

        with xr.open_dataset(self.fileobj.datafiles[tile], decode_cf=False) as dataset:

            slice_dict = {}

            if klevel>-1 and self.dims.z.here: slice_dict[self.dims.z.name] = klevel
            if timepoint>-1 and self.dims.time.here: slice_dict[self.dims.time.name] = timepoint

        self.data = dataset[self.variable].isel(slice_dict).values
        return self.data

    
    def prepare_data(self):

        #missing value mask
        missing_value_mask = None
        if self.missing_value is not None:
            missing_value_mask = self.data == self.missing_value
        
        if self.offset: self.data += self.offset
        if self.scale_factor: self.data *= self.scale_factor
        
        #zero out missing values so it doens't contribute to remapping
        if missing_value_mask is not None:
            self.data = xr.where(missing_value_mask, 0.0, self.data)

        return self.data
        
