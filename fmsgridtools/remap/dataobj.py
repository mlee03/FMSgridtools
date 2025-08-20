import numpy as np
from pathlib import Path
import xarray as xr

import pyfms

class DataObj():

  time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)

  def __init__(self,
               datafile: str,
               variable: str,
               tile: int = None,
               input_dir: str = "./"):

    """
    DataObj class to handle data files and variables.
    """

    self.input_dir = Path(input_dir)
    self.tile = tile
    self.datafile = datafile
    self.variable = variable
    self.dtype = None
    self.time: str = None
    self.has_time: bool = False
    self.has_z: bool = False
    self.x: str = None
    self.y: str = None
    self.z: str = None
    self.time: str = None
    self.nx: int = None
    self.ny: int = None
    self.nz: int = None
    self.ntime: int = None
    self.ndim: int = None

    self.cell_measures: str = None
    self.area_averaged = False
    self.scale_factor: np.float32 | np.float64 | np.int32 | np.int64 = None
    self.offset: np.float32 | np.float64 | np.int32 | np.int64 = None
    self.missing_value: np.float32 | np.float64 | np.int32 | np.int64 = None
    self.fill_value: np.float32 | np.float64 | np.int32 | np.int64 = None
    self.static_area: dict = None
    self.data: np.float32 | np.float64 | np.int32 | np.int64 = None

    self.coords = False

    if tile is None:
      self.datafile = Path(self.datafile + ".nc")
    else:
      self.datafile = Path(self.datafile + f".tile{tile}.nc")

    #get coordinates
    with xr.open_dataset(self.input_dir/self.datafile, decode_cf=False) as dataset:

      if self.variable not in dataset: raise RuntimeError("variable not found")

      self.dtype = dataset[self.variable].dtype

      if not self.coords: self.get_coords(dataset)

      attributes = dataset[self.variable].attrs

      get_value = lambda attr_key: attributes[attr_key] if attr_key in attributes else None

      #get missing value
      self.missing_value = get_value("missing_value")
      self.fill_value = get_value("_FillValue")
      self.offset = get_value("add_offset")
      self.scale_factor = get_value("scale_factor")

      #check if cell methods is area mean
      if "cell_methods" in attributes:
        if "area" in attributes["cell_methods"]: self.area_averaged = True

      #get areas in associated_files
      if self.area_averaged:
        self.static_area = {}
        if "associated_files" in dataset.attrs:
          splitted_string = dataset.attrs["associated_files"].split()
          for i in range(0, len(splitted_string), 2):
            if tile is None:
              self.static_area[splitted_string[i].replace(':','')] = self.input_dir/splitted_string[i+1]
            else:
              self.static_area[splitted_string[i].replace(':','')] = self.input_dir/Path(splitted_string[i+1].replace(".nc", f".tile{tile}.nc"))

        #get area file indicated in cell_methods
        if "cell_measures" in attributes:
          splitted_string = attributes["cell_measures"].split()
          if splitted_string[0] == "area:":
            self.cell_measures = splitted_string[1]
            if self.cell_measures not in self.area: raise RuntimeError("area type not found")



  def get_coords(self, dataset):
    for coords in dataset.coords:
      if "axis" in dataset.coords[coords].attrs:
        if dataset.coords[coords].attrs["axis"] == "X":
          self.x = coords
          self.nx = dataset.sizes[coords]
        if dataset.coords[coords].attrs["axis"] == "Y":
          self.y = coords
          self.ny = dataset.sizes[coords]
        if dataset.coords[coords].attrs["axis"] == "Z":
          if self.has_z:
            if dataset.sizes[coords] < self.nz:
              self.z = coords
              self.nz = dataset.sizes[coords]
              self.has_z = True
          else:
            self.z = coords
            self.nz = dataset.sizes[coords]
            self.has_z = True
        if dataset.coords[coords].attrs["axis"] == "T":
          self.time = coords
          self.ntime = dataset.sizes[coords]
          self.has_time = True

    self.coords = True


  def get(self, klevel: int = None, timepoint: int = None)

    """
    Get slice of a variable from the dataset.
    """

    with xr.open_dataset(self.input_dir/self.datafile) as dataset:
      subset = dataset[self.variable]
      if timepoint is not None:
        if self.has_time: subset = dataset[self.variable].isel({self.time:timepoint})
      if klevel is not None:
        if self.has_z: subset = subset.isel({self.z:klevel})

    #need to get every other point
    self.data = subset


  def pre_scale(self, grid):

    if self.area_averaged:
      with xr.open_dataset(self.area[self.cell_measures]) as dataset:
        area_from_file = dataset[self.cell_measures].values[::2, ::2]

      area_from_here = pyfms.get_grid_area(nlon=grid.nx,
                                           nlat=grid.ny,
                                           lon=grid.x,
                                           lat=grid.y)

      self.data *= area_from_file/area_from_here


    #return np.multiply(subset.values, area, where=np.invert(subset.isnull().values))


data = DataObj(input_dir="/home/Mikyung.Lee/FRE-NCTools/DONOTDELETEME_DATA/TESTS/TESTS_INPUT/Testc-input/",
               datafile="00010101.land_month_cmip",
               tile=1,
               variable="nbp")

data.get(timepoint=0)



