from itertools import pairwise
from pathlib import Path
from types import SimpleNamespace

import xarray as xr

class DimObj():

    def __init__(self, axis: str, name: str = None, here: bool = False, size: int = None):
        self.axis = axis
        self.name = name
        self.here = here
        self.size = size


class DimsObj():

    def __init__(self):
        self.x = DimObj("X")
        self.y = DimObj("Y")
        self.z = DimObj("Z")
        self.time = DimObj("T")

    def get(self, da_coords: xr.Coordinates):

        """
        get dimensions
        """

        dims_list = [self.x, self.y, self.z, self.time]

        for name, coord in da_coords.items():
            for dim in dims_list:
                if dim.axis == coord.attrs["axis"]:
                    dim.name = name
                    dim.size = coord.size
                    dim.here = True
                    dims_list.remove(dim)
                    break

    def __repr__(self):

        repr_str ="\n"
        for obj in [self.x, self.y, self.z, self.time]:
            repr_str += f"axis={obj.axis}, name={obj.name}, here={obj.here}, size={obj.size}\n"
        return repr_str


class VariableObj():

    time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)

    def __init__(self, datafile: str, tiles: list = None, input_dir: str | Path = Path("./")):

        self.tiles = tiles
        self.dims = DimsObj()
        self.input_dir = Path(input_dir)

        if tiles is None:
            self.datafiles = {"tile1": input_dir/Path(datafile).with_suffix(".nc")}
        else:
            self.datafiles = {tile: input_dir/Path(datafile.with_suffix(tile + ".nc")) for tile in tiles}

        self.attrs = SimpleNamespace(
            missing = None,
            fill_value = None,
            offset = None,
            scale_factor = None
        )

        self.area = SimpleNamespace(
          static_files = None,
          cell_measures = None,
          area = None
        )


    def get_attributes(self, variable):

        infile = list(self.datafiles.values())[0]

        if not infile.exists:
            raise RuntimeError("file does not exist")

        with xr.open_dataset(infile, decode_cf=False) as dataset:

            if variable not in dataset:
                raise RuntimeError("variable not found")
            dataarray = dataset[variable]

            self.dims.get(dataarray.coords)

            attributes = dataarray.attrs
            self.attrs.missing = attributes.get("missing_value")
            self.attrs.fill_value = attributes.get("_FillValue")
            self.attrs.offset = attributes.get("add_offset")
            self.attrs.scale_factor = attributes.get("scale_factor")

            if "area" in str(attributes.get("cell_method")):
              self._get_static_files(dataset, variable)


    def slice(self, time: int = None, z: int = None):


    def _get_static_files(self, dataset, variable):

       # get cell measures (area type)
        cell_measures = str(dataset[variable].attrs.get("cell_measures"))
        if "area:" in cell_measures:
            cell_measures = cell_measures.split()[1]
        else:
            return

        # soil_area: 00010101.land_static.nc cell_area: 00010101.land_static_sg.nc
        global_attrs = str(dataset.attrs.get("associated_files"))
        if cell_measures in global_attrs:
          global_attrs_dict = {keyval.strip(":"): areaval for keyval, areaval in pairwise(global_attrs.split())}
          static_file = global_attrs_dict[cell_measures]
        else:
          raise RuntimeError("cannot find static file")

        if self.tiles is not None:
            self.area.static_files = {tile: self.input_dir/static_file.replace(".nc", tile+".nc") for tile in self.tiles}
        else:
            self.area.static_files = {"tile1": self.input_dir/static_file}

        self.area.cell_measures = cell_measures