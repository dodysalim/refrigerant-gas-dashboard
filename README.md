# KrioMetrics - Pipeline ETL & Ecosistema Analítico de Refrigeración

Este proyecto es una plataforma completa de analítica e ingeniería de datos termodinámicos enfocada en el estudio de **55 gases refrigerantes** clasificados en refrigeración **Básica**, **Intermedia** e **Industrial**.

Integra una tubería de procesamiento de datos (ETL) escrita en Python bajo principios **SOLID** y patrones orientados a objetos, un **Modelo Estrella (Star Schema)** relacional analítico en **SQLite**, un **Cuaderno Jupyter** de modelado científico y **dos Dashboards Interactivos Premium**: una aplicación analítica en **HTML5/Vanilla CSS/JS** y un panel científico interactivo en **Streamlit (Python & Plotly)**.

---

## 1. Estructura del Proyecto

El proyecto está diseñado bajo una arquitectura de software limpia y modular:

```text
proyectodegasesrefrigerante/
│
├── src/                          # Backend en Python (Arquitectura de Tubería)
│   ├── domain/
│   │   └── entities.py           # Modelos/Clases puras del dominio (OOP)
│   ├── infrastructure/
│   │   ├── readers.py            # Lectores de datos (Factory Pattern, Ecuaciones P-T)
│   │   └── exporters.py          # Exportadores a SQLite (Almacén) y CSV/JSON
│   └── application/
│       └── pipeline.py           # Orquestador del ETL (Template Method Pattern)
│
├── data/                         # Almacenamiento físico de datos (Esquema Estrella)
│   └── processed/
│       ├── dim_refrigerant.csv   # Dimensión CSV: Detalles de gases y métricas GWP/ODP
│       ├── dim_temperature.csv   # Dimensión CSV: Rango de temperaturas C/F (-50°C a +70°C)
│       ├── dim_state.csv         # Dimensión CSV: Fases físicas (Burbuja y Rocío)
│       ├── fact_pressure_temperature.csv # Hechos CSV: Presiones de saturación medidas en bar/psi
│       ├── eda_report.md         # Reporte Markdown del Análisis Exploratorio de Datos (EDA)
│       └── refrigerants.db       # BASE DE DATOS SQLITE RELACIONAL COMPLETA (Almacén OLAP)
│
├── notebooks/                    # Modelado y Ciencia de Datos Científica
│   └── eda_and_modeling.ipynb    # Jupyter Notebook: SQL Queries, Plots Seaborn y ML K-Means
│
├── web/                          # Dashboard 1: Interfaz de Usuario Premium SPA (HTML/CSS/JS)
│   ├── index.html                # Maquetado semántico y contenedores Chart.js
│   ├── styles.css                # Estilos oscuros "Deep Space", glassmorphism y flujos
│   ├── app.js                    # Motor JS de filtrado, simulador de ciclo y gráficos
│   └── data/
│       └── refrigerants_dashboard.json # Copia unificada del Modelo Estrella para el cliente
│
├── dashboard.py                  # Dashboard 2: Interfaz Streamlit (Python & Plotly interactivo)
│├── run_etl.py                    # Script de entrada para ejecutar la tubería ETL
│├── generate_notebook.py          # Script generador programático del Jupyter Notebook
├── requirements.txt              # Requerimientos de Python
└── README.md                     # Documentación general del proyecto (este archivo)
```

---

## 2. Principios SOLID Aplicados en Python

Para garantizar la mantenibilidad y extensibilidad industrial del software, aplicamos los siguientes principios:

- **Single Responsibility Principle (SRP)**: Cada módulo tiene una única razón para cambiar. `entities.py` define los modelos, `readers.py` extrae y calcula curvas de presión, `exporters.py` persiste las tablas a disco y a SQLite, y `pipeline.py` orquesta los flujos.
- **Open/Closed Principle (OCP)**: El motor termodinámico y las interfaces de los lectores permiten agregar nuevos orígenes de datos (como una API remota o un parser de PDF online) extendiendo el código mediante herencia sin alterar la tubería core.
- **Liskov Substitution Principle (LSP)**: `FallbackStaticDataReader` y cualquier futuro cargador heredan de la clase base abstracta `IDataReader`, pudiendo sustituirse de forma transparente sin romper la aplicación.
- **Interface Segregation Principle (ISP)**: La interfaz `IDataReader` está segregada únicamente para las funciones específicas de lectura de refrigerantes y curvas P-T correspondientes.
- **Dependency Inversion Principle (DIP)**: El pipeline de la aplicación no depende directamente de un cargador estático, sino de la abstracción `IDataReader`, inyectando la dependencia mediante una factoría.

