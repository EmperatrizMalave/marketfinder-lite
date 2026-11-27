"""Ventana principal de MarketFinder Lite."""

from __future__ import annotations

import customtkinter as ctk

from marketfinder.config import theme
from marketfinder.config.settings import Settings
from marketfinder.ui.sidebar import Sidebar
from marketfinder.ui.views.home import HomeView


class MainWindow(ctk.CTk):
    """Shell de la aplicación: sidebar + área de contenido."""

    def __init__(self, settings: Settings | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.settings = settings or Settings()

        self.title(self.settings.app_name)
        self.geometry("1100x680")
        self.minsize(900, 560)
        self.configure(fg_color=theme.BG)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, on_select=self._on_section)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.content = ctk.CTkFrame(self, fg_color=theme.BG, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self._current_view: ctk.CTkFrame | None = None
        self._show_home()

    def _clear_content(self) -> None:
        if self._current_view is not None:
            self._current_view.destroy()
            self._current_view = None

    def _show_home(self) -> None:
        self._clear_content()
        view = HomeView(self.content, settings=self.settings)
        view.grid(row=0, column=0, sticky="nsew")
        self._current_view = view

    def _on_section(self, key: str) -> None:
        # Etapa 0: solo Inicio; el resto está deshabilitado en el sidebar
        if key == "inicio":
            self._show_home()
