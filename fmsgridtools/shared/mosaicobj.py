"""
MosaicObj class
"""

import logging
from pathlib import Path

import numpy as np
import xarray as xr

import pyfms
from fmsgridtools.shared.gridobj import GridObj

logger = logging.getLogger(__name__)

attrs = dict(
    mosaic=dict(
        standard_name="grid_mosaic_spec",
        contact_regions="contacts",
        children="gridtiles",
        grid_descriptor="",
        _FillValue=False,
    ),
    gridlocation=dict(standard_name="grid_file_location", _FillValue=False),
    gridfiles=dict(),
    gridtiles=dict(),
    contacts=dict(
        standard_name="grid_contact_spec",
        contact_type="boundary",
        alignment="true",
        contact_index="contact_index",
        orientation="orient",
        _FillValue=False,
    ),
    contact_index=dict(
        standard_name="starting_ending_point_index_of_contact", _FillValue=False
    ),
)

dims = dict(
    mosaic=(),
    gridlocation=(),
    gridfiles=["ntiles"],
    gridtiles=["ntiles"],
    contacts=["ncontact"],
    contact_index=["ncontact"],
)


class Variable:

    def __init__(self, name: str = None, data=None):
        self.name = name
        self.data = data


class MosaicObj:
    """
    MosaicObj
    """

    def __init__(
        self,
        input_dir: str = "./",
        mosaicfile: str = None,
        mosaic: str = None,
        ntiles: int = None,
        gridlocation: str = "./",
        gridfiles: list[str] = None,
        gridtiles: list[str] = None,
        contacts: list[str] = None,
        contact_index: list[str] = None,
    ):

        self.input_dir = Path(input_dir)
        self.mosaicfile = mosaicfile

        self.ntiles = ntiles
        self.ncontacts = None

        self.mosaic_obj = Variable(name="mosaic", data=mosaic)
        self.gridlocation_obj = Variable(name="gridlocation", data=gridlocation)
        self.gridfiles_obj = Variable(name="gridfiles", data=gridfiles)
        self.gridtiles_obj = Variable(name="gridtiles", data=gridtiles)
        self.contacts_obj = Variable(name="contacts", data=contacts)
        self.contact_index_obj = Variable(name="contact_index", data=contact_index)
        self.objlist = [
            self.mosaic_obj,
            self.gridlocation_obj,
            self.gridfiles_obj,
            self.gridtiles_obj,
            self.contacts_obj,
            self.contact_index_obj,
        ]

    def read(self, mosaicfile: str | Path = None, input_dir: str | Path = "."):
        """
        Read the mosaic file
        """

        logger.info("Reading mosaicfile")

        if mosaicfile is None:
            if self.mosaicfile is None:
                logger.error("Please specify mosaic file")
        else:
            self.mosaicfile = mosaicfile

        if str(input_dir) != (self.input_dir):
            logger.warning("Resetting input_dir to %s", input_dir)
            self.input_dir = Path(input_dir)

        with xr.open_dataset(self.input_dir / self.mosaicfile) as ds:

            for obj in self.objlist:
                variable = ds.get(obj.name)
                if variable is not None:
                    if variable.dtype is bytes:
                        variable = variable.str.decode(encoding="utf-8")
                    if isinstance(variable.data, np.ndarray):
                        obj.data = variable.data.tolist()
                    else:
                        obj.data = str(variable.data)
            self.ntiles = ds.sizes.get("ntiles")
            self.ncontacts = ds.sizes.get("ncontact")
            self.input_dir = input_dir

            logger.info(
                "Finished reading file %s\n %s\n", self.mosaicfile, self.__repr__()
            )

        return self

    def from_dict(self, mosaic_dict: dict):
        """
        Generate mosaic file from dictionary
        """

        logger.info("Setting MosaicObj from dict")

        names = [obj.name for obj in self.objlist]
        for key in mosaic_dict:
            if key not in names:
                logger.error(f"{key} not a field in MosaicObj")

        for key in mosaic_dict:
            for obj in self.objlist:
                if obj.name == key:
                    obj.data = mosaic_dict[key]

        self.ntiles = None if self.gridfiles is None else len(self.gridfiles.data)
        self.ncontacts = None if self.contacts is None else len(self.contacts.data)

        logger.info("Finished setting mosaicobj from dict: %s\n", self.__repr__())

        return self

    def get_grid(
        self,
        input_dir: str | Path = "./",
        radians: bool = False,
        domain: pyfms.Domain = None,
    ) -> dict:
        """
        Get grids from gridfiles
        """

        logger.info("Reading in grid")

        if self.gridfiles is None:
            raise RuntimeError("Cannot find gridfiles to read")

        if self.gridtiles is None:
            raise RuntimeError("Cannot find gridtile information")

        if self.ntiles is None:
            ntiles = len(self.gridfiles)

        grid = {}

        for gridfile, gridtile in zip(self.gridfiles, self.gridtiles):
            readfile = Path(input_dir) / gridfile
            grid[gridtile] = GridObj(gridfile=readfile).read(
                radians=radians,
                domain=domain,
                on_domain=False if domain is None else True,
                xy_only=True,
            )

        logger.info("Finished reading in grid %s\n", grid)

        return grid

    def write(self, mosaicfile: str = None) -> None:
        """
        write mosaic file
        """

        if mosaicfile is None:
            if self.mosaicfile is None:
                raise RuntimeError("need to specify mosaic filename")
            else:
                mosaicfile = self.mosaicfile

        logger.info("Writing out mosaicfile %s\n", mosaicfile)

        ds = {}

        for obj in self.objlist:
            if obj.data is not None:
                name = obj.name
                ds[name] = xr.DataArray(
                    data=obj.data, attrs=attrs[name], dims=dims[name]
                )

        xr.Dataset(data_vars=ds).to_netcdf(mosaicfile)

    @property
    def mosaic(self):
        """
        retrieve mosaic
        """

        return self.mosaic_obj.data

    @mosaic.setter
    def mosaic(self, data):
        """
        set mosaic data
        """

        self.mosaic_obj.data = data

    @property
    def gridlocation(self):
        """
        retrieve gridlocation
        """

        return self.gridlocation_obj.data

    @gridlocation.setter
    def gridlocation(self, data):
        """
        set gridlocation data
        """

        self.gridlocation_obj.data = data

    @property
    def gridtiles(self):
        """
        retrieve gridtiles
        """

        return self.gridtiles_obj.data

    @gridtiles.setter
    def gridtiles(self, data):
        """
        set gridtiles data
        """

        self.gridtiles_obj.data = data

    @property
    def gridfiles(self):
        """
        retrieve gridfiles
        """

        return self.gridfiles_obj.data

    @gridfiles.setter
    def gridfiles(self, data):
        """
        set gridfiles data
        """

        self.gridfiles_obj.data = data

    @property
    def contacts(self):
        """
        retrieve contacts
        """

        return self.contacts_obj.data

    @contacts.setter
    def contacts(self, data):
        """
        set contacts data
        """

        self.contacts_obj.data = data

    @property
    def contact_index(self):
        """
        retrieve contact_index
        """

        return self.contact_index_obj.data

    @contact_index.setter
    def contact_index(self, data):
        """
        set contact_index data
        """

        self.contact_index_obj.data = data

    def __repr__(self):
        summary = "%s\n" % (self.__class__.__name__)
        summary += "ntiles = %s\n" % (self.ntiles)
        summary += "ncontacts = %s\n" % (self.ncontacts)

        for obj in self.objlist:
            summary += "%s = %s\n" % (obj.name, obj.data)

        return summary
