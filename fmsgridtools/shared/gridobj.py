import dataclasses
from typing import List, Optional
import numpy as np
import numpy.typing as npt
import xarray as xr
import pyfms

from fmsgridtools.shared.gridtools_utils import check_file_is_there


"""
GridObj:

Class for containing basic grid data to be used by other grid objects
"""
class GridObj:

    def __init__(self, dataset: type[xr.Dataset] = None, gridfile: str = None):
        self.gridfile = gridfile
        self.tile = None
        self.nx = None
        self.ny = None
        self.nxp = None
        self.nyp = None
        self.tile = None
        self.x = None
        self.y = None
        self.dx = None
        self.dy = None
        self.area = None
        self.angle_dx = None
        self.angle_dy = None
        self.arcx = None
        self.dataset = dataset


    """
    read:
    This function reads in the gridfile and initializes the instance variables
    """
    def read(self, toradians: bool = False, agrid: bool = False, free_dataset: bool = False):

        check_file_is_there(self.gridfile)
        self.dataset = xr.open_dataset(self.gridfile)
        self.get_attributes()

        if free_dataset:
            del self.dataset
            self.dataset = None

        if toradians:
            self.x = np.radians(self.x, dtype=np.float64)
            self.y = np.radians(self.y, dtype=np.float64)

        if agrid:
            self.x, self.y = self.agrid()
            [self.nyp, self.nxp] = self.x.shape
            self.nx = self.nxp - 1
            self.ny = self.nyp - 1

        return self


    def get_attributes(self):

        for key in self.dataset.data_vars:
            if isinstance(self.dataset.data_vars[key].values, np.ndarray):
                setattr(self, key, self.dataset[key].values)
            else:
                setattr(self, key, str(self.dataset[key].astype(str).values))

        for key in self.dataset.sizes:
            setattr(self, key, self.dataset.sizes[key])

    """
    write_out_grid:
    This method will generate a netcdf file containing the contents of the
    dataset attribute.
    """
    def write(self, filepath: str):

        if self.dataset is not None:
            self.dataset.to_netcdf(filepath)


    """
    get_variable_list:
    This method returns a list of variables contained within the dataset.
    """
    def get_variable_list(self) -> list:

        if self.dataset is not None:
            return list(self.dataset.data_vars.keys())
        else:
            return None


    def x_contiguous(self):

        if self.x is not None:
            return np.ascontiguousarray(self.x)
        else:
            return None


    def y_contiguous(self):

        if self.y is not None:
            return np.ascontiguousarray(self.y)
        else:
            return None


    def dx_contiguous(self):

        if self.dx is not None:
            return np.ascontiguousarray(self.dx)
        else:
            return None


    def dy_contiguous(self):

        if self.dy is not None:
            return np.ascontiguousarray(self.dataset.dy)
        else:
            return None


    def area_contiguous(self):

        if self.area is not None:
            return np.ascontiguousarray(self.dataset.area)
        else:
            return None


    def angle_dx_contiguous(self):

        if self.angle_dx is not None:
            return np.ascontiguousarray(self.dataset.angle_dx)
        else:
            return None


    def angle_dy_contiguous(self):

        if self.angle_dy is not None:
            return np.ascontiguousarray(self.dataset.angle_dy)
        else:
            return None


    def agrid(self)-> tuple[npt.NDArray, npt.NDArray]:

        """
        get_agrid_lonlat:

        This method returns the lon and lat for the A-grid as calculated from the
        x and y attributes of the GridObj.
        """
        if self.x is not None and self.y is not None:
            a_lon = np.ascontiguousarray(self.x[::2, ::2])
            a_lat = np.ascontiguousarray(self.y[::2, ::2])

        return a_lon, a_lat

#TODO: I/O method for passing to the host
