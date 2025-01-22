import ctypes as ct
from dataclasses import dataclass
from typing import Optional
import xarray as xr
from gridtools.shared.gridtools_utils import check_file_is_there
from gridtools.shared.gridobj import GridObj

@dataclass
class XGridObj() :

    src_mosaic : Optional[str] = None
    tgt_mosaic : Optional[str] = None
    restart_remap_file : Optional[str] = None
    out_remap_file     : Optional[str] = 'remap.nc'
    src_grid : Optional[GridObj] = None 
    tgt_grid : Optional[GridObj] = None 
    debug    : Optional[bool] = False
    order    : Optional[int] = 1
    on_gpu   : Optional[bool] = False

    dataset : Optional[xr.Dataset] = None 
    _dataset_exists = False
    
    def __post_init__(self) :

        if self._check_dataset()            or \
           self._check_restart_remap_file() or \
           self._check_mosaic()             or \
           self._check_grids()             :return
 
        raise RuntimeError("""Exchange grids can be generated from 
        (1) a restart remap_file
        (2) input and tgt mosaic files with grid file information
        (3) input and output grids as instances of GridObj 
        Please provide either the src_mosaic with the tgt_mosaic, 
                                  src_grid with the tgt_grid, 
                                  or a restart_remap_file""")
    
        
        
    def read_remap_file(self) :
        self.dataset = xr.open_dataset(self.restart_remap_file)
        self._dataset_exists = True
        
                
    def write_remap_file(self) :
        self.dataset.to_netcdf(self.out_remap_file)


    def create_xgrid(self) :
        if not any( i == self.order for i in (1,2) ) : raise RuntimeError("conservative order must be 1 or 2")
        #create_xgrid
    
        
    def _check_dataset(self) :
        if self.dataset is not None :
            self._dataset_exists = True
            return True
        else : return False
        
        
    def _check_restart_remap_file(self) :
        
        if self.restart_remap_file is not None :
            check_file_is_there(self.restart_remap_file)
            self.read_remap_file()
            return True
        else : return False

        
    def _check_mosaic(self) :
        
        if self.src_mosaic is not None and self.tgt_mosaic is not None :
            # file checks are done in mosaic
            # self.src_grid = MosaicObj(self.src_mosaic).get_grid(), MosaicObj(self.src_mosaic).grid ?
            # self.tgt_grid = MosaicObj(self.tgt_mosaic).get_grid()
            return True
        else : return False

        
    def _check_grids(self) :
        if self.src_grid is not None and self.tgt_grid is not None:
            return True
        else : return False
        

    #def create_xgrid(self) :
        
