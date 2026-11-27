"""Pruebas de calculadora y escenarios — fixtures ficticios."""

from __future__ import annotations

from decimal import Decimal

from marketfinder.core.models import FeeProfile, ScenarioName
from marketfinder.core.profitability import (
    calculate_all_scenarios,
    calculate_profit,
    min_price_for_target_margin,
)


def _fees() -> FeeProfile:
    return FeeProfile(
        name="ficticio_test",
        commission_rate=Decimal("0.13"),
        shipping_cost_fixed=Decimal("40"),
        target_margin=Decimal("0.25"),
        notes="FICTICIO",
    )


def test_profit_margin_with_fee_fixture() -> None:
    # P=200, C=30, comisión 13%=26, envío 40 → costos op=96 → profit=104 → margin=0.52
    r = calculate_profit(
        unit_cost=Decimal("30"),
        sale_price=Decimal("200"),
        fees=_fees(),
        quantity=10,
    )
    assert r is not None
    assert r.breakdown.commission == Decimal("26.00")
    assert r.unit_operating_profit == Decimal("104.00")
    assert r.margin == Decimal("0.52")
    assert r.meets_target_margin is True
    assert r.total_operating_profit == Decimal("1040.00")
    assert r.roi_merchandise == Decimal("104") / Decimal("30")


def test_respects_target_margin_flag() -> None:
    fees = _fees()
    # Precio bajo → no cumple 25%
    r = calculate_profit(
        unit_cost=Decimal("50"),
        sale_price=Decimal("100"),
        fees=fees,
    )
    assert r is not None
    # costos: 50 + 13 + 40 = 103 → profit -3 → margin -0.03
    assert r.meets_target_margin is False

    r2 = calculate_profit(
        unit_cost=Decimal("20"),
        sale_price=Decimal("200"),
        fees=fees,
    )
    assert r2 is not None
    assert r2.meets_target_margin is True


def test_missing_inputs_return_none_not_zero() -> None:
    assert calculate_profit(unit_cost=None, sale_price=Decimal("100"), fees=_fees()) is None
    assert calculate_profit(unit_cost=Decimal("10"), sale_price=None, fees=_fees()) is None


def test_all_scenarios_present() -> None:
    results = calculate_all_scenarios(
        unit_cost=Decimal("30"),
        sale_price=Decimal("200"),
        fees=_fees(),
        quantity=1,
    )
    assert set(results.keys()) == set(ScenarioName)
    assert results[ScenarioName.PRECIO_MENOS_10].sale_price == Decimal("180.00")
    assert results[ScenarioName.COSTO_MAS_20].breakdown.unit_cost == Decimal("36.00")


def test_min_price_for_target() -> None:
    # (C + fixed) / (1 - rates - target) = (30+40)/(1-0.13-0.25) = 70/0.62
    price = min_price_for_target_margin(unit_cost=Decimal("30"), fees=_fees())
    assert price is not None
    assert price == Decimal("112.90")
