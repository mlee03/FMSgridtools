import ctypes


# simple test to check if C libraries can be linked in without error
def test_c_libs():
    libfile = "./frenctools/cfrenctools/c_install/clib.so"
    c_lib = ctypes.CDLL(libfile)
