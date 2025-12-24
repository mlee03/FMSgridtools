import numpy as np

from fmsgridtools.shared.xgridobj import XGridObj

import pyfms


def remap(input_dir: str = "./",
      src_mosaic: str = None,
      tgt_mosaic: str = None,
      input_file: str = None,
      output_dir: str = "./",
      output_file: str = None,
      scalar_variables: list[str] = None,
      lon_bounds: list = None,
      lat_bounds: list = None,
      kbounds: list = None,
      tbounds: list = None,
      order: int = 1,
      check_conserve: bool = False,
      gpu: bool = False):      

      xgrid = XGridObj(input_dir=input_dir, src_mosaic_file = src_mosaic, tgt_mosaicfile=tgt_mosaic)
      tgt_tiles = list(xgrid.tgt.grid.keys())
      nsrc_tiles = list(xgrid.src.mosaic.ntiles)

      pyfms.fms.init(ndomain=len(tgt_tiles))

      for tgt_tile in tgt_tiles:

            pyfms.horiz_interp.init(nsrc_tiles)
            
            xgrid.domain = pyfms.mpp_domains.define_domains([0, xgrid.tgt.grid.nx-1, 0, xgrid.tgt.grid.ny-1])
            xgrid.set_target_tile(tgt_tile)
            xgrid.get_interp()

            





