"""
Módulos de Dominio - Validadores de Entidades
Implementa reglas de negocio para validar la integridad y calidad de los datos
de gases refrigerantes antes de cargarlos al modelo de datos.

Patrón aplicado: Strategy Pattern para validación composable.
"""

import re
from typing import List, Tuple
from dataclasses import dataclass
from src.domain.entities import Refrigerant, SaturatedPressureFact


@dataclass
class ValidationResult:
    """Resultado de una validación de entidad."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

    def __repr__(self) -> str:
        status = "✅ VÁLIDO" if self.is_valid else "❌ INVÁLIDO"
        lines = [f"ValidationResult({status})"]
        if self.errors:
            lines.append(f"  Errores ({len(self.errors)}):")
            for e in self.errors:
                lines.append(f"    - {e}")
        if self.warnings:
            lines.append(f"  Advertencias ({len(self.warnings)}):")
            for w in self.warnings:
                lines.append(f"    - {w}")
        return "\n".join(lines)


class RefrigerantValidator:
    """
    Validador de la entidad Refrigerant.
    Aplica reglas de negocio termodinámicas y de clasificación ASHRAE.
    """

    # Constantes de validación definidas por estándar ASHRAE 34
    VALID_COMPOUND_TYPES = {"CFC", "HCFC", "HFC", "HC", "Natural", "HFO", "Blend"}
    VALID_SAFETY_GROUPS = {"A1", "A2", "A2L", "A3", "B1", "B2", "B2L", "B3"}
    VALID_CATEGORIES = {"Basic", "Intermediate", "Industrial"}
    VALID_OIL_TYPES = {"Mineral", "POE", "PAG", "AB", "None"}
    VALID_STATUSES = {"Active", "Phased Out", "Phasing Down", "Emerging"}
    HEX_COLOR_PATTERN = re.compile(r'^#[0-9A-Fa-f]{6}$')

    # Límites físicos plausibles para gases refrigerantes reales
    MAX_GWP = 23900.0       # SF6 es el más alto conocido ~23900
    MAX_ODP = 1.2           # CFC-11 referencia = 1.0, algunos ligeramente > 1
    MIN_BOILING_POINT_C = -270.0  # Criogénicos extremos
    MAX_BOILING_POINT_C = 200.0   # Fluidos de alta temperatura
    MIN_CRITICAL_TEMP_C = -200.0
    MAX_CRITICAL_TEMP_C = 500.0

    def validate(self, refrigerant: Refrigerant) -> ValidationResult:
        """
        Valida un objeto Refrigerant contra todas las reglas de negocio.

        Args:
            refrigerant: Instancia de Refrigerant a validar.

        Returns:
            ValidationResult con estado de validación, errores y advertencias.
        """
        errors: List[str] = []
        warnings: List[str] = []

        # --- Reglas Obligatorias (Errores) ---
        if not refrigerant.ashrae_name or not refrigerant.ashrae_name.strip():
            errors.append("El campo 'ashrae_name' es obligatorio y no puede estar vacío.")

        if not refrigerant.chemical_formula or not refrigerant.chemical_formula.strip():
            errors.append("El campo 'chemical_formula' es obligatorio y no puede estar vacío.")

        if refrigerant.compound_type not in self.VALID_COMPOUND_TYPES:
            errors.append(
                f"Tipo de compuesto '{refrigerant.compound_type}' no es válido. "
                f"Valores permitidos: {sorted(self.VALID_COMPOUND_TYPES)}"
            )

        if refrigerant.safety_group not in self.VALID_SAFETY_GROUPS:
            errors.append(
                f"Grupo de seguridad ASHRAE '{refrigerant.safety_group}' no es válido. "
                f"Valores permitidos: {sorted(self.VALID_SAFETY_GROUPS)}"
            )

        if refrigerant.category not in self.VALID_CATEGORIES:
            errors.append(
                f"Categoría '{refrigerant.category}' no es válida. "
                f"Valores permitidos: {sorted(self.VALID_CATEGORIES)}"
            )

        if refrigerant.status not in self.VALID_STATUSES:
            errors.append(
                f"Estado '{refrigerant.status}' no es válido. "
                f"Valores permitidos: {sorted(self.VALID_STATUSES)}"
            )

        # --- Validaciones de Rangos Físicos ---
        if not (0.0 <= refrigerant.gwp <= self.MAX_GWP):
            errors.append(
                f"GWP={refrigerant.gwp} fuera de rango plausible [0, {self.MAX_GWP}]."
            )

        if not (0.0 <= refrigerant.odp <= self.MAX_ODP):
            errors.append(
                f"ODP={refrigerant.odp} fuera de rango plausible [0, {self.MAX_ODP}]."
            )

        if not (self.MIN_BOILING_POINT_C <= refrigerant.boiling_point_c <= self.MAX_BOILING_POINT_C):
            errors.append(
                f"Punto de ebullición {refrigerant.boiling_point_c}°C fuera de rango "
                f"[{self.MIN_BOILING_POINT_C}, {self.MAX_BOILING_POINT_C}]."
            )

        if not (self.MIN_CRITICAL_TEMP_C <= refrigerant.critical_temp_c <= self.MAX_CRITICAL_TEMP_C):
            errors.append(
                f"Temperatura crítica {refrigerant.critical_temp_c}°C fuera de rango "
                f"[{self.MIN_CRITICAL_TEMP_C}, {self.MAX_CRITICAL_TEMP_C}]."
            )

        if refrigerant.critical_pressure_bar < 0:
            errors.append(
                f"Presión crítica {refrigerant.critical_pressure_bar} bar no puede ser negativa."
            )

        # La temperatura crítica debe ser mayor que el punto de ebullición (principio termodinámico)
        if refrigerant.critical_temp_c <= refrigerant.boiling_point_c:
            errors.append(
                f"La temperatura crítica ({refrigerant.critical_temp_c}°C) debe ser "
                f"mayor que el punto de ebullición ({refrigerant.boiling_point_c}°C)."
            )

        # --- Validación de Color Hexadecimal ---
        if not self.HEX_COLOR_PATTERN.match(refrigerant.color_hex):
            errors.append(
                f"El código de color '{refrigerant.color_hex}' no es un valor hexadecimal válido (#RRGGBB)."
            )

        # --- Reglas de Advertencia (Warnings) ---
        # CFC y HCFC con ODP=0 podría ser un error de datos
        if refrigerant.compound_type in {"CFC", "HCFC"} and refrigerant.odp == 0.0:
            warnings.append(
                f"El tipo {refrigerant.compound_type} generalmente tiene ODP > 0. "
                f"Verificar si ODP=0 es correcto para {refrigerant.ashrae_name}."
            )

        # Refrigerantes "Phased Out" no deberían estar marcados como "Active"
        if refrigerant.status == "Active" and refrigerant.odp > 0.5:
            warnings.append(
                f"{refrigerant.ashrae_name} tiene ODP={refrigerant.odp} muy alto pero está marcado como 'Active'. "
                f"Considere verificar su estado regulatorio."
            )

        # Mezclas (Blends) deberían tener nombre que empiece con R-4xx o R-5xx
        if refrigerant.compound_type == "Blend" and not (
            "R-4" in refrigerant.ashrae_name or
            "R-5" in refrigerant.ashrae_name or
            "R-4" in refrigerant.ashrae_name
        ):
            warnings.append(
                f"La mezcla '{refrigerant.ashrae_name}' no sigue la convención ASHRAE R-4xx/R-5xx."
            )

        # GWP muy alto para gases en uso activo
        if refrigerant.gwp > 3000 and refrigerant.status == "Active":
            warnings.append(
                f"{refrigerant.ashrae_name} tiene GWP={refrigerant.gwp} > 3000 y está activo. "
                f"Podría estar sujeto a regulación Kigali a corto plazo."
            )

        # Descripción vacía es una advertencia de calidad de datos
        if not refrigerant.description or len(refrigerant.description.strip()) < 10:
            warnings.append(
                f"{refrigerant.ashrae_name}: Campo 'description' muy corto o vacío. "
                "La calidad de datos se verá afectada en el dashboard."
            )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class SaturatedPressureFactValidator:
    """
    Validador para la entidad SaturatedPressureFact.
    Verifica consistencia termodinámica en los puntos de presión-temperatura.
    """

    MAX_PRESSURE_BAR = 1000.0    # Límite supercrítico razonable
    MIN_PRESSURE_BAR = 0.001     # Vacío técnico (criogenia profunda)

    def validate(self, fact: SaturatedPressureFact, ref_key_range: range) -> ValidationResult:
        """
        Valida un punto de presión-temperatura.

        Args:
            fact: Instancia de SaturatedPressureFact.
            ref_key_range: Rango de claves de refrigerante válidas.

        Returns:
            ValidationResult con el resultado de la validación.
        """
        errors: List[str] = []
        warnings: List[str] = []

        if fact.refrigerant_key not in ref_key_range:
            errors.append(
                f"refrigerant_key={fact.refrigerant_key} no existe en el catálogo de refrigerantes."
            )

        if fact.state_key not in {1, 2}:
            errors.append(
                f"state_key={fact.state_key} inválido. Solo se permiten 1 (Liquid) y 2 (Vapor)."
            )

        if not (self.MIN_PRESSURE_BAR <= fact.pressure_bar <= self.MAX_PRESSURE_BAR):
            errors.append(
                f"pressure_bar={fact.pressure_bar} bar fuera del rango físico "
                f"[{self.MIN_PRESSURE_BAR}, {self.MAX_PRESSURE_BAR}]."
            )

        if not (self.MIN_PRESSURE_BAR <= fact.pressure_psi <= self.MAX_PRESSURE_BAR * 14.5038):
            errors.append(
                f"pressure_psi={fact.pressure_psi} PSI fuera del rango físico plausible."
            )

        # Verificar consistencia de conversión bar <-> PSI (tolerancia 1%)
        expected_psi = fact.pressure_bar * 14.5038
        if abs(fact.pressure_psi - expected_psi) / (expected_psi + 1e-9) > 0.01:
            warnings.append(
                f"Posible inconsistencia en conversión: "
                f"{fact.pressure_bar} bar debería ser ≈ {expected_psi:.2f} PSI "
                f"pero se registró {fact.pressure_psi:.2f} PSI."
            )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class DatasetValidator:
    """
    Validador a nivel de dataset completo.
    Verifica unicidad, integridad referencial y calidad global del conjunto de datos.
    """

    def __init__(self):
        self.ref_validator = RefrigerantValidator()
        self.fact_validator = SaturatedPressureFactValidator()

    def validate_refrigerants(self, refrigerants: List[Refrigerant]) -> Tuple[int, int, List[str]]:
        """
        Valida todos los refrigerantes del dataset.

        Returns:
            Tupla (total_valid, total_invalid, list_of_all_issues)
        """
        total_valid = 0
        total_invalid = 0
        all_issues: List[str] = []
        seen_names: set = set()

        for r in refrigerants:
            result = self.ref_validator.validate(r)

            # Verificar duplicados
            name_lower = r.ashrae_name.lower().strip()
            if name_lower in seen_names:
                result.errors.append(f"Nombre duplicado: '{r.ashrae_name}' ya existe en el dataset.")
                result.is_valid = False
            else:
                seen_names.add(name_lower)

            if result.is_valid:
                total_valid += 1
            else:
                total_invalid += 1
                for err in result.errors:
                    all_issues.append(f"[ERROR] {r.ashrae_name}: {err}")

            for warn in result.warnings:
                all_issues.append(f"[WARN] {r.ashrae_name}: {warn}")

        return total_valid, total_invalid, all_issues

    def validate_facts(
        self,
        facts: List[SaturatedPressureFact],
        refrigerants: List[Refrigerant]
    ) -> Tuple[int, int, List[str]]:
        """
        Valida la tabla de hechos de presión-temperatura.

        Returns:
            Tupla (total_valid, total_invalid, list_of_all_issues)
        """
        ref_key_range = range(1, len(refrigerants) + 1)
        total_valid = 0
        total_invalid = 0
        all_issues: List[str] = []

        for fact in facts:
            result = self.fact_validator.validate(fact, ref_key_range)
            if result.is_valid:
                total_valid += 1
            else:
                total_invalid += 1
                for err in result.errors:
                    all_issues.append(f"[ERROR] Fact ref_key={fact.refrigerant_key}: {err}")
            for warn in result.warnings:
                all_issues.append(f"[WARN] Fact ref_key={fact.refrigerant_key}: {warn}")

        return total_valid, total_invalid, all_issues

    def generate_quality_report(
        self,
        refrigerants: List[Refrigerant],
        facts: List[SaturatedPressureFact],
        output_path: str = "data/processed/data_quality_report.md"
    ) -> None:
        """
        Genera un reporte de calidad de datos completo en formato Markdown.
        """
        ref_valid, ref_invalid, ref_issues = self.validate_refrigerants(refrigerants)
        fact_valid, fact_invalid, fact_issues = self.validate_facts(facts, refrigerants)

        total_issues = len([i for i in ref_issues if i.startswith("[ERROR]")])
        total_warnings = len([i for i in ref_issues + fact_issues if i.startswith("[WARN]")])

        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# 📊 Reporte de Calidad de Datos - KrioMetrics\n\n")
            f.write(f"**Generado automáticamente por `DatasetValidator`**\n\n")
            f.write("---\n\n")
            f.write("## Resumen Ejecutivo\n\n")
            f.write(f"| Métrica | Valor |\n")
            f.write(f"| --- | --- |\n")
            f.write(f"| Total Refrigerantes | {len(refrigerants)} |\n")
            f.write(f"| Refrigerantes Válidos | {ref_valid} ✅ |\n")
            f.write(f"| Refrigerantes con Errores | {ref_invalid} ❌ |\n")
            f.write(f"| Total Puntos P-T | {len(facts)} |\n")
            f.write(f"| Puntos P-T Válidos | {fact_valid} ✅ |\n")
            f.write(f"| Puntos P-T con Errores | {fact_invalid} ❌ |\n")
            f.write(f"| Total Errores de Validación | {total_issues} |\n")
            f.write(f"| Total Advertencias | {total_warnings} |\n\n")

            quality_score = (ref_valid / len(refrigerants)) * 100 if refrigerants else 0
            f.write(f"**Índice de Calidad del Dataset: {quality_score:.1f}%**\n\n")

            if ref_issues or fact_issues:
                f.write("## Detalle de Problemas Encontrados\n\n")
                f.write("### Problemas en Refrigerantes\n\n")
                if ref_issues:
                    for issue in ref_issues:
                        marker = "🔴" if issue.startswith("[ERROR]") else "🟡"
                        f.write(f"- {marker} {issue}\n")
                else:
                    f.write("- ✅ Sin problemas en refrigerantes.\n")

                f.write("\n### Problemas en Tabla de Hechos P-T\n\n")
                if fact_issues:
                    for issue in fact_issues[:50]:  # Limitar output
                        marker = "🔴" if issue.startswith("[ERROR]") else "🟡"
                        f.write(f"- {marker} {issue}\n")
                    if len(fact_issues) > 50:
                        f.write(f"\n_... y {len(fact_issues) - 50} problemas adicionales._\n")
                else:
                    f.write("- ✅ Sin problemas en tabla de hechos.\n")
            else:
                f.write("## ✅ Dataset completamente válido - Sin problemas encontrados.\n")

            f.write("\n---\n*Reporte generado automáticamente por el sistema de validación KrioMetrics.*\n")

        print(f"[DatasetValidator] Reporte de calidad exportado a: {output_path}")
        print(f"[DatasetValidator] Resumen: {ref_valid}/{len(refrigerants)} refrigerantes válidos, "
              f"{fact_valid}/{len(facts)} hechos P-T válidos.")
