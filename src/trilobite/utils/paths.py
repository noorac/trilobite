from __future__ import annotations

from pathlib import Path

def project_root() -> Path:
    """
    Returns the root directory of the project. Assumes this file lives at 
    src/trilobite/utils/paths.py
    """
    return Path(__file__).resolve().parents[3]


