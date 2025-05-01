import ctypes
import numpy as np
import numpy.typing as npt
import xarray as xr
import pyfrenctools
import pyfms
from .gridtools_utils import check_file_is_there
from .gridobj import GridObj
from .mosaicobj import MosaicObj


class XGridObj() :

    def __init__(self,
                 src_mosaic: str = None,
                 tgt_mosaic: str = None,
                 remap_file: str = "remap.nc",
                 src_grid: type[GridObj] = None,
                 tgt_grid: type[GridObj] = None,
                 order: int = 1,
                 on_gpu: bool = False):
        self.src_mosaic = src_mosaic
        self.tgt_mosaic = tgt_mosaic
        self.remap_file = remap_file
        self.src_grid = src_grid
        self.tgt_grid = tgt_grid
        self.order: int = 1
        self.on_gpu: bool = False
        self.dataset = None
        self.tile1 = None
        self.tile1_cell = None
        self.tile2_cell = None
        self.xgrid_area = None
        self.ncells = None
        
        if self.__check_restart_remap_file() or \
           self.__check_mosaic() or \
           self.__check_grids(): return
 
        raise RuntimeError("""
        Exchange grids can be generated from 
        (1) a restart remap_file
        (2) input and tgt mosaic files with grid file information
        (3) input and output grids as instances of GridObj 
        Please provide either the src_mosaic with the tgt_mosaic, 
                                  src_grid with the tgt_grid, 
                                  or a restart_remap_file"""
        )
                    
    def read(self):        
        self.dataset = xr.open_dataset(self.remap_file)
        for key in self.dataset.data_vars.keys():
            setattr(self, key, self.dataset[key])
        
                
    def write(self, outfile: str = None):
        outfile = self.remap_file if outfile is None else outfile
        self.dataset.to_netcdf(outfile)


    def create_xgrid(self, mask: dict[str,npt.NDArray[np.float64]] = None) -> dict():

        PI = pyfms.constants(pyfms.pyFMS().cFMS).PI
        
        if self.order not in (1,2) : raise RuntimeError("conservative order must be 1 or 2")
        for tgt_tile in self.tgt_grid:
            xgrid={tgt_tile: dict()}
            for src_tile in self.src_grid.keys():
                xgrid_out = pyfrenctools.create_xgrid.get_2dx2d_order1(
                    nlon_src=self.src_grid[src_tile].nx,
                    nlat_src=self.src_grid[src_tile].ny,
                    nlon_tgt=self.tgt_grid[tgt_tile].nx,
                    nlat_tgt=self.tgt_grid[tgt_tile].ny,
                    lon_src=self.src_grid[src_tile].x * PI,
                    lat_src=self.src_grid[src_tile].y * PI,
                    lon_tgt=self.tgt_grid[tgt_tile].x * PI,
                    lat_tgt=self.tgt_grid[tgt_tile].y * PI                    
                )
                xgrid[tgt_tile][src_tile] = xgrid_out
        return self.create_dataset(xgrid)
                

    def create_dataset(self, xgrid: dict()):
        for i_xgrid in xgrid.values():
            src_tile_data = np.concatenate([i_xgrid[src_tile]["tile1"] for src_tile in i_xgrid.keys()])
            src_tile = xr.DataArray(data=tile1_data,
                                 dims=["nxcells"],
                                 attrs=dict(standard_name="tile number in input mosaic)")
            )
            for src_tile in i_xgrid.keys(): del i_xgrid[src_tile]["tile"]
            
            src_ij_data = np.concatenate([i_xgrid[src_tile]["src_ij"] for src_tile in i_xgrid.keys()])
            src_ij = xr.DataArray(data=src_ij_data,
                                  dims=["nxcells"],
                                  attrs=dict(standard_name="parent cell indices from src mosaic")
            )
            for src_tile in i_xgrid.keys(): del i_xgrid[src_tile]["src_ij"]
            
            tgt_ij_data = np.concatenate([i_xgrid[src_tile]["src_ij"] for src_tile in i_xgrid.keys()])
            tgt_ij = xr.DataArray(data=tgt_ij_data,
                                  dims=["nxcells"],
                                  attrs=dict(standard_name="parent cell indices from tgt mosaic")
            )
            for src_tile in i_xgrid.keys(): del i_xgrid[src_tile]["tgt_ij"]
            
            xarea_data = np.concatentate([i_xgrid[src_tile]["xarea"] for src_tile in i_xgrid.keys()])
            xarea = xr.DataArray(data=xarea_data,
                                 dims=["nxcells"],
                                 attrs=dict(standard_name="exchange grid cell area", units="m2")
            )
            del i_xgrid[src_tile]["xarea"]
            self.dataset = xr.Dataset(data_vars=dict(src_tile=src_tile,
                                                     src_ij=src_ij,
                                                     tgt_ij=tgt_ij,
                                                     xarea=xarea)
            )

    
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
        
