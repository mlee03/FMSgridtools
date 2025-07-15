import ctypes
import numpy as np
import numpy.typing as npt
import xarray as xr

import pyfrenctools
import pyfms

from fmsgridtools.shared.gridobj import GridObj
from fmsgridtools.shared.gridtools_utils import check_file_is_there
from fmsgridtools.shared.mosaicobj import MosaicObj

class cXgridObj(ctypes.Structure):
    _fields_ = [("nxcells", ctypes.c_int),
                ("input_parent_cell_index", ctypes.POINTER(ctypes.c_double)),
                ("output_parent_cell_index", ctypes.POINTER(ctypes.c_double)),
                ("xcell_area", ctypes.POINTER(ctypes.c_double)),
                ("dcentroid_lon", ctypes.POINTER(ctypes.c_double)),
                ("dcentroid_lat", ctypes.POINTER(ctypes.c_double))
    ]

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


    def write(self, outfile: str = None, old: bool = False):

        if outfile is None:
            outfile = self.write_remap_file

        if old:
            if len(self.dataset) == 1:
                i_src = self.dataset['src_ij']% self.src_grid['tile1'].nx
                j_src = self.dataset['src_ij']// self.src_grid['tile1'].nx
                i_tgt = self.dataset['tgt_ij']% self.tgt_grid['tile1'].nx
                j_tgt = self.dataset['tgt_ij']// self.tgt_grid['tile1'].nx                    
                ij_src = np.column_stack((i_src, j_src))
                ij_tgt = np.column_stack((i_tgt, j_tgt))    
                xr.Dataset(data_vars=dict(src_tile=self.dataset[ikey]['src_tile'],
                                src_ij=(["nxcells", "two"], ij_src),
                                tgt_ij=(["nxcells", "two"], ij_tgt),
                                xarea=self.dataset[ikey]['xarea'])
                ).to_netcdf(outfile)
            else:
                for ikey in self.dataset: #for each output tile
                    i_src = self.dataset[ikey]['src_ij']% self.src_grid['tile1'].nx
                    j_src = self.dataset[ikey]['src_ij']// self.src_grid['tile1'].nx
                    i_tgt = self.dataset[ikey]['tgt_ij']% self.tgt_grid['tile1'].nx
                    j_tgt = self.dataset[ikey]['tgt_ij']// self.tgt_grid['tile1'].nx                    
                    ij_src = np.column_stack((i_src, j_src))
                    ij_tgt = np.column_stack((i_tgt, j_tgt))    
                    xr.Dataset(data_vars=dict(src_tile=self.dataset[ikey]['src_tile'],
                                  src_ij=(["nxcells", "two"], ij_src),
                                  tgt_ij=(["nxcells", "two"], ij_tgt),
                                  xarea=self.dataset[ikey]['xarea'])
                    ).to_netcdf(outfile[:-2]+ikey+".nc")
            return                

        if len(self.dataset) == 1:
            for ikey in self.dataset: self.dataset[ikey].to_netcdf(outfile)
        else:
            for ikey in self.dataset:
                self.dataset[ikey].to_netcdf(outfile[:-2]+ikey+".nc")
        
        
    def create_xgrid(self, src_mask: dict[str,npt.NDArray] = None, tgt_mask: dict[str, npt.NDArray] = None) -> dict():

        if self.order not in (1,2):
            raise RuntimeError("conservative order must be 1 or 2")

        if self.on_gpu:
            create_xgrid_2dx2d_order1 = pyfrenctools.create_xgrid.get_2dx2d_order1_gpu
        else:
            create_xgrid_2dx2d_order1 = pyfrenctools.create_xgrid.get_2dx2d_order1

        for tgt_tile in self.tgt_grid:

            itile = 1
            xgrid = {}

            itgt_mask = None if tgt_mask is None else tgt_mask[tgt_tile]

            for src_tile in self.src_grid.keys():

                isrc_mask = None if src_mask is None else src_mask[src_tile]

                xgrid_out = create_xgrid_2dx2d_order1(
                    nlon_src = self.src_grid[src_tile].nx,
                    nlat_src = self.src_grid[src_tile].ny,
                    nlon_tgt = self.tgt_grid[tgt_tile].nx,
                    nlat_tgt = self.tgt_grid[tgt_tile].ny,
                    lon_src=self.src_grid[src_tile].x,
                    lat_src=self.src_grid[src_tile].y,
                    lon_tgt=self.tgt_grid[tgt_tile].x,
                    lat_tgt=self.tgt_grid[tgt_tile].y,
                    mask_src=isrc_mask,
                    mask_tgt=itgt_mask
                )
                if xgrid_out['nxcells'] > 0 :
                    xgrid_out["tile"] = np.full(xgrid_out["nxcells"], itile, dtype=np.int32)
                    xgrid[src_tile] = xgrid_out
                itile = itile + 1

            self.create_dataset(xgrid, tgt_tile)

    
    def create_dataset(self, xgrid: dict(), tgt_tile: str = "tile1"):

        src_tile_data = np.concatenate([xgrid[src_tile]["tile"] for src_tile in xgrid.keys()])
        src_tile = xr.DataArray(data=src_tile_data,
                                dims=["nxcells"],
                                attrs=dict(standard_name="tile number in input mosaic)")
        )

        src_ij_data = np.concatenate([xgrid[src_tile]["src_ij"] for src_tile in xgrid.keys()])
        src_ij = xr.DataArray(data=src_ij_data,
                                dims=["nxcells"],
                                attrs=dict(standard_name="parent cell indices from src mosaic")
        )            
            
        tgt_ij_data = np.concatenate([xgrid[src_tile]["tgt_ij"] for src_tile in xgrid.keys()])
        tgt_ij = xr.DataArray(data=tgt_ij_data,
                                dims=["nxcells"],
                                attrs=dict(standard_name="parent cell indices from tgt mosaic")
        )

        xarea_data = np.concatenate([xgrid[src_tile]["xarea"] for src_tile in xgrid.keys()])
        xarea = xr.DataArray(data=xarea_data,
                                dims=["nxcells"],
                                attrs=dict(standard_name="exchange grid cell area", units="m2")
        )
        
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
