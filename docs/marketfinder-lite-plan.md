# MarketFinder Lite — Plan maestro (presupuesto $0/mes)

**Fecha de actualización:** 26 nov 2026 (America/Mexico_City)  
**Máquina de desarrollo:** Windows `CORI_OMNI`  
**Repo local:** `C:\Users\emper\Documents\dev\marketfinder-lite`  
**Remoto:** https://github.com/EmperatrizMalave/marketfinder-lite  

**Estado:** Etapa 0 **completada**. Etapa 1 **IMPLEMENTADA** (26 nov 2026, America/Mexico_City) en CORI_OMNI — 1.1→1.7. Pendiente aprobación usuario para Etapa 2.  
**Fuera de alcance ahora:** Etapa 2+, web comercial (Etapa 6), pagos, licencias, APIs de IA, scraping.

Documentos relacionados:

- `docs/herramientas-gratuitas-y-licencias.md` — licencias y uso comercial  
- `docs/plan-etapa-1.md` — plan detallado Etapa 1 (para aprobación)  
- `docs/requisitos-api-mercado-libre.md` — orientación Etapa 3 (sin cuenta aún)

---

## 1. Visión y arquitectura definitiva

MarketFinder es un producto de **dos piezas**, no una app web funcional:

| Pieza | Rol | Tecnología |
|-------|-----|------------|
| **MarketFinder Desktop** | Producto real: investigación, finanzas, ranking, historial, Excel | Python 3.12 + CustomTkinter en Windows |
| **MarketFinder Website** | Landing comercial estática (descargas, propuestas de valor, contacto) | HTML/CSS/JS en Cloudflare Pages (Etapa 6) |

**Regla dura:** no hay segunda aplicación en el navegador. La website **no** replica el motor de investigación ni el núcleo financiero.

### Flujo lógico

```text
[Usuario Windows]
    → MarketFinder Desktop (offline-first)
         → SQLite local (%APPDATA%\MarketFinderLite\)
         → Motor financiero + ranking
         → Motor de investigación (fuentes gratis/oficiales/autorizadas)
         → Comparador Excel ↔ IA externa (sin API de IA embebida)
         → (Etapa 3+) Cliente API Mercado Libre solo con permisos verificados

[Visitante web]
    → Website estática (Cloudflare Pages)
         → Descarga vía GitHub Releases
         → Compra externa (nunca tarjeta en Cloudflare Free)
         → Sin backend propio de la app
```

---

## 2. Restricciones obligatorias ($0/mes)

Sin autorización expresa del usuario, **prohibido** gastar en:

- Dominio de pago  
- Hosting / VPS / PaaS de pago  
- Servidores propios o cloud de cómputo de pago  
- APIs de IA de pago  
- Pasarelas de pago embebidas en infra propia de costo recurrente  
- Servicios SaaS con cuota mensual  

**Permitido (gratis / freemium a verificar):** stack open source local, GitHub (repo + Releases), Cloudflare Pages (subdominio `*.pages.dev`), Cloudflare Web Analytics si el free tier aplica, herramientas de build locales (PyInstaller, Inno Setup).

Ver detalle de licencias y condiciones en `docs/herramientas-gratuitas-y-licencias.md`.

---

## 3. Stack gratuito confirmado

### Desktop (núcleo)

| Herramienta | Uso |
|-------------|-----|
| Python 3.12 | Runtime |
| CustomTkinter | UI Windows |
| SQLite | Persistencia local |
| Pandas | Tablas / análisis tabular |
| Openpyxl | Excel |
| Requests | HTTP a APIs autorizadas (desde Etapa 3) |
| python-dotenv | Config / secretos locales (nunca en el exe) |
| Pytest | Pruebas |
| Git | Control de versiones |
| PyInstaller | Empaquetado `.exe` (etapas de distribución) |
| Inno Setup | Instalador Windows (revisar licencia comercial; ver doc de licencias) |

### Website (Etapa 6)

- HTML / CSS / JS estático  
- Cloudflare Pages (subdominio gratis + HTTPS)  
- Enlaces a GitHub Releases para descargas  
- Cloudflare Web Analytics **solo si** el free tier y las condiciones permiten el uso previsto  
- **Verificar** uso comercial del free tier de Cloudflare antes de publicar como sitio de producto  

### Futuro (no implementar aún)

- Cryptography — licencias locales firmadas (Etapa 8)  
- Pagos **externos** (checkout fuera del free tier de Cloudflare; no procesar tarjetas en Pages free)  
- Clave privada de firma **fuera** del ejecutable  

---

## 4. Parámetros comerciales iniciales (configurables)

Valores por defecto del producto / escenarios de investigación. **Todos editables** en config; no hardcodear como verdad inmutable.

