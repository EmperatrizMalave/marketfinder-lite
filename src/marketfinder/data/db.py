"""Conexión SQLite, migraciones y seeds — Etapa 1.

Montos monetarios se guardan como INTEGER (centavos).
Valores desconocidos = NULL + proveniencia `pendiente` (nunca 0 inventado).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from marketfinder.core.models import COMMERCIAL_DEFAULTS, utc_now_iso
from marketfinder.utils.paths import db_path

SCHEMA_V1 = """
CREATE TABLE IF NOT EXISTS schema_migrations (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS suppliers (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  country TEXT DEFAULT 'MX',
  contact TEXT,
  url TEXT,
  notes TEXT,
  default_lead_days INTEGER,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY,
  sku TEXT,
  name TEXT NOT NULL,
  category TEXT,
  weight_grams REAL,
  currency TEXT NOT NULL DEFAULT 'MXN',
  kind TEXT NOT NULL DEFAULT 'unitario',
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

-- M2M productos ↔ proveedores vía ofertas
CREATE TABLE IF NOT EXISTS offers (
  id INTEGER PRIMARY KEY,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  supplier_id INTEGER NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
  unit_cost_cents INTEGER,
  unit_cost_provenance TEXT NOT NULL DEFAULT 'pendiente',
  min_order_qty INTEGER NOT NULL DEFAULT 1,
  pack_qty INTEGER NOT NULL DEFAULT 1,
  lead_days INTEGER,
  kind TEXT NOT NULL DEFAULT 'unitario',
  currency TEXT NOT NULL DEFAULT 'MXN',
  notes TEXT,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(product_id, supplier_id, kind)
);

CREATE TABLE IF NOT EXISTS market_metrics (
  id INTEGER PRIMARY KEY,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  sale_price_cents INTEGER,
  sale_price_provenance TEXT NOT NULL DEFAULT 'pendiente',
  demand_score REAL,
  demand_provenance TEXT NOT NULL DEFAULT 'pendiente',
  competition_score REAL,
  competition_provenance TEXT NOT NULL DEFAULT 'pendiente',
  logistics_score REAL,
  logistics_provenance TEXT NOT NULL DEFAULT 'pendiente',
  return_risk_score REAL,
  return_risk_provenance TEXT NOT NULL DEFAULT 'pendiente',
  investment_required_cents INTEGER,
  investment_provenance TEXT NOT NULL DEFAULT 'pendiente',
  monthly_sales_estimate REAL,
  monthly_sales_provenance TEXT NOT NULL DEFAULT 'pendiente',
  analysis_period_days INTEGER DEFAULT 14,
  source_notes TEXT,
  captured_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS price_history (
  id INTEGER PRIMARY KEY,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  offer_id INTEGER REFERENCES offers(id) ON DELETE SET NULL,
  kind TEXT NOT NULL,
  amount_cents INTEGER NOT NULL,
  provenance TEXT NOT NULL DEFAULT 'pendiente',
  source_notes TEXT,
  captured_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fee_profiles (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  commission_rate REAL NOT NULL DEFAULT 0,
  payment_fee_rate REAL NOT NULL DEFAULT 0,
  shipping_cost_fixed_cents INTEGER NOT NULL DEFAULT 0,
  shipping_cost_rate REAL NOT NULL DEFAULT 0,
  iva_rate REAL NOT NULL DEFAULT 0,
  retention_rate REAL NOT NULL DEFAULT 0,
  isr_rate REAL NOT NULL DEFAULT 0,
  other_cost_fixed_cents INTEGER NOT NULL DEFAULT 0,
  other_cost_rate REAL NOT NULL DEFAULT 0,
  packaging_cost_fixed_cents INTEGER NOT NULL DEFAULT 0,
  ads_cost_rate REAL NOT NULL DEFAULT 0,
  target_margin REAL NOT NULL DEFAULT 0.25,
  notes TEXT,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ranking_weights (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  w_demand REAL NOT NULL DEFAULT 0.30,
  w_profitability REAL NOT NULL DEFAULT 0.30,
  w_competition REAL NOT NULL DEFAULT 0.15,
  w_investment REAL NOT NULL DEFAULT 0.10,
  w_logistics REAL NOT NULL DEFAULT 0.10,
  w_return_risk REAL NOT NULL DEFAULT 0.05,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS research_runs (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  budget_limit_cents INTEGER DEFAULT 300000,
  reserve_amount_cents INTEGER DEFAULT 0,
  fee_profile_id INTEGER REFERENCES fee_profiles(id),
  market TEXT DEFAULT 'MX',
  platform TEXT DEFAULT 'ML',
  notes TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS research_items (
  id INTEGER PRIMARY KEY,
  run_id INTEGER NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
  product_id INTEGER NOT NULL REFERENCES products(id),
  metrics_id INTEGER REFERENCES market_metrics(id),
  offer_id INTEGER REFERENCES offers(id),
  qty_suggested INTEGER,
  capital_allocated_cents INTEGER,
  score REAL,
  confidence REAL,
  rank INTEGER,
  band TEXT,
  calc_json TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS app_settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_offers_product ON offers(product_id);
CREATE INDEX IF NOT EXISTS idx_offers_supplier ON offers(supplier_id);
CREATE INDEX IF NOT EXISTS idx_metrics_product ON market_metrics(product_id);
CREATE INDEX IF NOT EXISTS idx_price_history_product ON price_history(product_id);
"""


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    db = Path(path) if path else db_path()
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _migration_applied(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM schema_migrations WHERE name = ?", (name,)
    ).fetchone()
    return row is not None


def _record_migration(conn: sqlite3.Connection, name: str) -> None:
    conn.execute(
        "INSERT INTO schema_migrations (name, applied_at) VALUES (?, ?)",
        (name, utc_now_iso()),
    )


def _seed(conn: sqlite3.Connection) -> None:
    now = utc_now_iso()
    # Pesos de ranking
    existing = conn.execute("SELECT id FROM ranking_weights WHERE id = 1").fetchone()
    if existing is None:
        conn.execute(
            """
            INSERT INTO ranking_weights (
              id, w_demand, w_profitability, w_competition,
              w_investment, w_logistics, w_return_risk, updated_at
            ) VALUES (1, 0.30, 0.30, 0.15, 0.10, 0.10, 0.05, ?)
            """,
            (now,),
        )

    # Perfil de fees placeholder (NO tarifa oficial)
    fee = conn.execute(
        "SELECT id FROM fee_profiles WHERE name = ?", ("ml_mx_manual",)
    ).fetchone()
    if fee is None:
        conn.execute(
            """
            INSERT INTO fee_profiles (
              name, commission_rate, payment_fee_rate,
              shipping_cost_fixed_cents, shipping_cost_rate,
              iva_rate, retention_rate, isr_rate,
              other_cost_fixed_cents, other_cost_rate,
              packaging_cost_fixed_cents, ads_cost_rate,
              target_margin, notes, updated_at
            ) VALUES (
              'ml_mx_manual', 0.13, 0.0,
              0, 0.0,
              0.0, 0.0, 0.0,
              0, 0.0,
              0, 0.0,
              0.25,
              'Parámetro editable — verificar en ML / SAT. No es tarifa oficial.',
              ?
            )
            """,
            (now,),
        )

    for key, value in COMMERCIAL_DEFAULTS.items():
        row = conn.execute(
            "SELECT key FROM app_settings WHERE key = ?", (key,)
        ).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO app_settings (key, value, updated_at) VALUES (?, ?, ?)",
                (key, str(value), now),
            )


def initialize_db(path: Path | str | None = None) -> sqlite3.Connection:
    """Abre (o crea) la DB, aplica migraciones y seeds."""
    conn = connect(path)
    # Tabla de migraciones primero (idempotente)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL UNIQUE,
          applied_at TEXT NOT NULL
        );
        """
    )
    if not _migration_applied(conn, "001_etapa1_schema"):
        conn.executescript(SCHEMA_V1)
        _record_migration(conn, "001_etapa1_schema")
    _seed(conn)
    conn.commit()
    return conn
