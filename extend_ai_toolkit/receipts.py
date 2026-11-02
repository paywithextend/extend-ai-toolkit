"""Bounded receipt snapshots opened without following filesystem links."""

from __future__ import annotations

import hashlib
import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from .policy import ExecutionPolicy, ToolPermissionError


@dataclass
class ReceiptSnapshot:
    file: BinaryIO
    filename: str
    content_type: str
    size: int
    sha256: str

    def close(self):
        self.file.close()


def _content_type(filename: str, header: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    checks = [
        ({".pdf"}, header.startswith(b"%PDF-"), "application/pdf"),
        ({".png"}, header.startswith(b"\x89PNG\r\n\x1a\n"), "image/png"),
        ({".jpg", ".jpeg"}, header.startswith(b"\xff\xd8\xff"), "image/jpeg"),
        ({".gif"}, header[:6] in {b"GIF87a", b"GIF89a"}, "image/gif"),
        ({".bmp"}, header.startswith(b"BM"), "image/bmp"),
        ({".tif", ".tiff"}, header[:4] in {b"II*\x00", b"MM\x00*"}, "image/tiff"),
        (
            {".heic"},
            header[4:8] == b"ftyp"
            and header[8:12] in {b"heic", b"heix", b"hevc", b"hevx", b"mif1"},
            "image/heic",
        ),
    ]
    for suffixes, matches, mime in checks:
        if suffix in suffixes and matches:
            return mime
    raise ToolPermissionError(
        "Receipt extension and content signature must match a supported format"
    )


def snapshot_receipt(policy: ExecutionPolicy, file_path: str) -> ReceiptSnapshot:
    """Capture immutable bounded bytes, confined by directory FDs and O_NOFOLLOW.

    Symlinks are rejected at every component, including links within the root.
    A spooled temporary file fixes the bytes before host approval and bounds RAM.
    Unsupported platforms fail closed rather than falling back to unsafe open().
    """
    root = policy.receipt_root
    if root is None:
        raise ToolPermissionError("The host must configure a receipt root")
    if not hasattr(os, "O_NOFOLLOW") or os.open not in os.supports_dir_fd:
        raise ToolPermissionError("Safe receipt opening is unavailable on this platform")
    requested = Path(file_path)
    try:
        relative = requested.relative_to(root) if requested.is_absolute() else requested
    except ValueError as exc:
        raise ToolPermissionError("Receipt is outside the allowed root") from exc
    if not relative.parts or any(part in {"..", "."} for part in relative.parts):
        raise ToolPermissionError("Invalid receipt path")
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    file_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
    directory = os.open("/", directory_flags)
    fd = None
    output = tempfile.SpooledTemporaryFile(
        max_size=min(policy.max_receipt_bytes, 1024 * 1024), mode="w+b"
    )
    try:
        # Walk the trusted absolute root and the untrusted relative path by FD.
        for part in (*root.parts[1:], *relative.parts[:-1]):
            child = os.open(part, directory_flags, dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(relative.parts[-1], file_flags, dir_fd=directory)
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ToolPermissionError("Receipt must be a regular file with no hard links")
        if info.st_size > policy.max_receipt_bytes:
            raise ToolPermissionError("Receipt exceeds the host size limit")
        digest = hashlib.sha256()
        size = 0
        header = b""
        while True:
            chunk = os.read(fd, min(64 * 1024, policy.max_receipt_bytes - size + 1))
            if not chunk:
                break
            size += len(chunk)
            if size > policy.max_receipt_bytes:
                raise ToolPermissionError("Receipt exceeds the host size limit")
            if len(header) < 16:
                header = (header + chunk)[:16]
            digest.update(chunk)
            output.write(chunk)
        mime = _content_type(relative.name, header)
        output.seek(0)
        return ReceiptSnapshot(output, relative.name, mime, size, digest.hexdigest())
    except OSError as exc:
        output.close()
        raise ToolPermissionError("Receipt cannot be safely opened") from exc
    except BaseException:
        output.close()
        raise
    finally:
        if fd is not None:
            os.close(fd)
        os.close(directory)
