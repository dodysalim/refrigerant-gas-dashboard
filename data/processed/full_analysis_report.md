# 📊 Reporte Integral de Análisis - KrioMetrics
### Catálogo de Gases Refrigerantes

*Generado automáticamente el 2026-05-25 14:40:55 por el sistema KrioMetrics ETL Pipeline.*

---

## Resumen Ejecutivo

Este reporte presenta el análisis integral de **55 gases refrigerantes** catalogados en el sistema KrioMetrics.

| Indicador | Valor |
| --- | --- |
| Total de Refrigerantes | 55 |
| Activos en el mercado | 29 (52.7%) |
| En proceso de eliminación | 14 (25.5%) |
| Completamente eliminados | 12 (21.8%) |
| De ultra-bajo impacto (GWP≤150, ODP=0) | 14 (25.5%) |
| Total puntos P-T en base de datos | 2,750 |

> [!NOTE]
> Los datos son generados dinámicamente por la canalización ETL del proyecto KrioMetrics.
> Fuentes: ASHRAE Handbook of Refrigeration, EPA SNAP Program, EU F-Gas Directive 517/2014.


---

## Análisis de Impacto Ambiental

### Métricas Globales de Impacto Climático (GWP)

| Métrica | Valor | Referencia |
| --- | --- | --- |
| GWP Promedio del catálogo | 2340.2 CO₂eq | — |
| GWP Máximo | **14800** (R-23) | R-23 criogénico |
| Gases con GWP ≤ 1 | 7 gases | HFOs, Naturales |
| Gases con ODP = 0 | 42 (76.4%) | Sin daño ozono |
| Puntuación Eco Promedio | 62.29/100 | KrioMetrics Score |

### Ranking de Sostenibilidad (Top 5 🌿)

Los 5 gases más ecológicos del catálogo: **R-744**, **R-718**, **R-729**, **R-1234yf**, **R-1234ze**

### Gases con Mayor Impacto Ambiental (Bottom 5 🔴)

Los 5 gases de mayor impacto negativo: **R-502**, **R-11**, **R-12**, **R-113**, **R-503**

### Distribución por Etiqueta Ecológica

| Etiqueta | Cantidad | Descripción |
| --- | --- | --- |
| 🌿 Excelente (≥85 pts) | 14 | Alternativas futuras |
| ✅ Bueno (65-84 pts) | 5 | Opciones recomendables |
| ⚠️ Moderado (45-64 pts) | 26 | Uso transitorio |
| 🔶 Problemático (25-44 pts) | 6 | Reemplazar pronto |
| 🔴 Crítico (<25 pts) | 4 | Prohibidos/eliminando |

### Estado Regulatorio Global

- **Cumplimiento EU F-Gas 517/2014**: 36/55 gases (65.5%)
- **Restringidos por Enmienda de Kigali**: 27 gases
- **Afectados por Protocolo de Montreal**: 13 gases


---

## Correlaciones Termodinámicas

### Propiedades Termodinámicas Promedio

| Propiedad | Promedio | Extremo Notable |
| --- | --- | --- |
| Punto de Ebullición | -39.1 °C | R-729: -194.3°C (mínimo) |
| Temperatura Crítica | 93.3 °C | R-718: 374.0°C (máximo) |
| Presión Crítica | 47.8 bar | R-718: 220.6 bar (máximo) |

### Análisis por Categoría de Refrigeración

| Categoría | N° Gases | BP Promedio (°C) | TC Promedio (°C) | PC Promedio (bar) |
| --- | --- | --- | --- | --- |
| Basic | 15 | -29.0 | 106.8 | 41.1 |
| Industrial | 16 | -38.6 | 98.9 | 59.1 |
| Intermediate | 24 | -45.9 | 81.2 | 44.6 |

### Principio de la Relación P-T

La relación entre el **punto de ebullición** y la **presión de trabajo** sigue la ley de Antoine.
A menor punto de ebullición, el refrigerante requiere mayor presión para condensar a temperatura ambiente.

| Gas | Ebullición (°C) | Aprox. Presión a 25°C (bar) | Implicación |
| --- | --- | --- | --- |
| R-744 (CO₂) | -78.4 | ~65-70 | Sistemas transcríticos robustos |
| R-410A | -51.4 | ~16 | Alta presión, tuberías gruesas |
| R-32 | -51.7 | ~15 | Similar a R-410A pero más eco |
| R-134a | -26.3 | ~8 | Presión moderada, muy difundido |
| R-717 (NH₃) | -33.3 | ~11 | Sistemas industriales herméticos |
| R-290 (Propano) | -42.1 | ~12 | Cargas pequeñas, muy eficiente |


---

## Distribución por Tipo de Compuesto

| Tipo de Compuesto | N° Gases | GWP Promedio | ODP Promedio | Activos |
| --- | --- | --- | --- | --- |
| HFC | 21 | 2821 | 0.000 | 7 |
| Blend | 12 | 3425 | 0.072 | 9 |
| Natural | 7 | 2 | 0.000 | 7 |
| HCFC | 6 | 1092 | 0.035 | 0 |
| HC | 3 | 3 | 0.000 | 3 |
| CFC | 3 | 7260 | 0.933 | 0 |
| HFO | 3 | 1 | 0.000 | 3 |


---
*© KrioMetrics - Sistema de Análisis de Gases Refrigerantes*
