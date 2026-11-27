# Herramientas gratuitas y licencias — MarketFinder Lite

**Fecha:** 26 nov 2026 (America/Mexico_City)  
**Propósito:** orientar uso con presupuesto **$0/mes** y posible uso comercial futuro (Lite/Pro).  
**Aviso:** esto **no es asesoría legal**. Marca “revisar” / “incertidumbre” donde la verificación online no es 100 % concluyente; antes de distribuir comercialmente, releer textos oficiales vigentes.

---

## Resumen ejecutivo

| Veredicto | Herramientas |
|-----------|--------------|
| **OK comercial** (licencia permisiva conocida; conservar avisos) | CustomTkinter, SQLite, Pandas, Openpyxl, Requests, python-dotenv, Pytest, Git (uso del cliente), Cryptography (futuro), Python (PSF) |
| **OK con matices** | PyInstaller (GPL + excepción bootloader; no modifica → OK empaquetar comerciales), GitHub Releases (hospedar binarios propios; cumplir ToS GitHub) |
| **Revisar / riesgo** | **Inno Setup** (LICENSE permite comercial; autores **solicitan** licencia de pago si ingresos anuales > USD 5 000), **Cloudflare Pages / Analytics** (sin veto comercial explícito claro en Self-Serve Agreement; **prohibido** procesar tarjetas en Free Services; marketing Free habla de hobby — releer al publicar) |

---

## Tabla por herramienta

| Herramienta | Uso en MarketFinder | Licencia conocida | ¿OK comercial? | Notas / restricciones | Qué revisar si hay duda |
|-------------|---------------------|-------------------|----------------|----------------------|-------------------------|
| **Python 3.12** | Runtime Desktop | PSF License | **OK** | Permisiva estilo BSD. | https://docs.python.org/3/license.html |
| **CustomTkinter** | UI Desktop | **MIT** | **OK** | Conservar aviso copyright/MIT. | https://github.com/TomSchimansky/CustomTkinter/blob/master/LICENSE |
| **SQLite** | DB local | Public domain (blessing) | **OK** | | https://www.sqlite.org/copyright.html |
| **Pandas** | Tablas / análisis | BSD-3-Clause | **OK** | Conservar avisos. | PyPI / LICENSE |
| **Openpyxl** | Excel | MIT | **OK** | Conservar avisos. | PyPI / repo |
| **Requests** | HTTP APIs autorizadas | Apache-2.0 | **OK** | Conservar avisos; NOTICE si aplica. | PyPI / repo |
| **python-dotenv** | Carga `.env` | BSD-3-Clause | **OK** | No empaquetar secretos reales en el exe. | PyPI / repo |
| **Pytest** | Pruebas (dev) | MIT | **OK** | No redistribuir al usuario final. | PyPI / repo |
| **Git** | Control de versiones | GPL-2.0-only (Git) | **OK para uso** | Usar Git no contamina la licencia de la app. No redistribuir Git modificado sin cumplir GPL. | https://git-scm.com/about/free-and-open-source |
| **PyInstaller** | Generar `.exe` | GPL-2.0-or-later **con excepción de bootloader** (+ Apache en algunos archivos) | **OK empaquetar** apps comerciales si no redistribuyes PyInstaller modificado | Modificar y redistribuir PyInstaller → GPL. | https://pyinstaller.org/en/stable/license.html |
| **Inno Setup** | Instalador Windows | **Inno Setup License** | **OK legal según LICENSE**; **revisar** petición comercial | Permite uso comercial. Autores **solicitan** (FAQ: no estrictamente obligatorio) licencia de pago si org/freelancer con ingresos anuales **> USD 5 000**. Comprar cuando el instalador vaya a producción. Correr el Setup.exe final no cuenta como “usar” Inno. | https://jrsoftware.org/isinfo.php · https://jrsoftware.org/inno-setup/purchase · SPDX `InnoSetup` |
| **Cryptography** (futuro) | Licencias locales | Apache-2.0 **OR** BSD-3-Clause | **OK** | Clave **privada** fuera del exe; solo pública en cliente. | https://github.com/pyca/cryptography |
| **Cloudflare Pages** | Website estática Etapa 6 | ToS Self-Serve Subscription Agreement | **Revisar** (probable OK comercial; incertidumbre messaging Free) | Sin veto claro “solo personal” en restricciones 2.2.1 (lectura secundaria nov 2026). **Prohibido** procesar/colectar datos de tarjeta en Free Services → la landing usa **enlace de compra externo**. Cloudflare puede limitar abuso. | Self-Serve Subscription Agreement · límites Pages |
| **Cloudflare Web Analytics** | Métricas landing | Ecosistema Cloudflare | **Revisar** | Confirmar cobertura free + avisos de privacidad según audiencia (alineado a sección “Política de privacidad” de la landing). | Docs Web Analytics + Privacy |
| **GitHub Releases** | Distribución de instaladores / descarga gratuita | GitHub Terms of Service | **OK uso de la plataforma** | Hospedar **tus** binarios; cumplir ToS y cuotas free. Licencia del software la defines tú. | https://docs.github.com/en/site-policy/github-terms/github-terms-of-service |

---

## Inno Setup — condiciones (detalle)

Permiso base: usar para cualquier propósito, **incluidas aplicaciones comerciales**, con condiciones de conservar copyright/avisos, no tergiversar el origen y marcar versiones modificadas.

**Licencia comercial solicitada (jrsoftware):**

- Pedida a usuarios comerciales (ingresos anuales > USD 5 000 o equivalente).  
- FAQ: **no estrictamente obligatoria**, pero se solicita; razonable al shippear a producción con ingresos.  
- No requerida solo por experimentar.  
- Licencias por usuario/CI que **compila**; el usuario final del instalador no consume esa licencia.

**Recomendación MarketFinder:** free en desarrollo (Etapa 5/7); releer LICENSE + purchase antes de vender Pro a escala.

---

## Cloudflare — uso comercial del free tier

- No aparece veto explícito “prohibido uso comercial” en 2.2.1 del Self-Serve Agreement (fuentes revisadas 26 nov 2026).  
- Sí: **no** procesar/colectar información de tarjetas en Free Services.  
- Marketing Free a veces dice “personal or hobby” → **incertidumbre**; releer el día de publicar Etapa 6.  
- Mitigación $0: landing con secciones definidas (presentación … términos) + **compra externa**.

---

## Secretos y distribución

| Regla | Detalle |
|-------|---------|
| Nunca en Git | `.env` real, tokens ML, claves privadas |
| Nunca en el `.exe` | Client secrets, private keys de licencia |
| Sí en el cliente (futuro) | Clave **pública** de verificación |
| `.env.example` | Solo nombres vacíos |

---

## Dependencias Etapa 0 (ya en `.venv`)

customtkinter, python-dotenv, pytest (+ transitivas).  
**No** aún: pandas, openpyxl, requests, pyinstaller, cryptography.

---

## Incertidumbres pendientes de cierre humano

1. Releer Self-Serve Agreement + Service-Specific Terms de Cloudflare al publicar Etapa 6.  
2. Confirmar avisos de privacidad para Web Analytics según audiencia.  
3. Decisión Inno Setup commercial license al primer release de pago.  
4. ToS Mercado Libre Developers al registrar la app (Etapa 3).

*Documento vivo: actualizar si cambia una licencia o el modelo Lite/Pro.*
