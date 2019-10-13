import pytest # NOQA
import unittest
from pathlib import Path
from src.useful import normalize_path


@pytest.fixture
def data_dir():
    return Path(".") / "test" / "data" / "normalize_path"


def assert_count_equal(a, b, msg=None):
    case = unittest.TestCase()
    case.assertCountEqual(a, b, msg)


def test_simple_str(data_dir):
    path = str(data_dir / "main.c")

    actual = normalize_path(path)
    assert_count_equal(actual, (data_dir / "main.c",))


def test_str_path_to_dir_with_no_subdir(data_dir):
    dir_path = data_dir / "a"
    assert dir_path.is_dir()
    path = str(dir_path)

    actual = normalize_path(path)
    assert_count_equal(actual, dir_path.iterdir())


def test_str_path_to_dir_with_subdir(data_dir):
    # Passing a path to a directory should get all files in the directory, excluding subdirectories
    path = str(data_dir)
    actual = normalize_path(path)
    assert_count_equal(actual, (p for p in data_dir.iterdir() if p.is_file()))


def test_glob_str(data_dir):
    path = str(data_dir) + "/**/*.c"
    actual = normalize_path(path)
    assert_count_equal(actual, data_dir.glob("**/*.c"))


def test_str_iterable(data_dir):
    paths = [
        str(data_dir) + "/a/*",
        str(data_dir) + "/b/include/*",
        str(data_dir) + "/main.c"
    ]
    actual = normalize_path(paths)
    assert_count_equal(actual, [
        data_dir / "a/utils.c",
        data_dir / "a/utils.h",
        data_dir / "b/include/convertions.h",
        data_dir / "b/include/network.h",
        data_dir / "b/include/parse_http.h",
        data_dir / "main.c"
    ])


def test_mixed_iterable(data_dir):
    paths = [
        str(data_dir) + "/a/*",
        data_dir / "a" / "utils.h",
        str(data_dir) + "/b/src/*.c",
        str(data_dir) + "/b/include/*.c",
        data_dir / "main.c"
    ]

    actual = normalize_path(paths)
    assert_count_equal(actual, [
        data_dir / "a/utils.c",
        data_dir / "a/utils.h",
        data_dir / "b/src/convertions.c",
        data_dir / "b/src/network.c",
        data_dir / "b/src/parse_http.c",
        data_dir / "main.c"
    ])
