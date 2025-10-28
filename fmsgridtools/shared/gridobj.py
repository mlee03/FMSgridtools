import dataclasses
import numpy as np
import numpy.typing as npt
from pathlib import Path
from types import SimpleNamespace
import xarray as xr

import pyfms
from fmsgridtools.shared.gridtools_utils import check_file_is_there


"""
GridObj:

Class for containing basic grid data to be used by other grid objects
"""


class GridObj:

    def __init__(self,
                 input_dir: str = "./",
                 dataset: type[xr.Dataset] = None,
                 gridfile: str = None,
                 domain: pyfms.Domain = None,
                 tile: xr.DataArray|str = None
                 nx: int = None,
                 ny: int = None,
                 nxp: int = None,
                 nyp: int = None,
                 x: xr.DataArray|npt.NDArray = None,
                 y: xr.DataArray|npt.NDArray = None,
                 dx: xr.DataArray|npt.NDArray = None,
                 dy: xr.DataArray|npt.NDArray = None,
                 area: xr.DataArray|npt.NDArray = None,
                 angle_dx: xr.DataArray|npt.NDArray = None,
                 angle_dy: xr.DataArray|npt.NDArray = None,
                 arcx: xr.DataArray|npt.NDArray = None
    ):

        self.input_dir = Path(input_dir)
        self.gridfile = Path(gridfile)
        self.dataset = dataset
        self.domain = domain

        self.nx = nx
        self.ny = ny
        self.nxp = nxp
        self.nyp = nyp
        self.tile = tile
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.area = area
        self.angle_dx = angle_dx
        self.angle_dy = angle_dy
        self.arcx = arcx

        self.names = SimpleNamespace()
        self.names.tile=("tile", self.tile)
        self.names.x=("x", self.x)
        self.names.y=("y", self.y)
        self.names.dy=("dy", self.dy)
        self.names.dx=("dx", self.dx)
        self.names.area=("area", self.area)
        self.names.angle_dx=("angle_dx", self.angle_dx)
        self.names.angle_dy=("angle_dy", self.angle_dy)
        #self.arcx=("arcx", selfarc.x)

        
    def read_xy(self, center: bool = True, radians: bool = True):

        if center and tgrid:
            cFMS_error(FATAL, "cannot specify center and tgrid at the same time")
        
        with xr.open_dataset(self.input_dir/self.gridfile) as ds:

            for name, coord in [self.names.x, self.names.y]:
                coord = ds[name].values
                if center:
                    coord = coord[::2, ::2]                
                if radians:
                    coord = np.radians(coord, dtype=np.float64)
                coord = np.ascontiguousarray(coord)

        return self.x, self.y
        
                            
    def to_domain(self, domain: pyfms.Domain):

        if self.x is None or self.y is None:
            pyfms.fms.error(FATAL, "must read in grid first")

        isc, iec, jsc, jec = domain.isc, domain.iec, domain.jsc, domain.jec

        for name, coord in self.names:
            if coord is not None:
                coord = np.ascontiguousarray(coord[jsc:jec+1, isc:iec+1])
                if coord.shape != (domain.ysize_c+1, domain.xsize_c+1):
                    pyfms.fms.error(FATAL, "x and y on domain incorrect size")
            
        self.nx = domain.xsize_c
        self.ny = domain.ysize_c
        self.nxp = domain.xsize_c + 1
        self.nyp = domain.ysize_c + 1


    def get_fms_area(self):

        self.area = pyfms.grid_utils.get_grid_area(lon=self.x, lat=self.y)
        return self.area

    
    def read_all(self, radians: bool = False, center: bool = False, free_dataset: bool = False):

        """
        read:
        This function reads in the gridfile and initializes the instance variables
        """

        check_file_is_there(self.gridfile)
        self.dataset = xr.open_dataset(self.gridfile)
        self._get_attributes()

        for coord, name in self.names:
            if coord is None:
                pyfms.fms.error(WARNING, f"could not read in {name}")
            if radians:
                coord = np.radians(coord, dtype=np.float64)
            if center:
                coord = np.ascontiguousarray(coord[::2, ::2])

        if center:
            self.nx = self.nx // 2
            self.ny = self.ny // 2
            self.nxp = self.nx + 1
            self.nyp = self.ny + 1
            
        if free_dataset:
            del self.dataset
            self.dataset = None

        return self

    
    def _get_attributes(self):

        for key in self.dataset.data_vars:
            if isinstance(self.dataset.data_vars[key].values, np.ndarray):
                setattr(self, key, self.dataset[key].values)
            else:
                setattr(self, key, str(self.dataset[key].astype(str).values))

        for key in self.dataset.sizes:
            setattr(self, key, self.dataset.sizes[key])


    def write(self, filepath: str):

        """
        write_out_grid:
        This method will generate a netcdf file containing the contents of the
        dataset attribute.
        """
        
        if self.dataset is not None:
            self.dataset.to_netcdf(filepath)


    def get_variable_list(self) -> list:

        """
        get_variable_list:
        This method returns a list of variables contained within the dataset.
        """
        
        if self.dataset is not None:
            return list(self.dataset.data_vars.keys())
        else:
            return None
