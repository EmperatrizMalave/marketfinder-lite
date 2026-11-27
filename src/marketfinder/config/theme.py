"""Paleta y apariencia visual de MarketFinder Lite."""

from __future__ import annotations

import customtkinter as ctk

# Colores de marca (Etapa 0)
BG = "#10151D"
PANEL = "#1A222E"
PRIMARY = "#49DBA0"
TEXT = "#FFFFFF"
TEXT_MUTED = "#9AA4B2"
WARNING = "#F5C542"
ERROR = "#E85D5D"
BORDER = "#2A3545"
SIDEBAR_ACTIVE = "#243041"

FONT_FAMILY = "Segoe UI"


def apply_theme() -> None:
    """Aplica modo oscuro y color de acento globales de CustomTkinter."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


def color_map() -> dict[str, str]:
    """Diccionario de constantes de color (útil en pruebas y UI)."""
    return {
        "bg": BG,
        "panel": PANEL,
        "primary": PRIMARY,
        "text": TEXT,
        "text_muted": TEXT_MUTED,
        "warning": WARNING,
        "error": ERROR,
        "border": BORDER,
        "sidebar_active": SIDEBAR_ACTIVE,
    }
