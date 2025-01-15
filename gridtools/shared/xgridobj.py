import ctypes as ct
from dataclasses import dataclass
from typing import Optional
import xarray as xr
from .gridtools_utils import file_is_there
from .gridobj import GridObj

@dataclass
class XGridObj() :

    src_mosaic : Optional[str] = None
    tgt_mosaic : Optional[str] = None
    restart_remap_file : Optional[str] = None
    write_remap_file : Optional[str] = None
    src_grid : Optional[GridObj] = None 
    tgt_grid : Optional[GridObj] = None 
    dataset : Optional[xr.Dataset] = None 

    _dataset_exists = False
    
    def __post_init__(self) :

        self._set_write_remap_filename()
        
        if(self._check_restart_remap_file()) : return
        if(self._check_mosaic()) : return
        if(self._check_grids())  : return

        raise RuntimeError("""Exchange grids can be generated from 
        (1) a restart remap_file
        (2) input and tgt mosaic files with grid file information
        (3) input and output grids as instances of GridObj 
        Please provide either src_mosaic and tgt_mosaic, src_grid and tgt_grid, or a restart_remap_file""")
    

    def _set_write_remap_filename(self) :
        if self.write_remap_file is None : self.write_remap_file = 'remap.nc' 

        
    def _check_restart_remap_file(self) :
        
        if self.restart_remap_file is not None :
            file_is_there(self.restart_remap_file)
            self.read_remap_file()
            return True
        else : return False

        
    def _check_mosaic(self) :
        
        if self.src_mosaic is not None and self.tgt_mosaic is not None :
            file_is_there(self.src_mosaic)
            file_is_there(self.tgt_mosaic)
            # set self.src_grid and self.tgt_grid from mosaic files
            return True
        else : return False

        
    def _check_grids(self) :
        if self.src_grid is not None and self.tgt_grid is not None:
            return True
        else : return False

        
    def read_remap_file(self) :
        self.dataset = xr.open_dataset(self.restart_remap_file)
        self._dataset_exists = True
        
                
