"""Optimizador de presupuesto (greedy = aproximación).

No solo mercancía: considera capital por unidad (costo + empaque/envío
del perfil cuando aplique), mínimos de pedido, tamaño de paquete y reserva.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from marketfinder.core.models import RankBand

ZERO = Decimal("0")


@dataclass
class BudgetCandidate:
    product_id: int
    label: str
    unit_capital: Decimal  # capital por unidad (no solo C)
    score: Decimal | None
    band: RankBand
    min_order_qty: int = 1
    pack_qty: int = 1
    qty_min: int = 10
    qty_max: int = 20
    offer_id: int | None = None
    confidence: Decimal | None = None


@dataclass
class BudgetAllocation:
    candidate: BudgetCandidate
    quantity: int
    capital: Decimal


@dataclass
class BudgetResult:
    selected: list[BudgetAllocation] = field(default_factory=list)
    excluded: list[tuple[BudgetCandidate, str]] = field(default_factory=list)
    budget_limit: Decimal = Decimal("3000")
    reserve: Decimal = ZERO
    spent: Decimal = ZERO
    residual: Decimal = ZERO
    method: str = (
        "greedy-approx — aproximación greedy por score; "
        "no garantiza óptimo global"
    )

    @property
    def available(self) -> Decimal:
        return self.budget_limit - self.reserve


def _pack_aligned_qty(desired: int, *, min_order: int, pack: int, qty_max: int) -> int:
    """Ajusta cantidad a múltiplo de pack, respetando mínimo y tope."""
    pack = max(1, pack)
    min_order = max(1, min_order)
    floor = max(min_order, pack)
    # Empezar en el menor múltiplo de pack >= max(desired, min_order) capped
    target = max(desired, min_order)
    # redondear hacia arriba al múltiplo de pack
    qty = ((target + pack - 1) // pack) * pack
    if qty < min_order:
        qty = ((min_order + pack - 1) // pack) * pack
    if qty > qty_max:
        # bajar al mayor múltiplo <= qty_max que cumpla min_order
        qty = (qty_max // pack) * pack
        if qty < min_order:
            return 0
    return qty


def optimize_budget(
    candidates: list[BudgetCandidate],
    *,
    budget_limit: Decimal = Decimal("3000"),
    reserve: Decimal = ZERO,
    prefer_qty: int | None = None,
) -> BudgetResult:
    """Selecciona candidatos bajo presupuesto con greedy por score.

    - Excluye banda `pendiente` o sin score / sin capital unitario válido.
    - Respeta reserva (presupuesto usable = limit − reserve).
    - qty sugerida en [qty_min, qty_max], alineada a pack_qty y min_order_qty.
    """
    result = BudgetResult(budget_limit=budget_limit, reserve=reserve)
    available = budget_limit - reserve
    if available < ZERO:
        available = ZERO
    result.residual = available

    ranked: list[BudgetCandidate] = []
    for c in candidates:
        if c.band == RankBand.PENDIENTE:
            result.excluded.append((c, "banda pendiente — datos insuficientes"))
            continue
        if c.score is None:
            result.excluded.append((c, "sin score comercial"))
            continue
        if c.unit_capital is None or c.unit_capital <= ZERO:
            result.excluded.append((c, "capital unitario desconocido o inválido"))
            continue
        ranked.append(c)

    ranked.sort(key=lambda c: c.score or ZERO, reverse=True)

    remaining = available
    for c in ranked:
        desired = prefer_qty if prefer_qty is not None else c.qty_min
        desired = max(c.qty_min, min(desired, c.qty_max))
        qty = _pack_aligned_qty(
            desired,
            min_order=c.min_order_qty,
            pack=c.pack_qty,
            qty_max=c.qty_max,
        )
        if qty <= 0:
            result.excluded.append((c, "no cabe en mínimos/paquete/qty_max"))
            continue

        # Reducir qty si no cabe en presupuesto restante
        while qty >= max(c.min_order_qty, c.pack_qty):
            capital = (c.unit_capital * qty).quantize(Decimal("0.01"))
            if capital <= remaining:
                result.selected.append(
                    BudgetAllocation(candidate=c, quantity=qty, capital=capital)
                )
                remaining -= capital
                break
            # bajar un paquete
            qty -= c.pack_qty
        else:
            result.excluded.append(
                (c, f"excede presupuesto residual ({remaining})")
            )

    result.spent = available - remaining
    result.residual = remaining
    return result
