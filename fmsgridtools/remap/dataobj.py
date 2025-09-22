import numpy as np
import numpy.typing as npt
from pathlib import Path
import xarray as xr

import pyfms

from fmsgridtools.shared.mosaicobj import MosaicObj

class DataObj():

  time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)

  def __init__(self,
               datafile: str,
               variable: str,
               tile: str = None,
               input_dir: str = "./"):

    """
    DataObj class to handle data files and variables.
    """

    self.input_dir = Path(input_dir)
    self.tile = tile
    self.datafile = datafile
    self.variable = variable
    self.metadata = None

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
    
    self.cell_measures: str = None
    self.area_averaged = False
    self.scale_factor: np.float32 | np.float64 | np.int32 | np.int64 = None
    self.offset: np.float32 | np.float64 | np.int32 | np.int64 = None
    self.missing_list: list = None
    self.fill_value: np.float32 | np.float64 | np.int32 | np.int64 = None
    self.static_area: npt.NDArray = None
    self.data_in: npt.NDArray = None

    self.data_out = {}
    
    #set datafile
    if tile is None:
      self.datafile = Path(self.datafile + ".nc")
    else:
      self.datafile = Path(self.datafile + "." + self.tile + ".nc")

    #get coordinates
    with xr.open_dataset(self.input_dir/self.datafile, decode_cf=False) as dataset:

      if self.variable not in dataset: raise RuntimeError("variable not found")

      v_dataset = dataset[self.variable]
      
      # get time and vertical coordinates
      for coord in v_dataset.coords.dims:
        if dataset.coords[coord].attrs["axis"] == "X":
          self.x = coord
        if dataset.coords[coord].attrs["axis"] == "Y":
          self.y = coord
        if dataset.coords[coord].attrs["axis"] == "T":
          self.time = coord
          self.ntime = dataset.sizes[coord]
          self.has_t = True
        if dataset.coords[coord].attrs["axis"] == "Z":
          self.z = coord
          self.nz = dataset.sizes[coord]
          self.has_z = True          

      attributes = v_dataset.attrs
      get_value = lambda attr_key: attributes[attr_key] if attr_key in attributes else None

      #get missing value, offset, scale_factor
      #check if cell_methods is area mean
      self.fill_value = get_value("_FillValue")
      self.offset = get_value("add_offset")
      self.scale_factor = get_value("scale_factor")

      cell_method = get_value("cell_method")
      if cell_method is not None:
        self.area_averaged = True if "area" in cell_method else False
        
      #"soil_area: 00010101.land_static.nc cell_area: 00010101.land_static_sg.nc land_area: 00010101.land_static.nc"
      if self.area_averaged:
        if "cell_measures" in attributes:
          splitted_string = attributes["cell_measures"].split()
          if splitted_string[0] == "area:":
            self.cell_measures = splitted_string[1]            
        if "associated_files" in dataset.attrs:
          splitted_string = dataset.attrs["associated_files"].split()
          for i in range(0, len(splitted_string), 2):
            if splitted_string[i] == self.cell_measure + ":":              
              self.static_file = splitted_string[i+1]
          if self.tile is not None:
            self.static_file = self.static_file.replace(".nc", self.tile+".nc")
        with xr.open_dataset(self.input_dir/self.static_file) as dataset:
            self.static_area = dataset[self.cell_measures].values.astype(np.float64)

      self.metadata = attributes

      
  def get_slice(self, klevel: int = None, timepoint: int = None):

    """
    Get slice of a variable from the dataset.
    """

    with xr.open_dataset(self.input_dir/self.datafile, decode_cf=False) as dataset:
      self.data_in = dataset[self.variable]
      if self.has_t: self.data_in = self.data_in.isel({self.time:timepoint})
      if self.has_z: self.data_in = self.data_in.isel({self.z:klevel})

    self.data_in = self.data_in.values.astype(np.float64)

    if self.scale_factor is not None:
      self.data_in *= self.scale_factor
          
    if self.offset is not None:
      self.data_in += self.offset

    return self.data_in
      

  def check_missing_value(dataarray):

    if "missing_value" in dataarray.attrs:
      missing_value = dataarray.attrs["missing_value"]

    if np.any(dataarray.values == missing_value):
      raise RuntimeError("missing value found")


  def set_da(self, data: npt.NDArray):

    if self.has_t and self.has_z:
      return xr.DataArray(np.expand_dims(np.expand_dims(data, axis=0), axis=0),
                          [self.time, self.z, self.y, self.x])
    else if self.has_z:
      return xr.DataArray(np.expand_dims(data, axis=0), [self.z, self.y, self.x])
    else if self.has_t:
      return xr.DataArray(np.expand_dims(data, axis=0), [self.z, self.y, self.x])
    else:
      return xr.DataArray(data, [self.y, self.x])


  def set_data_out(self, data: npt.NDArray, klevel: int = None, timepoint: int = None):

    if self.data_out is None:
      self.data_out = self.set_da(data)
    else:
      if self.has_t and self.has_z:
        if self.data_out.get_axis_num(self.time) < timepoint:
          self.data_out = xr.concat([self.data_out, self.set_da(data)], self.t)
        else:
          self.data_out = xr.concat([self.data_out, self.set_da(data)], self.z)
      else if self.has_t:
        self.data_out = xr.concat([self.data_out, self.set_da(data)], self.t)
      else if self.has_z:
        self.data_out = xr.concat([self.data_out, self.set_da(data)], self.z)
      
