"""Lectores de datos de refrigerantes.

- `IDataReader` define el contrato (segregación de interfaces / sustitución de Liskov).
- `JsonCatalogReader` lee el catálogo de 55 gases desde `catalog/refrigerants.json`:
  los datos viven separados del código.
- `RefrigerantDataReaderFactory` crea lectores desde un registro: sumar una fuente nueva
  (PDF, API) es registrar una clase, sin modificar la fábrica.
"""
import abc
import json
from pathlib import Path
from typing import Callable, Dict, List

from src.domain.entities import Refrigerant, SaturatedPressureFact
from src.infrastructure.thermodynamics import BAR_TO_PSI, ThermodynamicEngine, glide

CATALOG_PATH = Path(__file__).resolve().parent / "catalog" / "refrigerants.json"
TEMPERATURE_RANGE_C = list(range(-50, 71, 5))
BUBBLE_POINT, DEW_POINT = 1, 2

__all__ = ["IDataReader", "JsonCatalogReader", "FallbackStaticDataReader", "RefrigerantDataReaderFactory",
           "ThermodynamicEngine", "generate_pt_facts"]


class IDataReader(abc.ABC):
    """Contrato para cualquier fuente de datos de refrigerantes."""

    @abc.abstractmethod
    def read_refrigerants(self) -> List[Refrigerant]:
        """Extrae la lista de entidades de refrigerantes."""

    @abc.abstractmethod
    def read_pressure_temperature_points(self, refrigerants: List[Refrigerant]) -> List[SaturatedPressureFact]:
        """Genera o extrae los registros de presión-temperatura para los gases dados."""


def generate_pt_facts(refrigerants: List[Refrigerant], temperatures=TEMPERATURE_RANGE_C,
                      engine=ThermodynamicEngine) -> List[SaturatedPressureFact]:
    """Curvas P-T de burbuja (líquido) y rocío (vapor) para cada gas.

    En mezclas zeotrópicas, a igual temperatura la presión de rocío es menor: se evalúa a T − glide.
    """
    facts = []
    for r in refrigerants:
        r_glide = glide(r)
        for temperature_key, temp_c in enumerate(temperatures, start=1):
            p_bubble = engine.calculate_vapor_pressure(r, temp_c)
            p_dew = engine.calculate_vapor_pressure(r, temp_c - r_glide) if r_glide > 0 else p_bubble
            for state, pressure in ((BUBBLE_POINT, p_bubble), (DEW_POINT, p_dew)):
                facts.append(SaturatedPressureFact(refrigerant_key=r.key, temperature_key=temperature_key,
                                                   state_key=state, pressure_bar=pressure,
                                                   pressure_psi=pressure * BAR_TO_PSI))
    return facts


class JsonCatalogReader(IDataReader):
    """Catálogo validado de 55 refrigerantes, con curvas P-T calculadas por el motor termodinámico."""

    def __init__(self, path: Path = CATALOG_PATH):
        self._path = Path(path)
        self._raw_data = json.loads(self._path.read_text(encoding="utf-8"))

    def read_refrigerants(self) -> List[Refrigerant]:
        return [Refrigerant(**record) for record in self._raw_data]

    def read_pressure_temperature_points(self, refrigerants: List[Refrigerant]) -> List[SaturatedPressureFact]:
        return generate_pt_facts(refrigerants)


# Nombre histórico, conservado por compatibilidad
FallbackStaticDataReader = JsonCatalogReader


class RefrigerantDataReaderFactory:
    """Patrón Factory con registro de lectores."""
    _registry: Dict[str, Callable[[], IDataReader]] = {"fallback": JsonCatalogReader, "json": JsonCatalogReader}

    @classmethod
    def register(cls, name: str, reader_cls: Callable[[], IDataReader]) -> None:
        cls._registry[name] = reader_cls

    @classmethod
    def get_reader(cls, reader_type: str = "fallback") -> IDataReader:
        try:
            return cls._registry[reader_type]()
        except KeyError:
            raise ValueError(f"Lector de datos '{reader_type}' no soportado.") from None
