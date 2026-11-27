"""Integración DB: schema, seeds, proveniencia, ofertas M2M."""

from __future__ import annotations

from decimal import Decimal

from marketfinder.core.models import Offer, Product, Provenance, Supplier
from marketfinder.data.repositories import (
    OfferRepository,
    PriceHistoryRepository,
    ProductRepository,
    SettingsRepository,
    SupplierRepository,
    WeightsRepository,
)


def test_schema_and_seed_settings_weights(db_conn) -> None:
    settings = SettingsRepository(db_conn).commercial_defaults()
    assert settings["budget_default"] == "3000"
    assert settings["target_margin"] == "0.25"
    assert settings["prefer_supplier_country"] == "MX"

    w = WeightsRepository(db_conn).get()
    assert float(w.w_demand) == 0.30
    assert float(w.w_return_risk) == 0.05

    row = db_conn.execute(
        "SELECT name FROM schema_migrations WHERE name = ?",
        ("001_etapa1_schema",),
    ).fetchone()
    assert row is not None


def test_provenance_default_pendiente(db_conn) -> None:
    products = ProductRepository(db_conn)
    suppliers = SupplierRepository(db_conn)
    offers = OfferRepository(db_conn)

    p = products.create(Product(name="FICTICIO Prov Default"))
    s = suppliers.create(Supplier(name="FICTICIO Sup Default"))
    o = offers.create(
        Offer(
            product_id=p.id,  # type: ignore[arg-type]
            supplier_id=s.id,  # type: ignore[arg-type]
            unit_cost=None,
        )
    )
    assert o.unit_cost is None
    assert o.unit_cost_provenance == Provenance.PENDIENTE

    # En SQLite el costo desconocido es NULL, no 0
    row = db_conn.execute(
        "SELECT unit_cost_cents, unit_cost_provenance FROM offers WHERE id = ?",
        (o.id,),
    ).fetchone()
    assert row["unit_cost_cents"] is None
    assert row["unit_cost_provenance"] == "pendiente"


def test_offers_m2m_and_price_history(db_conn, sample_catalog) -> None:
    p1 = sample_catalog["products"][0]
    offers = OfferRepository(db_conn).list_for_product(p1.id)
    assert len(offers) >= 1
    assert offers[0].unit_cost == Decimal("30.00")

    history = PriceHistoryRepository(db_conn).list_for_product(p1.id)
    kinds = {h.kind for h in history}
    assert "unit_cost" in kinds
    assert "sale_price" in kinds
