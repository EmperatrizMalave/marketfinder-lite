"""Contenedor base con scroll — evita recorte horizontal y permite resize."""

from __future__ import annotations

import customtkinter as ctk

from marketfinder.config import theme


class ScrollableView(ctk.CTkFrame):
    """Vista con CTkScrollableFrame que se estira con la ventana."""

    def __init__(self, master: ctk.CTk | ctk.CTkFrame, title: str, **kwargs) -> None:
        super().__init__(master, fg_color=theme.BG, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        heading = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=theme.TEXT,
            anchor="w",
        )
        heading.grid(row=0, column=0, padx=20, pady=(16, 4), sticky="ew")

        self.body = ctk.CTkScrollableFrame(
            self,
            fg_color=theme.BG,
            corner_radius=0,
        )
        self.body.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.body.grid_columnconfigure(0, weight=1)

        # Reajustar wrap al cambiar tamaño (evita recorte de texto)
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, _event=None) -> None:
        width = max(self.winfo_width() - 80, 320)
        for child in self.body.winfo_children():
            if isinstance(child, ctk.CTkLabel):
                try:
                    child.configure(wraplength=width)
                except Exception:
                    pass
