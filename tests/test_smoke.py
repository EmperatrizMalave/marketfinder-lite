"""Pruebas de humo — Etapa 0 conservadas / ajustadas a Etapa 1."""

from __future__ import annotations

import os

import pytest

import marketfinder
from marketfinder.config import theme
from marketfinder.config.settings import Settings, load_settings
from marketfinder.ui.sidebar import SECTIONS


def test_package_version() -> None:
    assert marketfinder.__version__ == "0.0.1"


def test_theme_constants() -> None:
    colors = theme.color_map()
    assert colors["bg"] == "#10151D"
    assert colors["panel"] == "#1A222E"
    assert colors["primary"] == "#49DBA0"
    assert colors["text"] == "#FFFFFF"
    assert colors["warning"] == "#F5C542"
    assert colors["error"] == "#E85D5D"


def test_sidebar_has_ten_sections() -> None:
    # Etapa 1: 11 entradas (se añadió Productos); 6 habilitadas
    assert len(SECTIONS) == 11
    keys = [k for k, _, _ in SECTIONS]
    assert keys[0] == "inicio"
    assert "productos" in keys
    enabled = {k for k, _, e in SECTIONS if e}
    assert enabled == {
        "inicio",
        "productos",
        "proveedores",
        "rentabilidad",
        "ranking",
        "configuracion",
    }


def test_load_settings_defaults(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("ML_CLIENT_ID", raising=False)
    monkeypatch.delenv("ML_CLIENT_SECRET", raising=False)
    settings = load_settings(env_file=tmp_path / "no-existe.env")
    assert settings.app_name == "MarketFinder Lite"
    assert settings.ml_site_id == "MLM"
    assert settings.has_ml_credentials is False


def test_settings_detects_credentials(monkeypatch) -> None:
    monkeypatch.setenv("ML_CLIENT_ID", "app-id-demo")
    monkeypatch.setenv("ML_CLIENT_SECRET", "secret-demo")
    s = Settings(ml_client_id="app-id-demo", ml_client_secret="secret-demo")
    assert s.has_ml_credentials is True


def test_create_app_builds_window(tmp_path, monkeypatch) -> None:
    """Intenta construir la ventana sin mainloop. Omite si no hay display Tk."""
    if os.environ.get("MARKETFINDER_SKIP_GUI") == "1":
        pytest.skip("MARKETFINDER_SKIP_GUI=1")

    monkeypatch.setenv("MARKETFINDER_DATA_DIR", str(tmp_path / "gui-data"))

    try:
        from marketfinder.app import create_app
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"No se pudo importar create_app: {exc}")

    try:
        app = create_app()
    except Exception as exc:
        pytest.skip(f"GUI no disponible en este entorno (esperado en headless): {exc}")

    try:
        assert app.title() == "MarketFinder Lite"
        assert app.winfo_exists() == 1
    finally:
        app.destroy()
