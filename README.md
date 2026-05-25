# KrioMetrics - Pipeline ETL & Ecosistema Analítico de Refrigeración

Este proyecto es una plataforma completa de analítica e ingeniería de datos termodinámicos enfocada en el estudio de **55 gases refrigerantes** clasificados en refrigeración **Básica**, **Intermedia** e **Industrial**.

Integra una tubería de procesamiento de datos (ETL) escrita en Python bajo principios **SOLID** y patrones de diseño orientados a objetos, un **Modelo Estrella (Star Schema)** relacional analítico en **SQLite**, un **Cuaderno Jupyter** de modelado científico con **Machine Learning (K-Means)** y **dos Dashboards Interactivos Premium**: una aplicación analítica en **HTML5/Vanilla CSS/JS** y un panel científico interactivo modularizado en **Streamlit (Python & Plotly)**.

---

## 1. Estructura del Proyecto

El proyecto está diseñado bajo una arquitectura de software limpia, desacoplada y dividida en capas lógicas:

```text
proyectodegasesrefrigerante/
│
├── src/                          # Código fuente en Python (Clean Architecture & SOLID)
│   ├── domain/
│   │   └── entities.py           # Modelos/Clases puras del dominio (OOP)
│   ├── infrastructure/
│   │   ├── readers.py            # Lectores de datos (Factory Pattern, Ecuaciones P-T)
│   │   └── exporters.py          # Exportadores a SQLite y formatos JS/JSON para dashboards
│   ├── application/
│   │   └── pipeline.py           # Orquestador del ETL (Template Method Pattern)
│   └── presentation/             # Capa de Presentación Modular
│       └── dashboard/            # Submódulos del Dashboard de Streamlit
│           ├── __init__.py       # Inicialización del paquete
│           ├── loader.py         # Cargador con caché de base relacional e imágenes reales
│           ├── pt_solver.py      # Motor termodinámico Clausius-Clapeyron e interpolación
│           ├── view_control.py   # Vista: Dashboard de Control, filtros y gráficos Plotly
│           ├── view_calculator.py# Vista: Calculadora P-T y fotorrealismo de tanques
│           ├── view_comparator.py# Vista: Comparación P-T lado a lado de 3 gases
│           ├── view_cycle.py     # Vista: Simulador termodinámico de ciclo de compresión
│           └── view_sql.py       # Vista: Consola interactiva de consultas SQL SQLite
│
├── data/                         # Almacenamiento físico de datos (Esquema Estrella)
│   └── processed/
│       ├── dim_refrigerant.csv   # Dimensión: Detalles de gases y métricas GWP/ODP
│       ├── dim_temperature.csv   # Dimensión: Rango de temperaturas C/F (-50°C a +70°C)
│       ├── dim_state.csv         # Dimensión: Fases físicas (Burbuja y Rocío)
│       ├── fact_pressure_temperature.csv # Hechos: Presiones de saturación en bar/psi
│       ├── eda_report.md         # Reporte analítico del Análisis Exploratorio de Datos
│       └── refrigerants.db       # BASE DE DATOS SQLITE RELACIONAL (Almacén OLAP físico)
│
├── notebooks/                    # Modelado y Ciencia de Datos Científica
│   └── eda_and_modeling.ipynb    # Jupyter Notebook: SQL Queries, Plots Seaborn y ML K-Means
│
├── images/                       # Álbum de fotos reales de tanques clasificadas por uso
│   └── Gases_Refrigerantes/      # 55 subcarpetas de cilindros fotorrealistas reales
│
├── web/                          # Dashboard 1: Interfaz SPA Premium (HTML/CSS/JS)
│   ├── index.html                # Maquetado semántico, glassmorphism y conectores SVG
│   ├── styles.css                # Estilos oscuros "Deep Space" y flujos de cañerías dinámicos
│   ├── app.js                    # Front-end core, simulador de ciclo Kosner y buscador O(1)
│   ├── images/                   # Copia de recursos gráficos y catálogo de fotos reales
│   └── data/
│       ├── refrigerants_dashboard_data.js # Pre-carga local de base de datos relacional
│       └── refrigerants_images_map.js     # Pre-carga local de fotos reales de catálogo
│
├── dashboard.py                  # Dashboard 2: Orquestador y enrutador principal en Streamlit
├── run_etl.py                    # Script de entrada para ejecutar la tubería ETL relacional
├── generate_gas_images_mapping.py# Generador utilitario de mapas de imágenes de catálogo
├── requirements.txt              # Requerimientos y dependencias de Python
└── README.md                     # Documentación general del proyecto (este archivo)
```

---

## 2. Principios SOLID & Arquitectura de Presentación

### Principios SOLID Aplicados en Python
Para garantizar la mantenibilidad y extensibilidad industrial del software, aplicamos los siguientes principios:
*   **Single Responsibility Principle (SRP):** Cada módulo tiene una única razón para cambiar. Los archivos de vistas en `presentation/` renderizan UI, `entities.py` define modelos, `readers.py` calcula curvas, `exporters.py` persiste en SQLite y `pipeline.py` orquesta los flujos.
*   **Open/Closed Principle (OCP):** El motor termodinámico y las interfaces permiten agregar nuevos orígenes de datos (como APIs remotas o parsers web) extendiendo código base mediante herencia sin alterar la tubería core.
*   **Liskov Substitution Principle (LSP):** Cualquier cargador hereda de la clase base abstracta `IDataReader`, pudiendo sustituirse de forma transparente sin romper la aplicación.
*   **Interface Segregation Principle (ISP):** Las interfaces base están segregadas para que los módulos solo implementen los contratos específicos que requieren.
*   **Dependency Inversion Principle (DIP):** El pipeline del ETL no depende directamente de cargadores estáticos concretos, sino de la abstracción `IDataReader`.

