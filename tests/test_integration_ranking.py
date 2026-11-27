"""Integración: catálogo ficticio → score + presupuesto."""

from __future__ import annotations

from decimal import Decimal

from marketfinder.core.budget import BudgetCandidate, optimize_budget
from marketfinder.core.profitability import calculate_profit
from marketfinder.core.scoring import (
    FactorScores,
    invert_0_100,
    profitability_factor_from_margin,
    score_opportunity,
)
from marketfinder.data.repositories import (
    MetricsRepository,
    OfferRepository,
    WeightsRepository,
)
from marketfinder.core.models import RankBand


def test_catalog_ranking_and_budget(db_conn, sample_catalog) -> None:
    products = sample_catalog["products"]
    fees = sample_catalog["fee_profile"]
    weights = WeightsRepository(db_conn).get()
    offers_repo = OfferRepository(db_conn)
    metrics_repo = MetricsRepository(db_conn)

    scored = []
    for p in products:
        offer = offers_repo.list_for_product(p.id)[0]
        m = metrics_repo.latest_for_product(p.id)
        profit = calculate_profit(
            unit_cost=offer.unit_cost,
            sale_price=m.sale_price if m else None,
            fees=fees,
        )
        result = score_opportunity(
            FactorScores(
                demand=m.demand_score if m else None,
                profitability=profitability_factor_from_margin(
                    profit.margin if profit else None
                ),
                competition=invert_0_100(m.competition_score if m else None),
                logistics=m.logistics_score if m else None,
                return_risk=invert_0_100(m.return_risk_score if m else None),
            ),
            weights,
            unit_cost=offer.unit_cost,
            sale_price=m.sale_price if m else None,
        )
        scored.append((p, offer, result))

    # El incompleto debe quedar pendiente
    incomplete = next(s for s in scored if s[0].sku == "FIC-X")
    assert incomplete[2].band == RankBand.PENDIENTE

    candidates = []
    for p, offer, result in scored:
        if offer.unit_cost is None:
            continue
        candidates.append(
            BudgetCandidate(
                product_id=p.id,
                label=p.name,
                unit_capital=offer.unit_cost,
                score=result.commercial_score,
                band=result.band,
                min_order_qty=offer.min_order_qty,
                pack_qty=offer.pack_qty,
            )
        )

    opt = optimize_budget(candidates, budget_limit=Decimal("3000"))
    assert opt.spent <= Decimal("3000")
    assert all(a.candidate.band != RankBand.PENDIENTE for a in opt.selected)
