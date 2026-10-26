# Guía de Contribución — KrioMetrics

¡Gracias por tu interés en contribuir a KrioMetrics! Este documento explica cómo puedes colaborar de manera efectiva.

---

## 🌿 Código de Conducta

Este proyecto adhiere a un código de conducta basado en respeto mutuo, comunicación constructiva y colaboración técnica de calidad.

---

## 🚀 Cómo Contribuir

### 1. Reportar un Bug

Si encuentras un error, [abre un Issue](https://github.com/dodysalim/refrigerant-gas-dashboard/issues/new) con:

- **Título claro**: describir el problema en una línea
- **Descripción**: qué esperabas que ocurriera vs. qué ocurrió
- **Pasos para reproducir**: lista numerada de pasos
- **Entorno**: versión de Python, sistema operativo
- **Trazas de error** (si aplica): pegar el traceback completo

### 2. Proponer una Mejora

Para propuestas de nuevas funcionalidades:

1. [Abre un Issue](https://github.com/dodysalim/refrigerant-gas-dashboard/issues/new) con etiqueta `enhancement`
2. Describe el problema que resuelve la mejora
3. Propone una solución o diseño inicial
4. Espera retroalimentación antes de implementar

### 3. Enviar un Pull Request

#### Flujo de trabajo recomendado

```bash
# 1. Fork y clonar el repositorio
git clone https://github.com/TU_USUARIO/refrigerant-gas-dashboard.git
cd refrigerant-gas-dashboard

# 2. Instalar dependencias de desarrollo
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# 3. Crear una rama descriptiva
git checkout -b feat/nombre-de-la-funcionalidad
# o
git checkout -b fix/descripcion-del-bug

# 4. Hacer cambios siguiendo los estándares del proyecto

# 5. Verificar que los tests pasan
python -m pytest tests/ -v

# 6. Formatear código con Black
black src/ tests/ scripts/

# 7. Verificar lint con flake8
flake8 src/ tests/ --max-line-length=100 --ignore=E402,W503

# 8. Commit con mensaje semántico
git commit -m "feat: descripción concisa del cambio"

# 9. Push y abrir PR
git push origin feat/nombre-de-la-funcionalidad
```

---

## 📐 Estándares de Código

### Convenciones de Python

- **Formateo**: Black (líneas máx. 100 caracteres)
- **Docstrings**: Google style para clases y funciones públicas
- **Type hints**: Requeridos en funciones públicas
- **Imports**: Ordenados (stdlib → terceros → locales)

### Arquitectura (Clean Architecture + SOLID)

| Capa | Carpeta | Reglas |
| --- | --- | --- |
| Dominio | `src/domain/` | Sin imports de capas externas. Solo Python stdlib. |
| Infraestructura | `src/infrastructure/` | Puede importar dominio. Sin Streamlit/web. |
| Aplicación | `src/application/` | Puede importar dominio e infraestructura. |
| Presentación | `src/presentation/` | Puede importar todo. Contiene Streamlit/HTML. |

**Regla de oro**: Las dependencias solo fluyen hacia adentro (→ Dominio). El dominio no conoce las capas externas.

### Patrones de Diseño

Si añades nueva funcionalidad significativa, documenta qué patrón de diseño aplicas y por qué en el docstring de la clase.

---

## 🧪 Tests

### Requerimientos

- **Cobertura mínima**: Todo código nuevo en `src/domain/` y `src/application/` debe tener tests
- **Nomenclatura**: `test_<nombre_descriptivo>()` en `tests/test_<módulo>.py`
- **Independencia**: Cada test debe ser independiente (usar `setUp`/`tearDown` si necesario)
- **Tipo**: Preferir tests unitarios con mocks sobre tests de integración

### Ejecutar tests

```bash
# Todos los tests
python -m pytest tests/ -v

# Con cobertura
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Solo un archivo
python -m pytest tests/test_domain.py -v

# Solo una clase
python -m pytest tests/test_sustainability.py::TestSustainabilityAnalyzer -v
```

### Estructura de un test bien escrito

```python
class TestMiModulo(unittest.TestCase):
    """Descripción de qué se está testeando."""

    def setUp(self):
        """Configuración común para cada test."""
        self.objeto_bajo_prueba = MiClase()

    def test_nombre_descriptivo_del_comportamiento(self):
        """El método debe hacer X cuando se dan las condiciones Y."""
        # Arrange
        entrada = crear_objeto_de_prueba(param="valor")
        
        # Act
        resultado = self.objeto_bajo_prueba.mi_metodo(entrada)
        
        # Assert
        self.assertEqual(resultado.campo, "valor_esperado")
```

---

## 📝 Convenciones de Commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

| Prefijo | Cuándo usarlo |
| --- | --- |
| `feat:` | Nueva funcionalidad |
| `fix:` | Corrección de bug |
| `docs:` | Cambios en documentación |
| `test:` | Añadir o mejorar tests |
| `refactor:` | Refactorización sin cambio de comportamiento |
| `perf:` | Mejora de rendimiento |
| `ci:` | Cambios en CI/CD |
| `chore:` | Tareas de mantenimiento |

**Ejemplos válidos:**
```
feat: add sustainability scoring module with EU F-Gas compliance check
fix(data): normalize compound_type for blend refrigerants
test: add 15 unit tests for RefrigerantValidator
docs: update README with architecture diagram
ci: add matrix test for Python 3.12
```

---

## 📊 Datos Termodinámicos

Si quieres añadir o corregir datos de refrigerantes en `src/infrastructure/readers.py`:

1. Toda propiedad debe tener una fuente citable (ASHRAE, NIST, fabricante)
2. El GWP debe ser AR6 (Sexto Informe del IPCC) o indicar el AR utilizado
3. Verificar consistencia termodinámica: `critical_temp_c > boiling_point_c`
4. Ejecutar `DatasetValidator` para confirmar que el gas pasa todas las validaciones

---

## 🌍 Áreas de Mejora Prioritarias

Si quieres contribuir pero no sabes por dónde empezar:

- [ ] Añadir más gases refrigerantes emergentes (R-466A, R-452B)
- [ ] Implementar curvas COP (Coefficient of Performance) en el simulador
- [ ] Añadir soporte para diagramas Mollier (P-H) en el dashboard
- [ ] Mejorar la exportación a Excel con formato condicional
- [ ] Añadir traducciones al inglés para los módulos

---

*¿Preguntas? Abre un [Issue](https://github.com/dodysalim/refrigerant-gas-dashboard/issues) o contáctanos.*
