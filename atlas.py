"""Namespace shim for Atlas Python modules.

This repo already contains an executable named ``atlas``. Exposing a module
file with ``__path__`` lets tests import ``atlas.plant_intel`` without
disturbing the existing shell script.
"""

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parent / "atlas_pkg")]
