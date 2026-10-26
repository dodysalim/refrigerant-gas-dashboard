# Changelog - KrioMetrics

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es/1.0.0/)
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [2.1.0] - 2026-05-25

### ✨ Añadido

- **`src/domain/validators.py`** — Módulo de validación de negocio con Strategy Pattern:
  - `RefrigerantValidator`: valida tipo de compuesto, grupo de seguridad, GWP/ODP, temperatura crítica, color hexadecimal
  - `SaturatedPressureFactValidator`: valida hechos P-T, consistencia de conversión bar↔PSI
  - `DatasetValidator`: validación a nivel de dataset completo (unicidad, integridad referencial)
  - `ValidationResult`: dataclass con errores, advertencias y representación clara

- **`src/domain/sustainability.py`** — Analizador de sostenibilidad ambiental:
  - `SustainabilityAnalyzer`: puntuación ecológica 0-100 con sub-scores GWP (0-40), ODP (0-30), Seguridad (0-20), Regulación (0-10)
  - Verificación de cumplimiento EU F-Gas 517/2014, restricciones Kigali, prohibiciones Montreal
  - Etiquetas ecológicas: 🌿 Excelente / ✅ Bueno / ⚠️ Moderado / 🔶 Problemático / 🔴 Crítico
  - Recomendaciones automáticas por gas

- **`src/application/reporter.py`** — Generador de reportes con Builder Pattern:
  - Secciones componibles: resumen ejecutivo, impacto ambiental, correlaciones, tipos de compuesto
  - Exportación en Markdown y JSON
  - `generate_full_report()` función de alto nivel

- **`tests/`** — Suite de 54 tests unitarios con pytest:
  - `test_domain.py`: 31 tests para entidades y validadores
  - `test_sustainability.py`: 23 tests para scoring ambiental
  - Cobertura: entidades, validadores, dataset validator, analyzer, scoring GWP/ODP

- **`notebooks/02_statistical_analysis.ipynb`** — Análisis estadístico avanzado:
  - Shapiro-Wilk (normalidad), Kruskal-Wallis (diferencias entre grupos)
  - Correlaciones Spearman y Pearson con heatmaps
  - PCA con biplot y scree plot
  - Detección de outliers por método IQR

- **`notebooks/03_ml_pipeline.ipynb`** — Pipeline ML completo con scikit-learn:
  - Clustering: K-Means, DBSCAN, Agglomerative (Ward/Complete)
  - Evaluación: Silhouette, Davies-Bouldin, Calinski-Harabász, Elbow method
  - Clasificación: Random Forest, Gradient Boosting, SVM, Logistic Regression, KNN
  - Cross-validation estratificado 5-fold
  - Feature Importance y Matriz de Confusión
  - Dendrograma de clustering jerárquico

- **`notebooks/04_advanced_viz.ipynb`** — Visualizaciones premium:
  - Mapa de calor ambiental (GWP heatmap + scatter GWP vs ODP)
  - Curvas de presión de saturación P-T para 10 gases representativos
  - Diagrama de burbujas de sostenibilidad
  - Timeline regulatorio histórico (1974-2030)

- **`scripts/analyze_sustainability.py`** — CLI para análisis de sostenibilidad
- **`scripts/generate_quality_report.py`** — CLI para reporte de calidad de datos
- **`.github/workflows/ci.yml`** — CI con GitHub Actions: tests en Python 3.10/3.11/3.12, lint
- **`.github/workflows/deploy.yml`** — Workflow de deployment para Streamlit Cloud
- **`pytest.ini`** — Configuración de pytest

### 🔧 Modificado

- **`run_etl.py`** — Mejorado con CLI completo:
  - Flags `--validate`, `--report`, `--sustainability`
  - Timer por paso y resumen de archivos generados
  - Integración con `DatasetValidator` y `KrioMetricsReportBuilder`

- **`README.md`** — Reescrito completamente con:
  - Badges de CI, tests, Python versions
  - Tabla de stack tecnológico
  - Diagrama de Clean Architecture por capas
  - Tabla de patrones de diseño implementados
  - Tabla de notebooks con técnicas
  - Documentación de todos los módulos nuevos

- **`.streamlit/config.toml`** — Añadidas secciones `[server]`, `[browser]`, `[runner]`

### 🐛 Corregido

- **`src/infrastructure/readers.py`** — Normalización de `compound_type` para gases mezcla:
  - `HCFC/HFC` → `Blend`
  - `HFO/HFC` → `Blend`
  - `CFC/HCFC` → `Blend`
  - `CFC/PFC` → `Blend`
  - `HFC/CF3I` → `Blend`
  - `HFC/PFC` → `Blend`
  - (Detectado automáticamente por `DatasetValidator`)

---

## [2.0.0] - 2026-05-20

### ✨ Añadido

- **Modularización del dashboard Streamlit** en `src/presentation/dashboard/`:
  - `loader.py` — Cargador con caché y mappings de imágenes reales
  - `pt_solver.py` — Motor termodinámico Clausius-Clapeyron
  - `view_control.py` — Vista: Dashboard de Control con filtros Plotly
  - `view_calculator.py` — Vista: Calculadora P-T y fotorrealismo de cilindros
  - `view_comparator.py` — Vista: Comparador de 3 gases
  - `view_cycle.py` — Vista: Simulador de ciclo termodinámico
  - `view_sql.py` — Vista: Consola SQL interactiva con SQLite

- **Catálogo fotorrealista** de 55 cilindros de gas organizados en 3 categorías

### 🔧 Modificado

- `dashboard.py` — Refactorizado para usar submódulos de presentación

---

## [1.0.0] - 2026-05-15

### ✨ Añadido

- **ETL Pipeline** con Clean Architecture y principios SOLID:
  - `src/domain/entities.py` — Entidades: `Refrigerant`, `TemperatureDimension`, `StateDimension`, `SaturatedPressureFact`
  - `src/infrastructure/readers.py` — Lector con ecuaciones Antoine para 55 gases
  - `src/infrastructure/exporters.py` — Exportadores a CSV, SQLite, JSON, JS
  - `src/application/pipeline.py` — Template Method Pattern para ETL

- **Star Schema SQLite** con 4 tablas: `dim_refrigerant`, `dim_temperature`, `dim_state`, `fact_saturated_pressure`

- **Dashboard HTML Premium** (`web/index.html`) con:
  - Visualizador de cilindros con colores reales
  - Gráficos interactivos con Canvas/Chart.js
  - Filtros dinámicos y tabla de propiedades

- **Dashboard Streamlit** (`dashboard.py`) — Versión inicial monolítica

- **Notebook EDA** (`notebooks/eda_and_modeling.ipynb`) — EDA básico y K-Means clustering

---

*Mantenido por [Dody Due�as](https://github.com/dodysalim)*
