"""Repositorios SQLite — productos, proveedores, ofertas, métricas, config."""

from __future__ import annotations

import sqlite3
from decimal import Decimal

from marketfinder.core.money import cents_to_decimal, decimal_to_cents
from marketfinder.core.models import (
    COMMERCIAL_DEFAULTS,
    FeeProfile,
    MarketMetrics,
    Offer,
    OfferKind,
    PriceHistoryEntry,
    Product,
    Provenance,
    RankingWeights,
    ResearchItem,
    ResearchRun,
    Supplier,
    utc_now_iso,
)


def _d(value: float | int | str | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _prov(value: str | None) -> Provenance:
    if not value:
        return Provenance.PENDIENTE
    return Provenance(value)


# ── Suppliers ──────────────────────────────────────────────────────────────


class SupplierRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, supplier: Supplier) -> Supplier:
        now = utc_now_iso()
        cur = self.conn.execute(
            """
            INSERT INTO suppliers (
              name, country, contact, url, notes, default_lead_days,
              created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                supplier.name,
                supplier.country,
                supplier.contact,
                supplier.url,
                supplier.notes,
                supplier.default_lead_days,
                now,
                now,
            ),
        )
        self.conn.commit()
        supplier.id = int(cur.lastrowid)
        supplier.created_at = now
        supplier.updated_at = now
        return supplier

    def update(self, supplier: Supplier) -> Supplier:
        if supplier.id is None:
            raise ValueError("supplier.id requerido para update")
        now = utc_now_iso()
        self.conn.execute(
            """
            UPDATE suppliers SET
              name=?, country=?, contact=?, url=?, notes=?,
              default_lead_days=?, updated_at=?
            WHERE id=?
            """,
            (
                supplier.name,
                supplier.country,
                supplier.contact,
                supplier.url,
                supplier.notes,
                supplier.default_lead_days,
                now,
                supplier.id,
            ),
        )
        self.conn.commit()
        supplier.updated_at = now
        return supplier

    def get(self, supplier_id: int) -> Supplier | None:
        row = self.conn.execute(
            "SELECT * FROM suppliers WHERE id = ?", (supplier_id,)
        ).fetchone()
        return self._from_row(row) if row else None

    def list_all(self) -> list[Supplier]:
        rows = self.conn.execute(
            "SELECT * FROM suppliers ORDER BY name COLLATE NOCASE"
        ).fetchall()
        return [self._from_row(r) for r in rows]

    def delete(self, supplier_id: int) -> None:
        self.conn.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
        self.conn.commit()

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Supplier:
        return Supplier(
            id=row["id"],
            name=row["name"],
            country=row["country"] or "MX",
            contact=row["contact"],
            url=row["url"],
            notes=row["notes"],
            default_lead_days=row["default_lead_days"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


# ── Products ───────────────────────────────────────────────────────────────


class ProductRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, product: Product) -> Product:
        now = utc_now_iso()
        cur = self.conn.execute(
            """
            INSERT INTO products (
              sku, name, category, weight_grams, currency, kind, notes,
              created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product.sku,
                product.name,
                product.category,
                float(product.weight_grams) if product.weight_grams is not None else None,
                product.currency,
                str(product.kind),
                product.notes,
                now,
                now,
            ),
        )
        self.conn.commit()
        product.id = int(cur.lastrowid)
        product.created_at = now
        product.updated_at = now
        return product

    def update(self, product: Product) -> Product:
        if product.id is None:
            raise ValueError("product.id requerido para update")
        now = utc_now_iso()
        self.conn.execute(
            """
            UPDATE products SET
              sku=?, name=?, category=?, weight_grams=?, currency=?,
              kind=?, notes=?, updated_at=?
            WHERE id=?
            """,
            (
                product.sku,
                product.name,
                product.category,
                float(product.weight_grams) if product.weight_grams is not None else None,
                product.currency,
                str(product.kind),
                product.notes,
                now,
                product.id,
            ),
        )
        self.conn.commit()
        product.updated_at = now
        return product

    def get(self, product_id: int) -> Product | None:
        row = self.conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        return self._from_row(row) if row else None

    def list_all(self) -> list[Product]:
        rows = self.conn.execute(
            "SELECT * FROM products ORDER BY name COLLATE NOCASE"
        ).fetchall()
        return [self._from_row(r) for r in rows]

    def count(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) AS c FROM products").fetchone()
        return int(row["c"])

    def delete(self, product_id: int) -> None:
        self.conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        self.conn.commit()

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Product:
        return Product(
            id=row["id"],
            sku=row["sku"],
            name=row["name"],
            category=row["category"],
            weight_grams=_d(row["weight_grams"]),
            currency=row["currency"] or "MXN",
            kind=OfferKind(row["kind"] or "unitario"),
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


# ── Offers (M2M) ───────────────────────────────────────────────────────────


class OfferRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, offer: Offer) -> Offer:
        now = utc_now_iso()
        cents = decimal_to_cents(offer.unit_cost)
        cur = self.conn.execute(
            """
            INSERT INTO offers (
              product_id, supplier_id, unit_cost_cents, unit_cost_provenance,
              min_order_qty, pack_qty, lead_days, kind, currency, notes,
              is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                offer.product_id,
                offer.supplier_id,
                cents,
                str(offer.unit_cost_provenance),
                offer.min_order_qty,
                offer.pack_qty,
                offer.lead_days,
                str(offer.kind),
                offer.currency,
                offer.notes,
                1 if offer.is_active else 0,
                now,
                now,
            ),
        )
        self.conn.commit()
        offer.id = int(cur.lastrowid)
        offer.created_at = now
        offer.updated_at = now
        if cents is not None:
            self._append_price_history(
                product_id=offer.product_id,
                offer_id=offer.id,
                kind="unit_cost",
                amount_cents=cents,
                provenance=offer.unit_cost_provenance,
            )
        return offer

    def update(self, offer: Offer) -> Offer:
        if offer.id is None:
            raise ValueError("offer.id requerido para update")
        now = utc_now_iso()
        cents = decimal_to_cents(offer.unit_cost)
        old = self.get(offer.id)
        self.conn.execute(
            """
            UPDATE offers SET
              product_id=?, supplier_id=?, unit_cost_cents=?,
              unit_cost_provenance=?, min_order_qty=?, pack_qty=?,
              lead_days=?, kind=?, currency=?, notes=?, is_active=?,
              updated_at=?
            WHERE id=?
            """,
            (
                offer.product_id,
                offer.supplier_id,
                cents,
                str(offer.unit_cost_provenance),
                offer.min_order_qty,
                offer.pack_qty,
                offer.lead_days,
                str(offer.kind),
                offer.currency,
                offer.notes,
                1 if offer.is_active else 0,
                now,
                offer.id,
            ),
        )
        self.conn.commit()
        offer.updated_at = now
        old_cents = decimal_to_cents(old.unit_cost) if old else None
        if cents is not None and cents != old_cents:
            self._append_price_history(
                product_id=offer.product_id,
                offer_id=offer.id,
                kind="unit_cost",
                amount_cents=cents,
                provenance=offer.unit_cost_provenance,
            )
        return offer

    def get(self, offer_id: int) -> Offer | None:
        row = self.conn.execute(
            "SELECT * FROM offers WHERE id = ?", (offer_id,)
        ).fetchone()
        return self._from_row(row) if row else None

    def list_for_product(self, product_id: int) -> list[Offer]:
        rows = self.conn.execute(
            "SELECT * FROM offers WHERE product_id = ? ORDER BY id",
            (product_id,),
        ).fetchall()
        return [self._from_row(r) for r in rows]

    def list_for_supplier(self, supplier_id: int) -> list[Offer]:
        rows = self.conn.execute(
            "SELECT * FROM offers WHERE supplier_id = ? ORDER BY id",
            (supplier_id,),
        ).fetchall()
        return [self._from_row(r) for r in rows]

    def list_active(self) -> list[Offer]:
        rows = self.conn.execute(
            "SELECT * FROM offers WHERE is_active = 1 ORDER BY id"
        ).fetchall()
        return [self._from_row(r) for r in rows]

    def delete(self, offer_id: int) -> None:
        self.conn.execute("DELETE FROM offers WHERE id = ?", (offer_id,))
        self.conn.commit()

    def _append_price_history(
        self,
        *,
        product_id: int,
        offer_id: int | None,
        kind: str,
        amount_cents: int,
        provenance: Provenance,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO price_history (
              product_id, offer_id, kind, amount_cents, provenance, captured_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (product_id, offer_id, kind, amount_cents, str(provenance), utc_now_iso()),
        )
        self.conn.commit()

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Offer:
        return Offer(
            id=row["id"],
            product_id=row["product_id"],
            supplier_id=row["supplier_id"],
            unit_cost=cents_to_decimal(row["unit_cost_cents"]),
            unit_cost_provenance=_prov(row["unit_cost_provenance"]),
            min_order_qty=int(row["min_order_qty"] or 1),
            pack_qty=int(row["pack_qty"] or 1),
            lead_days=row["lead_days"],
            kind=OfferKind(row["kind"] or "unitario"),
            currency=row["currency"] or "MXN",
            notes=row["notes"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


# ── Market metrics ─────────────────────────────────────────────────────────


class MetricsRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, metrics: MarketMetrics) -> MarketMetrics:
        sale_cents = decimal_to_cents(metrics.sale_price)
        inv_cents = decimal_to_cents(metrics.investment_required)
        cur = self.conn.execute(
            """
            INSERT INTO market_metrics (
              product_id, sale_price_cents, sale_price_provenance,
              demand_score, demand_provenance,
              competition_score, competition_provenance,
              logistics_score, logistics_provenance,
              return_risk_score, return_risk_provenance,
              investment_required_cents, investment_provenance,
              monthly_sales_estimate, monthly_sales_provenance,
              analysis_period_days, source_notes, captured_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                metrics.product_id,
                sale_cents,
                str(metrics.sale_price_provenance),
                float(metrics.demand_score) if metrics.demand_score is not None else None,
                str(metrics.demand_provenance),
                float(metrics.competition_score)
                if metrics.competition_score is not None
                else None,
                str(metrics.competition_provenance),
                float(metrics.logistics_score)
                if metrics.logistics_score is not None
                else None,
                str(metrics.logistics_provenance),
                float(metrics.return_risk_score)
                if metrics.return_risk_score is not None
                else None,
                str(metrics.return_risk_provenance),
                inv_cents,
                str(metrics.investment_provenance),
                float(metrics.monthly_sales_estimate)
                if metrics.monthly_sales_estimate is not None
                else None,
                str(metrics.monthly_sales_provenance),
                metrics.analysis_period_days,
                metrics.source_notes,
                metrics.captured_at,
            ),
        )
        self.conn.commit()
        metrics.id = int(cur.lastrowid)
        if sale_cents is not None:
            self.conn.execute(
                """
                INSERT INTO price_history (
                  product_id, offer_id, kind, amount_cents, provenance, captured_at
                ) VALUES (?, NULL, 'sale_price', ?, ?, ?)
                """,
                (
                    metrics.product_id,
                    sale_cents,
                    str(metrics.sale_price_provenance),
                    metrics.captured_at,
                ),
            )
            self.conn.commit()
        return metrics

    def latest_for_product(self, product_id: int) -> MarketMetrics | None:
        row = self.conn.execute(
            """
            SELECT * FROM market_metrics
            WHERE product_id = ?
            ORDER BY captured_at DESC, id DESC LIMIT 1
            """,
            (product_id,),
        ).fetchone()
        return self._from_row(row) if row else None

    def get(self, metrics_id: int) -> MarketMetrics | None:
        row = self.conn.execute(
            "SELECT * FROM market_metrics WHERE id = ?", (metrics_id,)
        ).fetchone()
        return self._from_row(row) if row else None

    @staticmethod
    def _from_row(row: sqlite3.Row) -> MarketMetrics:
        return MarketMetrics(
            id=row["id"],
            product_id=row["product_id"],
            sale_price=cents_to_decimal(row["sale_price_cents"]),
            sale_price_provenance=_prov(row["sale_price_provenance"]),
            demand_score=_d(row["demand_score"]),
            demand_provenance=_prov(row["demand_provenance"]),
            competition_score=_d(row["competition_score"]),
            competition_provenance=_prov(row["competition_provenance"]),
            logistics_score=_d(row["logistics_score"]),
            logistics_provenance=_prov(row["logistics_provenance"]),
            return_risk_score=_d(row["return_risk_score"]),
            return_risk_provenance=_prov(row["return_risk_provenance"]),
            investment_required=cents_to_decimal(row["investment_required_cents"]),
            investment_provenance=_prov(row["investment_provenance"]),
            monthly_sales_estimate=_d(row["monthly_sales_estimate"]),
            monthly_sales_provenance=_prov(row["monthly_sales_provenance"]),
            analysis_period_days=int(row["analysis_period_days"] or 14),
            source_notes=row["source_notes"],
            captured_at=row["captured_at"],
        )


