def remap(src_mosaic: str,
          input_dir: str = None,
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

    print("here")
