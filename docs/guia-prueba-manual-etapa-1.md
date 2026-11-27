# Guía de prueba manual — Etapa 1

**Fecha:** 26 nov 2026 (America/Mexico_City)  
**Rama:** `cursor/etapa-1-nucleo-offline-8c38`  
**App:** `python -m marketfinder` (venv del repo)  
**Regla:** todos los datos de esta guía son **FICTICIOS**. No Etapa 2.

Paleta esperada: fondo `#10151D`, paneles `#1A222E`, acento `#49DBA0`.

---

## Preparación

1. Abrir MarketFinder Lite en CORI_OMNI.
2. Redimensionar la ventana (más angosta / más ancha): el texto de Inicio no debe cortarse en horizontal; debe hacer wrap y/o scroll vertical.
3. Ir a **Configuración → Diagnóstico**: anotar rutas de DB, logs, exports y AppData.

---

## 1. Inicio

| Paso | Acción | Resultado esperado |
|------|--------|-------------------|
| 1 | Abrir Inicio | Título “Inicio”; intro Etapa 1; cards de productos y fuentes Offline |
| 2 | Estrechar ventana | Texto hace wrap; sin recorte horizontal; scroll si hace falta |
| 3 | Ver nota inferior | Remite a Configuración para rutas técnicas (no muestra paths largos de DB) |

---

## 2. Proveedores

| Paso | Acción | Resultado esperado |
|------|--------|-------------------|
| 1 | Nombre `FICTICIO Proveedor Norte`, país `MX`, Guardar | Aparece en lista |
| 2 | Nombre `FICTICIO Proveedor Sur`, país `MX`, Guardar | Segundo ítem en lista |
| 3 | Editar / Limpiar / Borrar (opcional) | CRUD responde; preferente MX por defecto |

---

## 3. Productos (+ oferta + métricas)

Usar proveedores ya creados.

### Producto A (completo)

| Campo | Valor FICTICIO |
|-------|----------------|
| Nombre | `FICTICIO Gadget A` |
| SKU | `FIC-A` |
| Peso (g) | `200` |
| Proveedor | FICTICIO Proveedor Norte |
| Costo unitario | `30` |
| Proveniencia costo | `estimado` |
| Precio venta | `199` |
| Demanda 0–100 | `80` |

**Esperado:** Guardado; lista muestra costo con proveniencia; notas incluyen FICTICIO.

### Producto B (completo, peor demanda)

| Campo | Valor FICTICIO |
|-------|----------------|
| Nombre | `FICTICIO Gadget B` |
| SKU | `FIC-B` |
| Proveedor | FICTICIO Proveedor Sur |
| Costo | `45` |
| Proveniencia | `estimado` |
| Precio venta | `249` |
| Demanda | `40` |

### Producto C (incompleto a propósito)

| Campo | Valor FICTICIO |
|-------|----------------|
| Nombre | `FICTICIO Incompleto` |
| SKU | `FIC-X` |
| Proveedor | Norte |
| Costo | *(vacío)* |
| Precio venta | *(vacío)* |

**Esperado:** se guarda; costo aparece como pendiente / sin inventar 0.

---

## 4. Rentabilidad

| Paso | Acción | Resultado esperado |
|------|--------|-------------------|
| 1 | Costo `30`, Precio `199`, Cantidad `10` → Calcular | 6 escenarios; desglose comisión/envío/etc. |
| 2 | Ver disclaimer | “No garantiza ganancias”; fees no oficiales |
| 3 | Dejar costo vacío y calcular | Mensaje de faltan datos; **no** calcula con ceros inventados |
| 4 | (Opcional) En Config poner `commission_rate=0.13` y `shipping_cost_fixed=40`, recalcular | Números cambian según fees |

Referencia aproximada (fees seed o 0.13 + envío 40): utilidad operativa positiva en escenario normal con C=30 P=199.

---

## 5. Ranking + presupuesto

| Paso | Acción | Resultado esperado |
|------|--------|-------------------|
| 1 | Calcular ranking + presupuesto | Lista score/confianza/banda por producto |
| 2 | Ver `FICTICIO Incompleto` | Banda **pendiente**; no se recomienda |
| 3 | Ver A y B | Score comercial y confianza; A suele rankear mejor que B si demanda 80 vs 40 |
| 4 | Bloque optimizador | `greedy-approx`; gastado ≤ presupuesto (default 3000); residual ≥ 0 |
| 5 | Export CSV / Excel | Archivos en carpeta Exports del Diagnóstico; abren con datos |

---

## 6. Configuración

| Paso | Acción | Resultado esperado |
|------|--------|-------------------|
| 1 | Diagnóstico | Rutas AppData, DB, logs, exports visibles y legibles con wrap/scroll |
| 2 | `budget_default` = `3000` | Ya sembrado; Guardar parámetros OK |
| 3 | Cambiar un fee (ej. comisión) y Guardar fees | Mensaje guardado; Rentabilidad/Ranking usan el nuevo valor al recalcular |
| 4 | Pesos | Solo lectura 0.30/0.30/0.15/0.10/0.10/0.05 |

---

## 7. Checklist visual rápido

- [ ] Colores de marca correctos  
- [ ] Resize sin recorte horizontal en Inicio y demás pantallas con scroll  
- [ ] Sin animaciones llamativas  
- [ ] Secciones Investigación / Demanda / Historial / Comparar Excel / Reportes siguen “Próximamente”  

---

## Qué no probar (fuera de Etapa 1)

API Mercado Libre, comparador Excel↔IA, web, pagos, instalador.
