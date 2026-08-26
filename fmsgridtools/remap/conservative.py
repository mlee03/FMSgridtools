import numpy as np

from fmsgridtools.remap.variableobj import SrcFileObj, TgtFileObj, VariableObj
from fmsgridtools.shared.xgridobj import XGridObj

import pyfms


def remap(input_dir: str = "./",
      src_mosaicfile: str = None,
      tgt_mosaicfile: str = None,
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

      xgrid = XGridObj(input_dir=input_dir, src_mosaicfile=src_mosaicfile, tgt_mosaicfile=tgt_mosaicfile)
      tgt_tiles = list(xgrid.tgt.grid.keys())
      src_tiles = list(xgrid.src.grid.keys())

      pyfms.fms.init(ndomain=len(tgt_tiles))

      for tgt_tile in tgt_tiles:

            pyfms.horiz_interp.init(len(src_tiles))

            nx_tgt, ny_tgt = xgrid.tgt.grid[tgt_tile].nx, xgrid.tgt.grid[tgt_tile].ny

            #get xgrid, make sure mpi works cause i don't think it will
            xgrid.domain = pyfms.mpp_domains.define_domains([0, nx_tgt-1, 0, ny_tgt-1])
            xgrid.set_target_tile(tgt_tile)
            xgrid.get_interp()

            if input_file is None: return
            if output_file is None: output_file = input_file
            if output_dir is None: output_dir = input_dir

            src_fileobj = SrcFileObj(datafile=input_file, input_dir=input_dir, tiles=src_tiles)
            tgt_fileobj = TgtFileObj(datafile=output_file, output_dir=output_dir, nx=nx_tgt, ny=ny_tgt)

            tgt_fileobj.copy_coords(src_fileobj, "T")
            tgt_fileobj.copy_coords(src_fileobj, "Z")

            for var in src_fileobj.variables:

                variable = VariableObj(var, src_fileobj, tgt_fileobj)

                for itime in variable.timelist:
                    for klevel in variable.zlist:

                        src_tile = src_tiles[0]
                        input_data = variable.slice(tile=src_tile, timepoint=itime, klevel=klevel, prepare_data=True)
                        data_slice = pyfms.horiz_interp.interp(xgrid.interps[src_tile].interp_id, input_data, convert_cf_order=False)

                        for src_tile in src_tiles[1:]:
                            input_data = variable.slice(tile=src_tile, timepoint=itime, klevel=klevel, prepare_data=True)
                            data_slice += pyfms.horiz_interp.interp(xgrid.interps[src_tile].interp_id, input_data, convert_cf_order=False)

                            #gather if parallel, for now, no
                        variable.set_tgt_data(data_slice, timepoint=itime, klevel=klevel)

            src_fileobj.close_datasets()
