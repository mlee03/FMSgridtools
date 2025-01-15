import ctypes as ct



def get_align_contact():

    size1_t = ct.c_int
    #generated shared library from c code
    #use CDLL function to load the shared library file, returns library object that can be used tto access functions
    clibrary = ct.CDLL('libcontact.so')

    #acquire function signature
    get_align_contact = clibrary.get_align_contact

    #represent parameters needed
    get_align_contact.argtypes = [size1_t, size1_t, size1_t, size1_t, size1_t, size1_t, ct.POINTER(ctypes.ct_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.c_double, ct.c_double, ct.POINTER(size1_t), ct.POINTER(size1_t), ct.POINTER(size1_t), ct.POINTER(size1_t), ct.POINTER(size1_t), ct.POINTER(size1_t), ct.POINTER(size1_t), ct.POINTER(size1_t)]

    #specify type of return value
    get_align_contact.restype = ctypes.c_int

    #create ctype doubles/ints from inputs

    count = get_align_contact()

    return count


