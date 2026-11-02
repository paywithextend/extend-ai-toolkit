"""Offline regressions for partial publication and recovery identity."""

import hashlib
from pathlib import Path

import pytest

from tools.verify_release_files import verify_files


@pytest.fixture
def distributions(tmp_path: Path):
    files = []
    for name, data in [("toolkit.whl", b"wheel"), ("toolkit.tar.gz", b"source")]:
        (tmp_path / name).write_bytes(data)
        files.append({"filename": name, "digests": {"sha256": hashlib.sha256(data).hexdigest()}})
    return tmp_path, files


def test_new_version(distributions):
    directory, _ = distributions
    verify_files(directory, [])


def test_matching_partial_upload(distributions):
    directory, files = distributions
    verify_files(directory, files[:1])
    with pytest.raises(ValueError, match="incomplete"):
        verify_files(directory, files[:1], complete=True)


def test_matching_complete_upload(distributions):
    directory, files = distributions
    verify_files(directory, files, complete=True)


@pytest.mark.parametrize("index", [0, 1])
def test_rebuilt_file_must_match(distributions, index):
    directory, files = distributions
    (directory / files[index]["filename"]).write_bytes(b"rebuilt from a different commit")
    with pytest.raises(ValueError, match="differs"):
        verify_files(directory, files)


def test_unexpected_published_file(distributions):
    directory, files = distributions
    files[0]["filename"] = "different.whl"
    with pytest.raises(ValueError, match="Unexpected"):
        verify_files(directory, files)


def test_duplicate_published_file(distributions):
    directory, files = distributions
    with pytest.raises(ValueError, match="duplicate"):
        verify_files(directory, files + files[:1])


def test_missing_local_distribution(distributions):
    directory, files = distributions
    (directory / files[0]["filename"]).unlink()
    with pytest.raises(ValueError, match="exactly one"):
        verify_files(directory, [])


def test_unpublished_version_is_not_complete(distributions):
    directory, _ = distributions
    with pytest.raises(ValueError, match="incomplete"):
        verify_files(directory, [], complete=True)
