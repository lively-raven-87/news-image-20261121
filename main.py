#!/usr/bin/env python3
"""Deliver the entry image for 'The World — 21 November 2026'.

Stdlib only: reads entry.png beside this file, checks it is a whole PNG
(signature, every chunk's CRC, dimensions, size cap), then copies it to
/output/entry.png and re-reads the copy to prove the copy is complete.
Exits non-zero on any failure.
"""

import os
import shutil
import struct
import sys
import zlib

LIMIT_BYTES = 1024 * 1024
LIMIT_SIDE = 1024
MAGIC = b"\x89PNG\r\n\x1a\n"


def die(msg):
    print("FAIL:", msg, file=sys.stderr)
    sys.exit(1)


def check_signature(blob):
    if len(blob) < 8 or blob[:8] != MAGIC:
        die("not a PNG (bad signature)")


def walk_chunks(blob):
    """Verify every chunk's CRC; return (width, height) from IHDR."""
    pos = 8
    dims = None
    closed = False
    while pos < len(blob):
        if pos + 8 > len(blob):
            die("chunk header cut off at %d" % pos)
        size = struct.unpack(">I", blob[pos:pos + 4])[0]
        kind = blob[pos + 4:pos + 8]
        stop = pos + 12 + size
        if stop > len(blob):
            die("chunk %r cut off at %d" % (kind, pos))
        payload = blob[pos + 8:pos + 8 + size]
        want = struct.unpack(">I", blob[pos + 8 + size:stop])[0]
        got = zlib.crc32(payload, zlib.crc32(kind)) & 0xFFFFFFFF
        if got != want:
            die("CRC mismatch in %r at %d" % (kind, pos))
        if kind == b"IHDR":
            if size != 13:
                die("IHDR length %d, expected 13" % size)
            dims = struct.unpack(">II", payload[:8])
        elif kind == b"IEND":
            closed = True
            break
        pos = stop
    if dims is None:
        die("no IHDR chunk")
    if not closed:
        die("no IEND chunk")
    return dims


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(base, "entry.png")
    if not os.path.isfile(src):
        die("entry.png missing: %s" % src)
    nbytes = os.path.getsize(src)
    if nbytes > LIMIT_BYTES:
        die("entry.png %d bytes, over 1 MiB" % nbytes)
    with open(src, "rb") as fh:
        blob = fh.read()
    check_signature(blob)
    width, height = walk_chunks(blob)
    if width > LIMIT_SIDE or height > LIMIT_SIDE:
        die("size %dx%d over %dx%d" % (width, height, LIMIT_SIDE,
                                       LIMIT_SIDE))
    if width <= 0 or height <= 0:
        die("bad size %dx%d" % (width, height))

    os.makedirs("/output", exist_ok=True)
    dst = os.path.join("/output", "entry.png")
    shutil.copyfile(src, dst)
    with open(dst, "rb") as fh:
        back = fh.read()
    if back != blob:
        die("copy to %s differs from source" % dst)
    # Re-check the copy's dimensions too: the delivered file must be
    # the same valid image, not just the same bytes on disk.
    back_w, back_h = walk_chunks(back)
    if (back_w, back_h) != (width, height):
        die("copy dimensions %dx%d differ from %dx%d"
            % (back_w, back_h, width, height))

    print("OK: entry.png %dx%d, %d bytes -> %s"
          % (width, height, nbytes, dst))
    return 0


if __name__ == "__main__":
    sys.exit(main())
