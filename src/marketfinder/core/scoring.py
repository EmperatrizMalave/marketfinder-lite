"""Scoring / ranking comercial + confianza.

Pesos fijos: Demanda 30, Rentabilidad 30, Competencia 15,
Inversión 10, Logística 10, Riesgo devolución 5.

Normalización documentada 0–100. Datos esenciales incompletos → pendiente.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from marketfinder.core.models import Provenance, RankBand, RankingWeights

ZERO = Decimal("0")
HUNDRED = Decimal("100")

ESSENTIAL_FIELDS = ("unit_cost", "sale_price")


@dataclass(frozen=True)
class FactorScores:
    """Factores ya normalizados a 0–100 (mayor = mejor oportunidad)."""

    demand: Decimal | None = None
    profitability: Decimal | None = None
    competition: Decimal | None = None  # favorable (alta competencia → bajo)
    investment: Decimal | None = None  # favorable (más inversión → bajo)
    logistics: Decimal | None = None
    return_risk: Decimal | None = None  # favorable (más riesgo → bajo)


@dataclass(frozen=True)
class ScoreResult:
    commercial_score: Decimal | None
    confidence: Decimal
    band: RankBand
    factors: FactorScores
    missing_essentials: tuple[str, ...]
    notes: str

    @property
    def is_actionable(self) -> bool:
        """Solo actionable si no está pendiente y hay score."""
        return self.band != RankBand.PENDIENTE and self.commercial_score is not None


def clamp_0_100(value: Decimal | float | int | None) -> Decimal | None:
    """Normaliza un valor ya en escala 0–100; None permanece None."""
    if value is None:
        return None
    d = Decimal(str(value))
    if d < ZERO:
        return ZERO
    if d > HUNDRED:
        return HUNDRED
    return d


def invert_0_100(value: Decimal | None) -> Decimal | None:
    """Invierte escala: 100 - value (para competencia / inversión / riesgo)."""
    if value is None:
        return None
    return HUNDRED - value


def band_for_score(score: Decimal | None, *, incomplete: bool) -> RankBand:
    if incomplete or score is None:
        return RankBand.PENDIENTE
    if score >= Decimal("80"):
        return RankBand.ALTA
    if score >= Decimal("60"):
        return RankBand.REQUIERE_INVESTIGACION
    return RankBand.POCO_ATRACTIVA


def profitability_factor_from_margin(margin: Decimal | None) -> Decimal | None:
    """Mapea margen (−∞..+∞) a 0–100. 25% → 100; 0% → 50; −25% → 0."""
    if margin is None:
        return None
    # score = clamp((margin + 0.25) / 0.50 * 100)
    raw = (margin + Decimal("0.25")) / Decimal("0.50") * HUNDRED
    return clamp_0_100(raw)


def investment_factor_from_amount(
    amount: Decimal | None,
    *,
    budget: Decimal = Decimal("3000"),
) -> Decimal | None:
    """Más inversión relativa al presupuesto → peor factor.

    0 → 100; budget → 50; 2*budget → 0.
    """
    if amount is None:
        return None
    if budget <= ZERO:
        return None
    ratio = amount / budget
    raw = HUNDRED - (ratio * Decimal("50"))
    return clamp_0_100(raw)


PROVENANCE_WEIGHT: dict[Provenance, Decimal] = {
    Provenance.VERIFICADO: Decimal("1.0"),
    Provenance.ESTIMADO: Decimal("0.6"),
    Provenance.PENDIENTE: Decimal("0.2"),
}


def compute_confidence(
    provenances: dict[str, Provenance],
    *,
    present_factors: dict[str, bool],
) -> Decimal:
    """Confianza 0–100 según proveniencia y cobertura de factores.

    Factores: demand, profitability, competition, investment, logistics, return_risk.
    """
    keys = (
        "demand",
        "profitability",
        "competition",
        "investment",
        "logistics",
        "return_risk",
    )
    total = ZERO
    for key in keys:
        present = present_factors.get(key, False)
        if not present:
            total += ZERO  # aporte 0
            continue
        prov = provenances.get(key, Provenance.PENDIENTE)
        total += PROVENANCE_WEIGHT.get(prov, Decimal("0.2")) * (HUNDRED / Decimal(len(keys)))
    return total.quantize(Decimal("0.01"))


def score_opportunity(
    factors: FactorScores,
    weights: RankingWeights | None = None,
    *,
    unit_cost: Decimal | None,
    sale_price: Decimal | None,
    provenances: dict[str, Provenance] | None = None,
) -> ScoreResult:
    """Calcula score comercial + confianza + banda.

    Normalización:
    - demanda / logística: ya 0–100 (mayor mejor)
    - rentabilidad: vía profitability_factor_from_margin
    - competencia / return_risk: se espera factor YA favorable (invertido)
    - inversión: factor YA favorable

    Si faltan unit_cost o sale_price → banda pendiente (no aprobar).
    """
    w = weights or RankingWeights()
    missing = tuple(f for f, v in (("unit_cost", unit_cost), ("sale_price", sale_price)) if v is None)

    # Factores disponibles
    f_demand = clamp_0_100(factors.demand)
    f_profit = clamp_0_100(factors.profitability)
    f_comp = clamp_0_100(factors.competition)
    f_inv = clamp_0_100(factors.investment)
    f_log = clamp_0_100(factors.logistics)
    f_ret = clamp_0_100(factors.return_risk)

    present = {
        "demand": f_demand is not None,
        "profitability": f_profit is not None,
        "competition": f_comp is not None,
        "investment": f_inv is not None,
        "logistics": f_log is not None,
        "return_risk": f_ret is not None,
    }

    # Score parcial: solo factores presentes; renormalizar pesos
    parts: list[tuple[Decimal, Decimal]] = []
    mapping = [
        (f_demand, w.w_demand),
        (f_profit, w.w_profitability),
        (f_comp, w.w_competition),
        (f_inv, w.w_investment),
        (f_log, w.w_logistics),
        (f_ret, w.w_return_risk),
    ]
    weight_sum = ZERO
    for val, weight in mapping:
        if val is not None:
            parts.append((val, weight))
            weight_sum += weight

    commercial: Decimal | None = None
    if parts and weight_sum > ZERO:
        commercial = sum((val * weight for val, weight in parts), ZERO) / weight_sum
        commercial = commercial.quantize(Decimal("0.01"))

    provs = provenances or {}
    confidence = compute_confidence(provs, present_factors=present)

    incomplete = bool(missing)
    band = band_for_score(commercial, incomplete=incomplete)

    notes = ""
    if incomplete:
        notes = (
            f"Datos esenciales incompletos ({', '.join(missing)}). "
            "Estado pendiente — no aprobar solo por score."
        )
    elif commercial is None:
        notes = "Sin factores de ranking disponibles."
        band = RankBand.PENDIENTE

    return ScoreResult(
        commercial_score=None if incomplete else commercial,
        confidence=confidence,
        band=band,
        factors=FactorScores(
            demand=f_demand,
            profitability=f_profit,
            competition=f_comp,
            investment=f_inv,
            logistics=f_log,
            return_risk=f_ret,
        ),
        missing_essentials=missing,
        notes=notes,
    )


# Documentación de normalización (para UI / docs)
NORMALIZATION_DOC = """
Normalización de factores (0–100, mayor = mejor oportunidad):

1. Demanda: score directo 0–100 (usuario / métrica).
2. Rentabilidad: margen operativo m → ((m + 0.25) / 0.50) * 100, clamp.
   Así 25% margen ≈ 100; 0% ≈ 50; −25% ≈ 0.
3. Competencia: score bruto 0–100 (mayor = más competencia) se INVIRTE:
   favorable = 100 − bruto.
4. Inversión: amount / budget → 100 − (ratio * 50), clamp
   (0 ≈ 100; budget ≈ 50; 2×budget ≈ 0).
5. Logística: score directo 0–100.
6. Riesgo de devolución: score bruto (mayor = más riesgo) se INVIRTE.

Score comercial = promedio ponderado de factores presentes
(pesos 30/30/15/10/10/5 renormalizados si faltan factores).

Confianza = cobertura × calidad de proveniencia
(verificado=1.0, estimado=0.6, pendiente=0.2) sobre 6 factores.

Si faltan costo unitario o precio de venta → banda `pendiente`
aunque el score parcial sea alto. No se recomienda la oportunidad.
"""
