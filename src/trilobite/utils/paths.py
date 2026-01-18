from __future__ import annotations

from pathlib import Path

def project_root() -> Path:
    """
    Returns the root directory of the project. Assumes this file lives at 
    src/trilobite/utils/paths.py
    """
    return Path(__file__).resolve().parents[3]

def logs_dir(create: bool = True) -> Path:
    """
    Returns a path object for the logs directory
    """
    path = project_root() / "logs"
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path

def data_dir(create: bool = True) -> Path:
    """
    Returns a path object for the data directory
    """
    path = project_root() / "data"
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path

def exports_dir(create: bool = True) -> Path:
    """
    Returns a path object for the exports directory
    """
    path = project_root() / "exports"
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path

def tmp_dir(create: bool = True) -> Path:
    """
    Returns a path object for the tmp directory
    """
    path = project_root() / "tmp"
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path
