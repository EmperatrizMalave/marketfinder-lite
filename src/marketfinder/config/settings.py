"""Carga de configuración desde variables de entorno / .env."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Raíz del repo (…/marketfinder-lite)
PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    """Ajustes de aplicación (sin llamadas a APIs en Etapa 1)."""

    app_name: str = "MarketFinder Lite"
    app_env: str = "development"
    ml_site_id: str = "MLM"
    ml_client_id: str = ""
    ml_client_secret: str = ""
    ml_access_token: str = ""
    ml_refresh_token: str = ""
    project_root: Path = PROJECT_ROOT
    data_dir: Path | None = None  # override APPDATA (tests)

    @property
    def has_ml_credentials(self) -> bool:
        """True solo si hay identificadores básicos; no implica token válido."""
        return bool(self.ml_client_id and self.ml_client_secret)


def load_settings(env_file: Path | None = None) -> Settings:
    """Lee `.env` si existe y construye Settings. No inventa secretos."""
    path = env_file or (PROJECT_ROOT / ".env")
    if path.is_file():
        load_dotenv(path)
    else:
        # Permite variables ya presentes en el entorno del proceso
        load_dotenv(override=False)

    data_override = os.getenv("MARKETFINDER_DATA_DIR")
    return Settings(
        app_name=os.getenv("APP_NAME", "MarketFinder Lite"),
        app_env=os.getenv("APP_ENV", "development"),
        ml_site_id=os.getenv("ML_SITE_ID", "MLM"),
        ml_client_id=os.getenv("ML_CLIENT_ID", ""),
        ml_client_secret=os.getenv("ML_CLIENT_SECRET", ""),
        ml_access_token=os.getenv("ML_ACCESS_TOKEN", ""),
        ml_refresh_token=os.getenv("ML_REFRESH_TOKEN", ""),
        project_root=PROJECT_ROOT,
        data_dir=Path(data_override) if data_override else None,
    )
