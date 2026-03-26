"""
Generates minimal valid PNG bytes without external dependencies.
Used by seed.py to upload placeholder product images to MinIO.
"""
import struct
import zlib


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    chunk = chunk_type + data
    return struct.pack(">I", len(data)) + chunk + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)


def make_placeholder_png(width: int = 200, height: int = 200, color: tuple = (180, 180, 180)) -> bytes:
    """Return raw bytes of a solid-color PNG image."""
    r, g, b = color
    raw_rows = b""
    for _ in range(height):
        row = b"\x00" + bytes([r, g, b] * width)
        raw_rows += row

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr = _png_chunk(b"IHDR", ihdr_data)
    idat = _png_chunk(b"IDAT", zlib.compress(raw_rows))
    iend = _png_chunk(b"IEND", b"")
    return signature + ihdr + idat + iend
