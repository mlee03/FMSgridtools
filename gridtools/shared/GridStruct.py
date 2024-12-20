import numpy as np
import numpy.typing as npt
import xarray as xr
from typing import List, Optional, Type
import dataclasses

#TODO: /home/Mikyung.Lee/FRE-NCTools/DONOTDELETEME_DATA/TESTS/TESTS_INPUT/Testn-input/C768_grid.tile1.nc for grid file contents to be used as attributes for GridStruct class

@dataclasses.dataclass
class GridStruct:
    tile: str = None
    x: npt.NDArray[np.float64] = None
    y: npt.NDArray[np.float64] = None
    dx: npt.NDArray[np.float64] = None
    dy: npt.NDArray[np.float64] = None
    area: npt.NDArray[np.float64] = None
    angle_dx: npt.NDArray[np.float64] = None
    angle_dy: npt.NDArray[np.float64] = None
    arcx: str = None

    @classmethod
    def grid_from_file(cls, file_path: str) -> "GridStruct":
        with xr.open_dataset(file_path) as ds:
            return cls(
                tile = ds.tile.values.item(),
                x = ds.x.values,
                y = ds.y.values,
                dx = ds.dx.values,
                dy = ds.dy.values,
                area = ds.area.values,
                angle_dx = ds.angle_dx.values,
                angle_dy = ds.angle_dy.values,
                arcx = ds.arcx.values,
            )    
        
    def write_out_grid(self, file_path: str):
    
    #TODO: I/O method for passing to the host