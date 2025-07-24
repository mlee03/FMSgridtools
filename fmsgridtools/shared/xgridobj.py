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
                 tgt_mosaic_file: str = None,
                 restart_remap_file: str = None,
                 write_remap_file: str = "remap.nc",
                 src_mosaic: type[MosaicObj] = None,
                 tgt_mosaic: type[MosaicObj] = None,
                 src_grid: dict[type[GridObj]] = None,
                 tgt_grid: dict[type[GridObj]] = None,    
                 dataset: type[xr.Dataset] = None,
                 datadict: dict = None,
                 on_agrid: bool = True,
                 order: int = 1,
                 on_gpu: bool = False):
        self.input_dir = input_dir
        self.src_mosaic_file = src_mosaic_file
        self.tgt_mosaic_file = tgt_mosaic_file
        self.restart_remap_file = restart_remap_file
        self.write_remap_file = write_remap_file
        self.src_mosaic = src_mosaic
        self.tgt_mosaic = tgt_mosaic
        self.src_grid = src_grid
        self.tgt_grid = tgt_grid
        self.order = order
        self.on_gpu = on_gpu
        self.on_agrid = on_agrid
        self.dataset = {} if dataset is None else dataset
        self.datadict = {} if datadict is None else datadict

        self._srcinfoisthere = False
        self._tgtinfoisthere = False
        
        if self._check_restart_remap_file(): return
        if self._check_grid(self.src_grid): self._srcinfoisthere = True
        if self._check_grid(self.tgt_grid): self._tgtinfoisthere = True
        if self._check_mosaic(self.src_mosaic): self._tgtinfoisthere = True
        if self._check_mosaic(self.tgt_mosaic): self._tgtinfoisthere = True
        if self._check_mosaic_file(self.src_mosaic_file, "src"): self._srcinfoisthere = True
        if self._check_mosaic_file(self.tgt_mosaic_file, "tgt"): self._tgtinfoisthere = True

        if not self._srcinfoisthere or not self._tgtinfoisthere:
            raise RuntimeError("Please provide grid information")


    def read(self, infile: str = None):

        if infile is None:
            if self.restart_remap_file is None:
                raise RuntimeError("must provide the input remap file for reading")
            infile = self.restart_remap_file

        self.dataset = xr.open_dataset(infile)

        for key in self.dataset.data_vars.keys():
            setattr(self, key, self.dataset[key].values)

        for key in self.dataset.sizes:
            setattr(self, key, self.dataset.sizes[key])

    def write(self, datadict = None, outfile: str = None):

        if outfile is None:
            outfile = self.write_remap_file

        if datadict is None: datadict = self.datadict
        for tgt_tile in datadict:
            for src_tile in datadict:
                thisdict = datadict[tgt_tile][src_tile]
                src_ij = xr.DataArray(np.column_stack((thisdict['src_i']+1, thisdict['src_j']+1)),
                                                      dims=["nxcells", "two"],
                                                      attrs={"src_ij": "parent cell indices in src mosaic", "_FillValue": False})
                tgt_ij = xr.DataArray(np.column_stack((thisdict['tgt_i']+1, thisdict['tgt_j']+1)),
                                          dims=["nxcells", "two"],
                                          attrs={"tgt_ij": "parent cell indices in tgt mosaic", "_FillValue": False})
                xarea = xr.DataArray(thisdict['xarea'], dims=["nxcells"], 
                                     attrs={"xarea": "exchange grid area", "_FillValue": False})

        xr.Dataset(data_vars={"src_ij": src_ij, "tgt_ij": tgt_ij, "xarea": xarea}).to_netcdf(outfile)

        return
        
        
    def create_xgrid(self, src_mask: dict[str,npt.NDArray] = None, tgt_mask: dict[str, npt.NDArray] = None) -> dict:

        if self.order not in (1,2):
            raise RuntimeError("conservative order must be 1 or 2")

        if self.on_gpu:
            create_xgrid_2dx2d_order1 = pyfrenctools.create_xgrid.get_2dx2d_order1_gpu
        else:
            create_xgrid_2dx2d_order1 = pyfrenctools.create_xgrid.get_2dx2d_order1

        for tgt_tile in self.tgt_grid:

            self.datadict[tgt_tile], itile = {}, 1

            itgt_mask = None if tgt_mask is None else tgt_mask[tgt_tile]
            
            for src_tile in self.src_grid:

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
                if nxcells > 0:
                    xgrid_out["tile"] = np.full(nxcells, itile, dtype=np.int32)
                    self.datadict[tgt_tile][src_tile] = xgrid_out
                itile = itile + 1


    def to_dataset(self):

        if self.datadict is None: raise RunTimeError("datadict is None")

        for tgt_tile in self.datadict:
            for src_tile in self.datadict[tgt_tile]:
                src_i = xr.DataArray(self.datadict[tgt_tile][src_tile]["src_i"], dims=["nxcells"],
                                     attrs={"src_i": "parent longitudonal (x) cell indices in src_mosaic"})
                src_j = xr.DataArray(self.datadict[tgt_tile][src_tile]["src_j"], dims=["nxcells"],
                                     attrs={"src_j": "parent latitudonal (y) cell indices in src_mosaic"})
                tgt_i = xr.DataArray(self.datadict[tgt_tile][src_tile]["tgt_i"], dims=["nxcells"],
                                     attrs={"src_i": "parent longitudonal (x) cell indices in src_mosaic"})
                tgt_j = xr.DataArray(self.datadict[tgt_tile][src_tile]["tgt_j"], dims=["nxcells"],
                                     attrs={"src_j": "parent latitudonal (y) cell indices in src_mosaic"})
                xarea = xr.DataArray(self.datadict[tgt_i][src_i]["xarea"], dims=["nxcells"],
                                     attrs={"xarea":"exchange grid cell area (m2)"})

                self.dataset[tgt_tile][src_tile] = xr.DataSet(data_vars={"src_i": src_i,
                                                                         "src_j": src_j,
                                                                         "tgt_i": tgt_i,
                                                                         "tgt_j": tgt_j,
                                                                         "xarea": xarea})

    def _check_restart_remap_file(self):
        if self.restart_remap_file is not None :
            check_file_is_there(self.restart_remap_file)
            self.read()
            return True
        return False


    def _check_grid(self, checkgrid):
        return False if checkgrid is None else True


    def _check_mosaic(self, checkmosaic):
        return False if checkmosaic is None else True


    def _check_mosaic_file(self, checkfile, checkgrid):
        if checkfile is not None:
            if checkgrid == "src":
                self.src_grid = MosaicObj(self.input_dir,
                                 self.src_mosaic_file).read().get_grid(toradians=True,
                                                                       agrid=self.on_agrid,
                                                                       free_dataset=True)
                return False if self.src_grid is None else True
            elif checkgrid == "tgt":
                self.tgt_grid = MosaicObj(self.input_dir,
                                 self.tgt_mosaic_file).read().get_grid(toradians=True,
                                                                       agrid=self.on_agrid,
                                                                       free_dataset=True)
                return False if self.tgt_grid is None else True
            return False