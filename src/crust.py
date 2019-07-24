"""
Main module for interacting with Crust. Mostly just some objects that store configuration
"""
from pathlib import Path
from typing import Union, Iterable, Optional, Dict
from useful import normalize_path


class CrustModule:
    """
    Defines a module. This is a directory of interest, with it's own namespace.
    """
    def __init__(self,
                 paths: Union[str, Iterable[str], Iterable[Path]],
                 name: Optional[str] = None,
                 variables: Dict[str, str] = {}):
        """
        Creates a new CrustModule.

        Parameters:
            - `paths` A string, list of strings or Path objects which point to the files that are part of this module.
                    Glob patterns are automatically parsed. Paths to directories load all files in the directory,
                    but ignore sub-directories.
            - `name` A string defining the name of the module.
            - `variable` Any build variables or flags to be defined for this module.
        """
        self.files: Iterable[Path] = normalize_path(paths)
        self.name = name
        self.variables = variables