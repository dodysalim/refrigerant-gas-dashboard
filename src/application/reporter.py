"""
Módulos de Aplicación - Reporter Automático
Genera reportes profesionales en múltiples formatos (Markdown, HTML, JSON)
a partir de los datos procesados del pipeline ETL.

Patrón aplicado: Builder Pattern para construcción flexible de reportes.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from src.domain.entities import Refrigerant, SaturatedPressureFact
from src.domain.sustainability import SustainabilityAnalyzer, SustainabilityScore


class ReportSection:
    """Sección individual de un reporte."""
    def __init__(self, title: str, content: str, level: int = 2):
        self.title = title
        self.content = content
        self.level = level

    def to_markdown(self) -> str:
        heading = "#" * self.level
        return f"{heading} {self.title}\n\n{self.content}\n"


class KrioMetricsReportBuilder:
    """
    Builder para construir reportes de análisis de gases refrigerantes.
    Permite componer el reporte sección por sección.
    """
    def __init__(self, refrigerants: List[Refrigerant], facts: List[SaturatedPressureFact]):
        self._refrigerants = refrigerants
        self._facts = facts
        self._sections: List[ReportSection] = []
        self._analyzer = SustainabilityAnalyzer()
        self._scores: Optional[List[SustainabilityScore]] = None
        self._generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _get_scores(self) -> List[SustainabilityScore]:
        if self._scores is None:
            self._scores = self._analyzer.score_all(self._refrigerants)
        return self._scores

    def add_executive_summary(self) -> "KrioMetricsReportBuilder":
        """Agrega el resumen ejecutivo al reporte."""
        r = self._refrigerants
        total = len(r)
        active = sum(1 for x in r if x.status == "Active")
        phased_out = sum(1 for x in r if x.status == "Phased Out")
        phasing_down = sum(1 for x in r if x.status == "Phasing Down")
        eco_count = sum(1 for x in r if x.gwp <= 150 and x.odp == 0.0)

        content = f"""Este reporte presenta el análisis integral de **{total} gases refrigerantes** catalogados en el sistema KrioMetrics.

| Indicador | Valor |
| --- | --- |
| Total de Refrigerantes | {total} |
| Activos en el mercado | {active} ({active/total*100:.1f}%) |
| En proceso de eliminación | {phasing_down} ({phasing_down/total*100:.1f}%) |
| Completamente eliminados | {phased_out} ({phased_out/total*100:.1f}%) |
| De ultra-bajo impacto (GWP≤150, ODP=0) | {eco_count} ({eco_count/total*100:.1f}%) |
| Total puntos P-T en base de datos | {len(self._facts):,} |

> [!NOTE]
> Los datos son generados dinámicamente por la canalización ETL del proyecto KrioMetrics.
> Fuentes: ASHRAE Handbook of Refrigeration, EPA SNAP Program, EU F-Gas Directive 517/2014.
"""
        self._sections.append(ReportSection("Resumen Ejecutivo", content, level=2))
        return self

    def add_environmental_impact_analysis(self) -> "KrioMetricsReportBuilder":
        """Agrega análisis de impacto ambiental."""
        r = self._refrigerants
        gwp_values = [x.gwp for x in r]
        odp_values = [x.odp for x in r]

        avg_gwp = sum(gwp_values) / len(gwp_values)
        max_gwp_ref = max(r, key=lambda x: x.gwp)
        min_gwp_refs = [x for x in r if x.gwp <= 1]
        zero_odp = sum(1 for x in r if x.odp == 0.0)

        scores = self._get_scores()
        summary = self._analyzer.get_ranking_summary(scores)

        top_eco = ", ".join([f"**{n}**" for n in summary["top_5_ecological"]])
        bot_eco = ", ".join([f"**{n}**" for n in summary["bottom_5_ecological"]])

        content = f"""### Métricas Globales de Impacto Climático (GWP)

| Métrica | Valor | Referencia |
| --- | --- | --- |
| GWP Promedio del catálogo | {avg_gwp:.1f} CO₂eq | — |
| GWP Máximo | **{max_gwp_ref.gwp:.0f}** ({max_gwp_ref.ashrae_name}) | R-23 criogénico |
| Gases con GWP ≤ 1 | {len(min_gwp_refs)} gases | HFOs, Naturales |
| Gases con ODP = 0 | {zero_odp} ({zero_odp/len(r)*100:.1f}%) | Sin daño ozono |
| Puntuación Eco Promedio | {summary["average_eco_score"]}/100 | KrioMetrics Score |

