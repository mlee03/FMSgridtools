import numpy as np

from fmsgridtools.remap.dataobj import DataObj
from fmsgridtools.shared.xgridobj import XGridObj

def remapping(xgrid: XGridObj, variable: str):

  for tgt_tile in xgrid.dataset:
    for src_tile in xgrid.dataset[tgt_tile]:
       pass

      


def remap(xgrid: type[XGridObj],
          input_file: str,
          scalar_variables: list[str],
          input_dir: str = "./",
          output_dir: str = "./",
          output_file: str = None,          
          lon_bounds: list = None,
          lat_bounds: list = None,
          kbounds: list = None,
          tbounds: list = None,
          order: int = 1,
          static_file: str = None,
          check_conserve: bool = False) -> type[XGridObj]:

    
    #read the data
    for variable in scalar_variables:
      for tgt_tile in xgrid.datadict:
        for src_tile in xgrid.datadict[tgt_tile]:

          data = DataObj(input_dir=input_dir,
                         datafile=input_file+f".tile{src_tile}.nc",
                         variable=variable,
                         tile=src_tile,
                         input_dir=input_dir)

          if kbounds is not None:
            for klevel in kbounds:
              data.get_klevel(klevel)
              if tbounds is not None: 
                for tlevel in tbounds:
                  data.get_tlevel(tlevel)

              



