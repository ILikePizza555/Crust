"""
Implementation for phase 1 and 2 of the C preprocessor. It replaces escape sequences, trigraphs,
and converts physical source lines to logical ones. Note that tokenization has not begun.
"""
from typing import List, Tuple
from itertools import accumulate


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
        self._acc_lengths: List[int] = list(accumulate((len(x[1]) for x in self.segments)))

    def __len__(self):
        return self._acc_lengths[-1]

    def __str__(self):
        return "".join((x[1] for x in self.segments))

    def __getitem__(self, index):
        if type(index) == int:
            seg_index = self._map_string_index_to_segment_index(index)
            segment = self.segments[seg_index]
            length = self._acc_lengths[seg_index]
            return segment[1][index - length]

        segment_start, segment_end, segments = self._map_string_range_to_segments(index)
        segment_str = "".join(x[1] for x in segments)

        index_correction = self._acc_lengths[segment_start - 1] if segment_start > 0 else 0
        return segment_str[index.start - index_correction:index.stop - index_correction:index.step]

    def __eq__(self, other) -> bool:
        if len(self.segments) != len(other.segments):
            return False

        for a, b in zip(self.segments, other.segments):
            if a[0] != b[0] or a[1] != b[1]:
                return False

        return True

    def _map_string_index_to_segment_index(self, string_index: int):
        if string_index >= len(self):
            raise IndexError(f"Index {string_index} is larger than length {len(self)}")

        length_iter = (i for i, length in enumerate(self._acc_lengths) if string_index < length)
        return next(length_iter)

    def _map_string_range_to_segments(self, string_range: range):
        start_index = self._map_string_index_to_segment_index(string_range.start)
        end_index = self._map_string_index_to_segment_index(string_range.stop)

        return (start_index, end_index, self.segments[start_index:end_index +  1])