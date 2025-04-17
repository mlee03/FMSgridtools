import ctypes
import numpy as np
import numpy.typing as npt
import xarray as xr
import pyfrenctools
from .gridtools_utils import check_file_is_there
from .gridobj import GridObj
from .mosaicobj import MosaicObj

class XGridObj() :

    def __init__(self,
                 src_mosaic: str = None,
                 tgt_mosaic: str = None,
                 restart_remap_file: str = None,
                 out_remap_file: str = "remap.nc",
                 src_grid: type[GridObj] = None,
                 tgt_grid: type[GridObj] = None,
                 debug: bool = False,
                 order: int = 1,
                 on_gpu: bool = False):
        self.src_mosaic = src_mosaic
        self.tgt_mosaic = tgt_mosaic
        self.restart_remap_file = restart_remap_file
        self.out_remap_file = out_remap_file
        self.src_grid = src_grid
        self.tgt_grid = tgt_grid
        self.debug: bool = False
        self.order: int = 1
        self.on_gpu: bool = False
        self.dataset = None
    
        if self.__check_restart_remap_file() or \
           self.__check_mosaic() or \
           self.__check_grids(): return
 
        raise RuntimeError("""Exchange grids can be generated from 
        (1) a restart remap_file
        (2) input and tgt mosaic files with grid file information
        (3) input and output grids as instances of GridObj 
        Please provide either the src_mosaic with the tgt_mosaic, 
                                  src_grid with the tgt_grid, 
                                  or a restart_remap_file""")
            
        
    def read_remap_file(self):
        self.dataset = xr.open_dataset(self.restart_remap_file)
        
                
    def write_remap_file(self):
        self.dataset.to_netcdf(self.out_remap_file)


    def create_xgrid(self, mask: dict[str,npt.NDArray[np.float64]] = None) -> dict():
        if not any( i == self.order for i in (1,2) ) : raise RuntimeError("conservative order must be 1 or 2")
        input_tile = 0
        xgrid=dict()
        for tgt_tile in self.tgt_grid:
            for src_tile in self.src_grid:
                nx_src = self.src_grid[src_tile].nxp-1
                ny_src = self.src_grid[src_tile].nyp-1
                nx_tgt = self.tgt_grid[tgt_tile].nxp-1
                ny_tgt = self.tgt_grid[tgt_tile].nyp-1
                x_src = np.deg2rad(np.array(self.src_grid[src_tile].x).flatten())
                y_src = np.deg2rad(np.array(self.src_grid[src_tile].y).flatten())
                x_tgt = np.deg2rad(np.array(self.tgt_grid[tgt_tile].x).flatten())
                y_tgt = np.deg2rad(np.array(self.tgt_grid[tgt_tile].y).flatten())
                if mask is None: mask = np.ones(nx_src*ny_src, dtype=np.float64)
                xgrid_out = pyfrenctools.CreateXgrid.get_2dx2d_order1(
                    nlon_src=nx_src, nlat_src=ny_src, nlon_tgt=nx_tgt, nlat_tgt=ny_tgt,
                    lon_src=x_src, lat_src=y_src, lon_tgt=x_tgt, lat_tgt=y_tgt, mask_src=mask
                )
                nxgrid = xgrid_out["nxgrid"]
                if input_tile == 0:
                    xgrid["tile1_cell"] = xgrid_out["xgrid_ij1"]
                    xgrid["tile2_cell"] = xgrid_out["xgrid_ij2"]
                    xgrid["xgrid_area"] = xgrid_out["xgrid_area"]
                    xgrid["tile1"] = np.array([input_tile+1]*nxgrid, dtype=np.int32)
                    input_tile += 1
                else:
                    xgrid["tile1_cell"] = np.concatenate(xgrid_out["xgrid_ij1"], xgrid_out["xgrid_ij1"])
                    xgrid["tile2_cell"] = np.concatenate(xgrid_out["xgrid_ij2"], xgrid_out["xgrid_ij2"])
                    xgrid["xgrid_area"] = np.concatenate(xgrid_out["xgrid_area"], xgrid_out["xgrid_area"])
                    xgrid["tile1"] = np.array([input_tile+1]*nxgrid, dtype=np.int32)
                    input_tile += 1
                xgrid["nxgrid"] = nxgrid
        return self.create_dataset(xgrid)


    def create_dataset(self, xgrid: dict()):
        tile1 = xr.DataArray(data=xgrid["tile1"],
                             dims=["ncells"],
                             attrs=dict(standard_name="tile number in input mosaic)")
        )
        tile1_cell = xr.DataArray(data=xgrid["tile1_cell"],
                                  dims=["ncells"],
                                  attrs=dict(standard_name="parent cell indices from src mosaic")
        )
        tile2_cell = xr.DataArray(data=xgrid["tile2_cell"],
                                  dims=["ncells"],
                                  attrs=dict(standard_name="parent cell indices from tgt mosaic")
        )
        xgrid_area = xr.DataArray(data=xgrid["xgrid_area"],
                                  dims=["ncells"],
                                  attrs=dict(standard_name="exchange grid cell area", units="m2")
        )                                  
        self.dataset = xr.Dataset(data_vars=dict(tile1=tile1,
                                                 tile1_cell=tile1_cell,
                                                 tile2_cell=tile2_cell,
                                                 xgrid_area=xgrid_area)
        )
        return self.dataset

    
    def __check_restart_remap_file(self):
        
        if self.restart_remap_file is not None :
            check_file_is_there(self.restart_remap_file)
            self.read_remap_file()
            return True
        else : return False

        
    def __check_mosaic(self):
        
        if self.src_mosaic is not None and self.tgt_mosaic is not None:
            # file checks are done in mosaic
            self.src_grid = MosaicObj(self.src_mosaic).griddict()
            self.tgt_grid = MosaicObj(self.tgt_mosaic).griddict()
            return True
        else : return False

        
    def __check_grids(self):
        return self.src_grid is not None and self.tgt_grid is not None
        
