import numpy as np

from fmsgridtools.remap.variableobj import FileObj, VariableObj
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
      src_tiles = list(xgrid.src.grid.keys())

      pyfms.fms.init(ndomain=len(tgt_tiles))

      for tgt_tile in tgt_tiles:

            pyfms.horiz_interp.init(len(src_tiles))

            #get xgrid
            xgrid.domain = pyfms.mpp_domains.define_domains([0, xgrid.tgt.grid.nx-1, 0, xgrid.tgt.grid.ny-1])
            xgrid.set_target_tile(tgt_tile)
            xgrid.get_interp()

            if input_file is None: return

            fileobj = FileObj(datafile=input_file, input_dir=input_dir, tiles=src_tiles)

            for var in fileobj.variables:

                variable = VariableObj(var, fileobj)
                variable.get_attributes()

                times = list(range(variable.dims.ntimes)) if variable.time.here else [None]
                klevels = list(range(variable.klevels.nz)) if variable.z.here else [None]

                for itime in times:
                    for klevel in klevels:
                        for src_tile in src_tiles:
                            input_data = variable.slice(tile=src_tile, timepoint=itime, klevel=klevel, prepare_data=True)
                            #HEREHEREHERE
                            pyfms.fms.horiz_interp(xgrid.interps[src_tile].interp_id, )






