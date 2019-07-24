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
        self.files: Iterable[Path] = normalize_path(paths)
        self.name = name
        self.variables = variables