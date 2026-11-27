"""Arranque de la aplicación MarketFinder Lite."""

from __future__ import annotations

import customtkinter as ctk

from marketfinder.config.settings import load_settings
from marketfinder.config.theme import apply_theme
from marketfinder.ui.main_window import MainWindow


def create_app() -> MainWindow:
    """Construye la ventana principal sin entrar al mainloop (útil en pruebas)."""
    settings = load_settings()
    apply_theme()
    return MainWindow(settings=settings)


def main() -> None:
    """Punto de entrada de la GUI."""
    app = create_app()
    app.mainloop()


if __name__ == "__main__":
    main()
