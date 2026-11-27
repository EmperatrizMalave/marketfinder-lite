"""Ventana principal de MarketFinder Lite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import customtkinter as ctk

from marketfinder.config import theme
from marketfinder.config.settings import Settings
from marketfinder.data.db import initialize_db
from marketfinder.data.repositories import ProductRepository
from marketfinder.ui.sidebar import Sidebar
from marketfinder.ui.views.config_view import ConfigView
from marketfinder.ui.views.home import HomeView
from marketfinder.ui.views.products import ProductsView
from marketfinder.ui.views.profitability import ProfitabilityView
from marketfinder.ui.views.ranking import RankingView
from marketfinder.ui.views.suppliers import SuppliersView
from marketfinder.utils.logging import setup_logging
from marketfinder.utils.paths import db_path


class MainWindow(ctk.CTk):
    """Shell de la aplicación: sidebar + área de contenido con scroll."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        conn: sqlite3.Connection | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.settings = settings or Settings()
        self.data_dir: Path | None = self.settings.data_dir

        setup_logging(data_dir=self.data_dir)
        self.conn = conn or initialize_db(db_path(self.data_dir))

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

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _clear_content(self) -> None:
        if self._current_view is not None:
            self._current_view.destroy()
            self._current_view = None

    def _show(self, view: ctk.CTkFrame) -> None:
        self._clear_content()
        view.grid(row=0, column=0, sticky="nsew")
        self._current_view = view

    def _show_home(self) -> None:
        count = ProductRepository(self.conn).count()
        self._show(HomeView(self.content, settings=self.settings, product_count=count))

    def _on_section(self, key: str) -> None:
        if key == "inicio":
            self._show_home()
        elif key == "productos":
            self._show(ProductsView(self.content, conn=self.conn))
        elif key == "proveedores":
            self._show(SuppliersView(self.content, conn=self.conn))
        elif key == "rentabilidad":
            self._show(ProfitabilityView(self.content, conn=self.conn))
        elif key == "ranking":
            self._show(RankingView(self.content, conn=self.conn, data_dir=self.data_dir))
        elif key == "configuracion":
            self._show(ConfigView(self.content, conn=self.conn, data_dir=self.data_dir))

    def _on_close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass
        self.destroy()
