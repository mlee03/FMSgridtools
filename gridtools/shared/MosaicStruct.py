from netCDF4 import Dataset
from dataclasses import dataclass,field
from datetime import datetime
import socket
import time
import sys
import xarray as xr


@dataclass
class MosaicStruct:
    output_file: str = field(default=None)
    ntiles: int = field(default=None)
    ncontacts: int = field(default=None)


    def get_gridfiles(self, mosaic_file: str):
        try:
            mosaic = xr.open_dataset(mosaic_file)
        except FileNotFoundError:
            sys.exit("No such file or directory: {}".format(mosaic_file))
        res = (mosaic['gridfiles'][:])
        gridfiles = list(mosaic['gridfiles'].values.flatten())
        return gridfiles


    def get_ntiles(self, mosaic_file: str):
        try:
            mosaic = xr.open_dataset(mosaic_file)
        except FileNotFoundError:
            sys.exit("No such file or directory: {}".format(mosaic_file))
        ntiles = mosaic['ntiles'].size
        return ntiles


    def write_out_mosaic(self):
        ncfile = Dataset(self.output_file, 'w', format='NETCDF4')

        #define dimensions
        ntiles_dim = ncfile.createDimension('ntiles', self.ntiles)
        ncontacts_dim = ncfile.createDimension('ncontact', self.ncontacts)
        string_dim = ncfile.createDimension('string', 255)


        #define variables
        mosaic = ncfile.createVariable('mosaic', 'S1', ('string'))
        mosaic.setncatts({"standard_name": "grid_mosaic_spec", "contact_regions": "contacts", "children": "gridtiles", "grid_descriptor": ""})

        gridlocation = ncfile.createVariable('gridlocation', 'S1', ('string'))
        gridlocation.standard_name = 'grid_file_location'


        gridfiles = ncfile.createVariable('gridfiles', 'S1', ('ntiles', 'string'))
        gridtiles = ncfile.createVariable('gridtiles', 'S1', ('ntiles', 'string'))


        contacts = ncfile.createVariable('contacts', 'S1', ('ncontact', 'string'))
        contacts.setncatts({"standard_name": "grid_contact_spec", "contact_type": "boundary", "alignment": "true", "contact_index": "contact_index", "orientation": "orient"})


        contactidx = ncfile.createVariable('contact_index', 'S1', ('ncontact', 'string'))
        contactidx.standard_name = 'starting_ending_point_index_of_contact'

        #global attributes
        ncfile.grid_version = '0.2'
        ncfile.code_release_verison = ''
        ncfile.git_hash = ''
        ncfile.creationtime = time.ctime(time.time())
        ncfile.hostname = socket.gethostname()
        ncfile.history = ''


        ncfile.close()
