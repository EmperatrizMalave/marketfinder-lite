"""Ranking comercial + optimizador de presupuesto + export."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import customtkinter as ctk

from marketfinder.config import theme
from marketfinder.core.budget import BudgetCandidate, optimize_budget
from marketfinder.core.models import Provenance, RankBand, ResearchItem, ResearchRun
from marketfinder.core.profitability import calculate_profit
from marketfinder.core.scoring import (
    NORMALIZATION_DOC,
    FactorScores,
    invert_0_100,
    investment_factor_from_amount,
    profitability_factor_from_margin,
    score_opportunity,
)
from marketfinder.data.excel_io import export_ranking_csv, export_ranking_xlsx
from marketfinder.data.repositories import (
    FeeProfileRepository,
    MetricsRepository,
    OfferRepository,
    ProductRepository,
    ResearchRepository,
    SettingsRepository,
    WeightsRepository,
)
from marketfinder.ui.views.base import ScrollableView


class RankingView(ScrollableView):
    def __init__(self, master, *, conn, data_dir: Path | None = None, **kwargs) -> None:
        super().__init__(master, title="Ranking", **kwargs)
        self.conn = conn
        self.data_dir = data_dir
        self.products = ProductRepository(conn)
        self.offers = OfferRepository(conn)
        self.metrics = MetricsRepository(conn)
        self.weights = WeightsRepository(conn)
        self.fees = FeeProfileRepository(conn)
        self.settings = SettingsRepository(conn)
        self.research = ResearchRepository(conn)
        self._last_rows: list[dict] = []
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(
            self.body,
            text=(
                "Score comercial ≠ confianza. Datos incompletos → pendiente "
                "(no se recomienda). Optimizador greedy = aproximación."
            ),
            text_color=theme.WARNING,
            anchor="w",
            justify="left",
        ).grid(row=0, column=0, sticky="ew", padx=12, pady=8)

        btns = ctk.CTkFrame(self.body, fg_color="transparent")
        btns.grid(row=1, column=0, sticky="w", padx=12, pady=4)
        ctk.CTkButton(
            btns, text="Calcular ranking + presupuesto", fg_color=theme.PRIMARY, text_color=theme.BG, command=self._run
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btns, text="Export CSV", fg_color=theme.BORDER, command=self._export_csv).pack(
            side="left", padx=(0, 8)
        )
        ctk.CTkButton(btns, text="Export Excel", fg_color=theme.BORDER, command=self._export_xlsx).pack(
            side="left"
        )

        self.out = ctk.CTkTextbox(self.body, height=420, fg_color=theme.PANEL, text_color=theme.TEXT)
        self.out.grid(row=2, column=0, sticky="nsew", padx=12, pady=8)
        self.body.grid_rowconfigure(2, weight=1)
        self.status = ctk.CTkLabel(self.body, text="", text_color=theme.TEXT_MUTED, anchor="w")
        self.status.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 8))

        self.out.insert("1.0", NORMALIZATION_DOC.strip() + "\n\nPulsa Calcular…\n")

    def _run(self) -> None:
        self.out.delete("1.0", "end")
        weights = self.weights.get()
        fees = self.fees.get_by_name("ml_mx_manual")
        if fees is None:
            self.out.insert("1.0", "Sin fee_profile.\n")
            return

        defaults = self.settings.commercial_defaults()
        budget = Decimal(defaults.get("budget_default", "3000"))
        reserve = Decimal(defaults.get("budget_reserve", "0"))
        qty_min = int(defaults.get("initial_qty_min", "10"))
        qty_max = int(defaults.get("initial_qty_max", "20"))

        candidates: list[BudgetCandidate] = []
        lines = [
            f"Presupuesto={budget}  reserva={reserve}  qty guías={qty_min}-{qty_max}",
            f"Pesos: {weights.as_dict()}",
            "",
        ]
        export_rows: list[dict] = []

        for product in self.products.list_all():
            assert product.id is not None
            offer_list = self.offers.list_for_product(product.id)
            offer = next((o for o in offer_list if o.is_active), None)
            m = self.metrics.latest_for_product(product.id)

            unit_cost = offer.unit_cost if offer else None
            sale_price = m.sale_price if m else None

            profit = None
            if fees and unit_cost is not None and sale_price is not None:
                profit = calculate_profit(
                    unit_cost=unit_cost, sale_price=sale_price, fees=fees, quantity=1
                )

            demand = m.demand_score if m else None
            competition_raw = m.competition_score if m else None
            logistics = m.logistics_score if m else None
            return_raw = m.return_risk_score if m else None
            investment = (
                m.investment_required
                if m and m.investment_required is not None
                else (unit_cost * qty_min if unit_cost is not None else None)
            )

            factors = FactorScores(
                demand=demand,
                profitability=profitability_factor_from_margin(profit.margin if profit else None),
                competition=invert_0_100(competition_raw),
                investment=investment_factor_from_amount(investment, budget=budget),
                logistics=logistics,
                return_risk=invert_0_100(return_raw),
            )
            provenances = {
                "demand": m.demand_provenance if m else Provenance.PENDIENTE,
                "profitability": (
                    Provenance.ESTIMADO
                    if profit
                    else Provenance.PENDIENTE
                ),
                "competition": m.competition_provenance if m else Provenance.PENDIENTE,
                "investment": m.investment_provenance if m else Provenance.PENDIENTE,
                "logistics": m.logistics_provenance if m else Provenance.PENDIENTE,
                "return_risk": m.return_risk_provenance if m else Provenance.PENDIENTE,
            }
            scored = score_opportunity(
                factors,
                weights,
                unit_cost=unit_cost,
                sale_price=sale_price,
                provenances=provenances,
            )

            unit_capital = unit_cost
            if profit is not None:
                unit_capital = profit.breakdown.unit_cost + profit.breakdown.packaging

            lines.append(
                f"#{product.id} {product.name} | score={scored.commercial_score} "
                f"conf={scored.confidence} banda={scored.band.value} | {scored.notes}"
            )
            export_rows.append(
                {
                    "product_id": product.id,
                    "product": product.name,
                    "score": float(scored.commercial_score) if scored.commercial_score is not None else None,
                    "confidence": float(scored.confidence),
                    "band": scored.band.value,
                    "unit_cost": float(unit_cost) if unit_cost is not None else None,
                    "sale_price": float(sale_price) if sale_price is not None else None,
                    "notes": scored.notes,
                }
            )

            if unit_capital is not None and unit_capital > 0:
                candidates.append(
                    BudgetCandidate(
                        product_id=product.id,
                        label=product.name,
                        unit_capital=unit_capital,
                        score=scored.commercial_score,
                        band=scored.band,
                        min_order_qty=offer.min_order_qty if offer else 1,
                        pack_qty=offer.pack_qty if offer else 1,
                        qty_min=qty_min,
                        qty_max=qty_max,
                        offer_id=offer.id if offer else None,
                        confidence=scored.confidence,
                    )
                )

        opt = optimize_budget(candidates, budget_limit=budget, reserve=reserve)
        lines.extend(["", "=== Optimizador (greedy-approx) ===", opt.method])
        lines.append(f"Gastado={opt.spent}  Residual={opt.residual}")

        run = self.research.create_run(
            ResearchRun(
                title="Ranking Etapa 1",
                budget_limit=budget,
                reserve_amount=reserve,
                fee_profile_id=fees.id,
                notes="FICTICIO / corrida local Etapa 1",
            )
        )
        assert run.id is not None

        for i, alloc in enumerate(opt.selected, start=1):
            lines.append(
                f"  ✓ {alloc.candidate.label} qty={alloc.quantity} capital={alloc.capital}"
            )
            export_rows_match = next(
                (r for r in export_rows if r["product_id"] == alloc.candidate.product_id),
                {},
            )
            export_rows_match["rank"] = i
            export_rows_match["qty"] = alloc.quantity
            export_rows_match["capital"] = float(alloc.capital)
            self.research.add_item(
                ResearchItem(
                    run_id=run.id,
                    product_id=alloc.candidate.product_id,
                    offer_id=alloc.candidate.offer_id,
                    qty_suggested=alloc.quantity,
                    capital_allocated=alloc.capital,
                    score=alloc.candidate.score,
                    confidence=alloc.candidate.confidence,
                    rank=i,
                    band=alloc.candidate.band,
                )
            )

        for c, reason in opt.excluded:
            lines.append(f"  ✗ {c.label}: {reason}")
            if c.band == RankBand.PENDIENTE:
                self.research.add_item(
                    ResearchItem(
                        run_id=run.id,
                        product_id=c.product_id,
                        offer_id=c.offer_id,
                        score=c.score,
                        confidence=c.confidence,
                        band=c.band,
                        calc_json=reason,
                    )
                )

        self._last_rows = export_rows
        self.out.insert("1.0", "\n".join(lines) + "\n")
        self.status.configure(text=f"Corrida #{run.id} guardada")

    def _export_csv(self) -> None:
        if not self._last_rows:
            self.status.configure(text="Calcula primero")
            return
        path = export_ranking_csv(self._last_rows, data_dir=self.data_dir)
        self.status.configure(text=f"CSV → {path}")

    def _export_xlsx(self) -> None:
        if not self._last_rows:
            self.status.configure(text="Calcula primero")
            return
        path = export_ranking_xlsx(self._last_rows, data_dir=self.data_dir)
        self.status.configure(text=f"Excel → {path}")
