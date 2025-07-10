
from typing import Optional, Dict, List, Any
import xarray as xr
from fmsgridtools.shared.gridobj import GridObj
from fmsgridtools.shared.gridtools_utils import check_file_is_there


class MosaicObj:

    def __init__(self, input_dir: str = "./",
                 mosaic_file: str = None,
                 ntiles: int = None,
                 mosaic_name: str = None,
                 gridlocation: str = None,
                 gridfiles: list[str] = None,
                 gridtiles: list[str] = None,
                 contacts: list[str] = None,
                 contact_index: list[str] = None,
                 dataset: type[xr.Dataset] = None,
                 grid: dict = None):

        self.input_dir = input_dir+"/"
        self.mosaic_file = mosaic_file
        self.ntiles = ntiles
        self.mosaic_name = mosaic_name
        self.gridlocation = gridlocation
        self.gridfiles = gridfiles
        self.gridtiles = gridtiles
        self.contacts = contacts
        self.contact_index = contact_index
        self.dataset = dataset
        self.grid = grid
        for key, value in self.__dict__.items():
            if key == 'gridfiles' or 'gridtiles' or 'contacts' or 'contact_index':
                if value is None:
                    self.__dict__[key] = []
            if key == 'grid':
                if value is None:
                    self.__dict__[key] = {}


    def read(self):

        if self.mosaic_file is None:
            raise IOError("Please specify mosaic_file")

        check_file_is_there(self.input_dir+self.mosaic_file)
        self.dataset = xr.open_dataset(self.input_dir+self.mosaic_file)

        self.get_attributes()
        return self

    
    def get_attributes(self) -> None:
        for key in self.dataset.data_vars:
            setattr(self, key, self.dataset[key].astype(str).values)

        for key in self.dataset.sizes:
            setattr(self, key, self.dataset.sizes[key])

            
    def add_attributes(self, attribute: str, value: Any = None) -> None:

        setattr(self, attribute, value)

        
    def get_grid(self, toradians: bool = False, agrid: bool = False, free_dataset: bool = False) -> dict:

        for i in range(self.ntiles):
            gridfile = str(self.input_dir) + str(self.gridlocation+self.gridfiles[i])
            self.grid[self.gridtiles[i]] = GridObj(gridfile=gridfile).read(toradians=toradians,
                                                                           agrid=agrid,
                                                                           free_dataset=free_dataset)
            
        return self.grid

    
    def write(self, outfile: str = None) -> None:

        dataset = {}
        if self.mosaic_name is not None:
            dataset["mosaic"] = xr.DataArray(
                data=self.mosaic_name.encode(),
                attrs=dict(
                    standard_name="grid_mosaic_spec",
                    contact_regions="contacts",
                    children="gridtiles",
                    grid_descriptor=""
                )
            )

        if self.gridlocation is not None:
            dataset["gridlocation"] =  xr.DataArray(
                data=self.gridlocation,
                attrs=dict(
                    standard_name="grid_file_location"
                )
            )

        if self.gridfiles is not None:
            dataset["gridfiles"] = xr.DataArray(
                data=self.gridfiles, dims=["ntiles"]
            )

        if self.gridtiles is not None:
            dataset["gridtiles"] = xr.DataArray(
                data=self.gridtiles, dims=["ntiles"]
            )

        if self.contacts is not None:
            dataset["contacts"] = xr.DataArray(
                data=self.contacts, dims=["ncontact"],
                attrs=dict(
                    standard_name="grid_contact_spec",
                    contact_type="boundary",
                    alignment="true", contact_index="contact_index",
                    orientation="orient"
                )
            )

        if self.contact_index is not None:
            dataset["contact_index"] = xr.DataArray(
                data=self.contact_index, dims=["ncontact"],
                attrs=dict(
                    standard_name="starting_ending_point_index_of_contact"
                )
            )

        xr.Dataset(data_vars=dataset).to_netcdf(outfile)

