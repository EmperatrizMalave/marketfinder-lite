# Requisitos API Mercado Libre — MarketFinder Lite

**Estado actual (Etapa 0):** no hay cuenta de desarrollador ni aplicación registrada del usuario conectada a este proyecto. No hay credenciales reales en el repositorio. Este documento orienta la futura Etapa 3; **no** implica que hoy se pueda llamar a la API.

---

## 1. Cómo registrar una aplicación

1. Entra a [developers.mercadolibre.com](https://developers.mercadolibre.com/) con tu cuenta de Mercado Libre.
2. Crea o selecciona una aplicación (App).
3. Anota el **App ID** (`ML_CLIENT_ID`) y el **Secret Key** (`ML_CLIENT_SECRET`).
4. Configura la **URL de redirección** (redirect URI) que usarás en el flujo OAuth (p. ej. `https://localhost` o la que documente ML para apps de escritorio / prueba).
5. Revisa los **scopes / permisos** que solicita la app y los **Términos de Uso** de la plataforma de desarrolladores.
6. Guarda los valores solo en un archivo `.env` local (nunca en Git). Usa `.env.example` como plantilla vacía.

Referencias oficiales (verificar siempre la documentación vigente):

- Portal de desarrolladores: https://developers.mercadolibre.com/
- Autenticación / OAuth: documentación de “Authentication” / “Authorization” en el portal
- API docs (REST): https://developers.mercadolibre.com.ar/es_ar/api-docs-es (las rutas regionales pueden variar; usa la del site que operes)

---

## 2. OAuth (resumen)

Mercado Libre usa OAuth 2.0. Flujo típico:

1. Redirigir al usuario a la URL de autorización con `client_id`, `response_type=code`, `redirect_uri`.
2. Recibir un **authorization code** en el redirect.
3. Intercambiar el code por `access_token` (y a menudo `refresh_token`) mediante POST al endpoint de token.
4. Enviar `Authorization: Bearer <access_token>` en las llamadas a la API.
5. Renovar el token con el refresh token antes de que expire.

**Importante:** los tokens son secretos. No hardcodear, no subir a Git, no pegar en issues públicos.

Variables previstas en este proyecto (ver `.env.example`):

| Variable | Uso |
|----------|-----|
| `ML_CLIENT_ID` | App ID |
| `ML_CLIENT_SECRET` | Secret |
| `ML_ACCESS_TOKEN` | Token de acceso |
| `ML_REFRESH_TOKEN` | Renovación (opcional) |
| `ML_SITE_ID` | Site; México = `MLM` |

---

## 3. Site México (MLM)

- El site de Mercado Libre México se identifica como **`MLM`**.
- Muchos endpoints públicos de búsqueda y catálogo usan el site en la ruta, p. ej. patrones del tipo `/sites/MLM/...` (confirmar en la docs actual).
- Precios, monedas, categorías y comisiones pueden diferir de otros países (MLA, MLB, etc.). No reutilizar supuestos de otro site sin verificar.

---

## 4. Límites conocidos (orientativos)

Los valores exactos cambian; **consultar la documentación y cabeceras de respuesta vigentes**. En la práctica suele haber:

- **Rate limiting** por aplicación / usuario (códigos HTTP 429 o equivalentes).
- Cuotas diarias o por ventana de tiempo.
- Restricciones según el tipo de app y los scopes aprobados.
- Posible necesidad de aprobación adicional para ciertos recursos.

Mitigaciones previstas en etapas futuras: caché local (SQLite), backoff, cola de peticiones, no martillar la API en pruebas automatizadas.

---

## 5. Qué NO asumir

| Asunción incorrecta | Por qué |
|---------------------|---------|
| “Puedo ver ventas exactas de competidores” | La API pública **no garantiza** volúmenes de venta de terceros. Cualquier proxy (visitas, #vendedores, etc.) debe marcarse como **estimado**. |
| “Scraping del sitio web es equivalente a la API” | El scraping suele violar ToS y no es la estrategia de este proyecto. Solo API oficial / fuentes con permiso. |
| “Con App ID ya tengo todos los permisos” | Scopes y aprobación importan; hay que verificar qué responde cada endpoint con la app real. |
| “Los datos de catálogo = demanda real” | Catálogo/búsqueda ≠ demanda verificada. |
| “Credenciales de ejemplo = producción” | Los placeholders de `.env.example` están vacíos a propósito. |

Proveniencia obligatoria en datos del producto (etapas futuras): `verificado` | `estimado` | `pendiente`.

---

## 6. ToS / uso comercial

- Leer y cumplir los **Términos y Condiciones** de Mercado Libre Developers y de la API.
- Uso personal vs. redistribución / producto comercial pueden tener reglas distintas; la Etapa 6 del plan (licenciamiento, pasarelas) está **fuera de alcance** ahora.
- No redistribuir datos de ML de forma que contradiga su licencia de uso de la API.
- Si en el futuro se vende MarketFinder Lite, hay que revisar de nuevo ToS, branding y límites comerciales de ML — no improvisar.

---

## 7. Situación del proyecto hoy

- **No** hay aplicación ML del usuario registrada y enlazada a este repo.
- **No** hay llamadas HTTP a ML en el código de Etapa 0.
- La UI muestra “Estado de fuentes: Pendiente”.
- Antes de implementar el cliente (`services/ml_client.py` en Etapa 3): registrar la app, probar scopes con llamadas manuales (Postman/curl), documentar en `docs/fuentes-datos.md` qué quedó autorizado.

---

## 8. Endpoints a investigar (sin afirmar permisos)

Lista **orientativa** de áreas a explorar cuando exista la app. No se afirma aquí que todos estén disponibles sin auth, ni con qué scopes:

| Área | Patrones / recursos a revisar en la docs oficial |
|------|--------------------------------------------------|
| Búsqueda | Búsqueda por site (`/sites/MLM/search` u homólogos actuales) |
| Ítem | Detalle de publicación (`/items/{id}`) |
| Categorías | Árbol / predicción de categorías |
| Usuarios | Datos del usuario autenticado (no de competidores privados) |
| Visitas / métricas | Solo si el endpoint y el scope lo permiten para el recurso propio o público documentado |
| Catálogo / productos | Recursos de product catalog si aplican a MLM |

**Regla:** cada endpoint se valida con la app real; se documenta respuesta, scopes y límites; se implementa solo lo verificado.

---

## 9. Checklist antes de Etapa 3

- [ ] App creada en developers.mercadolibre.com
- [ ] Redirect URI configurada
- [ ] `.env` local con client id/secret (fuera de Git)
- [ ] Flujo OAuth probado manualmente → access token
- [ ] Al menos una búsqueda MLM y un GET de ítem documentados
- [ ] Lista explícita de lo **no** disponible (p. ej. ventas de terceros)
- [ ] Aprobación del usuario para iniciar Etapa 3

---

*Documento vivo: actualizar cuando se verifiquen permisos reales. No sustituye la documentación oficial de Mercado Libre.*
