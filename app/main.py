"""FastAPI entrypoint.

The repo previously exposed the ASGI app at the project root (main.py).
Some runners (and docs) expect it at `app.main:app`.
"""

from __future__ import annotations

import importlib


# Re-export the FastAPI instance from the top-level `main.py`.
# This keeps backward compatibility while satisfying `uvicorn app.main:app`.
_main = importlib.import_module("main")
app = _main.app

