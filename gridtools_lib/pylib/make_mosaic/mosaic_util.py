import ctypes



def get_align_contact():

    #generated shared library from c code
    #use CDLL function to load the shared library file, returns library object that can be used tto access functions
    clibrary = ctypes.CDLL('libcontact.so')

    #acquire function signature
    get_align_contact = clibrary.get_align_contact

    #represent parameters needed
    get_align_contact.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.c_double, ctypes.c_double, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]

    #specify type of return value
    get_align_contact.restype = ctypes.c_int

    #create ctype doubles/ints from inputs

    count = get_align_contact()

    return count


