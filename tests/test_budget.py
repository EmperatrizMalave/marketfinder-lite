"""Pruebas del optimizador de presupuesto."""

from __future__ import annotations

from decimal import Decimal

from marketfinder.core.budget import BudgetCandidate, optimize_budget
from marketfinder.core.models import RankBand


def _cand(pid: int, score: float, capital: str, **kwargs) -> BudgetCandidate:
    return BudgetCandidate(
        product_id=pid,
        label=f"FICTICIO-{pid}",
        unit_capital=Decimal(capital),
        score=Decimal(str(score)),
        band=kwargs.get("band", RankBand.ALTA),
        min_order_qty=kwargs.get("min_order_qty", 10),
        pack_qty=kwargs.get("pack_qty", 10),
        qty_min=kwargs.get("qty_min", 10),
        qty_max=kwargs.get("qty_max", 20),
    )


def test_respects_budget_3000() -> None:
    # 30 * 10 = 300; 45 * 10 = 450 → ambos caben
    result = optimize_budget(
        [
            _cand(1, 90, "30"),
            _cand(2, 80, "45"),
            _cand(3, 70, "500"),  # 500*10=5000 > 3000
        ],
        budget_limit=Decimal("3000"),
    )
    spent = sum((a.capital for a in result.selected), Decimal("0"))
    assert spent <= Decimal("3000")
    assert result.spent == spent
    assert result.residual == Decimal("3000") - spent
    # el de 500 no debería entrar con qty mínima 10
    selected_ids = {a.candidate.product_id for a in result.selected}
    assert 3 not in selected_ids


def test_qty_in_range_10_20() -> None:
    result = optimize_budget(
        [_cand(1, 90, "50", qty_min=10, qty_max=20, pack_qty=10, min_order_qty=10)],
        budget_limit=Decimal("3000"),
    )
    assert len(result.selected) == 1
    qty = result.selected[0].quantity
    assert 10 <= qty <= 20
    assert qty % 10 == 0


def test_excludes_pending_and_respects_reserve() -> None:
    result = optimize_budget(
        [
            _cand(1, 99, "30", band=RankBand.PENDIENTE),
            _cand(2, 80, "30"),
        ],
        budget_limit=Decimal("3000"),
        reserve=Decimal("2500"),
    )
    assert all(a.candidate.product_id != 1 for a in result.selected)
    assert result.spent <= Decimal("500")
    assert "greedy" in result.method.lower()