# ── Config / fees / weights ────────────────────────────────────────────────


class SettingsRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get(self, key: str, default: str | None = None) -> str | None:
        row = self.conn.execute(
            "SELECT value FROM app_settings WHERE key = ?", (key,)
        ).fetchone()
        if row is None:
            return default
        return str(row["value"])

    def set(self, key: str, value: str) -> None:
        now = utc_now_iso()
        self.conn.execute(
            """
            INSERT INTO app_settings (key, value, updated_at) VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
            """,
            (key, value, now),
        )
        self.conn.commit()

    def all(self) -> dict[str, str]:
        rows = self.conn.execute("SELECT key, value FROM app_settings").fetchall()
        return {r["key"]: r["value"] for r in rows}

    def commercial_defaults(self) -> dict[str, str]:
        stored = self.all()
        out = {k: str(v) for k, v in COMMERCIAL_DEFAULTS.items()}
        out.update(stored)
        return out


class FeeProfileRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get_by_name(self, name: str) -> FeeProfile | None:
        row = self.conn.execute(
            "SELECT * FROM fee_profiles WHERE name = ?", (name,)
        ).fetchone()
        return self._from_row(row) if row else None

    def get(self, profile_id: int) -> FeeProfile | None:
        row = self.conn.execute(
            "SELECT * FROM fee_profiles WHERE id = ?", (profile_id,)
        ).fetchone()
        return self._from_row(row) if row else None

    def list_all(self) -> list[FeeProfile]:
        rows = self.conn.execute(
            "SELECT * FROM fee_profiles ORDER BY name"
        ).fetchall()
        return [self._from_row(r) for r in rows]

    def update(self, profile: FeeProfile) -> FeeProfile:
        if profile.id is None:
            raise ValueError("fee profile id requerido")
        now = utc_now_iso()
        self.conn.execute(
            """
            UPDATE fee_profiles SET
              name=?, commission_rate=?, payment_fee_rate=?,
              shipping_cost_fixed_cents=?, shipping_cost_rate=?,
              iva_rate=?, retention_rate=?, isr_rate=?,
              other_cost_fixed_cents=?, other_cost_rate=?,
              packaging_cost_fixed_cents=?, ads_cost_rate=?,
              target_margin=?, notes=?, updated_at=?
            WHERE id=?
            """,
            (
                profile.name,
                float(profile.commission_rate),
                float(profile.payment_fee_rate),
                decimal_to_cents(profile.shipping_cost_fixed) or 0,
                float(profile.shipping_cost_rate),
                float(profile.iva_rate),
                float(profile.retention_rate),
                float(profile.isr_rate),
                decimal_to_cents(profile.other_cost_fixed) or 0,
                float(profile.other_cost_rate),
                decimal_to_cents(profile.packaging_cost_fixed) or 0,
                float(profile.ads_cost_rate),
                float(profile.target_margin),
                profile.notes,
                now,
                profile.id,
            ),
        )
        self.conn.commit()
        profile.updated_at = now
        return profile

    @staticmethod
    def _from_row(row: sqlite3.Row) -> FeeProfile:
        return FeeProfile(
            id=row["id"],
            name=row["name"],
            commission_rate=Decimal(str(row["commission_rate"] or 0)),
            payment_fee_rate=Decimal(str(row["payment_fee_rate"] or 0)),
            shipping_cost_fixed=cents_to_decimal(row["shipping_cost_fixed_cents"])
            or Decimal("0"),
            shipping_cost_rate=Decimal(str(row["shipping_cost_rate"] or 0)),
            iva_rate=Decimal(str(row["iva_rate"] or 0)),
            retention_rate=Decimal(str(row["retention_rate"] or 0)),
            isr_rate=Decimal(str(row["isr_rate"] or 0)),
            other_cost_fixed=cents_to_decimal(row["other_cost_fixed_cents"])
            or Decimal("0"),
            other_cost_rate=Decimal(str(row["other_cost_rate"] or 0)),
            packaging_cost_fixed=cents_to_decimal(row["packaging_cost_fixed_cents"])
            or Decimal("0"),
            ads_cost_rate=Decimal(str(row["ads_cost_rate"] or 0)),
            target_margin=Decimal(str(row["target_margin"] or "0.25")),
            notes=row["notes"],
            updated_at=row["updated_at"],
        )


class WeightsRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get(self) -> RankingWeights:
        row = self.conn.execute(
            "SELECT * FROM ranking_weights WHERE id = 1"
        ).fetchone()
        if row is None:
            return RankingWeights()
        return RankingWeights(
            w_demand=Decimal(str(row["w_demand"])),
            w_profitability=Decimal(str(row["w_profitability"])),
            w_competition=Decimal(str(row["w_competition"])),
            w_investment=Decimal(str(row["w_investment"])),
            w_logistics=Decimal(str(row["w_logistics"])),
            w_return_risk=Decimal(str(row["w_return_risk"])),
            updated_at=row["updated_at"],
        )


class PriceHistoryRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def list_for_product(self, product_id: int) -> list[PriceHistoryEntry]:
        rows = self.conn.execute(
            """
            SELECT * FROM price_history
            WHERE product_id = ?
            ORDER BY captured_at DESC, id DESC
            """,
            (product_id,),
        ).fetchall()
        return [
            PriceHistoryEntry(
                id=r["id"],
                product_id=r["product_id"],
                offer_id=r["offer_id"],
                kind=r["kind"],
                amount=cents_to_decimal(r["amount_cents"]) or Decimal("0"),
                provenance=_prov(r["provenance"]),
                source_notes=r["source_notes"],
                captured_at=r["captured_at"],
            )
            for r in rows
        ]


class ResearchRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create_run(self, run: ResearchRun) -> ResearchRun:
        cur = self.conn.execute(
            """
            INSERT INTO research_runs (
              title, budget_limit_cents, reserve_amount_cents, fee_profile_id,
              market, platform, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run.title,
                decimal_to_cents(run.budget_limit) or 0,
                decimal_to_cents(run.reserve_amount) or 0,
                run.fee_profile_id,
                run.market,
                run.platform,
                run.notes,
                run.created_at,
            ),
        )
        self.conn.commit()
        run.id = int(cur.lastrowid)
        return run

    def add_item(self, item: ResearchItem) -> ResearchItem:
        cur = self.conn.execute(
            """
            INSERT INTO research_items (
              run_id, product_id, metrics_id, offer_id, qty_suggested,
              capital_allocated_cents, score, confidence, rank, band,
              calc_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.run_id,
                item.product_id,
                item.metrics_id,
                item.offer_id,
                item.qty_suggested,
                decimal_to_cents(item.capital_allocated),
                float(item.score) if item.score is not None else None,
                float(item.confidence) if item.confidence is not None else None,
                item.rank,
                str(item.band),
                item.calc_json,
                item.created_at,
            ),
        )
        self.conn.commit()
        item.id = int(cur.lastrowid)
        return item

    def items_for_run(self, run_id: int) -> list[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT ri.*, p.name AS product_name
            FROM research_items ri
            JOIN products p ON p.id = ri.product_id
            WHERE ri.run_id = ?
            ORDER BY CASE WHEN ri.rank IS NULL THEN 1 ELSE 0 END,
                     ri.rank ASC, ri.score DESC
            """,
            (run_id,),
        ).fetchall()