### Ranking de Sostenibilidad (Top 5 🌿)

Los 5 gases más ecológicos del catálogo: {top_eco}

### Gases con Mayor Impacto Ambiental (Bottom 5 🔴)

Los 5 gases de mayor impacto negativo: {bot_eco}

### Distribución por Etiqueta Ecológica

| Etiqueta | Cantidad | Descripción |
| --- | --- | --- |
| 🌿 Excelente (≥85 pts) | {summary["label_distribution"].get("🌿 Excelente", 0)} | Alternativas futuras |
| ✅ Bueno (65-84 pts) | {summary["label_distribution"].get("✅ Bueno", 0)} | Opciones recomendables |
| ⚠️ Moderado (45-64 pts) | {summary["label_distribution"].get("⚠️ Moderado", 0)} | Uso transitorio |
| 🔶 Problemático (25-44 pts) | {summary["label_distribution"].get("🔶 Problemático", 0)} | Reemplazar pronto |
| 🔴 Crítico (<25 pts) | {summary["label_distribution"].get("🔴 Crítico", 0)} | Prohibidos/eliminando |

### Estado Regulatorio Global

- **Cumplimiento EU F-Gas 517/2014**: {summary["eu_fgas_compliant"]}/{len(r)} gases ({summary["eu_fgas_compliant"]/len(r)*100:.1f}%)
- **Restringidos por Enmienda de Kigali**: {summary["kigali_restricted"]} gases
- **Afectados por Protocolo de Montreal**: {summary["montreal_banned"]} gases
"""
        self._sections.append(ReportSection("Análisis de Impacto Ambiental", content, level=2))
        return self

    def add_thermodynamic_correlations(self) -> "KrioMetricsReportBuilder":
        """Agrega análisis de correlaciones termodinámicas."""
        r = self._refrigerants
        avg_bp = sum(x.boiling_point_c for x in r) / len(r)
        avg_ct = sum(x.critical_temp_c for x in r) / len(r)
        avg_cp = sum(x.critical_pressure_bar for x in r) / len(r)

        lowest_bp = min(r, key=lambda x: x.boiling_point_c)
        highest_cp = max(r, key=lambda x: x.critical_pressure_bar)
        highest_ct = max(r, key=lambda x: x.critical_temp_c)

        # Distribución por categoría
        cats = {}
        for x in r:
            cats.setdefault(x.category, []).append(x)

        content = f"""### Propiedades Termodinámicas Promedio

| Propiedad | Promedio | Extremo Notable |
| --- | --- | --- |
| Punto de Ebullición | {avg_bp:.1f} °C | {lowest_bp.ashrae_name}: {lowest_bp.boiling_point_c:.1f}°C (mínimo) |
| Temperatura Crítica | {avg_ct:.1f} °C | {highest_ct.ashrae_name}: {highest_ct.critical_temp_c:.1f}°C (máximo) |
| Presión Crítica | {avg_cp:.1f} bar | {highest_cp.ashrae_name}: {highest_cp.critical_pressure_bar:.1f} bar (máximo) |

### Análisis por Categoría de Refrigeración

| Categoría | N° Gases | BP Promedio (°C) | TC Promedio (°C) | PC Promedio (bar) |
| --- | --- | --- | --- | --- |
""" + "".join([
    f"| {cat} | {len(gases)} | {sum(g.boiling_point_c for g in gases)/len(gases):.1f} | "
    f"{sum(g.critical_temp_c for g in gases)/len(gases):.1f} | "
    f"{sum(g.critical_pressure_bar for g in gases)/len(gases):.1f} |\n"
    for cat, gases in sorted(cats.items())
]) + f"""
### Principio de la Relación P-T

La relación entre el **punto de ebullición** y la **presión de trabajo** sigue la ley de Antoine.
A menor punto de ebullición, el refrigerante requiere mayor presión para condensar a temperatura ambiente.

