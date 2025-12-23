import logging
from pathlib import Path
import numpy as np
import numpy.typing as npt
import xarray as xr

import pyfrenctools
import pyfms

from fmsgridtools.shared.gridobj import GridObj
from fmsgridtools.shared.mosaicobj import MosaicObj

logger = logging.getLogger(__name__)


class Parent:

    def __init__(
        self,
        parent: str,
        input_dir: str | Path = "./",
        mosaicfile: str | Path = None,
        mosaic: MosaicObj = None,
        gridfile: str | Path = None,
        ntiles: int = None,
        grid: dict[str, GridObj] = None,
        mask: dict[str, npt.NDArray] = None,
        domain: pyfms.Domain = None,
    ):

        self.parent = parent
        self.input_dir = Path(input_dir)
        self.mosaicfile = mosaicfile
        self.mosaic = mosaic
        self.gridfile = gridfile
        self.ntiles = ntiles
        self.grid = grid
        self.mask = mask
        self.domain = domain

        if self.grid is None:
            if self.mosaic is None:
                if self.mosaicfile is None:
                    logger.warning("Cannot set %s grid", self.parent)
                self.mosaic = MosaicObj(
                    input_dir=self.input_dir, mosaicfile=self.mosaicfile
                ).read()
            self.grid = self.mosaic.get_grid(
                input_dir=self.input_dir, center=True, radians=True, domain=self.domain
            )
            logger.info("set grid for %s", self.parent)


