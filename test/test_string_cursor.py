import re
import pytest # NOQA
from src.useful import StringCursor


@pytest.mark.parametrize(
    "cursor,n_value,expected_str,expected_pos",
    argvalues=[
        (StringCursor("abcaabbc"), 5, "abcaa", 5),
        (StringCursor("abcaabbc", 3), 5, "aabbc", 8),
        (StringCursor("abcaabbc", 5), 5, "bbc", 8)
    ],
    ids=["Normal read", "Given a starting position", "N-value exceeding length of string"]
)
def test_read(cursor: StringCursor, n_value, expected_str, expected_pos):
    assert cursor.read(n_value) == expected_str
    assert cursor.position == expected_pos


@pytest.mark.parametrize(
    "cursor,condition,expected_str,expected_pos",
    argvalues=[
        (StringCursor("aaab"), "b", "aaa", 3),
        (StringCursor("aaa"), "b", "aaa", 3),
        (StringCursor("foobar"), "f", "", 0),
        (StringCursor("foobar"), set("bar"), "foo", 3),
        (StringCursor("foobar"), set("foo"), "", 0),
        (StringCursor("foobbar"), "bar", "foob", 4),
        (StringCursor("foobar"), lambda s: True, "", 0),
        (StringCursor("foobar"), lambda s: s[0] == "p", "foobar", 6)
    ],
    ids=[
        "until string",
        "until string eof",
        "until string starting on char",
        "until set",
        "until set starting on char",
        "until string matching string",
        "until lambda",
        "bounds check done before cond"
    ]
)
def test_read_until(cursor: StringCursor, condition, expected_str, expected_pos):
    assert cursor.read_until(condition) == expected_str
    assert cursor.position == expected_pos


@pytest.mark.parametrize(
    "cursor,pattern,expected,expected_pos",
    argvalues=[
        (StringCursor("foobar"), "foo", "foo", 3),
        (StringCursor("foobar"), "bar", None, 0),
        (StringCursor("foobar", 3), "bar", "bar", 6),
        (StringCursor("ababac"), re.compile(r"[ab]+c"), "ababac", 6),
        (StringCursor("ababac", 3), re.compile(r"[ab]+c"), "bac", 6),
        (StringCursor("cababac"), re.compile(r"[ab]+c"), None, 0)
    ],
    ids=[
        "String match",
        "Invalid string match",
        "String match with offset",
        "Regex match",
        "Regex match with offset",
        "Invalid regex match"
    ]
)
def test_read_match(cursor: StringCursor, pattern, expected, expected_pos):
    actual = cursor.read_match(pattern)

    if not expected:
        assert actual == expected
    else:
        assert actual.group() == expected

    assert cursor.position == expected_pos
