"""Fixtures compartidas — datos claramente ficticios."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from marketfinder.core.models import (
    FeeProfile,
    MarketMetrics,
    Offer,
    Product,
    Provenance,
    Supplier,
)
from marketfinder.data.db import initialize_db
from marketfinder.data.repositories import (
    FeeProfileRepository,
    MetricsRepository,
    OfferRepository,
    ProductRepository,
    SupplierRepository,
)


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    d = tmp_path / "MarketFinderLite"
    d.mkdir()
    return d


@pytest.fixture
def db_conn(data_dir: Path):
    conn = initialize_db(data_dir / "marketfinder.db")
    yield conn
    conn.close()


@pytest.fixture
def fee_profile(db_conn) -> FeeProfile:
    repo = FeeProfileRepository(db_conn)
    profile = repo.get_by_name("ml_mx_manual")
    assert profile is not None
    # Fixture ficticio de tarifas (NO oficiales)
    profile.commission_rate = Decimal("0.13")
    profile.payment_fee_rate = Decimal("0.00")
    profile.shipping_cost_fixed = Decimal("40")
    profile.iva_rate = Decimal("0.00")
    profile.retention_rate = Decimal("0.00")
    profile.isr_rate = Decimal("0.00")
    profile.target_margin = Decimal("0.25")
    profile.notes = "FICTICIO — fixture de prueba, no tarifa oficial"
    return repo.update(profile)


@pytest.fixture
def sample_catalog(db_conn, fee_profile):
    """Catálogo ficticio etiquetado para pruebas."""
    suppliers = SupplierRepository(db_conn)
    products = ProductRepository(db_conn)
    offers = OfferRepository(db_conn)
    metrics = MetricsRepository(db_conn)

    s1 = suppliers.create(
        Supplier(name="FICTICIO Proveedor Norte MX", country="MX", notes="DATO FICTICIO")
    )
    s2 = suppliers.create(
        Supplier(name="FICTICIO Proveedor Sur MX", country="MX", notes="DATO FICTICIO")
    )

    p1 = products.create(
        Product(name="FICTICIO Gadget A", sku="FIC-A", weight_grams=Decimal("200"), notes="FICTICIO")
    )
    p2 = products.create(
        Product(name="FICTICIO Gadget B", sku="FIC-B", weight_grams=Decimal("350"), notes="FICTICIO")
    )
    p3 = products.create(
        Product(name="FICTICIO Incompleto", sku="FIC-X", notes="FICTICIO sin precio")
    )

    offers.create(
        Offer(
            product_id=p1.id,  # type: ignore[arg-type]
            supplier_id=s1.id,  # type: ignore[arg-type]
            unit_cost=Decimal("30"),
            unit_cost_provenance=Provenance.ESTIMADO,
            min_order_qty=10,
            pack_qty=10,
            notes="FICTICIO",
        )
    )
    offers.create(
        Offer(
            product_id=p2.id,  # type: ignore[arg-type]
            supplier_id=s2.id,  # type: ignore[arg-type]
            unit_cost=Decimal("45"),
            unit_cost_provenance=Provenance.ESTIMADO,
            min_order_qty=5,
            pack_qty=5,
            notes="FICTICIO",
        )
    )
    # p3: oferta sin costo → desconocido (NULL), no cero
    offers.create(
        Offer(
            product_id=p3.id,  # type: ignore[arg-type]
            supplier_id=s1.id,  # type: ignore[arg-type]
            unit_cost=None,
            unit_cost_provenance=Provenance.PENDIENTE,
            notes="FICTICIO — costo desconocido",
        )
    )

    metrics.create(
        MarketMetrics(
            product_id=p1.id,  # type: ignore[arg-type]
            sale_price=Decimal("199"),
            sale_price_provenance=Provenance.ESTIMADO,
            demand_score=Decimal("80"),
            demand_provenance=Provenance.ESTIMADO,
            competition_score=Decimal("40"),
            competition_provenance=Provenance.ESTIMADO,
            logistics_score=Decimal("70"),
            logistics_provenance=Provenance.ESTIMADO,
            return_risk_score=Decimal("20"),
            return_risk_provenance=Provenance.ESTIMADO,
            source_notes="FICTICIO",
        )
    )
    metrics.create(
        MarketMetrics(
            product_id=p2.id,  # type: ignore[arg-type]
            sale_price=Decimal("249"),
            sale_price_provenance=Provenance.ESTIMADO,
            demand_score=Decimal("55"),
            demand_provenance=Provenance.ESTIMADO,
            competition_score=Decimal("70"),
            competition_provenance=Provenance.ESTIMADO,
            logistics_score=Decimal("60"),
            logistics_provenance=Provenance.ESTIMADO,
            return_risk_score=Decimal("35"),
            return_risk_provenance=Provenance.ESTIMADO,
            source_notes="FICTICIO",
        )
    )
    # p3 sin sale_price

    return {
        "suppliers": (s1, s2),
        "products": (p1, p2, p3),
        "fee_profile": fee_profile,
    }
