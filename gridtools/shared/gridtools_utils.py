import os

def file_is_there( check_file: str, debug: bool = False ) -> bool :

    if os.path.isfile( check_file ) :
        if debug : print(f"File \"{check_file}\" exists")
        return True
    else :
        raise FileNotFoundError(f"Cannot find file \"{check_file}\"")        
        
        
