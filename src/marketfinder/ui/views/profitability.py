"""Calculadora de rentabilidad + escenarios."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

import customtkinter as ctk

from marketfinder.config import theme
from marketfinder.core.models import ScenarioName
from marketfinder.core.profitability import (
    calculate_all_scenarios,
    calculate_profit,
    min_price_break_even,
    min_price_for_target_margin,
)
from marketfinder.data.repositories import FeeProfileRepository
from marketfinder.ui.views.base import ScrollableView


class ProfitabilityView(ScrollableView):
    def __init__(self, master, *, conn, **kwargs) -> None:
        super().__init__(master, title="Rentabilidad", **kwargs)
        self.fees_repo = FeeProfileRepository(conn)
        self._build()

    def _build(self) -> None:
        warn = ctk.CTkLabel(
            self.body,
            text=(
                "Parámetros editables — verificar en ML / SAT. "
                "No son tarifas oficiales. Escenarios ilustrativos; no garantizan ganancias. "
                "Si falta costo o precio, no se inventa 0."
            ),
            text_color=theme.WARNING,
            justify="left",
            anchor="w",
        )
        warn.grid(row=0, column=0, sticky="ew", padx=12, pady=8)

        form = ctk.CTkFrame(
            self.body, fg_color=theme.PANEL, corner_radius=10, border_width=1, border_color=theme.BORDER
        )
        form.grid(row=1, column=0, sticky="ew", padx=12, pady=8)
        form.grid_columnconfigure((1, 3), weight=1)

        self.cost_var = ctk.StringVar(value="25")
        self.price_var = ctk.StringVar(value="199")
        self.qty_var = ctk.StringVar(value="10")

        self._field(form, 0, 0, "Costo unitario", self.cost_var)
        self._field(form, 0, 2, "Precio venta", self.price_var)
        self._field(form, 1, 0, "Cantidad", self.qty_var)

        ctk.CTkButton(
            form,
            text="Calcular escenarios",
            fg_color=theme.PRIMARY,
            text_color=theme.BG,
            command=self._calculate,
        ).grid(row=2, column=0, columnspan=2, padx=12, pady=12, sticky="w")

        self.out = ctk.CTkTextbox(self.body, height=360, fg_color=theme.PANEL, text_color=theme.TEXT)
        self.out.grid(row=2, column=0, sticky="nsew", padx=12, pady=8)
        self.body.grid_rowconfigure(2, weight=1)

        profile = self.fees_repo.get_by_name("ml_mx_manual")
        if profile:
            self.out.insert(
                "1.0",
                f"Perfil fees: {profile.name}\n"
                f"Comisión={profile.commission_rate}  IVA={profile.iva_rate}  "
                f"Ret={profile.retention_rate}  ISR={profile.isr_rate}\n"
                f"Margen objetivo={profile.target_margin}\n"
                f"Nota: {profile.notes}\n\n"
                "Pulsa Calcular escenarios.\n",
            )

    def _field(self, parent, row, col, label, var):
        ctk.CTkLabel(parent, text=label, text_color=theme.TEXT_MUTED).grid(
            row=row, column=col, padx=12, pady=6, sticky="w"
        )
        ctk.CTkEntry(parent, textvariable=var).grid(
            row=row, column=col + 1, padx=8, pady=6, sticky="ew"
        )

    def _parse(self, raw: str) -> Decimal | None:
        raw = raw.strip()
        if not raw:
            return None
        try:
            return Decimal(raw)
        except InvalidOperation:
            raise ValueError(f"Número inválido: {raw}")

    def _calculate(self) -> None:
        self.out.delete("1.0", "end")
        try:
            cost = self._parse(self.cost_var.get())
            price = self._parse(self.price_var.get())
            qty = int(self.qty_var.get().strip() or "1")
        except (ValueError, InvalidOperation) as exc:
            self.out.insert("1.0", f"Error: {exc}\n")
            return

        if cost is None or price is None:
            self.out.insert(
                "1.0",
                "Faltan costo o precio. No se calcula con ceros inventados "
                "(proveniencia pendiente).\n",
            )
            return

        fees = self.fees_repo.get_by_name("ml_mx_manual")
        if fees is None:
            self.out.insert("1.0", "No hay fee_profile sembrado.\n")
            return

        results = calculate_all_scenarios(
            unit_cost=cost, sale_price=price, fees=fees, quantity=qty
        )
        lines = [
            "=== Escenarios (ficticios / ilustrativos) ===",
            f"Entrada: C={cost}  P={price}  qty={qty}",
            f"Precio mín. break-even: {min_price_break_even(unit_cost=cost, fees=fees)}",
            f"Precio mín. margen objetivo: {min_price_for_target_margin(unit_cost=cost, fees=fees)}",
            "",
        ]
        for name, r in results.items():
            lines.append(
                f"[{name.value}] P={r.sale_price}  C={r.breakdown.unit_cost}  "
                f"util_op={r.unit_operating_profit}  util_imp={r.unit_profit_after_tax}  "
                f"margen={r.margin}  ROI_merc={r.roi_merchandise}  "
                f"cumple_objetivo={r.meets_target_margin}  capital={r.total_capital}"
            )
        # Escenario normal detalle
        normal = results.get(ScenarioName.NORMAL)
        if normal:
            lines.extend(
                [
                    "",
                    "--- Desglose costos (normal) ---",
                    f"comisión={normal.breakdown.commission}",
                    f"pago={normal.breakdown.payment_fee}",
                    f"envío={normal.breakdown.shipping}",
                    f"empaque={normal.breakdown.packaging}",
                    f"ads={normal.breakdown.ads}",
                    f"otros={normal.breakdown.other}",
                    f"IVA={normal.breakdown.iva}",
                    f"retención={normal.breakdown.retention}",
                    f"ISR={normal.breakdown.isr}",
                    "",
                    normal.disclaimer,
                ]
            )
        self.out.insert("1.0", "\n".join(lines) + "\n")
