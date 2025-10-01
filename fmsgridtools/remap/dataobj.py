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
        self.cell_measures: str = None
        self.area_averaged = False
        self.scale_factor: np.float32 | np.float64 | np.int32 | np.int64 = None
        self.offset: np.float32 | np.float64 | np.int32 | np.int64 = None
        self.missing_list: list = None
        self.fill_value: np.float32 | np.float64 | np.int32 | np.int64 = None
        self.static_files = {}
        self.static_area = {}
        self.tgt_field: npt.NDArray = None
        
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
            self.attributes = v_dataset.attrs
      
            # get dimensions
            for coord in v_dataset.coords:
                match dataset.coords[coord].attrs["axis"]:
                    case "X":
                        self.dims.x = coord
                    case "Y":
                        self.dims.y = coord
                    case "T":
                        self.dims.time = coord
                        self.dims.ntime = dataset.sizes[coord]
                        self.dims.has_t = True
                    case "Z":
                        self.dims.z = coord
                        self.dims.nz = dataset.sizes[coord]
                        self.dims.has_z = True
               
            #get missing value, offset, scale_factor
            self.fill_value = self.attributes.get("_FillValue")
            self.offset = self.attributes.get("add_offset")
            self.scale_factor = self.attributes.get("scale_factor")
            
            cell_method = self.attributes.get("cell_method")
            if "area" in str(cell_method):
                self.area_averaged = True
                if "cell_measures" in self.attributes:
                    key, value = self.attributes["cell_measures"].split()
                    if key == "area:":
                        self.cell_measures = value
                    else:
                        pass
                if "associated_files" in dataset.attrs:
                    #"soil_area: 00010101.land_static.nc cell_area: 00010101.land_static_sg.nc"
                    globalattrs = dataset.attrs["associated_files"].split().replace(":", " ")
                    if self.cell_measures in globalattrs:
                        index = globalattrs.index[self.cell_measures]
                        static_file = globalattrs[index+1]
                else:
                    pass

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
            if self.dims.has_t: data = data.isel({self.dims.time:timepoint})
            if self.dims.has_z: data = data.isel({self.dims.z:klevel})
            
        data = data.values.astype(np.float64)
            
        if self.scale_factor is not None:
            data *= self.scale_factor
            
        if self.offset is not None:
            data += self.offset

        return data


    def set_da(self, data: npt.NDArray):
        
        if self.has_t and self.has_z:
            this = np.expand_dims(np.expand_dims(data, axis=0), axis=0)
            return xr.DataArray(np.expand_dims(np.expand_dims(data, axis=0), axis=0),
                                dims=[self.time, self.z, self.y, self.x])
        elif self.has_z:
            return xr.DataArray(np.expand_dims(data, axis=0), dims=[self.z, self.y, self.x])
        elif self.has_t:
            return xr.DataArray(np.expand_dims(data, axis=0), dims=[self.t, self.y, self.x])
        else:
            return xr.DataArray(data, dims=[self.y, self.x])


    def add_data(self, data: npt.NDArray, klevel: int = None, timepoint: int = None):
    
        if self.data_out is None:
            self.data_out = self.set_da(data)
        else:
            if self.has_t and self.has_z:
                print(klevel, timepoint)
                if self.data_out.get_axis_num(self.time) < timepoint:
                    self.data_out = xr.concat([self.data_out, self.set_da(data)], self.t)
                else:
                    self.data_out = xr.concat([self.data_out, self.set_da(data)], self.z)
            elif self.has_t:
                self.data_out = xr.concat([self.data_out, self.set_da(data)], self.t)
            elif self.has_z:
                self.data_out = xr.concat([self.data_out, self.set_da(data)], self.z)
      

    def complete_data_out(self):
        self.data_out.attrs = self.attributes
    

class TgtField():
    
    def __init__(self, variable: str):
        self.variable = variable
        self.data = None
        
    def convert_data(self, data: npt.NDArray):
        
        if self.has_t and self.has_z:
            this = np.expand_dims(np.expand_dims(data, axis=0), axis=0)
            return xr.DataArray(np.expand_dims(np.expand_dims(data, axis=0), axis=0),
                                dims=[self.time, self.z, self.y, self.x])
        elif self.has_z:
            return xr.DataArray(np.expand_dims(data, axis=0), dims=[self.z, self.y, self.x])
        elif self.has_t:
            return xr.DataArray(np.expand_dims(data, axis=0), dims=[self.t, self.y, self.x])
        else:
            return xr.DataArray(data, dims=[self.y, self.x])

        
    def save(self, data: npt.NDArray, klevel: int = None, timepoint: int = None):    
        if self.data is None:
            self.data_out = self.set_da(data)
        else:
            if self.has_t and self.has_z:
                print(klevel, timepoint)
                if self.data_out.get_axis_num(self.time) < timepoint:
                    self.data_out = xr.concat([self.data_out, self.set_da(data)], self.t)
                else:
                    self.data_out = xr.concat([self.data_out, self.set_da(data)], self.z)
            elif self.has_t:
                self.data_out = xr.concat([self.data_out, self.set_da(data)], self.t)
            elif self.has_z:
                self.data_out = xr.concat([self.data_out, self.set_da(data)], self.z)
        
