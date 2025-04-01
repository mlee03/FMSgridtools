import ctypes
import dataclasses
from typing import Optional
import os

@dataclasses.dataclass
class LIB():

    lib_path: Optional[str] = os.path.dirname(__file__) + "/../cfrenctools/c_build/clib.so"
    lib: Optional[ctypes.CDLL] = None

    def __post_init__(self):
        if self.lib is None:
            if not os.path.exists(self.lib_path) :
                raise IOError(f"{self.lib_path} does not exist")
            self.lib = ctypes.CDLL(self.lib_path)

        
