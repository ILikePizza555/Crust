"""
Implementation for phase 1 and 2 of the C preprocessor. It replaces escape sequences, trigraphs,
and converts physical source lines to logical ones. Note that tokenization has not begun.
"""
from typing import List, Tuple
from itertools import accumulate, chain


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
        self.lengths: List[int] = list(accumulate(chain((0,), (len(x[1]) for x in self.segments))))

    def __len__(self):
        return self.lengths[-1]

    def __str__(self):
        return "".join((x[1] for x in self.segments))

    def __getitem__(self, index):
        if type(index) == int:
            i = self._get_segment_from_index(index)
            segment = self.segments[i]
            length = self.lengths[i]
            return segment[1][index - length]

        i_start = self._get_segment_from_index(index.start)
        i_stop = self._get_segment_from_index(index.stop)
        length = self.lengths[i_start]

        segment_str = "".join(x[1] for x in self.segments[i_start:i_stop])
        return segment_str[index.start - length:index.stop - length:index.step]

    def __eq__(self, other) -> bool:
        if len(self.segments) != len(other.segments):
            return False

        for a, b in zip(self.segments, other.segments):
            if a[0] != b[0] or a[1] != b[1]:
                return False

        return True

    def _get_segment_from_index(self, index):
        if index >= self.lengths[-1]:
            raise IndexError(f"Index {index} is larger than length {self.lengths[-1]}")
        
        return next(i - 1 for i, length in enumerate(self.lengths) if index < length)