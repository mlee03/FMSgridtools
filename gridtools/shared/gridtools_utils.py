import os

def check_file_is_there( check_file: str, debug: bool = False ) :

    if os.path.isfile( check_file ) :
        if debug : print(f"File \"{check_file}\" exists")
    else :
        raise FileNotFoundError(f"Cannot find file \"{check_file}\"")        
        
        
