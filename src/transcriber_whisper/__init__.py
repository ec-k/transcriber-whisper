"""Package init that makes the pip-installed CUDA runtime loadable.

ctranslate2 resolves cublas/cudnn through the OS loader, so the DLL
directories must be registered before faster_whisper is imported.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _register_cuda_dlls() -> None:
    if sys.platform != "win32":
        return

    import nvidia

    for root in nvidia.__path__:
        for bin_dir in sorted(Path(root).glob("*/bin")):
            os.add_dll_directory(str(bin_dir))
            os.environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ['PATH']}"


_register_cuda_dlls()
