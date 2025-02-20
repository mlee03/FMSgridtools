import ctypes

# simple test to check if C libraries can be linked in without error 
def test_c_libs():
    libfile = "./FRENCTools_lib/cfrenctools/c_build/clib.so"
    c_lib = ctypes.CDLL(libfile)