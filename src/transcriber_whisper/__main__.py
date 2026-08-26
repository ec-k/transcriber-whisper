"""Entry point for `python -m transcriber_whisper` and for the Nuitka build."""

from __future__ import annotations

import sys

from transcriber_whisper.cli import main

if __name__ == "__main__":
    sys.exit(main())
