"""FastAPI entrypoint.

The repo previously exposed the ASGI app at the project root (main.py).
Some runners (and docs) expect it at `app.main:app`.
"""

from __future__ import annotations

import importlib

_main = importlib.import_module("main")
app = _main.app