### Arquitectura de Presentación Modular
Para evitar tener un archivo gigante y desordenado en Streamlit, modularizamos la interfaz en submódulos independientes:
*   **Desacoplamiento Visual:** Cada vista de la barra lateral se encuentra aislada en un archivo `view_*.py` autónomo.
*   **Mantenimiento Sencillo:** La adición o modificación de un gráfico en Plotly, cálculo de relación de compresión o cambios estéticos se realizan en su módulo específico, reduciendo el riesgo de romper otras pestañas.
*   **Rendimiento con Caching:** El módulo `loader.py` encapsula la carga física mediante `@st.cache_data`, compartiendo la memoria caché del motor de datos de manera óptima entre todas las vistas.

---

## 3. Modelo Estrella (Star Schema) en SQLite

Para optimizar las búsquedas y visualizaciones analíticas de los Dashboards, los datos se estructuran en un **Modelo Estrella relacional** clásico de Business Intelligence y se graban en la base de datos física `refrigerants.db`:

*   **Tabla de Hechos (`fact_pressure_temperature`):** Contiene las métricas numéricas variables (Presión en bar absoluto y psi absoluto) asociadas a llaves surrogadas (FK). Suma un total de **2,750 registros**.
*   **Dimensión Refrigerante (`dim_refrigerant`):** Contiene las propiedades descriptivas de los 55 refrigerantes (nombre, fórmula, tipo químico, grupo seguridad, ODP, GWP, lubricante, sustituto ecológico recomendado, estatus).
*   **Dimensión Temperatura (`dim_temperature`):** Contiene la dimensión escalar de temperaturas en incrementos de 5°C (de -50°C a +70°C).
*   **Dimensión Estado (`dim_state`):** Diferencia las fases termodinámicas críticas de saturación: Líquido Saturado (Punto de Burbuja) y Vapor Saturado (Punto de Rocío).

---

## 4. Instrucciones de Uso y Despliegue

### Requisitos Previos
Instala las librerías necesarias ejecutando en tu consola:
```bash
pip install -r requirements.txt streamlit scikit-learn
```

### Paso 1: Ejecutar la Tubería ETL Relacional
Para regenerar las tablas del Modelo Estrella, realizar la limpieza y cargar la base SQLite física junto con las pre-cargas del front-end, corre:
```bash
python run_etl.py
```

### Paso 2: Ejecutar el Mapa de Imágenes de Catálogo
Si agregas nuevas fotos fotorrealistas de cilindros y deseas recalcular de forma automatizada los mapas de conexión de los dashboards:
```bash
python generate_gas_images_mapping.py
```

### Paso 3: Levantar el Dashboard 1 (HTML Premium SPA)
¡Máxima portabilidad! El dashboard web tiene implementado un **Bypass CORS**. 
*   **Método Directo:** Haz **doble clic** directamente sobre el archivo [web/index.html](web/index.html) desde tu explorador de archivos para ejecutarlo localmente sin restricciones.
*   **Método Servidor Local (Opcional):**
    ```bash
    cd web
    python -m http.server 8000
    ```
    *Abre tu navegador en: `http://localhost:8000`*

### Paso 4: Levantar el Dashboard 2 (Streamlit & Plotly en Python)
Para visualizar el panel científico con gráficos de Plotly dinámicos, simuladores de ciclo y consultas SQL directas sobre SQLite:
```bash
streamlit run dashboard.py
```
*Abre tu navegador en: `http://localhost:8501` (o en la URL indicada en tu terminal)*

---

## 5. Características de los Dashboards

### Dashboard 1 (HTML/JS/CSS SPA):
*   **Calculadora Termodinámica P-T:** Slider interactivo con conversiones automáticas manométricas (`barg`/`psig`) y absolutas, con alerta de estado súper crítico.
*   **Ciclo de Refrigeración Kosner:** Animación en CSS del flujo de refrigerante en sentido horario. Sincroniza compresión, condensación, expansión y evaporación con su sustituto oficial.
*   **Visualizador del Modelo Estrella:** Líneas de curvas de Bézier dinámicas en SVG que representan físicamente las relaciones de la base SQLite.

### Dashboard 2 (Streamlit/Python Modular):
*   **Explorador Científico:** Gráficos dinámicos interactivos en Plotly Express de dispersión (ebullición vs temperatura crítica) y torta.
*   **Calculadora y Diagrama P-h:** Estimador de curva termodinámica con glide y dibujo dinámico del ciclo sobre el domo saturado en escala logarítmica.
*   **Terminal SQL OLAP:** Permite redactar sentencias SQL crudas interactivas directamente contra `refrigerants.db` para analizar cruzamientos complejos al instante.
