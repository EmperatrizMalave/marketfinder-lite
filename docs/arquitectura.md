# Arquitectura — MarketFinder Lite (Etapa 1)

## Objetivo

Aplicación de escritorio Python (CustomTkinter) para investigación offline de productos en Mercado Libre México. Etapa 1 entrega persistencia SQLite, motor financiero, ranking y UI mínima usable.

## Capas

| Capa | Ubicación | Responsabilidad |
|------|-----------|-----------------|
| UI | `src/marketfinder/ui/` | CustomTkinter: ventana, sidebar, vistas con scroll |
| Config | `src/marketfinder/config/` | Settings (`.env`), paleta `#10151D` / `#1A222E` / `#49DBA0` |
| Core | `src/marketfinder/core/` | Modelos, money/Decimal, rentabilidad, scoring, presupuesto |
| Data | `src/marketfinder/data/` | SQLite, repos, export CSV/Excel |
| Utils | `src/marketfinder/utils/` | paths (`%APPDATA%`), logging con redacción |
| Services (futuro) | `src/marketfinder/services/` | Cliente ML (Etapa 3+) |

## Arranque

```text
python -m marketfinder
  → load_settings + apply_theme + setup_logging
  → initialize_db (%APPDATA%\MarketFinderLite\marketfinder.db)
  → MainWindow.mainloop
```

## Dinero y proveniencia

- Cálculos en `Decimal`; persistencia en **centavos enteros** (`INTEGER`).
- Desconocido = `NULL` + proveniencia `pendiente` — **nunca** 0 inventado.
- Proveniencia por métrica: `verificado` | `estimado` | `pendiente`.

## Productos ↔ proveedores

Relación M2M vía tabla `offers` (costo, min_order, pack_qty, kind unitario/paquete/kit, lead_days). Historial en `price_history`.

## Motor financiero

- Líneas de costo independientes (comisión, pago, envío, empaque, ads, otros, IVA, retención, ISR).
- Utilidad operativa vs después de impuestos vs flujo (simplificado Etapa 1).
- Escenarios: normal, optimista, conservador, −10 % precio, +20 % costo, ambos.
- Fees en `fee_profiles` — **parámetros editables, no tarifas oficiales**.

## Ranking

Pesos fijos Demanda 30 / Rent 30 / Comp 15 / Inv 10 / Log 10 / Dev 5.  
Score comercial + confianza separados. Bandas: alta / requiere_investigacion / poco_atractiva / **pendiente** si faltan costo o precio.

## Presupuesto

Default $3 000 MXN configurable + reserva. Greedy por score; respeta mínimos/paquetes. Método documentado como aproximación.

## Principios

- Fuentes solo autorizadas (manual/Excel ahora; API ML después).
- Sin scraping, sin APIs de IA, sin pagos/licencias en Etapa 1.
- Logs sin secretos.
