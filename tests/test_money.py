"""Pruebas de Decimal ↔ centavos."""

from __future__ import annotations

from decimal import Decimal

from marketfinder.core.money import Money, cents_to_decimal, decimal_to_cents


def test_decimal_to_cents_round_half_up() -> None:
    assert decimal_to_cents(Decimal("10.005")) == 1001
    assert decimal_to_cents(Decimal("10.004")) == 1000
    assert decimal_to_cents(None) is None


def test_cents_to_decimal_none() -> None:
    assert cents_to_decimal(None) is None
    assert cents_to_decimal(19900) == Decimal("199.00")


def test_money_roundtrip() -> None:
    m = Money("25.50")
    assert m.to_cents() == 2550
    assert Money.from_cents(2550) == m
    assert Money.maybe(None) is None
