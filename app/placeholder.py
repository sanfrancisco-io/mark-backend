"""
PNG generation and thumbnail resize without external dependencies.
Used by seed.py (placeholder images) and admin image upload (thumbnail generation).
"""
import struct
import zlib

_PNG_SIG = b"\x89PNG\r\n\x1a\n"


# ── PNG encoding helpers ───────────────────────────────────────────────────────

def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    chunk = chunk_type + data
    return struct.pack(">I", len(data)) + chunk + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)


def _encode_png_rows(rows: list[bytes], width: int, height: int, color_type: int) -> bytes:
    raw = b"".join(b"\x00" + row for row in rows)  # filter type 0 (None) for all rows
    signature = _PNG_SIG
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    ihdr = _png_chunk(b"IHDR", ihdr_data)
    idat = _png_chunk(b"IDAT", zlib.compress(raw))
    iend = _png_chunk(b"IEND", b"")
    return signature + ihdr + idat + iend


# ── PNG filter reconstruction ──────────────────────────────────────────────────

def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def _reconstruct_row(ftype: int, row: bytes, prev: bytes, bpp: int) -> bytes:
    out = bytearray(len(row))
    for i in range(len(row)):
        raw = row[i]
        a = out[i - bpp] if i >= bpp else 0
        b = prev[i]
        c = prev[i - bpp] if i >= bpp else 0
        if ftype == 0:
            out[i] = raw
        elif ftype == 1:
            out[i] = (raw + a) & 0xFF
        elif ftype == 2:
            out[i] = (raw + b) & 0xFF
        elif ftype == 3:
            out[i] = (raw + (a + b) // 2) & 0xFF
        else:  # Paeth
            out[i] = (raw + _paeth(a, b, c)) & 0xFF
    return bytes(out)


# ── Public API ─────────────────────────────────────────────────────────────────

def make_placeholder_png(width: int = 200, height: int = 200, color: tuple = (180, 180, 180)) -> bytes:
    """Return raw bytes of a solid-color RGB PNG image."""
    r, g, b = color
    rows = [bytes([r, g, b] * width) for _ in range(height)]
    return _encode_png_rows(rows, width, height, color_type=2)


def make_thumbnail(data: bytes, max_size: int = 100) -> bytes:
    """
    Create a thumbnail from PNG bytes using stdlib only (nearest-neighbor resize).
    Falls back to a gray placeholder if input is not a valid PNG or uses unsupported features.
    """
    if not data.startswith(_PNG_SIG):
        return make_placeholder_png(max_size, max_size, (180, 180, 180))

    try:
        # ── Parse chunks ──
        pos = 8
        idat_raw = b""
        ihdr_data = None
        while pos < len(data):
            length = struct.unpack(">I", data[pos:pos + 4])[0]
            ctype = data[pos + 4:pos + 8]
            cdata = data[pos + 8:pos + 8 + length]
            pos += 12 + length
            if ctype == b"IHDR":
                ihdr_data = cdata
            elif ctype == b"IDAT":
                idat_raw += cdata
            elif ctype == b"IEND":
                break

        if not ihdr_data:
            raise ValueError("No IHDR")

        width, height = struct.unpack(">II", ihdr_data[:8])
        color_type = ihdr_data[9]
        bpp = {0: 1, 2: 3, 6: 4}.get(color_type)
        if bpp is None:
            raise ValueError(f"Unsupported color_type {color_type}")

        # ── Decompress and reconstruct rows ──
        raw = zlib.decompress(idat_raw)
        stride = width * bpp
        rows: list[bytes] = []
        prev = bytes(stride)
        rpos = 0
        for _ in range(height):
            ftype = raw[rpos]
            rpos += 1
            scanline = raw[rpos:rpos + stride]
            rpos += stride
            reconstructed = _reconstruct_row(ftype, scanline, prev, bpp)
            rows.append(reconstructed)
            prev = reconstructed

        # ── Scale ──
        scale = max_size / max(width, height)
        if scale >= 1.0:
            return data  # already small enough

        new_w = max(1, int(width * scale))
        new_h = max(1, int(height * scale))

        new_rows = []
        for y in range(new_h):
            src_y = int(y * height / new_h)
            src_row = rows[src_y]
            new_row = bytearray()
            for x in range(new_w):
                src_x = int(x * width / new_w) * bpp
                new_row.extend(src_row[src_x:src_x + bpp])
            new_rows.append(bytes(new_row))

        return _encode_png_rows(new_rows, new_w, new_h, color_type)

    except Exception:
        return make_placeholder_png(max_size, max_size, (180, 180, 180))
