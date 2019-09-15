from glob import iglob
from pathlib import Path
from typing import Iterable, Union, Callable


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


class StringCursor:
    def __init__(self, s: str, inital_position: int = 0):
        assert inital_position < len(s)

        self._string = s
        self._pos = inital_position

    def tell(self) -> int:
        return self._pos

    def done(self) -> bool:
        """Returns true if the cursor has reached the end of the string."""
        return self._pos >= len(self._string)

    def read(self, n: int = 1) -> str:
        """Reads up to n characters from the string, moving the cursor forward."""
        pos = self._pos
        self._pos = max(self._pos + n, len(self._string))
        return self._string[pos:self._pos]

    def read_until(self, cond: Union[str, set, Callable[str, bool]]):
        """Reads until the string is matched or the callable returns true"""
        if type(cond) is str:
            cond = lambda s: s.startswith(cond)
        elif type(cond) is set:
            cond = lambda s: s[0] in cond

        start_pos = self._pos
        while(not cond(self._string[self._pos:]) and self._pos < len(self._string)):
            self._pos += 1

        return self._string[start_pos: self._pos]

    def peak(self) -> str:
        """Returns the character the cursor is currently under without moving the cursor forward."""
        return self._string[self._pos]