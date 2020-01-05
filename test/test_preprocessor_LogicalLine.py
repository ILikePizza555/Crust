import pytest # NOQA
from .utilities import NamedTestMatrix
from src.preprocessor.string_santization import LogicalLine


def test_str_single():
    actual = str(LogicalLine([(0, "oh")]))
    assert actual == "oh"


def test_str_multiple():
    data = LogicalLine([(0, "trans girls, "), (1, "trans boys, "), (2, "and enbies "), (3, "are all valid")])
    actual = str(data)
    assert actual == "trans girls, trans boys, and enbies are all valid"


def test_len_single_segment():
    data = "Goth Mage Izzy"
    test_object = LogicalLine([(0, data)])
    assert len(test_object) == len(data)


def test_len_multi_segments():
    data = "test string 24"
    test_object = LogicalLine([(0, "test "), (1, "string "), (2, "42")])
    assert len(test_object) == len(data)


GET_ITEM_TEST_MATRIX = NamedTestMatrix(
    ("test_object", "test_range", "expected_str"),
    (
        ("single seg int",      LogicalLine([(0, "some body once told me")]),               5,              "b"),
        ("single seg range",    LogicalLine([(0, "the world was gonna roll me")]),          range(4, 9),    "world"),
        ("dual seg in",         LogicalLine([(0, "i ain't "), (1, "the sharpest tool")]),   9,              "h"),
        ("dual seg range",      LogicalLine([(0, "in the shed"), (1, "she was looking")]),  range(8, 16),   "hedshe w"),
        ("tri seg range",       LogicalLine([(0, "kinda dumb"), (1, "with her finger and her"), (2, "thumb in")]),   range(9, 36),   "bwith her finger and herthu"),
        ("index correction",    LogicalLine([(0, "the shape"), (1, "of an L on"), (2, "her forehead")]), range(21, 25), "r fo")
    )
)
@pytest.mark.parametrize(GET_ITEM_TEST_MATRIX.arg_names, GET_ITEM_TEST_MATRIX.arg_values, ids=GET_ITEM_TEST_MATRIX.test_names)
def test_get_item(test_object, test_range, expected_str):
    actual = test_object[test_range]
    assert actual == expected_str


LINE_SPLICING_MATRIX = NamedTestMatrix(
    ("test_input", "expected_objects"),
    (
        ("single line",         "h\n",                                          [LogicalLine([(0, "h")])]),
        ("multi line",          "h\nhh\nhhh\n",                                 [LogicalLine([(0, "h")]), LogicalLine([(1, "hh")]), LogicalLine([(2, "hhh")])]),
        ("single escaped line", "izzy \\\n lancaster",                          [LogicalLine([(0, "izzy "), (1, " lancaster")])]),
        ("multi escped line",   "i \\\n giorno \n giovanna \\\n have a dream",  [LogicalLine([(0, "i "), (1, " giorno ")]), LogicalLine([(2, " giovanna "), (3, " have a dream")])])
    )
)
@pytest.mark.parametrize(LINE_SPLICING_MATRIX.arg_names, LINE_SPLICING_MATRIX.arg_values, ids=LINE_SPLICING_MATRIX.test_names)
def test_line_splicer(test_input, expected_objects):
    actual = LogicalLine.splice_lines(test_input)
    assert actual == expected_objects