class XGridObj:

    def __init__(
        self,
        input_dir: str | Path = "./",
        src_mosaicfile: str = None,
        tgt_mosaicfile: str = None,
        remapfile: str | Path = None,
        src_mosaic: MosaicObj = None,
        tgt_mosaic: MosaicObj = None,
        src_gridfile: str | Path = None,
        tgt_gridfile: str | Path = None,
        src_grid: dict[str, GridObj] = None,
        tgt_grid: dict[str, GridObj] = None,
        tgt_tile: str = None,
        src_mask: dict[str, np.ndarray] = None,
        tgt_mask: dict[str, np.ndarray] = None,
        order: int = 1,
        domain: pyfms.Domain = None,
    ):

        """
        Create an XGridObj container for building/reading remap/interp data.

        Args:
            input_dir (str|Path): Base directory for input files.
            src_mosaicfile (str): Source mosaic filename (optional).
            tgt_mosaicfile (str): Target mosaic filename (optional).
            remapfile (str|Path): Remap weights filename (optional).
            src_mosaic (MosaicObj): Optional pre-built source MosaicObj.
            tgt_mosaic (MosaicObj): Optional pre-built target MosaicObj.
            src_gridfile (str|Path): Source grid filename (optional).
            tgt_gridfile (str|Path): Target grid filename (optional).
            src_grid (dict[str, GridObj]): Optional dict of source GridObj keyed by tile name.
            tgt_grid (dict[str, GridObj]): Optional dict of target GridObj keyed by tile name.
            tgt_tile (str): Name of the target tile to use (default: "tile1").
            src_mask (dict[str, np.ndarray]): Optional masks for source tiles.
            tgt_mask (dict[str, np.ndarray]): Optional masks for the target grid.
            order (int): Interpolation order (currently stored; semantics depend on downstream code).
            on_gpu (bool): If True, use GPU-based building of xgrid via pyfrenctools.

        The constructed object stores container namespaces for source (`self.src`) and
        target (`self.tgt`) data and an `interps` mapping that is populated by
        `read` or `get_interp`.
        """

        self.input_dir: str | Path = Path(input_dir)
        self.src = Parent(
            parent="src",
            input_dir=input_dir,
            mosaicfile=src_mosaicfile,
            gridfile=src_gridfile,
            mosaic=src_mosaic,
            grid=src_grid,
            mask=src_mask,
            domain=None,
        )
        self.tgt = Parent(
            parent="tgt",
            mosaicfile=tgt_mosaicfile,
            gridfile=tgt_gridfile,
            mosaic=tgt_mosaic,
            grid=tgt_grid,
            mask=tgt_mask,
            domain=domain,
        )

        self.tgt_tile = tgt_tile
        if self.tgt_tile is not None:
            self.tgt.grid = self.tgt.grid[tgt_tile]

        self.remapfile: str | Path = remapfile
        self.order = order

        self.interps: pyfms.ConserveInterp | dict[str, pyfms.ConserveInterp] = None


    def set_target_tile(self, tgt_tile: str = "tile1"):
        self.tgt_tile = tgt_tile
        self.tgt.grid = self.tgt.grid[tgt_tile]        

        
    def read(
        self,
        input_dir: Path | str = None,
        remapfile: Path | str = None,
        domain: pyfms.Domain = None,
    ):

        """
        read remap file and store as pyfms.ConserveInterp objects
        """

        input_dir = self.input_dir if input_dir is None else Path(input_dir)

        if remapfile is None:
            if self.remapfile is None:
                logger.error("Please specify remapfile to read")
            remapfile = self.remapfile
        remapfile = input_dir / Path(remapfile)

        if not remapfile.exists():
            logger.error("remap file %s does not exist", self.remapfile)

        if domain is None:
            domain = self.tgt.domain

        self.interps = {}
        for itile, src_tile in enumerate(self.src.grid):
            interp_id = pyfms.horiz_interp.read_weights_conserve(
                weight_filename=str(remapfile),
                weight_file_src="fregrid",
                nlon_src=self.src.grid[src_tile].nx,
                nlat_src=self.src.grid[src_tile].ny,
                nlon_tgt=self.tgt.grid.nx,
                nlat_tgt=self.tgt.grid.ny,
                domain=domain,
                src_tile=itile,
                save_xgrid_area=True,
            )
            self.interps[src_tile] = pyfms.ConserveInterp(interp_id, save_xgrid_area=True)


    def gather(self):

        """
        gathers xgrid 
        """

        isc, jsc = self.tgt.domain.isc, self.tgt.domain.jsc

        global_interps = {}
        for src_tile in self.interps:
            interp = self.interps[src_tile]
            global_interp = global_interps[src_tile] = pyfms.ConserveInterp()
            nxgrids = pyfms.mpp.gather(np.array([interp.nxgrid], dtype=np.int32), rbuf_size=len(self.interps))
            global_interp.nxgrid = np.sum(nxgrids) if pyfms.mpp.pe() == pyfms.mpp.root_pe() else None
            global_interp.i_src = pyfms.mpp.gatherv(interp.i_src, ssize=interp.nxgrid, rsize=nxgrids)
            global_interp.j_src = pyfms.mpp.gatherv(interp.j_src, ssize=interp.nxgrid, rsize=nxgrids)
            global_interp.i_dst = pyfms.mpp.gatherv(interp.i_dst + isc, ssize=interp.nxgrid, rsize=nxgrids)
            global_interp.j_dst = pyfms.mpp.gatherv(interp.j_dst + jsc, ssize=interp.nxgrid, rsize=nxgrids)
            global_interp.xgrid_area = pyfms.mpp.gatherv(interp.xgrid_area, ssize=interp.nxgrid, rsize=nxgrids)
        return global_interps


    def write(self, output_dir: Path | str = "./", outfile: str | Path = Path("remap.nc")):
        """
        write remap file
        """

        global_interps = self.interps if self.tgt.domain is None else self.gather()

        if pyfms.mpp.pe() == pyfms.mpp.root_pe():

            outfile = Path(output_dir) / outfile
            logger.info("writing remap file to %s", outfile)

            datasets = []
            for tile1, src_tile in enumerate(global_interps):
                
                interp = global_interps[src_tile]
                dataset = xr.Dataset()

                dataset["tile1"] = xr.DataArray(
                    np.full(interp.nxgrid, tile1),
                    dims=["ncells"],
                    attrs={"standard_name": "tile_number_in_mosaic1"},
                )
                dataset["tile1_cell"] = xr.DataArray(
                    np.column_stack((interp.i_src + 1, interp.j_src + 1)),
                    dims=["ncells", "two"],
                    attrs={"standard_name": "parent_cell_indices_in_mosaic1"},
                )
                dataset["tile2_cell"] = xr.DataArray(
                    np.column_stack((interp.i_dst + 1, interp.j_dst + 1)),
                    dims=["ncells", "two"],
                    attrs={"standard_name": "parent_cell_indices_in_mosaic2"},
                )
                dataset["xgrid_area"] = xr.DataArray(
                    interp.xgrid_area,
                    dims=["ncells"],
                    attrs={"standard_name": "exchange_grid_area", "units": "m2"},
                )
                datasets.append(xr.Dataset(dataset))

            dataset = xr.concat(datasets, dim="ncells")
            encoding = {variable: {"_FillValue": None} for variable in dataset}
            dataset.to_netcdf(outfile, encoding=encoding)

        pyfms.mpp.sync()


    def get_interp(self, on_gpu) -> dict:

        """
        call fms to compute xgrid
        """

        self.interps = {}

        for src_tile in self.src.grid:
            src_grid = self.src.grid[src_tile]
            src_mask = None if self.src.mask is None else self.src.mask[src_tile]
            if on_gpu:
                xdict = pyfrenctools.create_xgrid.get_2dx2d_order1_gpu(
                    src_nlon=src_grid.nx,
                    src_nlat=src_grid.ny,
                    tgt_nlon=self.tgt.grid.nx,
                    tgt_nlat=self.tgt.grid.ny,
                    src_lon=src_grid.x,
                    src_lat=src_grid.y,
                    tgt_lon=self.tgt.grid.x,
                    tgt_lat=self.tgt.grid.y,
                    src_mask=src_mask,
                    tgt_mask=self.tgt.mask,
                )
                interp = pyfms.ConserveInterp()
                interp.nxgrid = xdict["nxcells"]
                interp.i_src = xdict["src_i"]
                interp.j_src = xdict["src_j"]
                interp.i_dst = xdict["tgt_i"]
                interp.j_dst = xdict["tgt_j"]
                interp.xgrid_area = xdict["xarea"]
                self.interps[src_tile] = interp
            else:
                interp_id = pyfms.horiz_interp.get_weights(
                    lon_in=src_grid.x,
                    lat_in=src_grid.y,
                    lon_out=self.tgt.grid.x,
                    lat_out=self.tgt.grid.y,
                    mask_in=src_mask,
                    mask_out=self.tgt.mask,
                    is_latlon_in=False,
                    is_latlon_out=False,
                    save_xgrid_area=True,
                    convert_cf_order=False,
                    as_fregrid=True,
                    interp_method="conservative",
                )
                self.interps[src_tile] = pyfms.ConserveInterp(interp_id, save_xgrid_area=True)
