"""
VŌCIS RECITĀTIŌ — Launcher entry shim
======================================
The real app lives in src/. This shim puts src/ on sys.path and hands off to
src/main.py, so the flat sibling imports (from config import ..., etc.) keep
working unchanged.

This file is run by the Launcher (it's the manifest "main"). It is NOT the
MicroPython auto-run /boot.py — that only applies to a file at the flash root,
not to an app folder on the SD card.

This is free and unencumbered software released into the public domain.
See UNLICENSE for details.
"""

import sys

# Resolve this file's own directory so src/ is found no matter what the
# Launcher sets as the current working directory.
try:
    _path = __file__
except NameError:
    _path = ""

if "/" in _path:
    _here = _path.rsplit("/", 1)[0]
else:
    _here = "."

_src = _here + "/src"
if _src not in sys.path:
    sys.path.insert(0, _src)

import main  # src/main.py

if __name__ == "__main__":
    main.main()
