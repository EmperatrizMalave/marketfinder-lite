"""Pruebas de ranking: pesos, bandas, pendiente."""

from __future__ import annotations

from decimal import Decimal

from marketfinder.core.models import Provenance, RankBand, RankingWeights
from marketfinder.core.scoring import (
    FactorScores,
    band_for_score,
    invert_0_100,
    score_opportunity,
)


def test_weights_default_30_30_15_10_10_5() -> None:
    w = RankingWeights()
    assert w.w_demand == Decimal("0.30")
    assert w.w_profitability == Decimal("0.30")
    assert w.w_competition == Decimal("0.15")
    assert w.w_investment == Decimal("0.10")
    assert w.w_logistics == Decimal("0.10")
    assert w.w_return_risk == Decimal("0.05")
    assert w.total() == Decimal("1.00")


def test_stable_order_with_weights() -> None:
    w = RankingWeights()
    high = score_opportunity(
        FactorScores(
            demand=Decimal("90"),
            profitability=Decimal("90"),
            competition=Decimal("80"),
            investment=Decimal("80"),
            logistics=Decimal("80"),
            return_risk=Decimal("80"),
        ),
        w,
        unit_cost=Decimal("30"),
        sale_price=Decimal("200"),
    )
    low = score_opportunity(
        FactorScores(
            demand=Decimal("20"),
            profitability=Decimal("20"),
            competition=Decimal("20"),
            investment=Decimal("20"),
            logistics=Decimal("20"),
            return_risk=Decimal("20"),
        ),
        w,
        unit_cost=Decimal("30"),
        sale_price=Decimal("200"),
    )
    assert high.commercial_score is not None and low.commercial_score is not None
    assert high.commercial_score > low.commercial_score
    assert high.band == RankBand.ALTA
    assert low.band == RankBand.POCO_ATRACTIVA


def test_bands() -> None:
    assert band_for_score(Decimal("80"), incomplete=False) == RankBand.ALTA
    assert band_for_score(Decimal("79.99"), incomplete=False) == RankBand.REQUIERE_INVESTIGACION
    assert band_for_score(Decimal("60"), incomplete=False) == RankBand.REQUIERE_INVESTIGACION
    assert band_for_score(Decimal("59.99"), incomplete=False) == RankBand.POCO_ATRACTIVA
    assert band_for_score(Decimal("99"), incomplete=True) == RankBand.PENDIENTE


def test_incomplete_essentials_pending() -> None:
    result = score_opportunity(
        FactorScores(demand=Decimal("100"), profitability=Decimal("100")),
        unit_cost=None,
        sale_price=Decimal("200"),
    )
    assert result.band == RankBand.PENDIENTE
    assert result.commercial_score is None
    assert "unit_cost" in result.missing_essentials
    assert result.is_actionable is False


def test_invert_competition() -> None:
    assert invert_0_100(Decimal("20")) == Decimal("80")
    assert invert_0_100(None) is None


def test_confidence_uses_provenance() -> None:
    result = score_opportunity(
        FactorScores(
            demand=Decimal("50"),
            profitability=Decimal("50"),
            competition=Decimal("50"),
            investment=Decimal("50"),
            logistics=Decimal("50"),
            return_risk=Decimal("50"),
        ),
        unit_cost=Decimal("10"),
        sale_price=Decimal("100"),
        provenances={
            "demand": Provenance.VERIFICADO,
            "profitability": Provenance.VERIFICADO,
            "competition": Provenance.VERIFICADO,
            "investment": Provenance.VERIFICADO,
            "logistics": Provenance.VERIFICADO,
            "return_risk": Provenance.VERIFICADO,
        },
    )
    assert result.confidence == Decimal("100.00")