| Gas | Ebullición (°C) | Aprox. Presión a 25°C (bar) | Implicación |
| --- | --- | --- | --- |
| R-744 (CO₂) | -78.4 | ~65-70 | Sistemas transcríticos robustos |
| R-410A | -51.4 | ~16 | Alta presión, tuberías gruesas |
| R-32 | -51.7 | ~15 | Similar a R-410A pero más eco |
| R-134a | -26.3 | ~8 | Presión moderada, muy difundido |
| R-717 (NH₃) | -33.3 | ~11 | Sistemas industriales herméticos |
| R-290 (Propano) | -42.1 | ~12 | Cargas pequeñas, muy eficiente |
"""
        self._sections.append(ReportSection("Correlaciones Termodinámicas", content, level=2))
        return self

    def add_compound_type_breakdown(self) -> "KrioMetricsReportBuilder":
        """Agrega desglose por tipo de compuesto."""
        type_map: Dict[str, list] = {}
        for x in self._refrigerants:
            type_map.setdefault(x.compound_type, []).append(x)

        rows = []
        for t, gases in sorted(type_map.items(), key=lambda x: len(x[1]), reverse=True):
            avg_gwp = sum(g.gwp for g in gases) / len(gases)
            avg_odp = sum(g.odp for g in gases) / len(gases)
            active = sum(1 for g in gases if g.status == "Active")
            rows.append(f"| {t} | {len(gases)} | {avg_gwp:.0f} | {avg_odp:.3f} | {active} |")

        content = f"""| Tipo de Compuesto | N° Gases | GWP Promedio | ODP Promedio | Activos |
| --- | --- | --- | --- | --- |
""" + "\n".join(rows)
        self._sections.append(ReportSection("Distribución por Tipo de Compuesto", content, level=2))
        return self

    def build_markdown(self) -> str:
        """Construye el reporte completo en formato Markdown."""
        header = f"""# 📊 Reporte Integral de Análisis - KrioMetrics
### Catálogo de Gases Refrigerantes

*Generado automáticamente el {self._generated_at} por el sistema KrioMetrics ETL Pipeline.*

---

"""
        body = "\n---\n\n".join(section.to_markdown() for section in self._sections)
        footer = "\n\n---\n*© KrioMetrics - Sistema de Análisis de Gases Refrigerantes*\n"
        return header + body + footer

    def build_json(self) -> Dict:
        """Construye el reporte en formato JSON para consumo por APIs."""
        r = self._refrigerants
        scores = self._get_scores()
        summary = self._analyzer.get_ranking_summary(scores)

        return {
            "metadata": {
                "generated_at": self._generated_at,
                "system": "KrioMetrics ETL Pipeline",
                "version": "2.0.0"
            },
            "summary": {
                "total_refrigerants": len(r),
                "total_pt_points": len(self._facts),
                "active_count": sum(1 for x in r if x.status == "Active"),
                "phased_out_count": sum(1 for x in r if x.status == "Phased Out"),
                "eco_avg_score": summary["average_eco_score"],
                "eu_compliant_count": summary["eu_fgas_compliant"],
                "kigali_restricted_count": summary["kigali_restricted"]
            },
            "top_5_ecological": summary["top_5_ecological"],
            "bottom_5_ecological": summary["bottom_5_ecological"],
            "sustainability_scores": [s.to_dict() for s in scores]
        }

    def save(self, output_dir: str = "data/processed") -> Dict[str, str]:
        """
        Guarda el reporte en todos los formatos disponibles.

        Returns:
            Diccionario con las rutas de los archivos generados.
        """
        os.makedirs(output_dir, exist_ok=True)
        paths = {}

        # Markdown
        md_path = os.path.join(output_dir, "full_analysis_report.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self.build_markdown())
        paths["markdown"] = md_path
        print(f"[Reporter] Reporte Markdown guardado: {md_path}")

        # JSON
        json_path = os.path.join(output_dir, "full_analysis_report.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.build_json(), f, ensure_ascii=False, indent=2)
        paths["json"] = json_path
        print(f"[Reporter] Reporte JSON guardado: {json_path}")

        return paths


def generate_full_report(
    refrigerants: List[Refrigerant],
    facts: List[SaturatedPressureFact],
    output_dir: str = "data/processed"
) -> Dict[str, str]:
    """
    Función de alto nivel para generar el reporte completo de análisis.
    
    Args:
        refrigerants: Lista de refrigerantes del ETL.
        facts: Lista de hechos P-T del ETL.
        output_dir: Directorio de salida.

    Returns:
        Diccionario con rutas de los archivos generados.
    """
    builder = (
        KrioMetricsReportBuilder(refrigerants, facts)
        .add_executive_summary()
        .add_environmental_impact_analysis()
        .add_thermodynamic_correlations()
        .add_compound_type_breakdown()
    )
    return builder.save(output_dir)
