import os

def file_is_there( check_file: str ) -> bool :
    if os.path.isfile( check_file ) :
        print(f"File \"{check_file}\" exists")
        return True
    else :
        raise FileNotFoundError(f"Cannot find file \"{check_file}\"")        
        
        
