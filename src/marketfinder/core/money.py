"""Dinero con Decimal en memoria y centavos enteros en SQLite.

Regla: nunca rellenar con 0 un monto desconocido. Usar None / NULL
y marcar proveniencia `pendiente`.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import TypeAlias

Cents: TypeAlias = int


def _as_decimal(value: Decimal | int | str | float) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        # Evitar artefactos binarios: pasar por str
        return Decimal(str(value))
    return Decimal(str(value))


def decimal_to_cents(amount: Decimal | int | str | float | None) -> Cents | None:
    """Convierte unidades monetarias a centavos enteros (None si desconocido)."""
    if amount is None:
        return None
    d = _as_decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(d * 100)


def cents_to_decimal(cents: Cents | None) -> Decimal | None:
    """Centavos enteros → Decimal con 2 decimales (None si desconocido)."""
    if cents is None:
        return None
    return (Decimal(int(cents)) / Decimal(100)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


class Money:
    """Wrapper ligero sobre Decimal (unidad monetaria, no centavos)."""

    __slots__ = ("_value",)

    def __init__(self, value: Decimal | int | str | float) -> None:
        self._value = _as_decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @classmethod
    def from_cents(cls, cents: Cents) -> Money:
        return cls(Decimal(int(cents)) / Decimal(100))

    @classmethod
    def maybe(cls, value: Decimal | int | str | float | None) -> Money | None:
        if value is None:
            return None
        return cls(value)

    @property
    def amount(self) -> Decimal:
        return self._value

    def to_cents(self) -> Cents:
        result = decimal_to_cents(self._value)
        assert result is not None
        return result

    def __add__(self, other: Money) -> Money:
        return Money(self._value + other._value)

    def __sub__(self, other: Money) -> Money:
        return Money(self._value - other._value)

    def __mul__(self, factor: Decimal | int | str | float) -> Money:
        return Money(self._value * _as_decimal(factor))

    def __truediv__(self, divisor: Decimal | int | str | float) -> Money:
        return Money(self._value / _as_decimal(divisor))

    def __repr__(self) -> str:
        return f"Money({self._value})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._value == other._value
