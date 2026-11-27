# MarketFinder Lite

Herramienta de escritorio (Python + CustomTkinter) para investigar oportunidades de producto en **Mercado Libre México**. Offline-first, stack gratuito y datos con proveniencia clara.

## Estado: Etapa 1 — Núcleo offline + motor financiero

Incluye:

- SQLite local (`%APPDATA%\MarketFinderLite\marketfinder.db`) con centavos enteros
- CRUD productos / proveedores + ofertas M2M
- Calculadora Decimal (escenarios, IVA/retenciones/ISR configurables)
- Optimizador de presupuesto (greedy ≈ aproximación; default $3 000)
- Ranking comercial + confianza (pesos 30/30/15/10/10/5)
- UI: Inicio, Productos, Proveedores, Rentabilidad, Ranking, Configuración
- Export CSV / Excel básico del ranking
- Logging a `%APPDATA%\MarketFinderLite\logs\`

**No incluye:** API Mercado Libre, comparador Excel↔IA (Etapa 2), web, pagos, licencias, scraping.

## Requisitos

- Windows 10/11 (validado en `CORI_OMNI`)
- **Python 3.12**
- Git

## Instalación

```powershell
cd C:\Users\emper\Documents\dev\marketfinder-lite
py -V:Astral/CPython3.12.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
Copy-Item .env.example .env   # opcional
```

## Ejecutar

```powershell
python -m marketfinder
```

## Pruebas

```powershell
pytest
```

Datos de fixtures están etiquetados como **FICTICIO**.

## Dependencias Etapa 1

| Paquete | Versión instalada (CORI_OMNI) | Motivo |
|---------|-------------------------------|--------|
| customtkinter | 5.2.2 | UI |
| python-dotenv | 1.2.4 | `.env` |
| darkdetect | 0.8.0 | tema |
| pandas | 2.3.3 | tablas / export |
| openpyxl | 3.1.5 | Excel |
| numpy | 2.5.5 | transitiva de pandas |
| et-xmlfile | 2.0.0 | transitiva de openpyxl |
| pytest | 8.4.2 | tests (dev) |

**No instalados (prohibidos Etapa 1):** requests, PyInstaller, Inno, cryptography, FastAPI, uvicorn.

## Datos de usuario

| Recurso | Ruta |
|---------|------|
| DB | `%APPDATA%\MarketFinderLite\marketfinder.db` |
| Logs | `%APPDATA%\MarketFinderLite\logs\` |
| Exports | `%APPDATA%\MarketFinderLite\exports\` |

Override en tests: variable `MARKETFINDER_DATA_DIR`.

## Documentación

- [Plan maestro](docs/marketfinder-lite-plan.md)
- [Plan Etapa 1](docs/plan-etapa-1.md)
- [Arquitectura](docs/arquitectura.md)
- [Requisitos API Mercado Libre](docs/requisitos-api-mercado-libre.md)
- [Licencias / herramientas gratis](docs/herramientas-gratuitas-y-licencias.md)

## Nota

Etapa 2+ **no** iniciada. Pedir aprobación explícita antes de continuar.
