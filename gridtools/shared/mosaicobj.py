from typing import Optional, Dict
from dataclasses import dataclass,field
from datetime import datetime
import socket
import time
import sys
import xarray as xr
import numpy as np
import numpy.typing as npt

from gridtools_lib import GridObj

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
    mosaic: object = field(init=False)
    grid_dict: Optional[Dict] | None = field(default_factory=dict)

    def __post_init__(self):
        try:
            if self.mosaic_file is not None:
                self.mosaic = xr.open_dataset(self.mosaic_file)
        except FileNotFoundError:
                sys.exit("No such file or directory: {}".format(self.mosaic_file))

        if self.gridfiles is None and self.ntiles is None:
            self.gridfiles, self.ntiles = self.read_mosaic()


    def read_mosaic(self):
        files = list(self.mosaic['gridfiles'][:].values.flatten())
        gridfiles = [f.decode('utf-8') for f in files]
        ntiles = self.mosaic['ntiles'].size

        return gridfiles, ntiles

    def griddict(self):
        #parse gridfiles 
        i = 1
        for file in self.gridfiles:
            self.grid_dict[f'tile{i}'] = GridObj.from_file(file)
            i+=1

    def write_out_mosaic(self):
        #mosaic_vars = dict()
        
        mosaic = xr.DataArray([self.mosaic_name], attrs=dict(standard_name="grid_mosaic_spec", contact_regions="contacts", children="gridtiles", grid_descriptor=""))

        gridlocation = xr.DataArray([self.gridlocation], attrs=dict(standard_name="grid_file_location"))
        
        gridfiles = xr.DataArray(data=self.gridfiles, dims=["ntiles"])
        
        gridtiles = xr.DataArray(data=self.gridtiles, dims=["ntiles"])
        
        contacts = xr.DataArray(data=self.contacts, dims=["ncontact"], attrs=dict(standard_name="grid_contact_spec", contact_type="boundary", alignment="true", contact_index="contact_index", orientation="orient"))
        
        contact_index = xr.DataArray(data=self.contact_index, dims=["ncontact"], attrs=dict(standard_name="starting_ending_point_index_of_contact"))

        out = xr.Dataset(data_vars={ "mosaic": mosaic, "gridlocation": gridlocation, "gridfiles": gridfiles, "gridtiles": gridtiles, "contacts": contacts, "contact_index": contact_index})

        out.to_netcdf(self.output_file)

