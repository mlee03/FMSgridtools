import xarray as xr
import numpy as np
import numpy.typing as npt
from FMSgridtools.shared.gridobj import GridObj
from FMSgridtools.shared.gridtools_utils import check_file_is_there


class MosaicObj:
    def __init__(self, mosaic_file: str = None,
                 ntiles: int = None, 
                 mosaic_name : str = None,
                 gridlocation: str = None, 
                 gridfiles: npt.NDArray[np.str_] = None,
                 gridtiles: npt.NDArray[np.str_] = None,
                 contacts: npt.NDArray[np.str_] = None,
                 contact_index: npt.NDArray[np.str_] = None,
                 dataset: object = None,
                 grid_dict: dict | None = None):

        self.mosaic_file = mosaic_file
        self.ntiles = ntiles
        self.mosaic_name = mosaic_name 
        self.gridlocation = gridlocation
        self.gridfiles = gridfiles
        self.gridtiles = gridtiles
        self.contacts = contacts
        self.contact_index = contact_index
        self.grid_dict = {}
        self._post_init_()

        
    def _post_init_(self):
        if self.mosaic_file is not None and self.gridfiles is None:
            check_file_is_there(self.mosaic_file)
            self.dataset = xr.open_dataset(self.mosaic_file)
            self.gridfiles = self.get_gridfiles()

    def get_gridfiles(self) -> list:
        try:
            return [ifile.decode('ascii') for
                    ifile in self.dataset.gridfiles.values]
        except AttributeError:
                print("Error: Mosaic file not provided as an attribute, \
                    unable to return gridfiles")

    def get_ntiles(self) -> list:
        try:
            return  self.dataset.sizes['ntiles']
        except AttributeError:
            print("Error: Mosaic file not provided as an attribute, \
                  unable to return number of tiles")

    def griddict(self) -> dict:
        if self.gridtiles is None:
            gridtiles = [tile.decode('ascii') for
                         tile in self.dataset.gridtiles.values]
            for i in range(self.get_ntiles()):
                self.grid_dict[
                    gridtiles[i]] = GridObj.from_file(self.gridfiles[i])
        else:
            for i in range(len(self.gridfiles)):
                self.grid_dict[self.gridtiles[i]] = GridObj.from_file(self.gridfiles[i])

    def write_out_mosaic(self, outfile:str):
        if self.mosaic_name is not None:
            mosaic = xr.DataArray(data=self.mosaic_name,
                    attrs=dict(
                        standard_name="grid_mosaic_spec",
                        contact_regions="contacts",
                        children="gridtiles",
                        grid_descriptor="")).astype('|S255')
        else:
            mosaic = None
        if self.gridlocation is not None:
            gridlocation = xr.DataArray(
                        data=self.gridlocation,
                        attrs=dict(
                            standard_name="grid_file_location")).astype('|S255')
        else:
            gridlocation = None
        if self.gridfiles is not None:
            gridfiles = xr.DataArray(
                        data=self.gridfiles, dims=["ntiles"]).astype('|S255')
        else:
            gridfiles = None
        if self.gridtiles is not None:
            gridtiles = xr.DataArray(
                        data=self.gridtiles, dims=["ntiles"]).astype('|S255')
        else:
            gridtiles = None
        if self.contacts is not None:
            contacts = xr.DataArray(
                    data=self.contacts, dims=["ncontact"],
                    attrs=dict(
                        standard_name="grid_contact_spec",
                        contact_type="boundary",
                        alignment="true", contact_index="contact_index",
                        orientation="orient"))
        else:
            contacts = None
        if self.contact_index is not None:
            contact_index = xr.DataArray(
                        data=self.contact_index, dims=["ncontact"],
                        attrs=dict(
                            standard_name="starting_ending_point_index_of_contact"))
        else:
            contact_index = None
        out = xr.Dataset(
            data_vars={"mosaic": mosaic,
                        "gridlocation": gridlocation,
                        "gridfiles": gridfiles,
                        "gridtiles": gridtiles,
                        "contacts": contacts,
                        "contact_index": contact_index})

        out.to_netcdf(outfile)

    def write_out_regional_mosaic(self, outfile:str):
        if self.mosaic_name is not None:
            mosaic = xr.DataArray(data=self.mosaic_name,
                    attrs=dict(
                        standard_name="grid_mosaic_spec",
                        contact_regions="contacts",
                        children="gridtiles",
                        grid_descriptor="")).astype('|S255')
        else:
            mosaic = None
        if self.gridfiles is not None:
            gridfiles = xr.DataArray(
                        data=self.gridfiles, dims=["ntiles"]).astype('|S255')
        else:
            gridfiles = None
        if self.gridtiles is not None:
            gridtiles = xr.DataArray(
                        data=self.gridtiles, dims=["ntiles"]).astype('|S255')
        else:
            gridtiles = None

        out = xr.Dataset(
            data_vars={"mosaic": mosaic,
                        "gridfiles": gridfiles,
                        "gridtiles": gridtiles})

        out.to_netcdf(outfile)
