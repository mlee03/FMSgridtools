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
                )
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
        tgt_tile: str = "tile1",
        src_mask: dict[str, np.ndarray] = None,
        tgt_mask: dict[str, np.ndarray] = None,
        order: int = 1,
        domain: pyfms.Domain = None,
        on_gpu: bool = False,
    ):
        """Create an XGridObj container for building/reading remap/interp data.

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

        self.remapfile: str | Path = remapfile
        self.order = order
        self.on_gpu = on_gpu

        self.interps: pyfms.ConserveInterp | dict[str, pyfms.ConserveInterp] = None

    def read(
        self,
        input_dir: Path | str = None,
        remapfile: Path | str = None,
        domain: pyfms.Domain = None,
    ):
        """
        read remap file and store as pyfms.ConserveInterp objects
        """

        if input_dir is None:
            input_dir = self.input_dir
        input_dir = Path(input_dir)

        if remapfile is None:
            if self.remapfile is None:
                logger.error("Please specify remapfile to read")
            remapfile = self.remapfile
        remapfile = input_dir / Path(remapfile)

        if not remapfile.exists():
            logger.error("remap file %s does not exist", self.remapfile)

        itile = 1
        self.interps = {}
        for src_tile in self.src.grid:
            interp_id = pyfms.horiz_interp.read_weights_conserve(
                weight_filename=str(remapfile),
                weight_file_src="fregrid",
                nlon_src=self.src.grid[src_tile].nx,
                nlat_src=self.src.grid[src_tile].ny,
                nlon_tgt=self.tgt.grid.nx,
                nlat_tgt=self.tgt.grid.ny,
                domain=domain,
                src_tile=itile,
                save_weights_as_fregrid=True,
            )
            self.interps[src_tile] = pyfms.ConserveInterp(
                interp_id, weights_as_fregrid=True
            )
            itile += 1

    def write(self, output_dir: Path | str = "./", outfile: str | Path = None):
        """
        write remap file
        """

        is_root_pe = pyfms.mpp.pe() == pyfms.mpp.root_pe()

        if self.tgt.domain is None:
            i_src = {itile: self.interps[itile].i_src for itile in self.interps}
            j_src = {itile: self.interps[itile].j_src for itile in self.interps}
            i_dst = {itile: self.interps[itile].i_dst for itile in self.interps}
            j_dst = {itile: self.interps[itile].j_dst for itile in self.interps}
            xgrid_area = {
                itile: self.interps[itile].xgrid_area for itile in self.interps
            }
        else:
            i_src, j_src, i_dst, j_dst, xgrid_area = {}, {}, {}, {}, {}
            for src_tile in self.interps:
                interp = self.interps[src_tile]
                nxgrids = pyfms.mpp.gather(np.array([interp.nxgrid], dtype=np.int32))
                i_src[src_tile] = pyfms.mpp.gather(
                    interp.i_src, ssize=interp.nxgrid, rsize=nxgrids
                )
                j_src[src_tile] = pyfms.mpp.gather(
                    interp.j_src, ssize=interp.nxgrid, rsize=nxgrids
                )
                i_dst[src_tile] = pyfms.mpp.gather(
                    interp.i_dst, ssize=interp.nxgrid, rsize=nxgrids
                )
                j_dst[src_tile] = pyfms.mpp.gather(
                    interp.j_dst, ssize=interp.nxgrid, rsize=nxgrids
                )
                xgrid_area[src_tile] = pyfms.mpp.gather(
                    interp.xgrid_area, ssize=interp.nxgrid, rsize=nxgrids
                )

        if pyfms.mpp.pe() == pyfms.mpp.root_pe():

            if outfile is None:
                print("writing remap file to remap.nc")
                outfile = Path(output_dir) / "remap.nc"
            else:
                outfile = Path(output_dir) / outfile

            datasets, tile1 = [], 1
            for src_tile in self.interps:
                nxgrid = i_src[src_tile].size
                dataset = xr.Dataset()
                dataset["tile1"] = xr.DataArray(
                    np.full(nxgrid, tile1),
                    dims=["ncells"],
                    attrs={"standard_name": "tile_number_in_mosaic1"},
                )
                tile1 += 1
                dataset["tile1_cell"] = xr.DataArray(
                    np.column_stack((i_src[src_tile] + 1, j_src[src_tile] + 1)),
                    dims=["ncells", "two"],
                    attrs={"standard_name": "parent_cell_indices_in_mosaic1"},
                )
                dataset["tile2_cell"] = xr.DataArray(
                    np.column_stack((i_dst[src_tile] + 1, j_dst[src_tile] + 1)),
                    dims=["ncells", "two"],
                    attrs={"standard_name": "parent_cell_indices_in_mosaic2"},
                )
                dataset["xgrid_area"] = xr.DataArray(
                    xgrid_area[src_tile],
                    dims=["ncells"],
                    attrs={"standard_name": "exchange_grid_area", "units": "m2"},
                )
                datasets.append(xr.Dataset(dataset))

            dataset = xr.concat(datasets, dim="ncells")
            encoding = {variable: {"_FillValue": None} for variable in dataset}
            dataset.to_netcdf(outfile, encoding=encoding)

        pyfms.mpp.sync()

    def get_interp(self) -> dict:

        self.interps = {}

        for src_tile in self.src.grid:
            src_grid = self.src.grid[src_tile]
            src_mask = None if self.src.mask is None else self.src.mask[src_tile]
            if self.on_gpu:
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
                interp.nxgrid = (xdict["ncells"],)
                interp.i_src = (xdict["src_i"],)
                interp.j_src = (xdict["src_j"],)
                interp.i_tgt = (xdict["tgt_i"],)
                interp.j_tgt = (xdict["tgt_j"],)
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
                    save_weights_as_fregrid=True,
                    convert_cf_order=False,
                    interp_method="conservative",
                )
                self.interps[src_tile] = pyfms.ConserveInterp(
                    interp_id, weights_as_fregrid=True
                )

    def get_parents(self):

        input_dir = self.input_dir
        for parent in [self.src, self.tgt]:
            if parent.grid is None:
                if parent.mosaic is None:
                    if parent.mosaicfile is None:
                        raise RuntimeError("can't get grid")
                    parent.mosaic = MosaicObj(
                        input_dir=input_dir, mosaicfile=parent.mosaicfile
                    ).read()
                parent.grid = parent.mosaic.get_grid(
                    input_dir=input_dir, center=True, radians=True, domain=parent.domain
                )
            else:
                print("parent grid exists")

        self.tgt.grid = self.tgt.grid[self.tgt.tile]
        self.src.ntiles = len(self.src.grid)
