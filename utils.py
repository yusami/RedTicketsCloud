# -*- coding: utf-8 -*-
import sys
from pathlib import Path

def setup_folder(path):
    """
    Prepare the empty folder.

    Parameters
    ----------
    path : String
        Designated empty folder. All existing files are deleted.
    """
    # Create the folder if necessary.
    Path(path).mkdir(exist_ok=True)
    # Delete all files in the designated folder if necessary.
    t_dir = Path(path)
    for p in t_dir.iterdir():
        if p.is_file():
            # print(p)
            p.unlink()
        if p.is_dir():
            # print(p)
            setup_folder(p)

def validate_param(x):
    """
    Validate a parameter.

    Parameters
    ----------
    x : any
        Any data to validate.
    """
    if x == None:
        print("Error in param. (None)")
        sys.exit()

    if type(x) is str and len(x) == 0:
        print("Error in param. (str)")
        sys.exit()

if __name__ == '__main__':
    setup_folder("tmp")
