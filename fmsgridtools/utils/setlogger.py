import logging
import os
import datetime

def setconfig(filename: str, debug: bool = False):

    if os.path.isfile(filename):
        os.rename(filename, "OLDLOG")

    if debug:
        logging.basicConfig(filename=filename,
                            format=("[%(levelname)s]%(filename)s:%(module)s:"
                                    "%(funcName)s:%(lineno)d:"
                                    "%(asctime)s:\n  %(message)s\n"),
                            level=logging.DEBUG)
    else:
        logging.basicConfig(filename=filename,
                            format=("[%(levelname)s]%(module)s:%(funcName)s:" 
                                    "%(message)s\n"),
                            level=logging.INFO)
