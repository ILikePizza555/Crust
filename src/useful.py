import re
import string
from glob import iglob
from pathlib import Path
from typing import Iterable, Union, Callable, Optional


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
    """
    Maintains a cursor on a string.

    The cursor represents the characters that have yet to be read. 
    (i.e if the cursor is on index 2, then the character at index 2 has not been read yet)
    """
    def __init__(self, s: str, inital_position: int = 0):
        assert inital_position < len(s)

        self._string = s
        self._pos = inital_position

    @property
    def unread_slice(self) -> str:
        return self._string[self._pos:]

    @property
    def position(self) -> int:
        return self._pos

    def tell(self) -> int:
        return self._pos

    def done(self) -> bool:
        """Returns true if the cursor has reached the end of the string."""
        return self._pos >= len(self._string)

    def read(self, n: int = 1) -> str:
        """Reads up to n characters from the string, moving the cursor forward."""
        pos = self._pos
        self._pos = min(self._pos + n, len(self._string))
        return self._string[pos:self._pos]

    def read_until(self, cond: Union[str, set, Callable[[str], bool]]) -> str:
        """
        Reads until the string is matched, the character is a member of the given set, or the condition returns True.
        """
        if type(cond) is str:
            pattern = cond
            cond = lambda s: s.startswith(pattern) # NOQA
        elif type(cond) is set:
            match_set = cond
            cond = lambda s: s[0] in match_set # NOQA

        start_pos = self._pos
        while(len(self.unread_slice) != 0 and
              not cond(self.unread_slice) and
              self._pos < len(self._string)):
            self._pos += 1

        return self._string[start_pos: self._pos]

    def read_match(self, pattern) -> Optional[re.Match]:
        """
        If a match beginning at the cursor is found, read_match moves the cursor forward the length of the match and returns the match object.
        If no match is found, None is returned
        """

        if isinstance(pattern, re.Pattern):
            match = pattern.match(self.unread_slice)
        else:
            match = re.match(pattern, self.unread_slice)

        if match:
            self.read(len(match.group()))

        return match

    def peak(self, n: int = 1) -> str:
        """
        Returns the n characters the cursor is under without moving the cursor forward.
        """
        n = min(self._pos + n, len(self._string))
        return self._string[self._pos:n]

    @staticmethod
    def read_whitespace(inst: "StringCursor"):
        return inst.read_until(lambda s: s[0] not in set(string.whitespace))