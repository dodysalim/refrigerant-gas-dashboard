# KrioMetrics — Pipeline ETL & Ecosistema Analítico de Refrigeración

<div align="center">

[![CI Tests](https://github.com/dodysalim/refrigerant-gas-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/dodysalim/refrigerant-gas-dashboard/actions/workflows/ci.yml)
[![Deploy](https://github.com/dodysalim/refrigerant-gas-dashboard/actions/workflows/deploy.yml/badge.svg)](https://github.com/dodysalim/refrigerant-gas-dashboard/actions/workflows/deploy.yml)
![Python](https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.12-3776AB?logo=python&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-54%20passed-brightgreen?logo=pytest)
![Coverage](https://img.shields.io/badge/Coverage-src%2F-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Notebooks](https://img.shields.io/badge/Notebooks-4-orange?logo=jupyter)
![Gases](https://img.shields.io/badge/Refrigerantes-55-teal)

</div>

---

Una plataforma completa de **analítica e ingeniería de datos termodinámicos** enfocada en el estudio de **55 gases refrigerantes** clasificados en refrigeración **Básica**, **Intermedia** e **Industrial**.

Integra una tubería de procesamiento de datos (**ETL**) en Python bajo principios **SOLID** y patrones de diseño, un **Modelo Estrella** en **SQLite**, **4 notebooks Jupyter** de análisis científico con **ML Pipeline completo**, validación de datos con **54 tests unitarios**, y dos **Dashboards Interactivos Premium** (HTML5 + Streamlit).

---

## 📑 Tabla de Contenidos

1. [Stack Tecnológico](#stack-tecnológico)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Arquitectura Clean (SOLID)](#arquitectura-clean-solid)
4. [Notebooks de Análisis](#notebooks-de-análisis)
5. [Tests Unitarios](#tests-unitarios)
6. [CI/CD con GitHub Actions](#cicd-con-github-actions)
7. [Módulos del Dominio](#módulos-del-dominio)
8. [Instalación y Ejecución](#instalación-y-ejecución)
9. [Dashboards](#dashboards)
10. [Marco Regulatorio](#marco-regulatorio)

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Uso |
| --- | --- | --- |
| **Lenguaje** | Python 3.10+ | ETL, análisis, ML, dashboards |
| **Base de Datos** | SQLite (Star Schema) | Almacén OLAP de 55 gases × 7700+ hechos P-T |
| **Data Science** | Pandas, NumPy, SciPy | EDA, estadísticas descriptivas, hipótesis |
| **Machine Learning** | Scikit-learn | Pipeline ML, clustering, clasificación, PCA |
| **Visualización** | Matplotlib, Seaborn, Plotly | Curvas P-T, heatmaps, clustering, radarcharts |
| **Dashboard Web** | Streamlit + Plotly | Panel científico modularizado con 5 vistas |
| **Dashboard HTML** | HTML5 / CSS / JS | SPA premium con animaciones y fotorrealismo |
| **Testing** | Pytest + Coverage | 54 tests unitarios en dominio y sostenibilidad |
| **CI/CD** | GitHub Actions | Test automáticos en 3 versiones Python + deploy |
| **Contenedores** | — | Compatible con Docker (sin dependencias nativas) |

---

## 1. Estructura del Proyecto

```text
proyectodegasesrefrigerante/
│
├── src/                                # Código fuente Clean Architecture
│   ├── domain/
│   │   ├── entities.py                 # Entidades de dominio (OOP puro)
│   │   ├── validators.py               # [NEW] Validadores de negocio (Strategy Pattern)
│   │   └── sustainability.py           # [NEW] Analizador de sostenibilidad ambiental
│   ├── infrastructure/
│   │   ├── readers.py                  # Lectores de datos (Factory Pattern + Antoine Eq.)
│   │   └── exporters.py                # Exportadores SQLite/CSV/JSON/JS
│   ├── application/
│   │   ├── pipeline.py                 # Orquestador ETL (Template Method Pattern)
│   │   └── reporter.py                 # [NEW] Reporter automático (Builder Pattern)
│   └── presentation/
│       └── dashboard/                  # Submódulos del Dashboard Streamlit
│           ├── loader.py               # Cargador con caché y mappings de imágenes
│           ├── pt_solver.py            # Motor termodinámico Clausius-Clapeyron
│           ├── view_control.py         # Vista: Control y filtros con Plotly
│           ├── view_calculator.py      # Vista: Calculadora P-T + fotorrealismo
│           ├── view_comparator.py      # Vista: Comparación de 3 gases
│           ├── view_cycle.py           # Vista: Simulador de ciclo termodinámico
│           └── view_sql.py             # Vista: Consola SQL interactiva
│
├── tests/                              # [NEW] Suite de 54 tests unitarios
│   ├── __init__.py
│   ├── test_domain.py                  # 31 tests: entidades + validadores
│   └── test_sustainability.py          # 23 tests: scoring + regulatorio
│
├── notebooks/                          # 4 Jupyter Notebooks científicos
│   ├── eda_and_modeling.ipynb          # EDA + K-Means básico (original)
│   ├── 02_statistical_analysis.ipynb   # [NEW] PCA + Kruskal-Wallis + Shapiro-Wilk
│   ├── 03_ml_pipeline.ipynb            # [NEW] Pipeline ML: clustering + clasificación
│   └── 04_advanced_viz.ipynb           # [NEW] Visualizaciones avanzadas premium
│
├── data/processed/                     # Salida del ETL pipeline
│   ├── dim_refrigerant.csv             # Dimensión: 55 refrigerantes
│   ├── dim_temperature.csv             # Dimensión: Temperatura -50°C a +70°C
│   ├── dim_state.csv                   # Dimensión: Fases (líquido/vapor)
│   ├── fact_pressure_temperature.csv   # Hechos: ~7700 puntos P-T
│   ├── refrigerants_star_schema.db     # SQLite Star Schema completo
│   ├── eda_report.md                   # Reporte EDA en Markdown
│   └── full_analysis_report.md         # [NEW] Reporte integral auto-generado
│
├── .github/workflows/                  # [NEW] CI/CD GitHub Actions
│   ├── ci.yml                          # Tests en Python 3.10, 3.11, 3.12
│   └── deploy.yml                      # Pre-deploy validation + Streamlit Cloud
│
├── .streamlit/config.toml              # Configuración tema oscuro KrioMetrics
├── pytest.ini                          # [NEW] Configuración pytest
├── dashboard.py                        # Entry point Streamlit (5 vistas)
├── main.py                             # Entry point ETL Pipeline
├── requirements.txt                    # Dependencias Python
└── README.md                           # Este archivo
```

---

## 2. Arquitectura Clean (SOLID)

El proyecto implementa **Clean Architecture** con separación estricta de responsabilidades:

```
┌─────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                      │
│        (Streamlit Dashboard · HTML/JS SPA)              │
└──────────────────────┬──────────────────────────────────┘
                       │ (depende de)
┌──────────────────────▼──────────────────────────────────┐
│                 APPLICATION LAYER                        │
│   ETLPipeline (Template Method) · Reporter (Builder)    │
└──────────────────────┬──────────────────────────────────┘
                       │ (depende de)
┌──────────────────────▼──────────────────────────────────┐
│                   DOMAIN LAYER                           │
│  Entities · Validators (Strategy) · Sustainability      │
└──────────────────────┬──────────────────────────────────┘
                       │ (depende de)
┌──────────────────────▼──────────────────────────────────┐
│               INFRASTRUCTURE LAYER                       │
│        Readers (Factory) · Exporters (SQLite/CSV)       │
└─────────────────────────────────────────────────────────┘
```

### Patrones de Diseño Implementados

| Patrón | Módulo | Propósito |
| --- | --- | --- |
| **Template Method** | `pipeline.py` | Estructura del ETL con pasos intercambiables |
| **Factory Method** | `readers.py` | Creación de lectores de datos sin acoplar tipos |
| **Strategy** | `validators.py` | Intercambio de algoritmos de validación |
| **Builder** | `reporter.py` | Composición incremental de reportes |
| **Repository** | `exporters.py` | Abstracción del almacenamiento (SQLite/CSV) |

---

## 3. Notebooks de Análisis

| # | Notebook | Técnicas | Outputs |
| --- | --- | --- | --- |
| 01 | `eda_and_modeling.ipynb` | EDA, K-Means, visualizaciones Seaborn | Gráficos básicos |
| 02 | `02_statistical_analysis.ipynb` | Shapiro-Wilk, Kruskal-Wallis, Spearman, PCA | 4 gráficos avanzados |
| 03 | `03_ml_pipeline.ipynb` | Pipeline scikit-learn, RF, SVM, DBSCAN, dendrograma | 5 gráficos ML |
| 04 | `04_advanced_viz.ipynb` | Heatmaps, curvas P-T, burbujas, timeline regulatorio | 4 visualizaciones premium |

### Técnicas ML implementadas

- **Clustering**: K-Means, DBSCAN, Agglomerative (Ward/Complete)
- **Evaluación de clustering**: Silhouette, Davies-Bouldin, Calinski-Harabász, Elbow
- **Clasificación**: Random Forest, Gradient Boosting, SVM, Logistic Regression, KNN
- **Validación**: StratifiedKFold, cross_val_score, GridSearchCV
- **Reducción de dimensionalidad**: PCA (análisis de varianza explicada + biplot)
- **Estadísticas**: Shapiro-Wilk (normalidad), Kruskal-Wallis (no paramétrico), correlaciones Spearman/Pearson

---

## 4. Tests Unitarios

```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Con reporte de cobertura
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

**Resultado**: ✅ **54 tests pasando** en < 2 segundos

| Módulo de Tests | Tests | Cobertura |
| --- | --- | --- |
| `test_domain.py` | 31 tests | Entidades, Validadores, Dataset Validator |
| `test_sustainability.py` | 23 tests | Scoring GWP/ODP, EU F-Gas, Kigali, Montreal |

---

## 5. CI/CD con GitHub Actions

Dos workflows automatizados:

**`ci.yml`** — Se ejecuta en cada push/PR:
- ✅ Tests en Python 3.10, 3.11 y 3.12 (matrix)
- ✅ Lint con flake8 y Black
- ✅ Integración del pipeline ETL completo
- ✅ Upload de artefactos generados

**`deploy.yml`** — Se ejecuta al hacer push a `main`:
- ✅ Validación de tests antes del deploy
- ✅ Verificación de sintaxis de Streamlit app
- ✅ Notificación de deployment para Streamlit Cloud

---

## 6. Módulos del Dominio

### `validators.py` — Validación de Negocio

```python
from src.domain.validators import DatasetValidator

validator = DatasetValidator()
valid, invalid, issues = validator.validate_refrigerants(refrigerants)
validator.generate_quality_report(refrigerants, facts)
```

Reglas validadas: tipo de compuesto (ASHRAE), grupo de seguridad, GWP/ODP en rangos físicos,
temperatura crítica > punto de ebullición, color hexadecimal, unicidad de nombres, etc.

### `sustainability.py` — Scoring Ecológico

```python
from src.domain.sustainability import SustainabilityAnalyzer

analyzer = SustainabilityAnalyzer()
scores = analyzer.score_all(refrigerants)  # Ordenado de más a menos ecológico
summary = analyzer.get_ranking_summary(scores)
```

Puntuación 0-100 con sub-scores de GWP (0-40), ODP (0-30), seguridad (0-20) y regulación (0-10).
Verifica cumplimiento EU F-Gas, restricciones Kigali y prohibiciones Montreal.

### `reporter.py` — Reportes Automáticos

```python
from src.application.reporter import generate_full_report

paths = generate_full_report(refrigerants, facts)
# → data/processed/full_analysis_report.md
# → data/processed/full_analysis_report.json
```

---

## 7. Instalación y Ejecución

### Prerrequisitos

- Python 3.10 o superior
- pip

### Instalación

```bash
git clone https://github.com/dodysalim/refrigerant-gas-dashboard.git
cd refrigerant-gas-dashboard
pip install -r requirements.txt
```

### Ejecutar el Pipeline ETL

```bash
python main.py
```

Genera automáticamente:
- Archivos CSV del Esquema Estrella en `data/processed/`
- Base de datos SQLite `refrigerants_star_schema.db`
- Reporte EDA en `data/processed/eda_report.md`

### Ejecutar los Tests

```bash
python -m pytest tests/ -v
```

### Iniciar el Dashboard Streamlit

```bash
streamlit run dashboard.py
```

---

## 8. Dashboards

### 🌐 Dashboard HTML (SPA Premium)

Archivo: `web/index.html`

- Visualizador de cilindros fotorrealistas con colores reales por normativa
- Gráficos interactivos con Canvas y Chart.js
- Filtros dinámicos por categoría, tipo y seguridad
- Tabla de propiedades completa con búsqueda

### 🐍 Dashboard Streamlit (5 vistas científicas)

Comando: `streamlit run dashboard.py`

| Vista | Descripción |
| --- | --- |
| 🎛️ **Control** | Filtros interactivos, KPIs, distribución por tipo y seguridad |
| 🧮 **Calculadora P-T** | Consulta de presión a temperatura dada + fotorrealismo del cilindro |
| ⚖️ **Comparador** | Análisis lado a lado de 3 gases con curvas P-T superpuestas |
| 🔄 **Ciclo Termodinámico** | Simulador del ciclo de compresión de vapor simple |
| 🗄️ **Consola SQL** | Consultas SQL directas a la base de datos SQLite |

---

## 9. Marco Regulatorio

| Marco | Organismo | Impacto |
| --- | --- | --- |
| **Protocolo de Montreal (1987)** | UNEP | Eliminación total de CFCs (ODP > 0) |
| **Enmienda de Kigali (2016)** | UNEP | Reducción 85% de HFCs para 2047 |
| **EU F-Gas 517/2014** | Unión Europea | GWP < 150 para refrigeración doméstica |
| **ASHRAE 34** | ASHRAE | Clasificación de seguridad A1-B3 |

---

## 📄 Licencia

MIT License — Ver [LICENSE](LICENSE) para detalles.

---

<div align="center">

**KrioMetrics** · Desarrollado con ❄️ por [Dody Due�as](https://github.com/dodysalim)

*Pipeline ETL · Clean Architecture · Machine Learning · Streamlit · 55 Gases Refrigerantes*

</div>
