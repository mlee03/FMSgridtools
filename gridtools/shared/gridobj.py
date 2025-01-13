import numpy as np
import numpy.typing as npt
import xarray as xr
from typing import List, Optional, Type
import dataclasses

@dataclasses.dataclass
class GridObj:
    grid: xr.Dataset
    gridfile: str

    @classmethod
    def from_file(cls, filepath: str) -> "GridObj":
        with xr.open_dataset(filepath) as ds:
            return cls(grid=ds, gridfile=filepath)
        
    def write_out_grid(self, filepath: str):
        self.grid.to_netcdf(filepath)

#TODO: I/O method for passing to the host