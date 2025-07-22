import ctypes
import numpy as np
import numpy.typing as npt
import xarray as xr

import pyfrenctools
import pyfms

from fmsgridtools.shared.gridobj import GridObj
from fmsgridtools.shared.gridtools_utils import check_file_is_there
from fmsgridtools.shared.mosaicobj import MosaicObj

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
                 src_mosaic_file: str = None,
                 tgt_moasic_file: str = None,
                 restart_remap_file: str = None,
                 write_remap_file: str = "remap.nc",
                 src_mosaic: type[MosaicObj] = None,
                 tgt_mosaic: type[MosaicObj] = None,
                 src_grid: type[GridObj] = None,
                 tgt_grid: type[GridObj] = None,
                 on_agrid: bool = True,
                 order: int = 1,
                 on_gpu: bool = False):
        self.input_dir = input_dir
        self.src_mosaic_file = src_mosaic_file
        self.tgt_moasic_file = tgt_moasic_file
        self.restart_remap_file = restart_remap_file
        self.write_remap_file = write_remap_file
        self.src_mosaic = src_mosaic
        self.tgt_mosaic = tgt_mosaic
        self.src_grid = src_grid
        self.tgt_grid = tgt_grid
        self.order = order
        self.on_gpu = on_gpu
        self.on_agrid = on_agrid
        self.dataset = {}
        self.datadict = {}
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
        Please provide either the src_mosaic_file with the tgt_moasic_file,
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

    def write(cls, datadict = None, outfile: str = None):

        if outfile is None:
            outfile = self.write_remap_file

        ij_src = xr.DataArray(np.column_stack((datadict['i_src']+1, datadict['j_src']+1)),
                              dims=["nxcells", "two"],
                              attrs={"src_ij": "parent cell indices in src mosaic", "_FillValue": False})
        ij_tgt = xr.DataArray(np.column_stack((datadict['i_tgt']+1, datadict['j_tgt']+1)),
                              dims=["nxcells", "two"],
                              attrs={"tgt_ij": "parent cell indices in tgt mosaic", "_FillValue": False})
        xarea = xr.DataArray(datadict['xarea'], dims=["nxcells"], attrs={"xarea": "exchange grid area", "_FillValue": False})

        xr.Dataset(data_vars={"ij_src": ij_src, "ij_tgt": ij_tgt, "xarea": xarea}).to_netcdf(outfile)

        return
        
        
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
            self.datadict[tgt_tile] = {}

            itgt_mask = None if tgt_mask is None else tgt_mask[tgt_tile]
            
            for src_tile in self.src_grid.keys():

                isrc_mask = None if src_mask is None else src_mask[src_tile]

                nxcells, xgrid_out = create_xgrid_2dx2d_order1(
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
                if nxcells > 0 :
                    xgrid_out["tile"] = np.full(nxcells, itile, dtype=np.int32)
                    self.datadict[tgt_tile][src_tile] = xgrid_out
                itile = itile + 1


    def _check_restart_remap_file(self):

        if self.restart_remap_file is not None :
            check_file_is_there(self.restart_remap_file)
            self.read()
            return True
        else:
            return False

        
    def _check_mosaic(self):

        if self.src_mosaic is None:
            if self.src_mosaic_file is None: return False
            self.src_grid = MosaicObj(self.input_dir,
                                      self.src_mosaic_file).read().get_grid(toradians=True,
                                                                            agrid=self.on_agrid,
                                                                            free_dataset=True)
        else:
            self.src_grid = self.src_mosaic.grid
            
        if self.tgt_mosaic is None:
            if self.tgt_mosaic_file is None: return False
            self.tgt_grid = MosaicObj(self.input_dir,
                                      self.tgt_moasic_file).read().get_grid(toradians=True,
                                                                            agrid=self.on_agrid,
                                                                            free_dataset=True)
        else:
            self.tgt_grid = self.tgt_mosaic.grid
            
        return True
