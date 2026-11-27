"""Vista de inicio — Etapa 1."""

from __future__ import annotations

import customtkinter as ctk

from marketfinder.config import theme
from marketfinder.config.settings import Settings
from marketfinder.utils.paths import db_path, user_data_dir


class HomeView(ctk.CTkFrame):
    """Panel de inicio con estado vacío / pendiente."""

    def __init__(
        self,
        master: ctk.CTk | ctk.CTkFrame,
        settings: Settings,
        *,
        product_count: int = 0,
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color=theme.BG, **kwargs)
        self.settings = settings
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG, corner_radius=0)
        scroll.grid(row=0, column=0, sticky="nsew", rowspan=3)
        scroll.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        heading = ctk.CTkLabel(
            scroll,
            text="Inicio",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=24, weight="bold"),
            text_color=theme.TEXT,
            anchor="w",
        )
        heading.grid(row=0, column=0, padx=28, pady=(28, 4), sticky="ew")

        intro = ctk.CTkLabel(
            scroll,
            text=(
                "MarketFinder Lite — Etapa 1 (núcleo offline): productos, proveedores, "
                "calculadora, ranking y presupuesto local en SQLite. "
                "Sin API Mercado Libre, sin web, sin pagos."
            ),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=13),
            text_color=theme.TEXT_MUTED,
            wraplength=640,
            justify="left",
            anchor="w",
        )
        intro.grid(row=1, column=0, padx=28, pady=(0, 20), sticky="ew")

        cards = ctk.CTkFrame(scroll, fg_color="transparent")
        cards.grid(row=2, column=0, padx=28, pady=8, sticky="ew")
        cards.grid_columnconfigure((0, 1), weight=1)

        self._stat_card(
            cards,
            row=0,
            col=0,
            title="Productos en seguimiento",
            value=str(product_count),
            hint="CRUD en sección Productos",
        )
        fuente_estado = (
            "Credenciales presentes (no verificadas)"
            if settings.has_ml_credentials
            else "Pendiente — sin app/credenciales (OK en Etapa 1)"
        )
        self._stat_card(
            cards,
            row=0,
            col=1,
            title="Estado de fuentes",
            value="Offline",
            hint=fuente_estado,
            value_color=theme.WARNING,
        )

        note = ctk.CTkLabel(
            scroll,
            text=(
                f"Datos de usuario: {user_data_dir(settings.data_dir)}\n"
                f"Base de datos: {db_path(settings.data_dir)}\n"
                "Usa Configuración para fees y presupuesto. "
                "Los datos de prueba deben etiquetarse como ficticios."
            ),
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.TEXT_MUTED,
            wraplength=640,
            justify="left",
            anchor="w",
        )
        note.grid(row=3, column=0, padx=28, pady=(24, 12), sticky="ew")

        self.bind("<Configure>", lambda e: intro.configure(wraplength=max(e.width - 80, 320)))

    def _stat_card(
        self,
        parent: ctk.CTkFrame,
        *,
        row: int,
        col: int,
        title: str,
        value: str,
        hint: str,
        value_color: str | None = None,
    ) -> None:
        card = ctk.CTkFrame(
            parent,
            fg_color=theme.PANEL,
            corner_radius=12,
            border_width=1,
            border_color=theme.BORDER,
        )
        card.grid(row=row, column=col, padx=(0, 12) if col == 0 else (12, 0), pady=4, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=0, column=0, padx=18, pady=(16, 4), sticky="ew")

        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=28, weight="bold"),
            text_color=value_color or theme.PRIMARY,
            anchor="w",
        ).grid(row=1, column=0, padx=18, pady=(0, 4), sticky="ew")

        ctk.CTkLabel(
            card,
            text=hint,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11),
            text_color=theme.TEXT_MUTED,
            anchor="w",
            wraplength=280,
        ).grid(row=2, column=0, padx=18, pady=(0, 16), sticky="ew")
