"""
Main module for interacting with Crust. Mostly just some objects that store configuration
"""
from pathlib import Path
from typing import Union, Iterable
from useful import normalize_path


class CrustModule:
    """
    Defines a module. This is a directory of interest, with it's own namespace.
    """
    def __init__(self, path: Union[str, Iterable[str], Iterable[Path]]):
        self.files = normalize_path(path)