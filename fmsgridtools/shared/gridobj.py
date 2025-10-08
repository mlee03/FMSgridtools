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

    def __init__(self,
                 dataset: type[xr.Dataset] = None,
                 gridfile: str = None,
                 domain: pyfms.mpp.Domain = None):

        self.gridfile = gridfile
        self.dataset = dataset
        self.domain = domain

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

    def read_xy(self, toradians: bool = False, agrid: bool = False):

        with xr.open_dataset(self.gridfile) as dataset:

            for key in dataset.sizes:
                setattr(self, key, dataset.sizes[key])

            if agrid:
                self.x = np.ascontiguousarray(dataset["x"].values[::2, ::2])
                self.y = np.ascontiguousarray(dataset["y"].values[::2, ::2])
                self.nx, self.ny = self.nx//2, self.ny//2
                self.nxp, self.nyp = self.nx+1, self.ny+1
            if toradians:
                self.x = np.radians(self.x, dtype=np.float64)
                self.y = np.radians(self.y, dtype=np.float64)

    def to_domain(self, domain: pyfms.Domain):
        if self.domain is not None:
            isc, iec, jsc, jec = domain.isc, domain.iec, domain.jsc, domain.jec
            self.x = np.ascontiguousarray(self.x[jsc:jec+1, isc:iec+1])
            self.y = np.ascontiguousarray(self.y[jsc:jec+1, isc:iec+1])
            self.nx = domain.xsize
            self.ny = domain.nysize
            self.nxp = domain.xsize + 1
            self.nyp = domain.ysize + 1

    def get_fms_area(self):

        self.area = pyfms.grid_utils.get_grid_area(lon=self.x, lat=self.y)
        return self.area

    def read_all(self, toradians: bool = False, agrid: bool = False, free_dataset: bool = False):
        """
        read:
        This function reads in the gridfile and initializes the instance variables
        """

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
            self.nx = self.nx // 2
            self.ny = self.ny // 2
            self.nxp = self.nx + 1
            self.nyp = self.ny + 1

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

    def agrid(self) -> tuple[npt.NDArray, npt.NDArray]:
        """
        get_agrid_lonlat:

        This method returns the lon and lat for the A-grid as calculated from the
        x and y attributes of the GridObj.
        """
        if self.x is not None and self.y is not None:
            a_lon = np.ascontiguousarray(self.x[::2, ::2])
            a_lat = np.ascontiguousarray(self.y[::2, ::2])

        return a_lon, a_lat

# TODO: I/O method for passing to the host
