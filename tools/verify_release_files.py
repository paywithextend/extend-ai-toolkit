"""Verify that existing PyPI files match the distributions from this run."""

import argparse
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen


def verify_files(directory: Path, published: list[dict], *, complete: bool = False) -> None:
    wheels = list(directory.glob("*.whl"))
    sources = list(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sources) != 1:
        raise ValueError("Expected exactly one wheel and one source distribution")
    local = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in wheels + sources}
    seen = set()
    for item in published:
        name = item["filename"]
        if name in seen or name not in local:
            raise ValueError("Unexpected or duplicate published distribution")
        if item["digests"]["sha256"] != local[name]:
            raise ValueError("Published distribution differs from this run; reuse the original artifacts")
        seen.add(name)
    if complete and seen != set(local):
        raise ValueError("Publication is incomplete")


def published_files(project: str, version: str) -> list[dict]:
    url = f"https://pypi.org/pypi/{quote(project, safe='')}/{quote(version, safe='')}/json"
    try:
        with urlopen(url, timeout=30) as response:
            return json.load(response)["urls"]
    except HTTPError as error:
        if error.code == 404:
            return []
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--dist", type=Path, default=Path("dist"))
    parser.add_argument("--complete", action="store_true")
    args = parser.parse_args()
    verify_files(args.dist, published_files(args.project, args.version), complete=args.complete)


if __name__ == "__main__":
    main()
