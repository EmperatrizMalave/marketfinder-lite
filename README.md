# MarketFinder Lite

Herramienta de escritorio (Python + CustomTkinter) para investigar oportunidades de producto en **Mercado Libre México**. Pensada para uso personal, stack gratuito y datos con proveniencia clara.

## Estado: Etapa 0 — Cimientos

Incluye:

- Repositorio y empaquetado mínimo (`pyproject.toml`)
- Tema visual y ventana con menú lateral (10 secciones; solo **Inicio** activo)
- Configuración vía `.env` (sin secretos en el repo)
- Documentación de arquitectura y requisitos de la API de Mercado Libre
- Prueba de humo con pytest

**No incluye aún:** SQLite de dominio, cliente API, pandas/Excel, ranking ni empaquetado PyInstaller. Esas piezas llegan en etapas posteriores, **solo tras tu aprobación**.

## Requisitos

- Windows 10/11 (validado en `CORI_OMNI`)
- **Python 3.12** (recomendado; p. ej. `py -V:Astral/CPython3.12.14` o instalador oficial)
- Git

## Instalación

En PowerShell:

```powershell
cd C:\Users\emper\Documents\dev\marketfinder-lite

# Crear entorno virtual con Python 3.12
py -V:Astral/CPython3.12.14 -m venv .venv
# Alternativa si tienes python3.12 en PATH:
# python3.12 -m venv .venv

.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
# o: pip install -r requirements.txt
```

Copia variables de entorno (opcionales en Etapa 0):

```powershell
Copy-Item .env.example .env
# Edita .env solo cuando tengas credenciales reales de ML Developers
```

## Ejecutar la aplicación

Con el venv activado y desde la raíz del proyecto:

```powershell
python -m marketfinder
```

También, tras `pip install -e .`:

```powershell
marketfinder
```

## Pruebas

```powershell
pytest
```

La suite de Etapa 0 verifica imports, constantes de tema y, si el entorno lo permite, construcción de la ventana sin `mainloop`. Si Tk/CustomTkinter no puede abrirse en un entorno headless, las pruebas de GUI se omiten con un mensaje claro; en ese caso valida lanzando la app en el escritorio de Windows.

## Estructura (resumen)

```text
marketfinder-lite/
  docs/                 # arquitectura + requisitos API ML
  src/marketfinder/     # paquete principal (ui + config)
  tests/
  assets/
  .env.example
  pyproject.toml
  requirements.txt
```

## Documentación

- [Arquitectura](docs/arquitectura.md)
- [Requisitos API Mercado Libre](docs/requisitos-api-mercado-libre.md)

## Nota importante

No se ha registrado aún una aplicación en Mercado Libre Developers para este proyecto. No uses credenciales ficticias como si fueran reales. La Etapa 1 (núcleo offline) **no** debe iniciarse hasta que apruebes el avance de Etapa 0.
