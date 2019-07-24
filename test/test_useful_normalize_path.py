import pytest # NOQA
from src.useful import normalize_path


def test_simple_str(shared_datadir):
    path = str(shared_datadir / "main.c")

    actual = normalize_path(path)
    assert actual == (shared_datadir / "main.c",)


def test_str_path_to_dir_with_no_subdir(shared_datadir):
    dir_path = shared_datadir / "a"
    assert dir_path.is_dir()
    path = str(dir_path)

    actual = normalize_path(path)
    assert actual == dir_path.iterdir()


def test_str_path_to_dir_with_subdir(shared_datadir):
    # Passing a path to a directory should get all files in the directory, excluding subdirectories
    path = str(shared_datadir)
    actual = normalize_path(path)
    assert actual == (p for p in shared_datadir.iterdir() if p.is_file())


def test_glob_str(shared_datadir):
    path = str(shared_datadir) + "/**/*.c"
    actual = normalize_path(path)
    assert actual == shared_datadir.glob("**/*.c")


def test_str_iterable(shared_datadir):
    paths = [
        str(shared_datadir) + "/a/*",
        str(shared_datadir) + "/b/include/*",
        str(shared_datadir) + "/main.c"
    ]
    actual = normalize_path(paths)
    assert actual == [
        shared_datadir / "a/utils.c",
        shared_datadir / "a/utils.h",
        shared_datadir / "b/include/convertions.h",
        shared_datadir / "b/include/network.h",
        shared_datadir / "b/include/parse_http.h",
        shared_datadir / "main.c"
    ]


def test_mixed_iterable(shared_datadir):
    paths = [
        str(shared_datadir) + "/a/*",
        shared_datadir / "a" / "utils.h",
        str(shared_datadir) + "/b/src/*.c",
        str(shared_datadir) + "/b/include/*.c",
        shared_datadir / "main.c"
    ]

    actual = normalize_path(paths)
    assert actual == [
        shared_datadir / "a/utils.c",
        shared_datadir / "a/utils.h",
        shared_datadir / "b/src/convertions.c",
        shared_datadir / "b/src/network.c",
        shared_datadir / "b/src/parse_http.c",
        shared_datadir / "main.c"
    ]
