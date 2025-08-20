import numpy as np

from fmsgridtools.shared.xgridobj import XGridObj

def remapping(xgrid: XGridObj, variable: str):

  for tgt_tile in xgrid.dataset:
    for src_tile in xgrid.dataset[tgt_tile]:
       pass

      


def remap(src_mosaic: str,
          input_dir: str = "./",
          output_dir: str = None,
          input_file: str = None,
          output_file: str = None,
          tgt_mosaic: str = None,
          tgt_nlon: int = None,
          tgt_nlat: int =  None,
          lon_bounds: list = None,
          lat_bounds: list = None,
          kbounds: list = None,
          tbounds: list = None,
          order: int = 1,
          static_file: str = None,
          check_conserve: bool = False):

    #create an xgrid object
    xgrid = XGridObj(input_dir, src_mosaic_file=src_mosaic, tgt_mosaic_file=tgt_mosaic)

    #create xgrid
    xgrid.create_xgrid()

    #write
    xgrid.write()





