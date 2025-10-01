import numpy as np
import xarray as xr

from fmsgridtools.remap.dataobj import DataObj
from fmsgridtools.shared.xgridobj import XGridObj
from fmsgridtools.shared.mosaicobj import MosaicObj

import pyfms

def construct_dataset(field, finish = False):
  
  if dataset is None:    
    dataset = xr.Dataset({fieldname: dataarray})
  else:
    dataset = xr.merge([dataset, datarray])
  
  if finish:
    for dim, size in dataset.sizes.items():
      dataset.coords[dim] = np.arange(size)      


def remap(xgrid: type[XGridObj] = None,
          input_file: str = None,
          src_mosaic: str = None,
          tgt_mosaic: str = None,
          scalar_variables: list[str] = None,
          input_dir: str = "./",
          output_dir: str = "./",
          output_file: str = None,
          lon_bounds: list = None,
          lat_bounds: list = None,
          kbounds: list = None,
          tbounds: list = None,
          order: int = 1,
          static_file: str = None,
          check_conserve: bool = False) -> XGridObj:

  pyfms.fms.init()
  pyfms.horiz_interp.init(ninterp=6)

  mydir = "/home/Mikyung.Lee/FRE-NCTools/test-benchmark/tests_fregrid/Testa-conserve1-output/"
  data_dir = "/home/Mikyung.Lee/FRE-NCTools/DONOTDELETEME_DATA/TESTS/TESTS_INPUT/Testa-input/"
  src_mosaic = "C96_mosaic.nc"
  tgt_mosaic = "lonlat_288x180_mosaic.nc"
  src_data = "00010101.atmos_month_aer"

  #get input grid
  src_mosaic = MosaicObj(input_dir=mydir, mosaic_file=src_mosaic).read()
  src_grid_dict = src_mosaic.get_grid(toradians=True, agrid=True)

  #get target grid
  tgt_mosaic = MosaicObj(input_dir=mydir, mosaic_file=tgt_mosaic).read()
  tgt_grid_dict = tgt_mosaic.get_grid(toradians=True, agrid=True)

  for tgt_tile, tgt_grid in tgt_grid_dict.items():
    field_out = None
    interp_ids = {}
    for src_tile, src_grid in src_grid_dict.items():

      area = src_grid.get_fms_area()
      
      interp_ids[src_tile] = pyfms.horiz_interp.get_weights(lon_in=src_grid.x,
                                                 lat_in=src_grid.y,
                                                 lon_out=tgt_grid.x,
                                                 lat_out=tgt_grid.y,
                                                 nlon_in=src_grid.nx,
                                                 nlat_in=src_grid.ny,
                                                 nlon_out=tgt_grid.nx,
                                                 nlat_out=tgt_grid.ny,
                                                 convert_cf_order=False
      )

    tiles = list(src_grid_dict.keys())
    field = DataObj(input_dir=data_dir, tiles=tiles, datafile=src_data, variable="temp")

    tgt_data = np.zeros((tgt_grid.ny, tgt_grid.nx))

    for itime in range(field.dims.ntime):
      for k in range(field.dims.nz):
        for tile in field.tiles:
          if field.area_averaged: 
            field_in = field.get_slice(tile=tile, klevel=k, timepoint=itime) * field.static_area / area
          else:
            field_in = field.get_slice(tile=tile, klevel=k, timepoint=itime)
          
          tgt_data += pyfms.horiz_interp.interp(interp_id=interp_ids[src_tile],
                                                data_in=field_in,
                                                convert_cf_order=False)
            
        field.add_data(data=field_out, klevel=k, timepoint=itime)

    # print(field.data_out)
    #field.complete_data_out()
    #construct_dataset("temp", field.data_out, finish=True)    
    #dataset.to_netcdf("test.nc")
    

if __name__ == "__main__":
  remap()



