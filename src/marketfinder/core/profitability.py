"""Calculadora de rentabilidad con Decimal y escenarios.

Líneas de costo independientes. Fiscal configurable (IVA / retenciones / ISR).
No inventa tarifas oficiales. None ≠ 0.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Mapping

from marketfinder.core.models import FeeProfile, ScenarioName

ZERO = Decimal("0")
ONE = Decimal("1")
HUNDRED = Decimal("100")


@dataclass(frozen=True)
class CostBreakdown:
    """Desglose de costos unitarios (todas las líneas independientes)."""

    unit_cost: Decimal
    commission: Decimal
    payment_fee: Decimal
    shipping: Decimal
    packaging: Decimal
    ads: Decimal
    other: Decimal
    iva: Decimal
    retention: Decimal
    isr: Decimal

    @property
    def operating_costs(self) -> Decimal:
        """Costos operativos antes de impuestos sobre la utilidad."""
        return (
            self.unit_cost
            + self.commission
            + self.payment_fee
            + self.shipping
            + self.packaging
            + self.ads
            + self.other
            + self.iva
            + self.retention
        )

    @property
    def total_costs(self) -> Decimal:
        return self.operating_costs + self.isr


@dataclass(frozen=True)
class ProfitResult:
    sale_price: Decimal
    quantity: int
    breakdown: CostBreakdown
    target_margin: Decimal
    scenario: ScenarioName
    disclaimer: str = (
        "Escenario ilustrativo. No garantiza ganancias. "
        "Parámetros editables — verificar en ML / SAT."
    )

    @property
    def unit_operating_profit(self) -> Decimal:
        return self.sale_price - self.breakdown.operating_costs

    @property
    def unit_profit_after_tax(self) -> Decimal:
        return self.sale_price - self.breakdown.total_costs

    @property
    def unit_cash_flow(self) -> Decimal:
        # Flujo aproximado: utilidad después de impuestos
        # (sin CAPEX ni timing de cobro — Etapa 1 simplificado)
        return self.unit_profit_after_tax

    @property
    def total_operating_profit(self) -> Decimal:
        return self.unit_operating_profit * self.quantity

    @property
    def total_profit_after_tax(self) -> Decimal:
        return self.unit_profit_after_tax * self.quantity

    @property
    def total_cash_flow(self) -> Decimal:
        return self.unit_cash_flow * self.quantity

    @property
    def total_revenue(self) -> Decimal:
        return self.sale_price * self.quantity

    @property
    def total_merchandise_capital(self) -> Decimal:
        return self.breakdown.unit_cost * self.quantity

    @property
    def total_capital(self) -> Decimal:
        """Capital estimado: mercancía + empaque fijo × qty + otros fijos × qty."""
        per_unit_capital = (
            self.breakdown.unit_cost
            + self.breakdown.packaging
            + self.breakdown.shipping  # si shipping es costo asumido al vender
        )
        return per_unit_capital * self.quantity

    @property
    def margin(self) -> Decimal | None:
        if self.sale_price <= ZERO:
            return None
        return self.unit_operating_profit / self.sale_price

    @property
    def roi_merchandise(self) -> Decimal | None:
        if self.breakdown.unit_cost <= ZERO:
            return None
        return self.unit_operating_profit / self.breakdown.unit_cost

    @property
    def roi_capital(self) -> Decimal | None:
        cap = self.total_capital
        if cap <= ZERO:
            return None
        return self.total_operating_profit / cap

    @property
    def meets_target_margin(self) -> bool | None:
        m = self.margin
        if m is None:
            return None
        return m >= self.target_margin

    @property
    def break_even_units(self) -> Decimal | None:
        """Unidades para cubrir costos fijos del perfil repartidos (simplificado).

        En Etapa 1 los fijos del perfil ya están prorrateados por unidad
        vía shipping_cost_fixed / packaging / other. Break-even unitario:
        si contribución > 0, 1 unidad ya cubre; si no, indefinido.
        """
        contribution = self.sale_price - (
            self.breakdown.operating_costs - self.breakdown.unit_cost
        )
        # contribución = P - (fees + ship + …) sin C
        var_without_c = self.breakdown.operating_costs - self.breakdown.unit_cost
        contribution = self.sale_price - var_without_c
        if contribution <= ZERO:
            return None
        # Sin fijos separados del lote, BE = C / contribución… aquí C es costo mercancía
        # Break-even clásico de unidades para recuperar capital de 1 unidad de stock:
        if self.unit_operating_profit <= ZERO:
            return None
        return ONE  # con margen positivo, 1 u. ya aporta

    def min_sale_price_for_target(self) -> Decimal | None:
        """Precio mínimo para alcanzar target_margin (misma estructura de fees)."""
        # P - C - P*rates - fixed = target * P
        # P * (1 - rates - target) = C + fixed
        rates = (
            self._rate_sum_from_breakdown_ratio()
        )
        # Mejor: recalcular con algebra desde inputs — ver helper externo
        return None  # se expone vía compute_min_price

    def _rate_sum_from_breakdown_ratio(self) -> Decimal:
        if self.sale_price <= ZERO:
            return ZERO
        variable = (
            self.breakdown.commission
            + self.breakdown.payment_fee
            + self.breakdown.ads
            + self.breakdown.other
            - (  # other puede mezclar fijo+rate; ratio aproximado
                ZERO
            )
        )
        return variable / self.sale_price

    def as_dict(self) -> dict:
        return {
            "scenario": str(self.scenario),
            "sale_price": str(self.sale_price),
            "quantity": self.quantity,
            "unit_cost": str(self.breakdown.unit_cost),
            "unit_operating_profit": str(self.unit_operating_profit),
            "unit_profit_after_tax": str(self.unit_profit_after_tax),
            "unit_cash_flow": str(self.unit_cash_flow),
            "total_operating_profit": str(self.total_operating_profit),
            "total_profit_after_tax": str(self.total_profit_after_tax),
            "total_cash_flow": str(self.total_cash_flow),
            "margin": str(self.margin) if self.margin is not None else None,
            "roi_merchandise": str(self.roi_merchandise)
            if self.roi_merchandise is not None
            else None,
            "roi_capital": str(self.roi_capital)
            if self.roi_capital is not None
            else None,
            "meets_target_margin": self.meets_target_margin,
            "total_capital": str(self.total_capital),
            "disclaimer": self.disclaimer,
            "costs": {
                "commission": str(self.breakdown.commission),
                "payment_fee": str(self.breakdown.payment_fee),
                "shipping": str(self.breakdown.shipping),
                "packaging": str(self.breakdown.packaging),
                "ads": str(self.breakdown.ads),
                "other": str(self.breakdown.other),
                "iva": str(self.breakdown.iva),
                "retention": str(self.breakdown.retention),
                "isr": str(self.breakdown.isr),
            },
        }


SCENARIO_FACTORS: Mapping[ScenarioName, tuple[Decimal, Decimal]] = {
    # (price_factor, cost_factor)
    ScenarioName.NORMAL: (ONE, ONE),
    ScenarioName.OPTIMISTA: (Decimal("1.05"), Decimal("0.95")),
    ScenarioName.CONSERVADOR: (Decimal("0.95"), Decimal("1.05")),
    ScenarioName.PRECIO_MENOS_10: (Decimal("0.90"), ONE),
    ScenarioName.COSTO_MAS_20: (ONE, Decimal("1.20")),
    ScenarioName.PRECIO_MENOS_10_COSTO_MAS_20: (Decimal("0.90"), Decimal("1.20")),
}


def _dec(value: Decimal | int | str | float | None, default: Decimal = ZERO) -> Decimal:
    if value is None:
        return default
    return Decimal(str(value))


def build_breakdown(
    *,
    unit_cost: Decimal,
    sale_price: Decimal,
    fees: FeeProfile,
) -> CostBreakdown:
    commission = sale_price * _dec(fees.commission_rate)
    payment_fee = sale_price * _dec(fees.payment_fee_rate)
    shipping = _dec(fees.shipping_cost_fixed) + sale_price * _dec(fees.shipping_cost_rate)
    packaging = _dec(fees.packaging_cost_fixed)
    ads = sale_price * _dec(fees.ads_cost_rate)
    other = _dec(fees.other_cost_fixed) + sale_price * _dec(fees.other_cost_rate)
    iva = sale_price * _dec(fees.iva_rate)
    retention = sale_price * _dec(fees.retention_rate)

    operating_profit = sale_price - (
        unit_cost + commission + payment_fee + shipping + packaging + ads + other + iva + retention
    )
    isr = max(operating_profit, ZERO) * _dec(fees.isr_rate)

    return CostBreakdown(
        unit_cost=unit_cost,
        commission=commission,
        payment_fee=payment_fee,
        shipping=shipping,
        packaging=packaging,
        ads=ads,
        other=other,
        iva=iva,
        retention=retention,
        isr=isr,
    )


def calculate_profit(
    *,
    unit_cost: Decimal | None,
    sale_price: Decimal | None,
    fees: FeeProfile,
    quantity: int = 1,
    scenario: ScenarioName = ScenarioName.NORMAL,
) -> ProfitResult | None:
    """Calcula rentabilidad. Retorna None si faltan costo o precio (no inventa 0)."""
    if unit_cost is None or sale_price is None:
        return None
    if quantity < 1:
        raise ValueError("quantity debe ser >= 1")

    pf, cf = SCENARIO_FACTORS[scenario]
    adj_price = (sale_price * pf).quantize(Decimal("0.01"))
    adj_cost = (unit_cost * cf).quantize(Decimal("0.01"))
    breakdown = build_breakdown(unit_cost=adj_cost, sale_price=adj_price, fees=fees)
    return ProfitResult(
        sale_price=adj_price,
        quantity=quantity,
        breakdown=breakdown,
        target_margin=_dec(fees.target_margin, Decimal("0.25")),
        scenario=scenario,
    )


def calculate_all_scenarios(
    *,
    unit_cost: Decimal | None,
    sale_price: Decimal | None,
    fees: FeeProfile,
    quantity: int = 1,
) -> dict[ScenarioName, ProfitResult]:
    results: dict[ScenarioName, ProfitResult] = {}
    for name in ScenarioName:
        r = calculate_profit(
            unit_cost=unit_cost,
            sale_price=sale_price,
            fees=fees,
            quantity=quantity,
            scenario=name,
        )
        if r is not None:
            results[name] = r
    return results


def min_price_for_target_margin(
    *,
    unit_cost: Decimal,
    fees: FeeProfile,
    target_margin: Decimal | None = None,
) -> Decimal | None:
    """Precio mínimo P tal que margen operativo >= target.

    P - C - P*(r_c+r_p+r_s+r_ads+r_other+r_iva+r_ret) - fixed = target * P
    P * (1 - sum_rates - target) = C + fixed
    """
    target = _dec(target_margin, _dec(fees.target_margin, Decimal("0.25")))
    sum_rates = (
        _dec(fees.commission_rate)
        + _dec(fees.payment_fee_rate)
        + _dec(fees.shipping_cost_rate)
        + _dec(fees.ads_cost_rate)
        + _dec(fees.other_cost_rate)
        + _dec(fees.iva_rate)
        + _dec(fees.retention_rate)
    )
    fixed = (
        _dec(fees.shipping_cost_fixed)
        + _dec(fees.packaging_cost_fixed)
        + _dec(fees.other_cost_fixed)
    )
    denom = ONE - sum_rates - target
    if denom <= ZERO:
        return None
    price = (unit_cost + fixed) / denom
    return price.quantize(Decimal("0.01"))


def min_price_break_even(
    *,
    unit_cost: Decimal,
    fees: FeeProfile,
) -> Decimal | None:
    """Precio mínimo con margen operativo 0."""
    return min_price_for_target_margin(
        unit_cost=unit_cost, fees=fees, target_margin=ZERO
    )
