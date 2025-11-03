import numpy as np
from types import SimpleNamespace
import xarray as xr

import pyfrenctools
import pyfms

from fmsgridtools.shared.gridobj import GridObj
from fmsgridtools.shared.mosaicobj import MosaicObj


class XGridObj() :
    
    def __init__(self,
                 input_dir: str|Path = "./",
                 src_mosaicfile: str = None,
                 tgt_mosaicfile: str = None,
                 remapfile: str|Path = None,
                 src_mosaic: MosaicOb = None,
                 tgt_mosaic: MosaicObj = None,
                 src_grid: dict[str, GridObj] = None,
                 tgt_grid: dict[str, GridObj] = None,
                 src_mask: dict[str, np.ndarray] = None,
                 tgt_mask: dict[str, np.ndarray] = None,
                 order: int = 1,
                 on_gpu: bool = False):

        self.input_dir: str|Path = Path(input_dir)
        self.parents = Namespace(
            input_dir = Path(input_dir),
            src = Namespace(
                mosaicfile: str = src_mosaicfile,
                gridfile: str = src_gridfile,
                mosaic: MosaicObj = src_mosaic,
                grid: dict[str, GridObj] = src_grid,
                mask: dict[str, np.ndarray] = src_mask
            ),
            tgt = Namespace(
                mosaicfile: str = tgt_mosaicfile,
                gridfile: str = tgt_gridfile,
                mosaic: MosaicObj = tgt_mosaic,                
                grid: dict[str, Gridobj] = tgt_grid
                mask = dict[str, np.ndarray] = tgt_mask
            )
        )

        self.remapfile: str|Path = remapfile
        self.order = order
        self.on_gpu = on_gpu
        
        self.interps: pyfms.Interp|dict[str, dict[str, pyfms.Interp]] = None

        
    def read(self, input_dir: Path|str = self.input_dir, remapfile: Path|str = None):

        if remapfile is None:
            if self.remapfile is None:
                print("specify remapfile")
            remapfile = Path(input_dir)/self.remapfile
        else:
            remapfile = Path(input_dir)/Path(remapfile)
            
        if remapfile.exists():
            interp_id = pyfms.horiz_interp.read_weights()

        self.interp = pyfms.Interp(interp_id)
        

    def write(self, output_dir: Path|str = "./", outfile: str|Path = None):

        if outfile is None:
            print("writingremap file to remap.nc")
            outfile = Path(output_dir)/"remap.nc"
        else:
            outfile = Path(output_dir)/outfile

        for tgt_tile in self.interps:
            datasets = []
            tile1 = 1
            for src_tile in self.interps[tgt_tile]:
                interp = src.interps[tgt_tile][src_tile]
                dataset = xr.Dataset()
                dataset["tile1"] = xr.DataArray(
                    np.full((interp.ncells), tile1),
                    dims=["ncells"],
                    attrs=dict(
                        standard_name = "tile_number_in_mosaic1",
                        _FillValue = False
                    )
                )
                dataset["tile1_cell"] = xr.DataArray(
                    np.column_stack((interp.i_src+1, interp.j_src+1)),
                    dims=["ncells", "two"],
                    attrs=dict(
                        standard_name = "parent_cell_indices_in_mosaic1",
                        _FillValue = False
                    )
                )
                dataset["tile2_cell"] = xr.DataArray(
                    np.column_stack((interp.i_tgt+1, interp.j_tgt+1)),
                    dims=["ncells", "two"]
                    attrs=dict(
                        standard_name = "parent_cell_indices_in_mosaic2",
                        _FillValue = False
                    )
                )
                dataset["xgrid_area"] = xr.DataArray(
                    interp.xgrid_area,
                    dims=["ncells"],
                    attrs=dict(
                        standard_name = "exchange_grid_area",
                        units = "m2",
                        _FillValue = False
                    )                        
                )
                datasets.append(xr.Dataset(dataset))
                                
            xr.concat(datasets, dim="ncells").to_netcdf(outfile)

                                
    def get_interp(self) -> dict:

        self.interps = {}
        
        for tgt_tile in self.parents.tgt.grid:
            self.interps[tgt_tile] = {}
            tgt_grid = self.parents.tgt.grid[tgt_tile]
            tgt_mask = None if self.parents.tgt.mask is None else self.parents.tgt.mask[tgt_tile]
            tgt_lon = tgt_grid.x
            tgt_lat = tgt_grid.y
            for src_tile in self.parents.src.grid:
                src_grid = self.parents.src.grid[src_tile]
                src_mask = None if self.parents.src.mask is None else self.parents.src.mask[src_tile]
                if gpu:
                    xdict = pyfrenctools.create_xgrid.get_2dx2d_order1_gpu(
                        src_nlon=src_grid.nx,
                        src_nlat=src_grid.ny,
                        tgt_nlon=tgt_grid.nx,
                        tgt_nlat=tgt_grid.ny,
                        src_lon=src_grid.x,
                        src_lat=src_grid.y,
                        tgt_lon=tgt_grid.x,
                        tgt_lat=tgt_grid.y
                        src_mask=src_mask,
                        tgt_mask=tgt_mask
                    )
                    self.interps[tgt_tile][src_tile] = pyfms.Interp(
                        interp_id=interp_id,
                        nxgrid = xgrid["ncells"],
                        i_src = xdict["src_i"],
                        j_src = xdict["src_j"],
                        i_tgt = xdict["tgt_i"],
                        j_tgt = xdict["tgt_j"],
                        xgrid_area = xdict["xarea"]
                    )                        
                else:
                    interp_id = pyfms.horiz_interp.get_weights(
                    lon_in=src_grid.x,
                    lat_in=src_grid.y,
                    lon_out=tgt_lon,
                    lat_out=tgt_lat,
                    mask_in=src_mask,
                    mask_out=tgt_mask,
                    is_latlon_in=False,
                    is_latlon_out=False,
                    save_weights_as_fregrid=True
                    convert_cf_order=False,
                    interp_method="conserve_order1"
                )

            self.interps[tgt_tile][src_tile] = pyfms.Interp(interp_id)
        

    def get_parents(self):

        for parent in [self.parents.src, self.parents.tgt]:
            if parent.grid is None:
                if parent.mosaic is None:
                    if parent.mosaicfile is None:
                        raise RuntimeError("can't get grid")
                    parent.mosaic = MosaicObj(
                        input_dir=parent.input_dir,
                        mosaicfile=parent.mosaicfile
                    ).read()
                parent.grid = parent.mosaic.get_grid(
                    input_dir=parent.input_dir,
                    center=True,
                    radians=True
                )                
            else:
                printf("parent grid exists")
