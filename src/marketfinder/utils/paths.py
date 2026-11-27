"""Rutas de datos de usuario (%APPDATA%\\MarketFinderLite)."""

from __future__ import annotations

import os
from pathlib import Path


APP_DIR_NAME = "MarketFinderLite"


def user_data_dir(override: Path | str | None = None) -> Path:
    """Directorio raíz de datos de usuario.

    Override útil en tests (tmp_path). En Windows: %APPDATA%\\MarketFinderLite.
    """
    if override is not None:
        path = Path(override)
    else:
        env = os.environ.get("MARKETFINDER_DATA_DIR")
        if env:
            path = Path(env)
        else:
            appdata = os.environ.get("APPDATA")
            if appdata:
                path = Path(appdata) / APP_DIR_NAME
            else:
                path = Path.home() / f".{APP_DIR_NAME.lower()}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path(override_dir: Path | str | None = None) -> Path:
    return user_data_dir(override_dir) / "marketfinder.db"


def logs_dir(override_dir: Path | str | None = None) -> Path:
    path = user_data_dir(override_dir) / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def exports_dir(override_dir: Path | str | None = None) -> Path:
    path = user_data_dir(override_dir) / "exports"
    path.mkdir(parents=True, exist_ok=True)
    return path
