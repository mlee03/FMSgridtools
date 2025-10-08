import ast
import numpy as np
import numpy.typing as npt
from pathlib import Path
import xarray as xr

import pyfms
from fmsgridtools.shared.mosaicobj import MosaicObj


class Dims():

    def __init__(self):
        self.x: str = None
        self.y: str = None
        self.z_full: str = None
        self.z_half: str = None
        self.time: str = None
        self.nx: int = None
        self.ny: int = None
        self.nz: int = None
        self.ntime: int = None
        self.has_t = False
        self.has_z = False
        self.has_t_and_z = False
        self.dims_list: list = None
        
    def get(self, dataarray):

        # get dimensions
        for name, coord in dataarray.coords.items():
            match coord.attrs["axis"]:
                case "X":
                    self.x = name
                case "Y":
                    self.y = name
                case "T":
                    self.time = name
                    self.ntime = coord.size
                    self.has_t = True
                case "Z":
                    self.z = name
                    self.nz = coord.size
                    self.has_z = True
        self.has_t_and_z = self.has_z and self.has_t
        self.dims_list = list(datarray.dims)
               
class Tgt():

    def __init__(self, data: xr.DataArray = None, dims: Dims = None, attributes: dict = None):

        self.data: xr.DataArray = None
        self.dims: Dims = None
        self.attributes: None

        
    def set_data(self, data: npt.NDArray, nexpand: int):

        if nexpand == 2:    
            return xr.DataArray(np.expand_dims(np.expand_dims(data, axis=0), axis=0), dims=self.dims.dims_list)
        elif nexpand == 1:
            return xr.DataArray(np.expand_dims(data, axis=0), dims=self.dims.dims_list)
        else:
            return xr.DataArray(data, dims=self.dims.dims_list)

        
    def save(self, data: npt.NDArray, new_z: bool = False, new_t: bool = False):

        if self.data is None:
            if self.dims.has_t_and_z:
                self.data = self.set_data(data, nexpand=2)
                self.dims.nz = 1
                self.dims.ntimes = 1
            elif self.dims.has_z:
                self.data = self.set_data(data, nexpand=1)
                self.dims.nz = 1
            elif self.dims.has_t:
                self.data = self.set_data(data, nexpand=1)
                self.dims.ntime = 1
            else:
                self.data = self.set_data(data, nexpand=0)
        else:
            if self.dims.has_t_and_z:
                if new_t:
                    self.data = xr.concat([self.data, self.set_data(data, nexpand=2)], self.dims.time)
                    self.dims.ntimes += 1
                elif new_z:
                    self.data = xr.concat([self.data, self.set_data(data, nexpand=2)], self.dims.z)
                    self.dims.nz += 1 
            elif self.dims_has_t:
                self.data = xr.concat([self.data, self.set_data(data, nexpand=1)], self.dims.time)
                self.dims.ntimes += 1
            elif self.dims.has_z:
                self.data = xr.concat([self.data, self.set_data(data, nexpand=1)], self.dims.z)
                self.nz += 1

                
    def complete(self):
        self.data.attrs = self.attributes
        return self.data
                
                    
class DataObj():
    
    time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)

    def __init__(self,
                 datafile: str,
                 variable: str,
                 tiles: list = None,
                 input_dir: str = "./"):
        
        """
        DataObj class to handle data files and variables.
        """
        
        self.input_dir = Path(input_dir)
        self.tiles = tiles
        self.datafiles = {}
        self.variable = variable
        self.attributes: dict = None
        self.is_tiled = False    

        self.dims = Dims()    

        self.scale_factor: np.float32 | np.float64 | np.int32 | np.int64 = None
        self.offset: np.float32 | np.float64 | np.int32 | np.int64 = None
        self.fill_value: np.float32 | np.float64 | np.int32 | np.int64 = None
        self.missing_list: list = None

        self.area_averaged = False
        self.cell_measures: str = None
        self.static_files = {}
        self.static_area = {}

        self.tgt = Tgt()
        
        #set datafile
        if tiles is None:
            self.tiles = ['tile1']
            self.datafiles['tile1'] = Path(datafile + ".nc")
        else:
            self.is_tiled = True
            for tile in self.tiles:
                self.datafiles[tile] = Path(datafile + "." + tile + ".nc")
            
        #get coordinates
        with xr.open_dataset(self.input_dir/self.datafiles.get(self.tiles[0]), decode_cf=False) as dataset:

            if self.variable not in dataset:
                raise RuntimeError("variable not found")

            v_dataset = dataset[self.variable]

            self.dims.get(dataset[v_dataset])

            self.attributes = v_dataset.attrs
            
            #get missing value, offset, scale_factor
            self.fill_value = self.attributes.get("_FillValue")
            self.offset = self.attributes.get("add_offset")
            self.scale_factor = self.attributes.get("scale_factor")

            if "area" in str(self.attributes.get("cell_method")):
                self.get_static_area(dataset)

        self.tgt.attributes = self.attributes
        self.tgt.dims = self.dims
        self.tgt.dims.ntimes = 0
        self.tgt.dims.nz = 0
                
                
    def get_static_area(self, dataset):
        self.area_averaged = True

        # get cell measures (area type)
        cell_measures = str(self.attributes.get("cell_measures"))
        if "area:" in cell_measures:
            self.cell_measures = cell_measures.split()[1]
        else:
            return

        # get file holding area data
        # soil_area: 00010101.land_static.nc cell_area: 00010101.land_static_sg.nc
        global_attrs = str(dataset.attrs.get("associated_files"))
        if self.cell_measures in global_attrs:
            global_attrs_split = global_attrs.split().replace(":", " ")
            index = global_attrs_split.index[self.cell_measures]
            static_file = global_attrs_split[index+1]
        else:
            raise RuntimeError("cannot find static file")

        if self.is_tiled:
            for tile in self.tiles:
                self.static_files[tile] = static_file.replace(".nc", tile+".nc")
        else:
            self.static_files[self.tile[0]] = static_file

        for tile, static_file in self.static_files.items():
            with xr.open_dataset(self.input_dir/static_file) as dataset:
                self.static_area[tile] = dataset[self.cell_measures].values.astype(np.float64)


    def get_slice(self, tile: str = 'tile1', klevel: int = None, timepoint: int = None):
        
        """
        Get slice of a variable from the dataset.
        """

        with xr.open_dataset(self.input_dir/self.datafiles[tile], decode_cf=False) as dataset:
            data = dataset[self.variable]
            if klevel is not None:
                if self.dims.has_z: data = data.isel({self.dims.z:klevel})
            if timepoint is not None:
                if self.dims.has_t: data = data.isel({self.dims.time:timepoint})
            
        data = data.values.astype(np.float64)
            
        if self.scale_factor is not None:
            data *= self.scale_factor
            
        if self.offset is not None:
            data += self.offset

        return data    

