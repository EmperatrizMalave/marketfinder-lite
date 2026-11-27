"""Menú lateral con las secciones de MarketFinder Lite."""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from marketfinder.config import theme

# Etapa 1: Inicio + Productos + Proveedores + Rentabilidad + Ranking + Config
SECTIONS: list[tuple[str, str, bool]] = [
    ("inicio", "Inicio", True),
    ("productos", "Productos", True),
    ("proveedores", "Proveedores", True),
    ("rentabilidad", "Rentabilidad", True),
    ("ranking", "Ranking", True),
    ("investigacion", "Investigación", False),
    ("demanda", "Demanda", False),
    ("historial", "Historial", False),
    ("comparar_excel", "Comparar Excel", False),
    ("reportes", "Reportes", False),
    ("configuracion", "Configuración", True),
]


class Sidebar(ctk.CTkFrame):
    """Barra lateral con navegación."""

    def __init__(
        self,
        master: ctk.CTk | ctk.CTkFrame,
        on_select: Callable[[str], None],
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            fg_color=theme.PANEL,
            corner_radius=0,
            width=220,
            **kwargs,
        )
        self.on_select = on_select
        self._buttons: dict[str, ctk.CTkButton] = {}
        self._active = "inicio"

        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(99, weight=1)

        title = ctk.CTkLabel(
            self,
            text="MarketFinder Lite",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=16, weight="bold"),
            text_color=theme.PRIMARY,
            anchor="w",
        )
        title.grid(row=0, column=0, padx=16, pady=(20, 8), sticky="ew")

        subtitle = ctk.CTkLabel(
            self,
            text="Etapa 1 · Núcleo offline",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        )
        subtitle.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="ew")

        for i, (key, label, enabled) in enumerate(SECTIONS, start=2):
            btn = ctk.CTkButton(
                self,
                text=label if enabled else f"{label}  · Próximamente",
                anchor="w",
                height=36,
                corner_radius=8,
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
                fg_color=theme.SIDEBAR_ACTIVE if key == "inicio" else "transparent",
                hover_color=theme.BORDER,
                text_color=theme.TEXT if enabled else theme.TEXT_MUTED,
                state="normal" if enabled else "disabled",
                command=(lambda k=key: self._handle_click(k)),
            )
            btn.grid(row=i, column=0, padx=10, pady=3, sticky="ew")
            self._buttons[key] = btn

    def _handle_click(self, key: str) -> None:
        self.set_active(key)
        self.on_select(key)

    def set_active(self, key: str) -> None:
        self._active = key
        for k, btn in self._buttons.items():
            if k == key:
                btn.configure(fg_color=theme.SIDEBAR_ACTIVE, text_color=theme.TEXT)
            else:
                enabled = next(e for kk, _, e in SECTIONS if kk == k)
                btn.configure(
                    fg_color="transparent",
                    text_color=theme.TEXT if enabled else theme.TEXT_MUTED,
                )
