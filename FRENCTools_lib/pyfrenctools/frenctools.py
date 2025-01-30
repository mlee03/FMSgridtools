import ctypes
import dataclasses
from pyfrenctools.shared.create_xgrid import CreateXgrid
from pyfrenctools.shared.shared_utils import check_file_is_there

@dataclasses.dataclass
class FRENCToolsObj():

    cFMS_so: str = None
    cFMS: ctypes.CDLL = None
    xgrid: CreateXgrid = None

    __is_initialized: bool = False
    
    def __post_init__(self):

        if not self.__is_initialized: 
            check_file_is_there(self.cFMS_so)
            self.cFMS = ctypes.cdll.LoadLibrary(self.cFMS_so)
            self.__init_modules

    def __init_modules(self):
        self.xgrid = CreateXgrid(self.cFMS)    
