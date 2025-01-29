import ctypes as ct
from pylib.shared import CreateXgrid

class pylib() :

    cFMS_so : str = None
    cFMS : ct.CDLL = None

    create_xgrid : shared.CreateXgrid = None

    __is_initialized : bool = False
    
    def __post_init__(self) :

        if not __is_initialized : 
            check_file_is_there( self.cFMS_so )
            self.cFMS = ct.cdll.LoadLibrary( self.cFMS_so )        
            self.__init_modules

    def __init_modules(self) :
        self.create_xgrid = CreateXgrid(self.cFMS)    
