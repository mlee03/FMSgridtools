import numpy as np

from fmsgridtools.remap.dataobj import DataObj
from fmsgridtools.shared.xgridobj import XGridObj
from fmsgridtools.shared.mosaicobj import MosaicObj

import pyfms


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
    for src_tile, src_grid in src_grid_dict.items():

      area = src_grid.get_fms_area()
      
      interp_id = pyfms.horiz_interp.get_weights(lon_in=src_grid.x,
                                                 lat_in=src_grid.y,
                                                 lon_out=tgt_grid.x,
                                                 lat_out=tgt_grid.y,
                                                 nlon_in=src_grid.nx,
                                                 nlat_in=src_grid.ny,
                                                 nlon_out=tgt_grid.nx,
                                                 nlat_out=tgt_grid.ny,
                                                 convert_cf_order=False
      )

      #data
      data = DataObj(input_dir=data_dir,
                     tile=src_tile,
                     datafile=src_data,
                     variable="temp"
      )
      
      for itime in range(data.ntime):
        for k in range(data.nz):          
          if data.area_averaged: 
            data_in = data.get_slice(klevel=k, timepoint=itime) * data.static_area / area
          else:
            data_in = data.get_slice(klevel=k, timepoint=itime)

          data_out = pyfms.horiz_interp.interp(interp_id=interp_id,
                                               data_in=data_in,
                                               convert_cf_order=False
          )

          data.set_out_data(data=data_out, klevel=k, timepoint=itime)



if __name__ == "__main__":
  remap()