### Patrones de Diseño Utilizados:
1. **Factory Pattern (`RefrigerantDataReaderFactory`)**: Permite desacoplar la lógica de creación de lectores y devolver la fuente correcta según los parámetros.
2. **Template Method Pattern (`BaseETLPipeline` -> `RefrigerantETLPipeline`)**: Define la plantilla del algoritmo ETL (`extract()`, `transform()`, `load()`) permitiendo que clases hijas implementen los pasos de limpieza específicos.

---

## 3. Modelo Estrella (Star Schema) en SQLite

Para optimizar las búsquedas y visualizaciones analíticas de los Dashboards, los datos se estructuran en un **Modelo Estrella relacional** clásico de Business Intelligence y se graban en la base de datos física `refrigerants.db`:

- **Tabla de Hechos (`fact_pressure_temperature`)**: Contiene las métricas numéricas variables (Presión en bar absoluto y psi absoluto) asociadas a llaves surrogadas (FK). Suma un total de **2,750 registros**.
- **Dimensión Refrigerante (`dim_refrigerant`)**: Contiene las propiedades descriptivas de los 55 refrigerantes (nombre, fórmula, tipo químico, grupo seguridad, ODP, GWP, lubricante, estatus).
- **Dimensión Temperatura (`dim_temperature`)**: Contiene la dimensión temporal/escalar de temperaturas en incrementos de 5°C (de -50°C a +70°C).
- **Dimensión Estado (`dim_state`)**: Diferencia las dos fases termodinámicas críticas de saturación: Líquido Saturado (Punto de Burbuja) y Vapor Saturado (Punto de Rocío), ideal para analizar mezclas zeotrópicas con deslizamiento (glide).

---

## 4. Instrucciones de Uso y Despliegue

### Requisitos Previos:
Instala las librerías necesarias con:
```bash
pip install -r requirements.txt streamlit scikit-learn
```

### Paso 1: Ejecutar la Tubería ETL
Para regenerar las tablas del Modelo Estrella, realizar la limpieza y cargar la base SQLite física, corre:
```bash
python run_etl.py
```

### Paso 2: Generar y Abrir el Jupyter Notebook
Si deseas inspeccionar el análisis científico de K-Means y los plots estáticos con Seaborn:
```bash
python generate_notebook.py
jupyter notebook notebooks/eda_and_modeling.ipynb
```

### Paso 3: Levantar el Dashboard 1 (HTML Premium SPA)
Para visualizar el dashboard premium interactivo en HTML5/JS, levanta un servidor local rápido debido a restricciones CORS:
```bash
cd web
python -m http.server 8000
```
*Luego abre tu navegador en: **`http://localhost:8000`***

### Paso 4: Levantar el Dashboard 2 (Streamlit & Plotly en Python)
Para visualizar el dashboard científico interactivo en Streamlit con gráficos de Plotly dinámicos y consultas SQL directas sobre SQLite:
```bash
streamlit run dashboard.py
```
*Luego abre tu navegador en: **`http://localhost:8501`***

---

## 5. Características de los Dashboards

### Dashboard 1 (HTML/JS/CSS):
- **Calculadora Termodinámica P-T**: Slider interactivo de temperatura con glide termodinámico y alerta de estado Supercrítico.
- **Comparador Gráfico**: Permite graficar simultáneamente y comparar las curvas de presión de hasta 3 gases con Chart.js.
- **Simulador de Ciclo de Refrigeración**: Animación viva del flujo de partículas en tuberías calculando dinámicamente presiones y relaciones de compresión críticas.
- **Visualizador del Modelo Estrella**: Panel interactivo con el diseño relacional del modelo.

### Dashboard 2 (Streamlit/Python):
- **Plotly Express Interactivos**: Gráficos de dispersión y pie charts con tags de hover dinámicas sobre los 55 refrigerantes.
- **Calculadora P-T y Ciclo de Refrigeración en Python**: Motores de cálculo integrados directamente en backend.
- **Consola SQL Directa**: Entrada interactiva para escribir consultas SQL crudas directamente sobre el archivo `refrigerants.db` y visualizar los DataFrames resultantes.
