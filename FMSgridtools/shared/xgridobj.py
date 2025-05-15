import ctypes

import numpy as np
import numpy.typing as npt
import pyfms
import pyfrenctools
import xarray as xr

from .gridobj import GridObj
from .gridtools_utils import check_file_is_there
from .mosaicobj import MosaicObj


class XGridObj() :

    def __init__(self,
                 src_mosaic: str = None,
                 tgt_mosaic: str = None,
                 restart_remap_file: str = None,
                 write_remap_file: str = "remap.nc",
                 src_grid: type[GridObj] = None,
                 tgt_grid: type[GridObj] = None,
                 order: int = 1,
                 on_gpu: bool = False):
        self.src_mosaic = src_mosaic
        self.tgt_mosaic = tgt_mosaic
        self.restart_remap_file = restart_remap_file
        self.write_remap_file = write_remap_file
        self.src_grid = src_grid
        self.tgt_grid = tgt_grid
        self.order: int = 1
        self.on_gpu: bool = False
        self.dataset = None
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

        self.dataset.to_netcdf(outfile)

    def create_xgrid(self, mask: dict[str,npt.NDArray] = None) -> dict():

        DEG_TO_RAD = pyfms.constants.DEG_TO_RAD

        if self.order not in (1,2):
            raise RuntimeError("conservative order must be 1 or 2")

        if self.on_gpu:
            create_xgrid_2dx2d_order1 = pyfrenctools.create_xgrid.get_2dx2d_order1_gpu
        else:
            create_xgrid_2dx2d_order1 = pyfrenctools.create_xgrid.get_2dx2d_order1

        for tgt_tile in self.tgt_grid:

            itile = 1
            xgrid={tgt_tile: dict()}

            for src_tile in self.src_grid.keys():
                xgrid_out = create_xgrid_2dx2d_order1(
                    nlon_src=self.src_grid[src_tile].nxp - 1,
                    nlat_src=self.src_grid[src_tile].nyp - 1,
                    nlon_tgt=self.tgt_grid[tgt_tile].nxp - 1,
                    nlat_tgt=self.tgt_grid[tgt_tile].nyp - 1,
                    lon_src=self.src_grid[src_tile].x * DEG_TO_RAD,
                    lat_src=self.src_grid[src_tile].y * DEG_TO_RAD,
                    lon_tgt=self.tgt_grid[tgt_tile].x * DEG_TO_RAD,
                    lat_tgt=self.tgt_grid[tgt_tile].y * DEG_TO_RAD
                )
                xgrid_out["tile"] = np.full(xgrid_out["nxcells"], itile, dtype=np.int32)
                xgrid[tgt_tile][src_tile] = xgrid_out
                itile = itile + 1

        return self.create_dataset(xgrid)

    def create_dataset(self, xgrid: dict()):

        for i_xgrid in xgrid.values():

            src_tile_data = np.concatenate([i_xgrid[src_tile]["tile"] for src_tile in i_xgrid.keys()])
            src_tile = xr.DataArray(data=src_tile_data,
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

            tgt_ij_data = np.concatenate([i_xgrid[src_tile]["tgt_ij"] for src_tile in i_xgrid.keys()])
            tgt_ij = xr.DataArray(data=tgt_ij_data,
                                  dims=["nxcells"],
                                  attrs=dict(standard_name="parent cell indices from tgt mosaic")
            )
            for src_tile in i_xgrid.keys(): del i_xgrid[src_tile]["tgt_ij"]

            xarea_data = np.concatenate([i_xgrid[src_tile]["xarea"] for src_tile in i_xgrid.keys()])
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

    def _check_restart_remap_file(self):

        if self.restart_remap_file is not None :
            check_file_is_there(self.restart_remap_file)
            self.read()
            return True
        else:
            return False

    def _check_mosaic(self):

        if self.src_mosaic is not None and self.tgt_mosaic is not None:
            self.src_grid = MosaicObj(self.src_mosaic).griddict()
            self.tgt_grid = MosaicObj(self.tgt_mosaic).griddict()
            return True
        else:
            return False
