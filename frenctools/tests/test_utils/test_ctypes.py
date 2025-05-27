from pyfrenctools.utils.ctypes import(
    set_c_bool,
    set_c_double,
    set_c_float,
    set_c_int,
    set_list,
    set_c_str,
    set_array
)
import ctypes
import numpy as np

def test_ctypes_utils():

    answers = [ctypes.c_bool(True),
               ctypes.c_double(1.0),
               ctypes.c_float(1.0),
               ctypes.c_int(1),
               np.array([1,2,3],dtype=np.float32),
               ctypes.c_char_p("test".encode("utf-8")),
               np.array([1,2,3],dtype=np.float32)
    ]
    
    arglist = []
    set_c_bool(True, arglist)
    set_c_double(1.0, arglist)
    set_c_float(1.0, arglist)
    set_c_int(1, arglist)
    set_list([1,2,3], np.float32, arglist)
    set_c_str("test", arglist)
    set_array(np.array([1,2,3], dtype=np.float32), arglist)

    nargs = len(answers)
    
    assert nargs == len(answers)
    for i in [0,1,2,3,5]:
        answer, arg = answers[i], arglist[i]
        assert type(answer) == type(arg)
        assert answer.value == arg.value

    for i in [4,6]:
        assert np.all(answers[i]==arglist[i])
    
                       
              
