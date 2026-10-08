![KrioMetrics](docs/cover.svg)

# KrioMetrics

**Un catálogo de refrigerantes convertido en análisis, comparación y visualización interactiva.**

PERSONAL · ANALÍTICA DE REFRIGERANTES · Python · SQLite · Plotly · Streamlit

[Portafolio](https://dodysalim.github.io/) · [Caso y alcance](docs/PORTFOLIO_CASE.md) · [Verificación](docs/VALIDATION.md)

## La pregunta

¿Cómo comparar propiedades, seguridad e impacto ambiental manteniendo claras las hipótesis de los cálculos?

## Qué puedes revisar

- ETL y almacén SQLite para gases y propiedades P-T.
- Cinco vistas de control, cálculo, comparación, ciclo y consulta SQL.
- Power BI con curvas, escenarios y tablas relacionadas.

## Inicio local

Usa Python 3.11 o 3.12 en un entorno independiente. Desde la raíz:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install pytest
```

Después de configurar los datos:

```bash
python -m streamlit run dashboard.py
```

## Datos y configuración

Datos incluidos: catálogo de 55 refrigerantes. El ciclo Power BI pide un solo gas y un escenario de temperaturas para evitar promediar condiciones físicas diferentes.

## Power BI · PC y móvil

[Archivos e instrucciones](powerbi/README.md). Descarga el repositorio completo y abre `powerbi/Abrir-PowerBI.bat` en Windows; después pulsa **Actualizar**. Incluye A4 horizontal a tamaño real (100 %) y diseño móvil vertical. El archivo `.pbip` necesita sus carpetas Report, SemanticModel y data.

## Recorrido por el código

| Ruta | Qué contiene |
| --- | --- |
| [src/domain/](src/domain/) | Entidades y reglas de dominio |
| [src/application/](src/application/) | Pipeline y reportes |
| [src/presentation/dashboard/](src/presentation/dashboard/) | Cinco vistas analíticas |
| [tests/](tests/) | Pruebas de dominio y sostenibilidad |

## Comprobación y alcance

54 pruebas aprobadas; cinco vistas Streamlit probadas sin excepciones. KrioMetrics Power BI abrió con datos en el PC durante la entrega anterior.

Las curvas y ciclos son estimaciones del modelo usado en la aplicación, no tablas certificadas para ingeniería. La malla de ciclos de Power BI usa intervalos de 5 °C.

Para repetir las pruebas desde la raíz:

```bash
python -m pytest tests -q
```

## Autoría

Proyecto personal. Dody Salim Dueñas Remache.

[Documentación anterior](docs/ORIGINAL_README.md), conservada como referencia histórica.
