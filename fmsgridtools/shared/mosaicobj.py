import numpy as np
from pathlib import Path
from types import SimpleNamespace
import xarray as xr

from fmsgridtools.shared.gridobj import GridObj

attrs = dict(
    mosaic = dict(
        standard_name="grid_mosaic_spec",
        contact_regions="contacts",
        children="gridtiles",
        grid_descriptor=""
    ),
    gridlocation = dict(
        standard_name="grid_file_location"
    ),
    gridfiles = dict(),
    gridtiles = dict(),
    contacts = dict(
        standard_name="grid_contact_spec",
        contact_type="boundary",
        alignment="true",
        contact_index="contact_index",
        orientation="orient"
    ),
    contact_index = dict(
        standard_name="starting_ending_point_index_of_contact"
    )
)

dims = dict(
    mosaic = (),
    gridlocation = (),
    gridfiles = ["ntiles"],
    gridtiles = ["ntiles"],
    contacts = ["ncontact"],
    contact_index = ["ncontact"]
)


def set_attribute(variable: str, var_attr: dict):

    global attrs
    
    if variable in attrs:
        attrs[variable] = var_attr
    else:
        raise RuntimeError(f"{variable} does not exist in attributes")

    
def set_dims(variable: str, var_dim: list):

    global dims

    if variable in dims:
        dims[variable] = var_dim
    else:
        raise RuntimeError(f"{variable} does not exist in dims")    


class MosaicObj:

    def __init__(self,
                 input_dir: str = "./",
                 mosaicfile: str = None,
                 mosaic: str = None,
                 ntiles: int = None,
                 gridlocation: str = "./",
                 gridfiles: list[str] = None,
                 gridtiles: list[str] = None,
                 contacts: list[str] = None,
                 contact_index: list[str] = None,
                 grid: dict = None):

        self.input_dir = Path(input_dir)
        self.mosaicfile = mosaicfile

        self.ntiles = ntiles
        
        self.mosaic_obj = SimpleNamespace(
            name = "mosaic",
            data = mosaic
        )
        self.gridlocation_obj = SimpleNamespace(
            name = "gridlocation",
            data = gridlocation
        )
        self.gridfiles_obj = SimpleNamespace(
            name = "gridfiles",
            data = gridfiles
        )
        self.gridtiles_obj = SimpleNamespace(
            name = "gridtiles",
            data = gridtiles
        )
        self.contacts_obj = SimpleNamespace(
            name = "contacts",
            data = contacts
        )
        self.contact_index_obj = SimpleNamespace(
            name = "contact_index",
            data = contact_index
        )

        self.objlist = [
            self.mosaic_obj,
            self.gridlocation_obj,
            self.gridfiles_obj,
            self.gridtiles_obj,
            self.contacts_obj,
            self.contact_index_obj
        ]


    def read(self, mosaicfile: str|Path = None, input_dir: str|Path = "."):

        if mosaicfile is None:
            if self.mosaicfile is None:
                raise IOError("Please specify the mosaic file")
            else:
                mosaicfile = self.mosaicfile
        
        with xr.open_dataset(Path(self.input_dir)/mosaicfile) as ds:

            for obj in self.objlist:
                variable = ds.get(obj.name)
                if variable is not None:
                    variable = variable.str.decode(encoding="utf-8")
                    if type(variable.data) is np.ndarray:
                        obj.data = variable.data.tolist()
                    else:
                        obj.data = str(variable.data)
            self.ntiles = ds.sizes.get("ntile")
            self.ncontact = ds.sizes.get("ncontact")
            self.input_dir = input_dir
            self.mosaicfile = mosaicfile

        return self

    
    def from_dict(self, mosaic_dict: dict):

        names = [obj.name for obj in self.objlist]
        for key in mosaic_dict:
            if key not in names:
                raise RuntimeError(f"{key} not a field in MosaicObj")            
        
        for key in mosaic_dict:
            for obj in self.objlist:
                if obj.name == key:
                    obj.data = mosaic_dict[key]

        for obj in self.objlist:
            if obj.data is None:
                printf(f"{obj.name} not set")

        self.ntiles = None if self.gridfiles is None else len(self.gridfiles.data)
        self.ncontacts = None if self.contacts is None else len(self.contacts.data)
                
        return self

    
    def get_grid(self, input_dir: str|Path = "./", radians: bool = False, center: bool = False) -> dict:

        if self.gridfiles is None:
            raise RuntimeError("need to set gridfiles")

        if self.gridtiles is None:
            raise RuntimeError("need to set gridtiles")
        
        if self.ntiles is None:
            ntiles = len(self.gridfiles)
                    
        grid = {}
        
        for gridfile, gridtile in zip(self.gridfiles, self.gridtiles):
            readfile = Path(input_dir)/gridfile
            grid[gridtile] = GridObj(gridfile=readfile).read_xy(radians=radians, center=center)

        return grid


    def write(self, mosaicfile: str = None) -> None:

        if mosaicfile is None:
            if self.mosaicfile is None:
                raise RuntimeError("need to specify mosaic filename")
            else:
                mosaicfile = self.mosaicfile
        
        ds = {}

        for obj in self.objlist:
            name = obj.name
            ds[name] = xr.DataArray(
                data=obj.data,
                attrs=attrs[name],
                dims=dims[name]
            )
                    
        xr.Dataset(data_vars=ds).to_netcdf(mosaicfile)


    @property
    def mosaic(self):
        return self.mosaic_obj.data

    @mosaic.setter
    def mosaic(self, data):
        self.mosaic_obj.data = data

    @property
    def gridlocation(self):
        return self.gridlocation_obj.data

    @gridlocation.setter
    def gridlocation(self, data):
        self.gridlocation_obj.data = data

    @property
    def gridtiles(self):
        return self.gridtiles_obj.data

    @gridtiles.setter
    def gridtiles(self, data):
        self.gridtiles_obj.data = data
        
    @property
    def gridfiles(self):
        return self.gridfiles_obj.data

    @gridfiles.setter
    def gridfiles(self, data):
        self.gridfiles_obj.data = data

    @property
    def contacts(self):
        return self.contacts_obj.data

    @contacts.setter
    def contacts(self, data):
        self.contacts_obj.data = data

    @property
    def contact_index(self):
        return self.contact_index_obj.data

    @contact_index.setter
    def contact_index(self, data):
        self.contact_index_obj.data = data
    
