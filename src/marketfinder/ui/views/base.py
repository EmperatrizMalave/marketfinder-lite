"""Contenedor base con scroll — evita recorte horizontal y permite resize."""

from __future__ import annotations

import customtkinter as ctk

from marketfinder.config import theme


def apply_wraplength(widget: ctk.CTkBaseClass | ctk.CTkFrame, width: int) -> None:
    """Ajusta wraplength en labels anidados (evita recorte al estrechar ventana)."""
    if isinstance(widget, ctk.CTkLabel):
        try:
            widget.configure(wraplength=width)
        except Exception:
            pass
        return
    try:
        children = widget.winfo_children()
    except Exception:
        return
    for child in children:
        apply_wraplength(child, width)


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

        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event=None) -> None:
        # Ignorar eventos de hijos muy pequeños; usar ancho de esta vista
        if event is not None and event.widget is not self:
            return
        width = max(self.winfo_width() - 64, 280)
        apply_wraplength(self.body, width)
