# Plan detallado — Etapa 1 (Núcleo offline + motor financiero)

**Fecha:** 26 nov 2026 (America/Mexico_City)  
**Estado:** **IMPLEMENTADA** (26 nov 2026, America/Mexico_City) — 1.1→1.7 en CORI_OMNI. Aprobada con mejoras. Pendiente OK usuario antes de Etapa 2.  
**Regla:** no iniciar Etapa 2 sin aprobación explícita.

Proyecto: `C:\Users\emper\Documents\dev\marketfinder-lite`  
Plan maestro: `docs/marketfinder-lite-plan.md`

---

## 1. Objetivos

1. Persistir datos locales en **SQLite** (productos, proveedores, escenarios, métricas, proveniencia).  
2. Implementar **calculadora de rentabilidad** parametrizable (comisiones, envío, impuestos, otros costos) **sin** fijar tarifas “oficiales” desactualizadas en código duro.  
3. Implementar **optimizador de presupuesto** (asignar capital limitado entre oportunidades candidatas; default presupuesto **$3 000 MXN**).  
4. Implementar **scoring / ranking** con la ponderación y bandas definitivas del usuario.  
5. CRUD básico de **productos** y **proveedores** (UI mínima usable + capa `core`/`data`).  
6. **Logging** estructurado a archivo bajo `%APPDATA%\MarketFinderLite\logs\`.  
7. Cargar **parámetros comerciales iniciales** como defaults configurables.  
8. Pruebas unitarias de fórmulas y ranking; humo de DB.  
9. Conservar Etapa 0 (tema, sidebar, navegación).

---

## 2. Módulos a entregar

| Módulo | Responsabilidad | Ubicación prevista |
|--------|-----------------|-------------------|
| Modelos de dominio | Dataclasses / esquemas; proveniencia | `src/marketfinder/core/models.py` |
| Productos | Alta/edición/listado; vínculo a métricas | `data/repositories` + vista UI |
| Proveedores | Alta/edición; costo, lead time, notas; preferente MX | igual |
| Calculadora | Margen, ROI, break-even estimado; margen objetivo 25 % | `core/profitability.py` |
| Optimizador presupuesto | Selección bajo tope de inversión ($3 000 default) | `core/budget.py` |
| Scoring / ranking | Score ponderado + bandas | `core/scoring.py` |
| SQLite | Conexión, migraciones simples, repos | `data/db.py`, `data/repositories.py` |
| Logging | Rotación básica / niveles | `utils/logging.py` |
| Config params | Pesos, tarifas, parámetros comerciales | `config/settings.py` + tablas |
| Export mínimo | CSV o Excel básico de ranking | `data/excel_io.py` (parcial) |

---

## 3. Parámetros comerciales iniciales (defaults configurables)

| Parámetro | Default |
|-----------|---------|
| Mercado | México |
| Plataforma | Mercado Libre (MLM) |
| Presupuesto | $3 000 MXN |
| Costo de adquisición | $5–50 MXN |
| Precio de venta | $149–299 MXN |
| Margen objetivo | 25 % |
| Peso producto | ≤ 500 g |
| Proveedores | Preferente México |
| Periodo de análisis | 14 días |
| Compra inicial | 10–20 unidades |

Estos valores alimentan seeds de `app_settings` / perfiles; el usuario puede cambiarlos en Configuración. No son tarifas oficiales de ML.

---

## 4. Ranking definitivo

### 4.1 Ponderación (fijada por el usuario)

| Factor | Peso | Clave sugerida |
|--------|------|----------------|
| Demanda | **30 %** | `w_demand` |
| Rentabilidad | **30 %** | `w_profitability` |
| Competencia | **15 %** | `w_competition` |
| Inversión requerida | **10 %** | `w_investment` |
| Logística | **10 %** | `w_logistics` |
| Riesgo de devolución | **5 %** | `w_return_risk` |
| **Total** | **100 %** | |

Normalizar cada factor a 0–100 antes de ponderar. Para competencia, inversión y riesgo de devolución, un valor “peor” baja el factor (p. ej. más competencia → menor aporte al score).

```text
score = 0.30*demanda + 0.30*rentabilidad + 0.15*competencia_favorable
      + 0.10*inversion_favorable + 0.10*logistica + 0.05*bajo_riesgo_devolucion
```

### 4.2 Bandas

| Score | Etiqueta |
|-------|----------|
| 80–100 | **Alta** |
| 60–79 | **Requiere investigación** |
| &lt; 60 | **Poco atractiva** |
| Datos esenciales incompletos | **Pendiente** — no aprobar por score solo |

Regla de negocio: si faltan datos esenciales (p. ej. costo y precio de venta), el ítem queda `pendiente` aunque el score parcial sea alto.

---

## 5. Esquema DB propuesto (SQLite)

Ubicación archivo: `%APPDATA%\MarketFinderLite\marketfinder.db`

```sql
-- proveniencia: 'verificado' | 'estimado' | 'pendiente'
-- banda ranking: 'alta' | 'requiere_investigacion' | 'poco_atractiva' | 'pendiente'