| Parámetro | Valor inicial |
|-----------|---------------|
| Mercado | México |
| Plataforma | Mercado Libre (MLM) |
| Presupuesto | **$3 000 MXN** |
| Costo de adquisición | **$5–50** MXN |
| Precio de venta | **$149–299** MXN |
| Margen objetivo | **25 %** |
| Peso del producto | **≤ 500 g** |
| Proveedores | Preferente **México** |
| Periodo de análisis | **14 días** |
| Compra inicial | **10–20 unidades** |

---

## 5. Ranking definitivo (ponderación del usuario)

| Factor | Peso |
|--------|------|
| Demanda | **30 %** |
| Rentabilidad | **30 %** |
| Competencia | **15 %** |
| Inversión requerida | **10 %** |
| Logística | **10 %** |
| Riesgo de devolución | **5 %** |
| **Total** | **100 %** |

### Bandas de interpretación

| Score | Interpretación |
|-------|----------------|
| **80–100** | Oportunidad **alta** |
| **60–79** | **Requiere investigación** adicional |
| **&lt; 60** | **Poco atractiva** |
| Datos esenciales incompletos | Estado **pendiente** — **no aprobar solo por score** |

La proveniencia (`verificado` | `estimado` | `pendiente`) aplica a cada métrica de entrada. Un score alto con datos esenciales faltantes **no** autoriza la oportunidad.

---

## 6. Motor de investigación (alcance completo, sin reducir)

El alcance de investigación se mantiene completo a lo largo del roadmap. No se recorta por presupuesto: se **aplaza** lo que dependa de cuentas/permisos, no se elimina.

Incluye (según etapa):

- Investigación de productos (entrada manual, Excel, luego API autorizada)  
- Demanda y competencia con marcadores `verificado` | `estimado` | `pendiente`  
- Proveedores (manual / Excel primero; automatización solo con fuente autorizada)  
- Rentabilidad, scoring, historial, reportes  
- Comparador con resultados de IA **externa** vía plantilla Excel (**sin** APIs de IA en el producto)

**Fuentes:** solo gratis, oficiales o con permiso explícito. **Cero scraping** no autorizado. **Sin APIs de IA** embebidas.

---

## 7. Mercado Libre (estado actual)

| Ítem | Estado |
|------|--------|
| Cuenta developers | **Aún no** |
| App registrada | **Pendiente** |
| Auth / OAuth | **Pendiente de verificación** |
| Cliente en código | **No** (Etapa 0–2 offline) |

Antes de Etapa 3 hay que verificar: permisos/scopes, límites, costos, condiciones de uso, ToS comercial.  
**No scraping.** Secretos solo en `.env` / almacén local del usuario — **nunca** embebidos en el `.exe`.

Si OAuth exige infraestructura (redirect HTTPS público, etc.):

1. Preferir flujos documentados para apps de escritorio / localhost si ML los permite.  
2. Alternativas gratis (p. ej. Pages solo como redirect estático mínimo, o URI localhost) y documentar **limitaciones**.  
3. Si la única opción viable tiene costo > $0/mes → **parar y pedir decisión al usuario**.

Detalle: `docs/requisitos-api-mercado-libre.md`.

---

## 8. Modelo Lite / Pro (futuro; no implementar)

| Edición | Intención (futuro) |
|---------|-------------------|
| **Lite** | Gratis / uso personal o entrada; funciones núcleo |
| **Pro** | Comercial; funciones ampliadas |

- Pagos: **externos** (no procesar tarjetas en Cloudflare Free).  
- Licencias: verificación **local** con Cryptography más adelante.  
- Clave privada de firma: **fuera** del exe (solo verificación con clave pública en cliente).  
- **NO** implementar pagos ni licencias en Etapas 0–7 de código productivo sin aprobación dedicada (Etapa 8 = diseño + posible prototipo bajo aprobación).

---

## 9. Roadmap Etapas 0–8

### Etapa 0 — Cimientos ✅ (completada en CORI_OMNI, 26 nov 2026)

- Repo `marketfinder-lite`, venv, CustomTkinter (ventana + sidebar), tema, settings/dotenv, docs API ML, pytest humo.  
- Verificación reconfirmada al actualizar este plan: **pytest 6/6**, GUI abre.

### Etapa 1 — Núcleo offline + motor financiero ✅ (IMPLEMENTADA)

- Productos, proveedores, calculadora de rentabilidad, optimizador de presupuesto, scoring/ranking (pesos y bandas de la §5), SQLite, logging, parámetros comerciales de la §4.  
- Plan detallado: `docs/plan-etapa-1.md`. Entrega lista; **no** iniciar Etapa 2 sin OK.

### Etapa 2 — Comparador Excel ↔ IA externa

- Plantilla contractual, importación, diff propio vs externo.  
- Sin APIs de IA.

### Etapa 3 — Fuentes autorizadas Mercado Libre

- Solo tras cuenta + scopes verificados.  
- Cliente Requests, caché, rate limit, proveniencia.  
- Documentar en `docs/fuentes-datos.md` lo permitido y lo prohibido.

