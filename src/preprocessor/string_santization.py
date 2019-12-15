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
            current_line.append((physical_line_index, value.strip("\\")))

            if not value.endswith("\\"):
                rv.append(cls(current_segments))

        return rv

    def __init__(self, segments: list):
        self.segments = segments

    def __str__(self):
        return "".join((x[1] for x in self.segments))
    
    @property
    def segments(self) -> List[Tuple[int, str]]:
        """
        Gets the various physical line segments 