CREATE TABLE schema_migrations (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  applied_at TEXT NOT NULL
);

CREATE TABLE suppliers (
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

CREATE TABLE products (
  id INTEGER PRIMARY KEY,
  sku TEXT,
  name TEXT NOT NULL,
  category TEXT,
  supplier_id INTEGER REFERENCES suppliers(id),
  unit_cost REAL,                    -- costo adquisición
  unit_cost_provenance TEXT NOT NULL DEFAULT 'pendiente',
  weight_grams REAL,                 -- objetivo ≤ 500
  currency TEXT NOT NULL DEFAULT 'MXN',
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE market_metrics (
  id INTEGER PRIMARY KEY,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  sale_price REAL,
  sale_price_provenance TEXT NOT NULL DEFAULT 'pendiente',
  demand_score REAL,                 -- 0–100 o NULL
  demand_provenance TEXT NOT NULL DEFAULT 'pendiente',
  competition_score REAL,            -- bruto; el scoring lo invierte al pesar
  competition_provenance TEXT NOT NULL DEFAULT 'pendiente',
  logistics_score REAL,
  logistics_provenance TEXT NOT NULL DEFAULT 'pendiente',
  return_risk_score REAL,            -- mayor = más riesgo
  return_risk_provenance TEXT NOT NULL DEFAULT 'pendiente',
  investment_required REAL,          -- capital estimado del escenario
  investment_provenance TEXT NOT NULL DEFAULT 'pendiente',
  monthly_sales_estimate REAL,
  monthly_sales_provenance TEXT NOT NULL DEFAULT 'pendiente',
  analysis_period_days INTEGER DEFAULT 14,
  source_notes TEXT,
  captured_at TEXT NOT NULL
);

CREATE TABLE fee_profiles (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,         -- ej. 'ml_mx_manual'
  -- PARAMETROS editables, no "tarifa oficial congelada"
  commission_rate REAL NOT NULL,
  payment_fee_rate REAL NOT NULL DEFAULT 0,
  shipping_cost_fixed REAL NOT NULL DEFAULT 0,
  shipping_cost_rate REAL NOT NULL DEFAULT 0,
  tax_rate REAL NOT NULL DEFAULT 0,
  other_cost_fixed REAL NOT NULL DEFAULT 0,
  target_margin REAL NOT NULL DEFAULT 0.25,
  notes TEXT,
  updated_at TEXT NOT NULL
);

CREATE TABLE ranking_weights (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  w_demand REAL NOT NULL DEFAULT 0.30,
  w_profitability REAL NOT NULL DEFAULT 0.30,
  w_competition REAL NOT NULL DEFAULT 0.15,
  w_investment REAL NOT NULL DEFAULT 0.10,
  w_logistics REAL NOT NULL DEFAULT 0.10,
  w_return_risk REAL NOT NULL DEFAULT 0.05,
  updated_at TEXT NOT NULL
);

CREATE TABLE research_runs (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  budget_limit REAL DEFAULT 3000,
  fee_profile_id INTEGER REFERENCES fee_profiles(id),
  market TEXT DEFAULT 'MX',
  platform TEXT DEFAULT 'ML',
  notes TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE research_items (
  id INTEGER PRIMARY KEY,
  run_id INTEGER NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
  product_id INTEGER NOT NULL REFERENCES products(id),
  metrics_id INTEGER REFERENCES market_metrics(id),
  qty_suggested INTEGER,             -- default escenario 10–20
  capital_allocated REAL,
  score REAL,
  rank INTEGER,
  band TEXT,                         -- alta | requiere_investigacion | poco_atractiva | pendiente
  calc_json TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE app_settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

**Seeds sugeridos en `app_settings`:** `budget_default=3000`, `cost_min=5`, `cost_max=50`, `price_min=149`, `price_max=299`, `target_margin=0.25`, `max_weight_g=500`, `prefer_supplier_country=MX`, `analysis_period_days=14`, `initial_qty_min=10`, `initial_qty_max=20`.

**Notas:** no guardar tokens/secretos; migraciones versionadas en código.

---

## 6. Fórmulas configurables (calculadora)

Entradas (por producto / perfil):

- `C` = costo unidad (rango guía $5–50)  
- `P` = precio de venta (rango guía $149–299)  
- `r_c`, `r_p`, `r_s`, `r_t`, `O` = comisión, fee pago, envío rate, impuesto, otros  
- `target_margin` = 0.25 (referencia; no oculta el cálculo real)

Propuesta de desglose:

```text
fees_var    = P * (r_c + r_p + r_s)
tax_amount  = P * r_t
cost_total  = C + fees_var + S_fijo + tax_amount + O
profit      = P - cost_total
margin      = profit / P       # si P > 0
roi         = profit / C       # si C > 0
meets_target = margin >= target_margin
```

Valores de fees: **placeholders editables** con etiqueta “verificar en ML”. No afirmar vigencia oficial.

### Optimizador de presupuesto

1. Filtrar candidatos con datos esenciales (`C`, `P`).  
2. Calcular score y banda; excluir o marcar `pendiente` si faltan esenciales.  
3. Ordenar por score (y/o profit/capital).  
4. Greedy bajo `budget_limit` (default 3000).  
5. Sugerir `qty` dentro de 10–20 cuando el capital lo permita.  
6. Devolver selección, usado, residual, excluidos con motivo.

---

## 7. Dependencias a instalar en Etapa 1 (solo necesarias)

| Paquete | ¿Etapa 1? | Motivo |
|---------|-----------|--------|
| **pandas** | **Sí** | Tablas de ranking / exportación |
| **openpyxl** | **Sí** | Excel mínimo (evita rehacer en Etapa 2) |
| requests | **No** | Etapa 3+ |
| pyinstaller | **No** | Etapa 5 |
| cryptography | **No** | Etapa 8 |

Ya presentes: customtkinter, python-dotenv, pytest, stdlib `sqlite3`.

---

## 8. Pruebas (Etapa 1)

| Caso | Tipo |
|------|------|
| Calculadora: profit/margen con fixture de tarifas | unit |
| Calculadora: respeta margen objetivo 25 % como flag | unit |
| Ranking: pesos 30/30/15/10/10/5 producen orden estable | unit |
| Ranking: banda 80–100 / 60–79 / &lt;60 | unit |
| Ranking: datos esenciales incompletos → `pendiente` (no aprueba) | unit |
| Optimizador: respeta budget 3000 | unit |
| Optimizador: qty sugerida en rango 10–20 cuando aplica | unit |
| DB: schema + seed settings/weights | integration |
| Proveniencia default `pendiente` | unit |
| Logging sin secretos | unit |
| Smoke UI Etapa 0 | mantener 6 tests |

Sin red. Fixtures en `tests/fixtures/`.

---

## 9. Criterios de aceptación

- [ ] SQLite en ruta de usuario (o override en tests).  
- [ ] Proveedor y producto registrables (UI o API interna).  
- [ ] Calculadora con desglose y `fee_profiles` editables.  
- [ ] Ranking usa exactamente los pesos 30/30/15/10/10/5.  
- [ ] Bandas y regla “pendiente si faltan esenciales” correctas.  
- [ ] Optimizador no excede presupuesto; defaults comerciales cargados.  
- [ ] Proveniencia visible en métricas sensibles.  
- [ ] Logs sin secretos.  
- [ ] `pytest` verde (Etapa 0 + nuevos).  
- [ ] README / nota de dónde está la DB.  
- [ ] **Ningún** cliente ML, **ninguna** web, **ningún** pago/licencia.

---

## 10. Fuera de alcance (Etapa 1)

- Comparador Excel ↔ IA (Etapa 2)  
- API Mercado Libre / OAuth (Etapa 3)  
- Website / landing Cloudflare (Etapa 6) — secciones ya definidas en el plan maestro; **no construir**  
- PyInstaller / Inno Setup  
- Pagos, Lite/Pro, Cryptography  
- Scraping / APIs de IA  
- Tarifas ML “definitivas” hardcodeadas como verdad  
- Otros proyectos fuera de `marketfinder-lite`

---

## 11. Pasos ordenados

1. Aprobación del usuario de este documento.  
2. Añadir `pandas` y `openpyxl` al proyecto e instalar en `.venv`.  
3. Crear paquetes `core/`, `data/`, `utils/`.  
4. `paths` (APPDATA) + `logging`.  
5. `db.py` + migración inicial (schema arriba).  
6. Repositorios + seeds (pesos, settings comerciales, fee profile placeholder).  
7. `profitability.py` + tests.  
8. `scoring.py` (pesos + bandas + pendiente) + tests.  
9. `budget.py` + tests.  
10. Vistas UI mínimas: Productos, Proveedores, Rentabilidad, Ranking.  
11. Export CSV/Excel del ranking.  
12. Actualizar `docs/arquitectura.md` y README.  
13. Pytest final + checklist.  
14. Commit + push en rama de Etapa 1.  
15. **Parar** y pedir aprobación para Etapa 2.

---

## 12. Riesgos Etapa 1

| Riesgo | Mitigación |
|--------|------------|
| Placeholder de comisión tomado como oficial | UI: “Parámetro editable — verificar en ML” |
| Aprobar oportunidad solo por score alto | Regla `pendiente` si faltan esenciales |
| Scope creep hacia Excel/web | Fuera de alcance explícito |
| Tests frágiles de paths | `tmp_path` / monkeypatch APPDATA |

---

## 13. Decisión pedida al usuario

¿**Aprueba** este plan de Etapa 1 (alcance, schema, pesos/bandas definitivos, parámetros comerciales, deps pandas+openpyxl) para implementar en `CORI_OMNI`?

Respuestas útiles: “sí”, “sí con cambios: …”, o “no, ajustar …”.
