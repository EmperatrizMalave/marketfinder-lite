"""Configuración: parámetros comerciales, fees y diagnóstico de rutas."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

import customtkinter as ctk

from marketfinder.config import theme
from marketfinder.core.models import COMMERCIAL_DEFAULTS
from marketfinder.data.repositories import FeeProfileRepository, SettingsRepository, WeightsRepository
from marketfinder.ui.views.base import ScrollableView
from marketfinder.utils.paths import db_path, exports_dir, logs_dir, user_data_dir


class ConfigView(ScrollableView):
    def __init__(self, master, *, conn, data_dir=None, **kwargs) -> None:
        super().__init__(master, title="Configuración", **kwargs)
        self.conn = conn
        self.data_dir = data_dir
        self.settings = SettingsRepository(conn)
        self.fees = FeeProfileRepository(conn)
        self.weights = WeightsRepository(conn)
        self._vars: dict[str, ctk.StringVar] = {}
        self._fee_vars: dict[str, ctk.StringVar] = {}
        self._build()

    def _build(self) -> None:
        # Diagnóstico de almacenamiento (rutas técnicas)
        diag = ctk.CTkFrame(
            self.body,
            fg_color=theme.PANEL,
            corner_radius=10,
            border_width=1,
            border_color=theme.BORDER,
        )
        diag.grid(row=0, column=0, sticky="ew", padx=12, pady=8)
        diag.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(diag, text="Diagnóstico de almacenamiento", text_color=theme.PRIMARY).grid(
            row=0, column=0, padx=12, pady=(10, 4), sticky="w"
        )
        ctk.CTkLabel(
            diag,
            text=(
                f"AppData / datos: {user_data_dir(self.data_dir)}\n"
                f"Base de datos (SQLite): {db_path(self.data_dir)}\n"
                f"Logs: {logs_dir(self.data_dir)}\n"
                f"Exports: {exports_dir(self.data_dir)}\n"
                "Override de tests: variable de entorno MARKETFINDER_DATA_DIR."
            ),
            text_color=theme.TEXT_MUTED,
            justify="left",
            anchor="w",
            wraplength=520,
        ).grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")

        warn = ctk.CTkLabel(
            self.body,
            text=(
                "Fees = parámetros editables (verificar en ML / SAT). "
                "No son tarifas oficiales. Presupuesto $0 de infra: sin servicios de pago."
            ),
            text_color=theme.WARNING,
            justify="left",
            anchor="w",
            wraplength=520,
        )
        warn.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        # Comerciales
        box = ctk.CTkFrame(
            self.body, fg_color=theme.PANEL, corner_radius=10, border_width=1, border_color=theme.BORDER
        )
        box.grid(row=2, column=0, sticky="ew", padx=12, pady=8)
        box.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(box, text="Parámetros comerciales", text_color=theme.PRIMARY).grid(
            row=0, column=0, columnspan=2, padx=12, pady=(10, 6), sticky="w"
        )
        stored = self.settings.commercial_defaults()
        for i, key in enumerate(COMMERCIAL_DEFAULTS.keys(), start=1):
            var = ctk.StringVar(value=stored.get(key, str(COMMERCIAL_DEFAULTS[key])))
            self._vars[key] = var
            ctk.CTkLabel(box, text=key, text_color=theme.TEXT_MUTED).grid(
                row=i, column=0, padx=12, pady=3, sticky="w"
            )
            ctk.CTkEntry(box, textvariable=var).grid(row=i, column=1, padx=12, pady=3, sticky="ew")

        ctk.CTkButton(
            box,
            text="Guardar parámetros",
            fg_color=theme.PRIMARY,
            text_color=theme.BG,
            command=self._save_settings,
        ).grid(row=len(COMMERCIAL_DEFAULTS) + 1, column=0, columnspan=2, padx=12, pady=12, sticky="w")

        # Fees
        fee_box = ctk.CTkFrame(
            self.body, fg_color=theme.PANEL, corner_radius=10, border_width=1, border_color=theme.BORDER
        )
        fee_box.grid(row=3, column=0, sticky="ew", padx=12, pady=8)
        fee_box.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            fee_box,
            text="Perfil fees ml_mx_manual (editable)",
            text_color=theme.PRIMARY,
        ).grid(row=0, column=0, columnspan=2, padx=12, pady=(10, 6), sticky="w")

        profile = self.fees.get_by_name("ml_mx_manual")
        fee_fields = [
            ("commission_rate", profile.commission_rate if profile else "0"),
            ("payment_fee_rate", profile.payment_fee_rate if profile else "0"),
            ("shipping_cost_fixed", profile.shipping_cost_fixed if profile else "0"),
            ("shipping_cost_rate", profile.shipping_cost_rate if profile else "0"),
            ("iva_rate", profile.iva_rate if profile else "0"),
            ("retention_rate", profile.retention_rate if profile else "0"),
            ("isr_rate", profile.isr_rate if profile else "0"),
            ("other_cost_fixed", profile.other_cost_fixed if profile else "0"),
            ("other_cost_rate", profile.other_cost_rate if profile else "0"),
            ("packaging_cost_fixed", profile.packaging_cost_fixed if profile else "0"),
            ("ads_cost_rate", profile.ads_cost_rate if profile else "0"),
            ("target_margin", profile.target_margin if profile else "0.25"),
        ]
        for i, (key, val) in enumerate(fee_fields, start=1):
            var = ctk.StringVar(value=str(val))
            self._fee_vars[key] = var
            ctk.CTkLabel(fee_box, text=key, text_color=theme.TEXT_MUTED).grid(
                row=i, column=0, padx=12, pady=3, sticky="w"
            )
            ctk.CTkEntry(fee_box, textvariable=var).grid(row=i, column=1, padx=12, pady=3, sticky="ew")

        ctk.CTkButton(
            fee_box,
            text="Guardar fees",
            fg_color=theme.PRIMARY,
            text_color=theme.BG,
            command=self._save_fees,
        ).grid(row=len(fee_fields) + 1, column=0, columnspan=2, padx=12, pady=12, sticky="w")

        w = self.weights.get()
        weights_lbl = ctk.CTkLabel(
            self.body,
            text=f"Pesos ranking (fijos Etapa 1): {w.as_dict()}  total={w.total()}",
            text_color=theme.TEXT_MUTED,
            anchor="w",
            wraplength=520,
        )
        weights_lbl.grid(row=4, column=0, sticky="ew", padx=12, pady=8)

        self.status = ctk.CTkLabel(self.body, text="", text_color=theme.TEXT_MUTED, anchor="w")
        self.status.grid(row=5, column=0, sticky="ew", padx=12, pady=8)

    def _save_settings(self) -> None:
        for key, var in self._vars.items():
            self.settings.set(key, var.get().strip())
        self.status.configure(text="Parámetros guardados", text_color=theme.PRIMARY)

    def _save_fees(self) -> None:
        profile = self.fees.get_by_name("ml_mx_manual")
        if profile is None:
            self.status.configure(text="Perfil no encontrado", text_color=theme.ERROR)
            return
        try:
            profile.commission_rate = Decimal(self._fee_vars["commission_rate"].get())
            profile.payment_fee_rate = Decimal(self._fee_vars["payment_fee_rate"].get())
            profile.shipping_cost_fixed = Decimal(self._fee_vars["shipping_cost_fixed"].get())
            profile.shipping_cost_rate = Decimal(self._fee_vars["shipping_cost_rate"].get())
            profile.iva_rate = Decimal(self._fee_vars["iva_rate"].get())
            profile.retention_rate = Decimal(self._fee_vars["retention_rate"].get())
            profile.isr_rate = Decimal(self._fee_vars["isr_rate"].get())
            profile.other_cost_fixed = Decimal(self._fee_vars["other_cost_fixed"].get())
            profile.other_cost_rate = Decimal(self._fee_vars["other_cost_rate"].get())
            profile.packaging_cost_fixed = Decimal(self._fee_vars["packaging_cost_fixed"].get())
            profile.ads_cost_rate = Decimal(self._fee_vars["ads_cost_rate"].get())
            profile.target_margin = Decimal(self._fee_vars["target_margin"].get())
            profile.notes = (
                "Parámetro editable — verificar en ML / SAT. No es tarifa oficial."
            )
        except (InvalidOperation, KeyError) as exc:
            self.status.configure(text=f"Error: {exc}", text_color=theme.ERROR)
            return
        self.fees.update(profile)
        self.status.configure(text="Fees guardados", text_color=theme.PRIMARY)
