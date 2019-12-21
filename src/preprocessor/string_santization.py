"""
Implementation for phase 1 and 2 of the C preprocessor. It replaces escape sequences, trigraphs,
and converts physical source lines to logical ones. Note that tokenization has not begun.
"""
from typing import List, Tuple


class LogicalLine:
    """
    Represents a logical line. Holds the physical lines (and indices) that make up the logical line.
    """

    @classmethod
    def splice_lines(cls, file_text: str) -> List["LogicalLine"]:
        lines = file_text.splitlines()
        rv: List["LogicalLine"] = []
        current_segments: List[Tuple[int, str]] = []

        for physical_line_index, value in enumerate(lines):
            current_segments.append((physical_line_index, value.strip("\\")))

            if not value.endswith("\\"):
                rv.append(cls(current_segments))
                current_segments = []

        return rv

    def __init__(self, segments: List[Tuple[int, str]]):
        self.segments = segments

    def __len__(self):
        return sum(map(lambda x: len(x[1]), self.segments))

    def __str__(self):
        return "".join((x[1] for x in self.segments))

    def __eq__(self, other) -> bool:
        if len(self.segments) != len(other.segments):
            return False

        for a, b in zip(self.segments, other.segments):
            if a[0] != b[0] or a[1] != b[1]:
                return False

        return True