### Etapa 4 — Motor de investigación completo (UI + orquestación)

- Pantallas y flujos de investigación, demanda, competencia, proveedores.  
- Orquestación offline + API cuando exista.  
- Sin reducir el alcance funcional; honestidad de datos incompletos.

### Etapa 5 — Reportes, pulido Desktop y empaquetado

- Reportes Excel/CSV, configuración avanzada, pytest amplio.  
- PyInstaller; preparación Inno Setup (sin distribución comercial masiva obligatoria aún).

### Etapa 6 — MarketFinder Website (estática) — **no desarrollar ahora**

Landing HTML/CSS/JS en Cloudflare Pages (HTTPS + subdominio gratis), descargas vía GitHub Releases, analytics gratuito solo si aplica.

**Secciones definitivas de la landing** (definidas por el usuario):

1. Presentación  
2. Funcionalidades  
3. Capturas  
4. Videos  
5. Descarga gratuita  
6. Comparación de versiones  
7. Precios  
8. Enlace de compra externo  
9. Documentación  
10. Soporte  
11. Política de privacidad  
12. Términos de uso  

Restricción Cloudflare Free: el enlace de compra debe ser **externo**; no procesar tarjetas en Pages Free.

### Etapa 7 — Distribución y operación $0

- Pipeline de release documentado (tag → GitHub Release → enlace en Pages).  
- Checklist de secretos, versionado, notas de versión.  
- Revisión de límites free (Pages, Releases, Analytics).  
- Guía de usuario Desktop.

### Etapa 8 — Comercialización Lite/Pro (diseño; implementación solo con aprobación)

- Definir límites Lite vs Pro.  
- Pagos externos.  
- Licencias locales (Cryptography), clave privada fuera del exe.  
- Releer ToS de ML, Cloudflare, GitHub e Inno Setup si hay uso comercial con ingresos.  
- **No implementar** hasta aprobación explícita.

---

## 10. Estructura de carpetas (Desktop; vigente Etapa 0 + evolución)

```text
marketfinder-lite/
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── docs/
│   ├── marketfinder-lite-plan.md      # este plan
│   ├── plan-etapa-1.md
│   ├── herramientas-gratuitas-y-licencias.md
│   ├── requisitos-api-mercado-libre.md
│   ├── arquitectura.md
│   └── … (fuentes-datos, plantilla-ia, etc. en etapas posteriores)
├── src/marketfinder/
│   ├── ui/          # CustomTkinter
│   ├── config/      # settings, theme
│   ├── core/        # Etapa 1+: modelos, scoring, rentabilidad
│   ├── data/        # Etapa 1+: SQLite, repos, excel_io
│   ├── services/    # Etapa 3+: ml_client, research
│   └── utils/       # logging, paths
├── tests/
└── assets/
```

Website (Etapa 6): preferible carpeta/repo dedicado (p. ej. `marketfinder-web` o `website/` aislado) para no mezclar build estático con el paquete Python — decisión al aprobar Etapa 6.

Datos de usuario: `%APPDATA%\MarketFinderLite\`.

---

## 11. Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| ToS / scraping ML | Solo API oficial; cero scrapers |
| OAuth sin infra | Alternativas gratis + límites; escalar al usuario si hay costo |
| Free tier Cloudflare (tarjetas) | Pagos externos; no cobrar en Pages Free |
| Inno Setup uso comercial | Revisar LICENSE + petición de licencia comercial si ingresos > umbral |
| Datos incompletos | Proveniencia; banda “pendiente”; no aprobar solo por score |
| Secretos en exe | dotenv local; nunca empaquetar `.env` ni client secret |
| Contaminar otros proyectos | Solo `marketfinder-lite` (+ website en su etapa) |
| Adelantar Etapa 1/6/8 | Aprobación explícita por etapa |

---

## 12. Pruebas (estrategia global)

- Unitarias: rentabilidad, scoring (pesos 30/30/15/10/10/5), optimizador, proveniencia, bandas.  
- Integración: SQLite, Excel, cliente ML con mocks.  
- UI smoke: abrir app y navegar (Windows).  
- Sin golpear API real en CI sin flag.  
- Etapa 0 actual: 6 tests de humo en verde.

---

## 13. Decisiones abiertas (usuario)

1. **Aprobar Etapa 1** (`docs/plan-etapa-1.md`) para instalar deps necesarias e implementar núcleo offline.  
2. Crear (o no) app en Mercado Libre Developers cuando se acerque Etapa 3.  
3. Cuándo entrar a Etapa 8 (Lite/Pro + licencias).

Ranking, landing y parámetros comerciales iniciales ya están **definidos** (secciones 4, 5 y 9 / Etapa 6).

---

## 14. Próximo paso

Etapa 1 entregada. **Pedir aprobación del usuario antes de Etapa 2** (comparador Excel ↔ IA externa). Sin web comercial y sin pagos/licencias.
