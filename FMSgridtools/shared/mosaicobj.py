from typing import Optional, Dict
from dataclasses import dataclass,field
import xarray as xr
import numpy as np
import numpy.typing as npt
from gridtools.shared import GridObj
from gridtools.shared.gridtools_utils import check_file_is_there

@dataclass
class MosaicObj:
    mosaic_file: str = None
    output_file: str = None
    ntiles: int = None
    ncontact: int = None
    mosaic_name: str = None
    gridlocation: str = None
    gridfiles: npt.NDArray[np.str_] = None
    gridtiles: npt.NDArray[np.str_] = None
    contacts: npt.NDArray[np.str_] = None
    contact_index: npt.NDArray[np.str_] = None
    dataset: object = field(init=False) 
    grid_dict: Optional[Dict] | None = field(default_factory=dict)

    def __post_init__(self):
        if self.mosaic_file is not None and self.gridfiles is None:
            check_file_is_there(self.mosaic_file)
            self.dataset = xr.open_dataset(self.mosaic_file)

            self.gridfiles = self.get_gridfiles()

    def get_gridfiles(self):
        try:
            return [ifile.decode('ascii') for ifile in self.dataset.gridfiles.values]
        except AttributeError:
                print("Error: Mosaic file not provided as an attribute, unable to return gridfiles")

    def get_ntiles(self):
        try:
            return  self.dataset.sizes['ntiles']
        except AttributeError:
            print("Error: Mosaic file not provided as an attribute, unable to return number of tiles")

    def griddict(self):
        gridtiles = [tile.decode('ascii') for tile in self.dataset.gridtiles.values]
        for i in range(self.get_ntiles()):
            self.grid_dict[gridtiles[i]] = GridObj.from_file(self.gridfiles[i])

    def write_out_mosaic(self):

        mosaic = xr.DataArray(
                [self.mosaic_name],
                attrs=dict(standard_name="grid_mosaic_spec", contact_regions="contacts",
                        children="gridtiles", grid_descriptor=""))

        gridlocation = xr.DataArray(
                    [self.gridlocation], attrs=dict(standard_name="grid_file_location"))

        gridfiles = xr.DataArray(
                    data=self.gridfiles, dims=["ntiles"])

        gridtiles = xr.DataArray(
                    data=self.gridtiles, dims=["ntiles"])

        contacts = xr.DataArray(
                   data=self.contacts, dims=["ncontact"],
                            attrs=dict(standard_name="grid_contact_spec", contact_type="boundary",
                                alignment="true", contact_index="contact_index", orientation="orient"))

        contact_index = xr.DataArray(
                        data=self.contact_index, dims=["ncontact"],
                            attrs=dict(standard_name="starting_ending_point_index_of_contact"))

        out = xr.Dataset(
            data_vars={"mosaic": mosaic,
                        "gridlocation": gridlocation,
                        "gridfiles": gridfiles,
                        "gridtiles": gridtiles,
                        "contacts": contacts,
                        "contact_index": contact_index})

        out.to_netcdf(self.output_file)

