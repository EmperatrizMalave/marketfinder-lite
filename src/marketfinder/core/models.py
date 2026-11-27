"""Modelos de dominio (dataclasses) — Etapa 1."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Provenance(StrEnum):
    VERIFICADO = "verificado"
    ESTIMADO = "estimado"
    PENDIENTE = "pendiente"


class RankBand(StrEnum):
    ALTA = "alta"
    REQUIERE_INVESTIGACION = "requiere_investigacion"
    POCO_ATRACTIVA = "poco_atractiva"
    PENDIENTE = "pendiente"


class OfferKind(StrEnum):
    UNITARIO = "unitario"
    PAQUETE = "paquete"
    KIT = "kit"


class ScenarioName(StrEnum):
    NORMAL = "normal"
    OPTIMISTA = "optimista"
    CONSERVADOR = "conservador"
    PRECIO_MENOS_10 = "precio_menos_10"
    COSTO_MAS_20 = "costo_mas_20"
    PRECIO_MENOS_10_COSTO_MAS_20 = "precio_menos_10_costo_mas_20"


@dataclass
class Supplier:
    name: str
    id: int | None = None
    country: str = "MX"
    contact: str | None = None
    url: str | None = None
    notes: str | None = None
    default_lead_days: int | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)


@dataclass
class Product:
    name: str
    id: int | None = None
    sku: str | None = None
    category: str | None = None
    weight_grams: Decimal | None = None
    currency: str = "MXN"
    notes: str | None = None
    kind: OfferKind = OfferKind.UNITARIO
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)


@dataclass
class Offer:
    """Oferta producto↔proveedor (M2M). Montos en unidades; repos usan centavos."""

    product_id: int
    supplier_id: int
    id: int | None = None
    unit_cost: Decimal | None = None
    unit_cost_provenance: Provenance = Provenance.PENDIENTE
    min_order_qty: int = 1
    pack_qty: int = 1
    lead_days: int | None = None
    kind: OfferKind = OfferKind.UNITARIO
    currency: str = "MXN"
    notes: str | None = None
    is_active: bool = True
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)


@dataclass
class MarketMetrics:
    product_id: int
    id: int | None = None
    sale_price: Decimal | None = None
    sale_price_provenance: Provenance = Provenance.PENDIENTE
    demand_score: Decimal | None = None
    demand_provenance: Provenance = Provenance.PENDIENTE
    competition_score: Decimal | None = None
    competition_provenance: Provenance = Provenance.PENDIENTE
    logistics_score: Decimal | None = None
    logistics_provenance: Provenance = Provenance.PENDIENTE
    return_risk_score: Decimal | None = None
    return_risk_provenance: Provenance = Provenance.PENDIENTE
    investment_required: Decimal | None = None
    investment_provenance: Provenance = Provenance.PENDIENTE
    monthly_sales_estimate: Decimal | None = None
    monthly_sales_provenance: Provenance = Provenance.PENDIENTE
    analysis_period_days: int = 14
    source_notes: str | None = None
    captured_at: str = field(default_factory=utc_now_iso)


@dataclass
class FeeProfile:
    """Parámetros fiscales/comerciales editables — NO tarifas oficiales congeladas."""

    name: str
    id: int | None = None
    commission_rate: Decimal = Decimal("0")
    payment_fee_rate: Decimal = Decimal("0")
    shipping_cost_fixed: Decimal = Decimal("0")
    shipping_cost_rate: Decimal = Decimal("0")
    iva_rate: Decimal = Decimal("0")
    retention_rate: Decimal = Decimal("0")
    isr_rate: Decimal = Decimal("0")
    other_cost_fixed: Decimal = Decimal("0")
    other_cost_rate: Decimal = Decimal("0")
    packaging_cost_fixed: Decimal = Decimal("0")
    ads_cost_rate: Decimal = Decimal("0")
    target_margin: Decimal = Decimal("0.25")
    notes: str | None = (
        "Parámetro editable — verificar en ML / SAT. No es tarifa oficial."
    )
    updated_at: str = field(default_factory=utc_now_iso)


@dataclass
class RankingWeights:
    w_demand: Decimal = Decimal("0.30")
    w_profitability: Decimal = Decimal("0.30")
    w_competition: Decimal = Decimal("0.15")
    w_investment: Decimal = Decimal("0.10")
    w_logistics: Decimal = Decimal("0.10")
    w_return_risk: Decimal = Decimal("0.05")
    updated_at: str = field(default_factory=utc_now_iso)

    def as_dict(self) -> dict[str, Decimal]:
        return {
            "w_demand": self.w_demand,
            "w_profitability": self.w_profitability,
            "w_competition": self.w_competition,
            "w_investment": self.w_investment,
            "w_logistics": self.w_logistics,
            "w_return_risk": self.w_return_risk,
        }

    def total(self) -> Decimal:
        return sum(self.as_dict().values(), Decimal("0"))


@dataclass
class PriceHistoryEntry:
    product_id: int
    kind: str  # 'sale_price' | 'unit_cost'
    amount: Decimal
    provenance: Provenance
    id: int | None = None
    offer_id: int | None = None
    source_notes: str | None = None
    captured_at: str = field(default_factory=utc_now_iso)


@dataclass
class ResearchRun:
    title: str
    id: int | None = None
    budget_limit: Decimal = Decimal("3000")
    reserve_amount: Decimal = Decimal("0")
    fee_profile_id: int | None = None
    market: str = "MX"
    platform: str = "ML"
    notes: str | None = None
    created_at: str = field(default_factory=utc_now_iso)


@dataclass
class ResearchItem:
    run_id: int
    product_id: int
    id: int | None = None
    metrics_id: int | None = None
    offer_id: int | None = None
    qty_suggested: int | None = None
    capital_allocated: Decimal | None = None
    score: Decimal | None = None
    confidence: Decimal | None = None
    rank: int | None = None
    band: RankBand = RankBand.PENDIENTE
    calc_json: str | None = None
    created_at: str = field(default_factory=utc_now_iso)


# Defaults comerciales (configurables; no verdad inmutable)
COMMERCIAL_DEFAULTS: dict[str, Any] = {
    "budget_default": "3000",
    "budget_reserve": "0",
    "cost_min": "5",
    "cost_max": "50",
    "price_min": "149",
    "price_max": "299",
    "target_margin": "0.25",
    "max_weight_g": "500",
    "prefer_supplier_country": "MX",
    "analysis_period_days": "14",
    "initial_qty_min": "10",
    "initial_qty_max": "20",
    "market": "MX",
    "platform": "ML",
}
