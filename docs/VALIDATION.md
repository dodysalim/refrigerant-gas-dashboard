# Verificación · KrioMetrics

Fecha: 7 de octubre de 2026 (Ecuador). Entorno local Python 3.12.14. Las dependencias de QA se registran aparte; esta comprobación no certifica todas las combinaciones de versiones del proyecto.

## Ejecutado

54 pruebas aprobadas; cinco vistas Streamlit probadas sin excepciones. KrioMetrics Power BI abrió con datos en el PC durante la entrega anterior.

## Dependencias externas y límites

Datos incluidos: catálogo de 55 refrigerantes. El ciclo Power BI pide un solo gas y un escenario de temperaturas para evitar promediar condiciones físicas diferentes.

Las curvas y ciclos son estimaciones del modelo usado en la aplicación, no tablas certificadas para ingeniería. La malla de ciclos de Power BI usa intervalos de 5 °C.

## Presentación Power BI

Las definiciones se revisaron para límites y superposiciones, y el diseño móvil sigue el esquema oficial PBIR. La prueba nativa completa en teléfono permanece pendiente. Las fuentes externas deben exportarse antes de actualizar las páginas sin datos.
