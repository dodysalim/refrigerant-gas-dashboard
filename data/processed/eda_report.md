# Reporte del Análisis Exploratorio de Datos (EDA) - Gases Refrigerantes

Este reporte detalla las características ecológicas, de seguridad y termodinámicas de los refrigerantes analizados en nuestro pipeline.

## 1. Métricas de Impacto Ecológico Global

- **Total de Gases Analizados**: 55
- **GWP Promedio**: 2340.16 (CO2 eq.)
- **GWP Máximo**: 14800.00 (R-23 con 14800)
- **GWP Mínimo**: 0.00 (Varios como R-717, R-1234yf con <= 1)
- **ODP Promedio**: 0.0703
- **ODP Máximo**: 1.00 (R-12 y R-11 con 1.0)
- **Porcentaje de Gases Libres de Daño de Ozono (ODP=0)**: 76.4%
- **Porcentaje de Gases de Ultra-bajo Impacto Climático (GWP <= 150 y ODP = 0)**: 25.5%

## 2. Análisis por Categoría de Refrigeración

Diferenciación de impacto ambiental y cantidad según el segmento de aplicación:

| Categoría | Cantidad de Gases | GWP Promedio | Uso Principal | Ejemplos Clave |
| --- | --- | --- | --- | --- |
| **Basic** | 15 | 1751.67 | Doméstico y autos | R-134a, R-600a, R-290, R-1234yf |
| **Intermediate** | 24 | 2004.04 | Aire Acondicionado y Cámaras | R-22, R-410A, R-404A, R-32 |
| **Industrial** | 16 | 3396.06 | Grandes plantas y criogenia | R-717 (Amoníaco), R-744 (CO2), R-23 |

> [!NOTE]
> La refrigeración industrial presenta un promedio de GWP mayor debido a la presencia de refrigerantes criogénicos (R-23, R-508B) de altísimo GWP, aunque este sector está liderado por las alternativas naturales con GWP casi nulo (Amoníaco R-717 y CO2 R-744).

## 3. Distribución de Tipos de Compuestos Químicos

| Tipo de Compuesto | Cantidad | Descripción Termodinámica | Estado de Regulación |
| --- | --- | --- | --- |
| HFC | 21 | Hidrofluorocarbonos. Cero daño a ozono pero alto calentamiento global. | Reducción gradual regulada (Enmienda de Kigali). |
| HFO/HFC | 7 | Mezclas complejas de múltiples tipos. | Regulado según su GWP ponderado. |
| Natural | 7 | Compuestos de la propia naturaleza (CO2, Amoníaco, Agua, Aire). | Uso fuertemente incentivado por sostenibilidad. |
| HCFC | 6 | Hidroclorofluorocarbonos. Menor daño, usados en transición. | Eliminación casi total completándose. |
| HC | 3 | Hidrocarburos naturales. Rendimiento termodinámico altísimo, inflamables. | Uso libre con límites de carga de seguridad. |
| CFC | 3 | Clorofluorocarbonos. Excelentes fluidos pero destructores del ozono. | Prohibición Total (Protocolo de Montreal). |
| HFO | 3 | Hidrofluoroolefinas de 4ta generación. Descomposición rápida, bajo GWP. | Uso libre promovido. |
| HCFC/HFC | 1 | Mezclas complejas de múltiples tipos. | Regulado según su GWP ponderado. |
| CFC/HCFC | 1 | Mezclas complejas de múltiples tipos. | Regulado según su GWP ponderado. |
| HFC/CF3I | 1 | Mezclas complejas de múltiples tipos. | Regulado según su GWP ponderado. |
| HFC/PFC | 1 | Mezclas complejas de múltiples tipos. | Regulado según su GWP ponderado. |
| CFC/PFC | 1 | Mezclas complejas de múltiples tipos. | Regulado según su GWP ponderado. |

## 4. Clasificación de Seguridad ASHRAE (Toxidad e Inflamabilidad)

Distribución de los gases según el estándar ASHRAE 34:

| Grupo de Seguridad | Cantidad | Significado Técnico | Nivel de Riesgo |
| --- | --- | --- | --- |
| A1 | 39 | Baja toxicidad, no inflamable. | Mínimo |
| A3 | 6 | Baja toxicidad, alta inflamabilidad (hidrocarburos). | Alto |
| A2L | 6 | Baja toxicidad, inflamabilidad muy leve (propaga lento). | Bajo-Moderado |
| A2 | 2 | Baja toxicidad, inflamabilidad moderada. | Moderado |
| B2L | 1 | Alta toxicidad, inflamabilidad muy leve (ej. R-717). | Muy Alto (industrial controlado) |
| B1 | 1 | Alta toxicidad, no inflamable. | Moderado-Alto |

## 5. Correlación Termodinámica de Operación

- **Punto de Ebullición Promedio a 1 atm**: -39.15 °C
- **Temperatura Crítica Promedio**: 93.32 °C
- **Relación P-T**: A menor punto de ebullición, mayor es la presión de trabajo requerida por el gas para condensar a temperatura ambiente. Esto explica por qué el R-410A (ebullición -51.4°C) opera a presiones tan superiores comparado con el R-134a (ebullición -26.3°C), y por qué el CO2 (R-744, sublimación a -78.4°C) requiere sistemas ultra-robustos que soporten más de 100 bar de presión transcrítica.

---
*Reporte compilado dinámicamente por la canalización ETL del proyecto.*