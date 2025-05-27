from ctypes import (
    c_bool,
    CDLL,
    c_char_p,
    c_double,
    c_float,
    c_int,
    POINTER
)
import numpy as np
import numpy.typing as npt
from typing import Union

ctypelist = Union[type(c_int),
                  type(c_float),
                  type(c_double),
                  type(c_bool)]

nptypelist = Union[np.int32,
                   np.int64,
                   np.float32,
                   np.float64,
                   np.bool]

def setNone(arglist) -> None:
    arglist.append(None)
    return None


def set_c_bool(arg: ctypelist|None,
               arglist: list) -> ctypelist|None:

    if arg is None: return setNone(arglist)
    
    arg_c = c_bool(arg)
    arglist.append(arg_c)
    return arg_c


def set_c_double(arg: ctypelist|None,
                 arglist: list) -> ctypelist|None:

    if arg is None: return setNone(arglist)
    
    arg_c = c_double(arg)
    arglist.append(arg_c)
    return arg_c


def set_c_float(arg: ctypelist|None,
                  arglist: list) -> ctypelist|None:

    if arg is None: return setNone(arglist)
    
    arg_c = c_float(arg)
    arglist.append(arg_c)
    return arg_c


def set_c_int(arg: ctypelist|None,
              arglist: list) -> ctypelist|None:

    if arg is None: return setNone(arglist)
    
    arg_c = c_int(arg)
    arglist.append(arg_c)
    return arg_c


def set_list(arg: list|None,
             nptype: nptypelist,
             arglist: list) -> npt.ArrayLike|None:
    
    if arg is None: return setNone(arglist)

    arg_c = np.array(arg, dtype=nptype)
    arglist.append(arg_c)
    return arg_c
        

def set_c_str(arg: str|None,              
              arglist: list) -> type(c_char_p)|None:
    
    if arg is None: return setNone(arglist)

    arg_c = c_char_p(arg.encode("utf-8"))
    arglist.append(arg_c)
    return arg_c


def set_array(arg: npt.ArrayLike|None,
              arglist: list) -> npt.ArrayLike|None:
    
    if arg is None: return setNone(arglist)

    arglist.append(arg)
    return arg
