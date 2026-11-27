# Arquitectura — MarketFinder Lite (Etapa 0)

## Objetivo

Aplicación de escritorio en Python para investigar oportunidades de producto en Mercado Libre México (site `MLM`). Etapa 0 deja listos el esqueleto, el tema y la ventana; no hay aún núcleo de datos ni cliente API.

## Capas (separación intencional)

| Capa | Ubicación | Responsabilidad |
|------|-----------|-----------------|
| UI | `src/marketfinder/ui/` | CustomTkinter: ventana, sidebar, vistas |
| Config | `src/marketfinder/config/` | Settings (`.env`), paleta / tema |
| Core (futuro) | `src/marketfinder/core/` | Modelos, scoring, rentabilidad, proveniencia |
| Data (futuro) | `src/marketfinder/data/` | SQLite, repositorios, Excel I/O |
| Services (futuro) | `src/marketfinder/services/` | Cliente ML y orquestación |

En Etapa 0 solo existen UI y config. Las carpetas futuras se crearán cuando se apruebe la etapa correspondiente.

## Arranque

```text
python -m marketfinder
  → marketfinder.__main__
  → marketfinder.app.main
  → load_settings + apply_theme + MainWindow.mainloop
```

## Datos de usuario (previsto)

Fuera del código, p. ej. `%APPDATA%\MarketFinderLite\` (DB, exports, config local). Credenciales solo por `.env` o almacén local — nunca en el repositorio.

## Principios

- Fuentes de datos solo autorizadas (API oficial ML, importación manual/Excel).
- Etiquetar siempre la proveniencia: `verificado` | `estimado` | `pendiente`.
- No asumir ventas reales de competidores ni permisos de API no verificados.
- Stack gratuito: Python 3.12, CustomTkinter, pytest; sin APIs de IA embebidas en v1 personal.
