import numpy as np
import numpy.typing as npt
import xarray as xr
from typing import List, Optional, Type
import dataclasses

@dataclasses.dataclass
class GridObj:
    grid: Optional[xr.Dataset] = None
    gridfile: Optional[str] = None

    @classmethod
    def from_file(cls, filepath: str) -> "GridObj":
        with xr.open_dataset(filepath) as ds:
            return cls(grid=ds, gridfile=filepath)
        
    def write_out_grid(self, filepath: str):
        self.grid.to_netcdf(filepath)

    def get_agrid_lonlat(self)-> tuple[npt.NDArray, npt.NDArray]:
        D2R = np.pi/180
        a_lon = None
        a_lat = None
        if self.grid.x.values is not None and self.grid.y.values is not None:
            x_flat = self.grid.x.values.flatten()
            y_flat = self.grid.y.values.flatten()
            nx = self.grid.sizes['nx']//2
            ny = self.grid.sizes['ny']//2

            a_lon = np.zeros(shape=nx)
            a_lat = np.zeros(shape=ny)

            for i in range(nx):
                a_lon[i] = x_flat[2*nx+1+2*i+1]*D2R
            for j in range(ny):
                a_lat[i] = y_flat[(2*j+1)*(2*nx+1)+1]*D2R

        return a_lon, a_lat

#TODO: I/O method for passing to the host