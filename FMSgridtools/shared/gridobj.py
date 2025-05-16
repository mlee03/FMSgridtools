import dataclasses
from typing import List, Optional

import numpy as np
import numpy.typing as npt
import xarray as xr

#from FMSgridtools.shared.gridtools_utils import check_file_is_there

"""
GridObj:

Dataclass for containing basic grid data to be used by other grid objects
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
    def read(self):

        #check_file_is_there(self.gridfile)
        self.dataset = xr.open_dataset(self.gridfile)
        self.get_attributes()

        return self

    def get_attributes(self):
        numbers = [np.ndarray]

        for key in self.dataset.data_vars:
            if isinstance(self.dataset.data_vars[key].values, np.ndarray):
                setattr(self, key, self.dataset.data_vars[key].values)
            else:
                setattr(self, key, self.dataset.data_vars[key].astype(str).values)

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

        return list(self.dataset.data_vars.keys())

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


    """
    get_agrid_lonlat:

    This method returns the lon and lat for the A-grid as calculated from the
    x and y attributes of the GridObj.
    """
    def get_agrid_lonlat(self)-> tuple[npt.NDArray, npt.NDArray]:
        D2R = np.pi/180
        a_lon = None
        a_lat = None
        if self.x is not None and self.y is not None:
            nx = (self.x.shape[1]-1)//2
            ny = (self.x.shape[0]-1)//2
            x_flat = self.x.flatten()
            y_flat = self.y.flatten()

            a_lon = np.zeros(shape=nx)
            a_lat = np.zeros(shape=ny)

            for i in range(nx):
                a_lon[i] = x_flat[2*nx+1+2*i+1]*D2R
            for j in range(ny):
                a_lat[i] = y_flat[(2*j+1)*(2*nx+1)+1]*D2R

        return np.ascontiguousarray(a_lon), np.ascontiguousarray(a_lat)



#TODO: I/O method for passing to the host
