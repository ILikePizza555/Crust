"""
Main module for interacting with Crust. Mostly just some objects that store configuration
"""
from enum import IntEnum, auto
from pathlib import Path
from urllib.parse import urlsplit
from typing import Union, Optional, Iterable, Dict, NamedTuple
from useful import normalize_path


class CrustRemoteExternal(NamedTuple):
    """
    An external that exists somewhere on the Internet, and needs to be
    downloaded and built locally.
    """
    url: str
    name: str
    script: Iterable[str]
    artifacts: Iterable[str]
    required: bool


class CrustSystemExternal(NamedTuple):
    """
    A pre-compiled external that is installed on the system.
    """
    name: str
    directory: Optional[Path]
    required: bool


class CrustLocalExternal(NamedTuple):
    """
    An external that exists somewhere on the system, but still needs to be built.
    """
    path: Path
    name: str
    script: Iterable[str]
    artifacts: Iterable[str]
    required: bool


class ExternalManagerMixin:
    def __init__(self):
        self.externals = []

    def add_remote_external(self,
                            url: str,
                            name: Optional[str] = None,
                            script: Iterable[str] = [],
                            artifacts: Iterable[str] = [],
                            required: bool = True) -> "CrustModule":
        """
        Adds a remote dependency as a requirement for this module.
        """
        if not name:
            name = urlsplit(url)["path"]

        self.externals.append(CrustRemoteExternal(
            url, name, script, artifacts, required
        ))

        return self

    def add_system_external(self, 
                            name: str, 
                            directory: Union[str, Path, None] = None,
                            required: bool = True) -> "CrustModule":

        self.externals.append(CrustSystemExternal(name, directory, required))
        return self

    def add_local_external(self,
                           path: Union[str, Path],
                           script: Iterable[str] = [],
                           artifacts: Iterable[str] = [],
                           required: bool = True) -> "CrustModule":
        if type(path) is str:
            path = Path(str)

        self.externals.append(CrustLocalExternal(path, script, artifacts, required))
        return self


class CrustModule(ExternalManagerMixin):
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
        ExternalManagerMixin.__init__(self)

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
                 compiler: Optional[Path] = None,
                 optimization: Optimization = Optimization.NORMAL,
                 warnings: WarningConfig = WarningConfig.PEDANTIC,
                 warnings_are_errors: bool = True,
                 enable_static_linking: bool = True,
                 *additional_params):
        """
        Creates a new CrustBuildConfiguration

        Parameters:
            - `name` The name of the build configuration
            - `compiler` The path to the compiler. 'None' uses the default compiler.
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
        self.enable_static_linking = enable_static_linking
        self.additional_params = additional_params

        self.modules = []

    def add_module(self, module: CrustModule):
        self.modules.append(module)
        return self


class CrustGlobal(ExternalManagerMixin):
    """
    Defines the global config.
    """
    def __init__(self):
        ExternalManagerMixin.__init__(self)
        self.name = "global"
        self.modules = []
        self.default_compiler = None
        self.variables = {}
        self.compiler_flags = []

    def __call__(self):
        pass


crust = CrustGlobal()