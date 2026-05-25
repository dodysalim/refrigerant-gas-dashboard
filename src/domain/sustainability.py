"""
Módulos de Dominio - Métricas de Sostenibilidad
Implementa el sistema de puntuación ecológica y análisis de impacto ambiental
de los gases refrigerantes según marcos regulatorios internacionales.

Marcos regulatorios implementados:
- Protocolo de Montreal (ODP)
- Acuerdo de París / Enmienda de Kigali (GWP)
- ASHRAE 34 (Seguridad)
- Directiva F-Gas de la UE 517/2014
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
from src.domain.entities import Refrigerant


@dataclass
class SustainabilityScore:
    """
    Puntuación de sostenibilidad para un gas refrigerante.
    Score de 0 (peor) a 100 (mejor ecológicamente).
    """
    ashrae_name: str
    eco_score: float            # Puntuación ecológica global [0-100]
    gwp_score: float            # Sub-puntuación por GWP [0-40]
    odp_score: float            # Sub-puntuación por ODP [0-30]
    safety_score: float         # Sub-puntuación por seguridad [0-20]
    regulation_score: float     # Sub-puntuación por estado regulatorio [0-10]
    eco_label: str              # "Excelente", "Bueno", "Moderado", "Problemático", "Crítico"
    eu_fgas_compliant: bool     # ¿Cumple con la directiva F-Gas UE?
    kigali_restricted: bool     # ¿Está restringido por la Enmienda de Kigali?
    montreal_banned: bool       # ¿Está prohibido por el Protocolo de Montreal?
    recommendation: str         # Recomendación de uso

    def to_dict(self) -> Dict:
        return {
            "ashrae_name": self.ashrae_name,
            "eco_score": round(self.eco_score, 2),
            "gwp_score": round(self.gwp_score, 2),
            "odp_score": round(self.odp_score, 2),
            "safety_score": round(self.safety_score, 2),
            "regulation_score": round(self.regulation_score, 2),
            "eco_label": self.eco_label,
            "eu_fgas_compliant": self.eu_fgas_compliant,
            "kigali_restricted": self.kigali_restricted,
            "montreal_banned": self.montreal_banned,
            "recommendation": self.recommendation
        }


class SustainabilityAnalyzer:
    """
    Analizador de sostenibilidad para gases refrigerantes.
    
    Implementa el patrón Strategy para cálculos de impacto ambiental,
    permitiendo intercambiar algoritmos de scoring sin modificar el código cliente.
    """

    # Umbrales de GWP según directiva EU F-Gas 517/2014
    EU_FGAS_GWP_THRESHOLD_DOMESTIC = 150      # Refrigeración doméstica: GWP < 150
    EU_FGAS_GWP_THRESHOLD_COMMERCIAL = 2500   # Refrigeración comercial: GWP < 2500
    EU_FGAS_GWP_THRESHOLD_MOBILE_AC = 150     # Aires acondicionados móviles: GWP < 150

    # Umbral de Kigali para reducción gradual
    KIGALI_HFC_REDUCTION_THRESHOLD = 1000     # GWP > 1000 en regulación de reducción

    # Pesos de la puntuación ecológica
    GWP_WEIGHT = 40
    ODP_WEIGHT = 30
    SAFETY_WEIGHT = 20
    REGULATION_WEIGHT = 10

    def score_refrigerant(self, refrigerant: Refrigerant) -> SustainabilityScore:
        """
        Calcula la puntuación de sostenibilidad completa de un refrigerante.

        Args:
            refrigerant: Entidad Refrigerant a evaluar.

        Returns:
            SustainabilityScore con todas las métricas calculadas.
        """
        gwp_score = self._calculate_gwp_score(refrigerant.gwp)
        odp_score = self._calculate_odp_score(refrigerant.odp)
        safety_score = self._calculate_safety_score(refrigerant.safety_group)
        regulation_score = self._calculate_regulation_score(refrigerant.status, refrigerant.gwp)

        eco_score = gwp_score + odp_score + safety_score + regulation_score
        eco_label = self._get_eco_label(eco_score)

        eu_fgas_compliant = self._check_eu_fgas_compliance(refrigerant)
        kigali_restricted = self._check_kigali_restriction(refrigerant)
        montreal_banned = refrigerant.odp > 0.0 or refrigerant.status == "Phased Out"
        recommendation = self._generate_recommendation(refrigerant, eco_score, eu_fgas_compliant)

        return SustainabilityScore(
            ashrae_name=refrigerant.ashrae_name,
            eco_score=eco_score,
            gwp_score=gwp_score,
            odp_score=odp_score,
            safety_score=safety_score,
            regulation_score=regulation_score,
            eco_label=eco_label,
            eu_fgas_compliant=eu_fgas_compliant,
            kigali_restricted=kigali_restricted,
            montreal_banned=montreal_banned,
            recommendation=recommendation
        )

    def _calculate_gwp_score(self, gwp: float) -> float:
        """
        Calcula la sub-puntuación GWP (0-40 puntos).
        Escala logarítmica para reflejar la naturaleza no lineal del impacto climático.
        """
        if gwp <= 1:
            return self.GWP_WEIGHT          # Perfecto: CO2, R-717, HFOs naturales
        elif gwp <= 10:
            return self.GWP_WEIGHT * 0.95   # Casi perfecto
        elif gwp <= 150:
            return self.GWP_WEIGHT * 0.80   # Muy bueno: R-1234yf, R-1234ze
        elif gwp <= 500:
            return self.GWP_WEIGHT * 0.60   # Aceptable: R-32
        elif gwp <= 1000:
            return self.GWP_WEIGHT * 0.40   # Moderado: R-134a
        elif gwp <= 2000:
            return self.GWP_WEIGHT * 0.20   # Problemático: R-404A, R-410A
        elif gwp <= 5000:
            return self.GWP_WEIGHT * 0.10   # Muy problemático
        elif gwp <= 14000:
            return self.GWP_WEIGHT * 0.05   # Crítico: R-23
        else:
            return 0.0                       # Inaceptable

    def _calculate_odp_score(self, odp: float) -> float:
        """
        Calcula la sub-puntuación ODP (0-30 puntos).
        Penalización severa por daño a la capa de ozono.
        """
        if odp == 0.0:
            return self.ODP_WEIGHT         # Sin daño al ozono
        elif odp < 0.05:
            return self.ODP_WEIGHT * 0.30  # Daño mínimo (algunos HCFCs)
        elif odp < 0.20:
            return self.ODP_WEIGHT * 0.15  # Daño bajo
        elif odp < 0.60:
            return self.ODP_WEIGHT * 0.05  # Daño moderado
        else:
            return 0.0                      # Daño severo (CFCs históricos)

    def _calculate_safety_score(self, safety_group: str) -> float:
        """
        Calcula la sub-puntuación de seguridad ASHRAE (0-20 puntos).
        Mayor puntuación = menor riesgo para el operador.
        """
        safety_scores = {
            "A1":  self.SAFETY_WEIGHT,          # Ideal: No tóxico, no inflamable
            "A2L": self.SAFETY_WEIGHT * 0.80,   # Muy bueno: Inflamabilidad mínima
            "B1":  self.SAFETY_WEIGHT * 0.65,   # Bueno: Tóxico pero no inflamable
            "A2":  self.SAFETY_WEIGHT * 0.55,   # Moderado: Inflamable pero no tóxico
            "B2L": self.SAFETY_WEIGHT * 0.45,   # Moderado-Alto: Tóxico + mínimamente inflamable
            "A3":  self.SAFETY_WEIGHT * 0.35,   # Alto riesgo: Muy inflamable
            "B2":  self.SAFETY_WEIGHT * 0.25,   # Alto: Tóxico + inflamable
            "B3":  self.SAFETY_WEIGHT * 0.10,   # Muy alto: Tóxico + muy inflamable
        }
        return safety_scores.get(safety_group, self.SAFETY_WEIGHT * 0.50)

    def _calculate_regulation_score(self, status: str, gwp: float) -> float:
        """
        Calcula la sub-puntuación regulatoria (0-10 puntos).
        """
        if status == "Active" and gwp <= 150:
            return self.REGULATION_WEIGHT
        elif status == "Active" and gwp <= 750:
            return self.REGULATION_WEIGHT * 0.75
        elif status == "Active":
            return self.REGULATION_WEIGHT * 0.50
        elif status == "Phasing Down":
            return self.REGULATION_WEIGHT * 0.25
        elif status == "Emerging":
            return self.REGULATION_WEIGHT * 0.90
        else:  # Phased Out
            return 0.0

    def _get_eco_label(self, score: float) -> str:
        """Convierte la puntuación numérica en una etiqueta ecológica descriptiva."""
        if score >= 85:
            return "🌿 Excelente"
        elif score >= 65:
            return "✅ Bueno"
        elif score >= 45:
            return "⚠️ Moderado"
        elif score >= 25:
            return "🔶 Problemático"
        else:
            return "🔴 Crítico"

    def _check_eu_fgas_compliance(self, refrigerant: Refrigerant) -> bool:
        """Verifica cumplimiento con la Directiva F-Gas UE 517/2014."""
        if refrigerant.odp > 0:
            return False
        if refrigerant.category == "Basic" and refrigerant.gwp > self.EU_FGAS_GWP_THRESHOLD_DOMESTIC:
            return False
        if refrigerant.status == "Phased Out":
            return False
        return True

    def _check_kigali_restriction(self, refrigerant: Refrigerant) -> bool:
        """Verifica si el gas está sujeto a restricciones de la Enmienda de Kigali."""
        return (
            refrigerant.compound_type in {"HFC", "Blend"} and
            refrigerant.gwp > self.KIGALI_HFC_REDUCTION_THRESHOLD
        )

    def _generate_recommendation(
        self,
        refrigerant: Refrigerant,
        score: float,
        eu_compliant: bool
    ) -> str:
        """Genera una recomendación de uso basada en el perfil del refrigerante."""
        name = refrigerant.ashrae_name

        if refrigerant.status == "Phased Out":
            return (f"❌ {name} está completamente prohibido por el Protocolo de Montreal. "
                    "No usar bajo ninguna circunstancia.")

        if score >= 85:
            return (f"✅ {name} es una excelente opción ecológica. "
                    "Recomendado para nuevas instalaciones sin restricciones regulatorias.")

        if score >= 65:
            if eu_compliant:
                return (f"👍 {name} es una buena opción con cumplimiento EU F-Gas. "
                        "Adecuado para la mayoría de aplicaciones modernas.")
            else:
                return (f"⚠️ {name} tiene buen perfil ambiental pero no cumple EU F-Gas 517/2014 "
                        "en algunas categorías. Verificar regulaciones locales.")

        if score >= 45:
            return (f"⚠️ {name} tiene impacto ambiental moderado. "
                    "Considerar alternativas de menor GWP en nuevos proyectos. "
                    "Usar solo donde no existan alternativas viables.")

        if score >= 25:
            return (f"🔶 {name} tiene impacto ambiental significativo (GWP alto o ODP > 0). "
                    f"Reemplazarlo con alternativas como {refrigerant.alternatives or 'HFOs o Naturales'} "
                    "al vencer el ciclo de vida del equipo.")

        return (f"🔴 {name} tiene impacto ambiental crítico. "
                f"Está siendo eliminado gradualmente. "
                f"Reemplazarlo urgentemente con {refrigerant.true_replacement or 'alternativas naturales'}.")

    def score_all(self, refrigerants: List[Refrigerant]) -> List[SustainabilityScore]:
        """Calcula la puntuación de sostenibilidad para todos los refrigerantes."""
        scores = [self.score_refrigerant(r) for r in refrigerants]
        return sorted(scores, key=lambda s: s.eco_score, reverse=True)

    def get_ranking_summary(self, scores: List[SustainabilityScore]) -> Dict:
        """Genera un resumen del ranking de sostenibilidad."""
        labels = {}
        for s in scores:
            labels[s.eco_label] = labels.get(s.eco_label, 0) + 1

        eu_compliant_count = sum(1 for s in scores if s.eu_fgas_compliant)
        kigali_restricted_count = sum(1 for s in scores if s.kigali_restricted)
        montreal_banned_count = sum(1 for s in scores if s.montreal_banned)
        avg_score = sum(s.eco_score for s in scores) / len(scores) if scores else 0

        top5 = scores[:5]
        bottom5 = scores[-5:]

        return {
            "total_analyzed": len(scores),
            "average_eco_score": round(avg_score, 2),
            "label_distribution": labels,
            "eu_fgas_compliant": eu_compliant_count,
            "kigali_restricted": kigali_restricted_count,
            "montreal_banned": montreal_banned_count,
            "top_5_ecological": [s.ashrae_name for s in top5],
            "bottom_5_ecological": [s.ashrae_name for s in bottom5]
        }
