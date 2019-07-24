from glob import iglob
from pathlib import Path
from typing import Iterable, Union


def normalize_path(path: Union[str, Iterable[Union[Path, str]]]) -> Iterable[Path]:
    # Convert a single instance to an interable
    if type(path) is str:
        path = [path]

    def handle_path(path_obj: Path):
        if path_obj.is_file():
            return (path_obj,)
        elif path_obj.is_dir():
            return (x for x in path_obj.iterdir() if x.is_file())

    accepted_files = set()
    for p in path:
        try:
            # Try to handle p as if it was a string
            for g in map(Path, iglob(p, recursive=True)):
                accepted_files.update(handle_path(g))
        except TypeError:
            # Not a string, try to handle it like a path
            accepted_files.update(handle_path(p))

    return accepted_files