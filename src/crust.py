"""
Main module for interacting with Crust. Mostly just some objects that store configuration
"""
from enum import IntEnum, auto
from pathlib import Path
from typing import Union, Optional, Iterable, Dict
from useful import normalize_path


class CrustExternal:
    """
    Defines an external project that's needed to build the current one.
    The object defines the location of the external, instructions on how to build it,
    and any artifacts to be used.
    """
    def __init__(self,
                 location: Union[str, Path],
                 name: Optional[str] = None,
                 script: Iterable[str] = [],
                 artifacts: Iterable[Union[str, Path]] = []):
        self.location = location
        self.name = name
        self.script = script
        self.artifacts = artifacts


class CrustModule:
    """
    Defines a module. This is a directory of interest, with it's own namespace.
    """
    def __init__(self,
                 paths: Union[str, Iterable[str], Iterable[Path]],
                 name: str,
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


class CrustBuildConfiguration:
    class WarningConfig(IntEnum):
        NONE = 0,
        PEDANTIC = auto(),
        ALL = auto(),
        EXTRA = auto()

    class Optimization(IntEnum):
        NONE = 0,
        NORMAL = auto(),
        SPEED = auto(),
        CODE_SIZE = auto()

    """
    Defines a build configuration. Effectively, this is a name tied to a compiler and
    any command-line options.
    """
    def __init__(self,
                 name: str,
                 compiler: Path,
                 optimization: Optimization = Optimization.NORMAL,
                 warnings: WarningConfig = WarningConfig.PEDANTIC,
                 warnings_are_errors: bool = True,
                 *additional_params):
        """
        Creates a new CrustBuildConfiguration

        Parameters:
            - `name` The name of the build configuration
            - `compiler` The path to the compiler
            - `optimization` The level of optimization to use for this configuration
            - `warnings` The level of warnings to use for this configuration
            - `warnings_are_errors` Set to `True` if warnings should be errors
            - `additional_params` Any additional command-line option to pass to the compiler
        """
        self.name = name
        self.compiler = compiler
        self.optimization = optimization
        self.warnings = warnings
        self.warnings_are_errors = warnings_are_errors
        self.additional_params = additional_params

        self.modules = []

    def add_module(self, module: CrustModule):
        self.modules.append(module)
        return self
