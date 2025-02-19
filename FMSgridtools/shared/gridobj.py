import dataclasses
from typing import List, Optional

import numpy as np
import numpy.typing as npt
import xarray as xr

from FMSgridtools.shared.gridtools_utils import check_file_is_there

"""
GridObj:

Dataclass for containing basic grid data to be used by other grid objects
"""
@dataclasses.dataclass
class GridObj:
    grid_data: Optional[xr.Dataset] = None
    grid_file: Optional[str] = None

    def __post_init__(self):
        if self.grid_file is not None:
            check_file_is_there(self.grid_file)
            with xr.open_dataset(self.grid_file) as ds:
                self.grid_data = ds

    """
    from_file:

    This class method will return an instance of GridObj with attributes
    matching the contents of the passed netcdf file containing the grid
    data.
    """
    @classmethod
    def from_file(cls, filepath: str) -> "GridObj":
        check_file_is_there(filepath)
        with xr.open_dataset(filepath) as ds:
            return cls(
                grid_data=ds,
                grid_file=filepath,
            )
        
    """
    write_out_grid:

    This method will generate a netcdf file containing the contents of the
    grid_data attribute.
    """
    def write_out_grid(self, filepath: str):
        if self.grid_data is not None:
            self.grid_data.to_netcdf(filepath)

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
    
    """
    get_variable_list:

    This method returns a list of variables contained within the grid_data
    dataset.
    """
    def get_variable_list(self) -> List:
        return list(self.grid_data.data_vars)
    
    @property
    def tile(self):
        if self.grid_data is not None:
            return self.grid_data.tile.values.item().decode('ascii')
        else:
            return None
        
    @property
    def x(self):
        if self.grid_data is not None:
            return np.ascontiguousarray(self.grid_data.x.values)
        else:
            return None
    
    @property
    def y(self):
        if self.grid_data is not None:
            return np.ascontiguousarray(self.grid_data.y.values)
        else:
            return None
        
    @property
    def dx(self):
        if self.grid_data is not None:
            return np.ascontiguousarray(self.grid_data.dx.values)
        else:
            return None
        
    @property
    def dy(self):
        if self.grid_data is not None:
            return np.ascontiguousarray(self.grid_data.dy.values)
        else:
            return None
    
    @property
    def area(self):
        if self.grid_data is not None:
            return np.ascontiguousarray(self.grid_data.area.values)
        else:
            return None
        
    @property
    def angle_dx(self):
        if self.grid_data is not None:
            return np.ascontiguousarray(self.grid_data.angle_dx.values)
        else:
            return None
        
    @property
    def angle_dy(self):
        if self.grid_data is not None:
            return np.ascontiguousarray(self.grid_data.angle_dy.values)
        else:
            return None
        
    @property
    def arcx(self):
        if self.grid_data is not None:
            return self.grid_data.arcx.values.item().decode('ascii')
        else:
            return None

    @property
    def nx(self):
        if self.grid_data is not None:
            return self.grid_data.sizes['nx']
        else:
            return None
        
    @property
    def ny(self):
        if self.grid_data is not None:
            return self.grid_data.sizes['ny']
        else:
            return None
        
    @property
    def nxp(self):
        if self.grid_data is not None:
                return self.grid_data.sizes['nxp']
        else:
            return None
        
    @property
    def nyp(self):
        if self.grid_data is not None:
            return self.grid_data.sizes['nyp']
        else:
            return None

#TODO: I/O method for passing to the host