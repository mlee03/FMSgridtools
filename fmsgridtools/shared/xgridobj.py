import numpy as np
import numpy.typing as npt
import xarray as xr

import pyfrenctools
import pyfms

from fmsgridtools.shared.gridobj import GridObj
from fmsgridtools.shared.gridtools_utils import check_file_is_there
from fmsgridtools.shared.mosaicobj import MosaicObj


class XGridObj() :

    def __init__(self,
                 input_dir: str = "./", 
                 src_mosaic: str = None,
                 tgt_mosaic: str = None,
                 restart_remap_file: str = None,
                 write_remap_file: str = "remap.nc",
                 src_grid: type[GridObj] = None,
                 tgt_grid: type[GridObj] = None,
                 on_agrid: bool = True,
                 order: int = 1,
                 on_gpu: bool = False):
        self.input_dir = input_dir
        self.src_mosaic = src_mosaic
        self.tgt_mosaic = tgt_mosaic
        self.restart_remap_file = restart_remap_file
        self.write_remap_file = write_remap_file
        self.src_grid = src_grid
        self.tgt_grid = tgt_grid
        self.order = order
        self.on_gpu = on_gpu
        self.on_agrid = on_agrid
        self.dataset = {}
        self.src_tile = None
        self.src_ij = None
        self.tgt_ij = None
        self.xarea = None
        self.nxcells = None

        if self._check_restart_remap_file(): return
        if self._check_mosaic(): return

        raise RuntimeError("""
        Exchange grids can be generated from
        (1) a restart remap_file
        (2) input and tgt mosaic files with grid file information
        (3) input and output grids as instances of GridObj
        Please provide either the src_mosaic with the tgt_mosaic,
                                  src_grid with the tgt_grid,
                                  or a restart_remap_file"""
        )

    def read(self, infile: str = None):

        if infile is None:
            infile = self.restart_remap_file

        self.dataset = xr.open_dataset(infile)

        for key in self.dataset.data_vars.keys():
            setattr(self, key, self.dataset[key])

        for key in self.dataset.sizes:
            setattr(self, key, self.dataset.sizes[key])


    def write(self, outfile: str = None):

        if outfile is None:
            outfile = self.write_remap_file

        if len(self.dataset) == 1:
            for ikey in self.dataset: self.dataset[ikey].to_netcdf(outfile)
        else:
            for ikey in self.dataset:
                self.dataset.to_netcdf(outfile[:-3]+ikey+".nc")
        
        
    def create_xgrid(self, mask: dict[str,npt.NDArray] = None) -> dict():

        DEG_TO_RAD = pyfms.constants.DEG_TO_RAD

        if self.order not in (1,2):
            raise RuntimeError("conservative order must be 1 or 2")

        if self.on_gpu:
            create_xgrid_2dx2d_order1 = pyfrenctools.create_xgrid.get_2dx2d_order1_gpu
        else:
            create_xgrid_2dx2d_order1 = pyfrenctools.create_xgrid.get_2dx2d_order1

        for tgt_tile in self.tgt_grid:
            
            itile = 0
            xgrid = {tgt_tile: dict()}

            for src_tile in self.src_grid.keys():
                
                xgrid_out = create_xgrid_2dx2d_order1(
                    nlon_src = self.src_grid[src_tile].nx,
                    nlat_src = self.src_grid[src_tile].ny,
                    nlon_tgt = self.tgt_grid[tgt_tile].nx,
                    nlat_tgt = self.tgt_grid[tgt_tile].ny,
                    lon_src=self.src_grid[src_tile].x,
                    lat_src=self.src_grid[src_tile].y,
                    lon_tgt=self.tgt_grid[tgt_tile].x,
                    lat_tgt=self.tgt_grid[tgt_tile].y
                )
                xgrid_out["tile"] = np.full(xgrid_out["nxcells"], itile, dtype=np.int32)
                xgrid[tgt_tile][src_tile] = xgrid_out
                itile = itile + 1
                
        return self.create_dataset(xgrid, tgt_tile)

    
    def create_dataset(self, xgrid: dict(), tgt_tile: str = "tile1"):

        for i_xgrid in xgrid.values():

            src_tile_data = np.concatenate([i_xgrid[src_tile]["tile"] for src_tile in i_xgrid.keys()])
            src_tile = xr.DataArray(data=src_tile_data,
                                 dims=["nxcells"],
                                 attrs=dict(standard_name="tile number in input mosaic)")
            )
            for isrc_tile in i_xgrid.keys(): del i_xgrid[isrc_tile]["tile"]

            src_ij_data = np.concatenate([i_xgrid[src_tile]["src_ij"] for src_tile in i_xgrid.keys()])
            src_ij = xr.DataArray(data=src_ij_data,
                                  dims=["nxcells"],
                                  attrs=dict(standard_name="parent cell indices from src mosaic")
            )            
            for isrc_tile in i_xgrid.keys(): del i_xgrid[isrc_tile]["src_ij"]
            
            tgt_ij_data = np.concatenate([i_xgrid[src_tile]["tgt_ij"] for src_tile in i_xgrid.keys()])
            tgt_ij = xr.DataArray(data=tgt_ij_data,
                                  dims=["nxcells"],
                                  attrs=dict(standard_name="parent cell indices from tgt mosaic")
            )
            for isrc_tile in i_xgrid.keys(): del i_xgrid[isrc_tile]["tgt_ij"]

            xarea_data = np.concatenate([i_xgrid[src_tile]["xarea"] for src_tile in i_xgrid.keys()])
            xarea = xr.DataArray(data=xarea_data,
                                 dims=["nxcells"],
                                 attrs=dict(standard_name="exchange grid cell area", units="m2")
            )
            for isrc_tile in i_xgrid.keys(): del i_xgrid[isrc_tile]["xarea"]
            
            self.dataset[tgt_tile] = xr.Dataset(data_vars=dict(src_tile=src_tile,
                                                               src_ij=src_ij,
                                                               tgt_ij=tgt_ij,
                                                               xarea=xarea)
            )                        
            
    def _check_restart_remap_file(self):

        if self.restart_remap_file is not None :
            check_file_is_there(self.restart_remap_file)
            self.read()
            return True
        else:
            return False

    def _check_mosaic(self):

        if self.src_mosaic is not None and self.tgt_mosaic is not None:
            self.src_grid = MosaicObj(self.input_dir, self.src_mosaic).read().get_grid(toradians=True,
                                                                                       agrid=self.on_agrid,
                                                                                       free_dataset=True)
            self.tgt_grid = MosaicObj(self.input_dir, self.tgt_mosaic).read().get_grid(toradians=True,
                                                                                       agrid=self.on_agrid,
                                                                                       free_dataset=True)
            return True
        else:
            return False
