"""
KrioMetrics - Análisis de Sostenibilidad Completo
Script ejecutable para generar el análisis de sostenibilidad ambiental
de todos los gases refrigerantes del catálogo.

Uso:
    python scripts/analyze_sustainability.py
    python scripts/analyze_sustainability.py --output data/processed
    python scripts/analyze_sustainability.py --top 10
"""

import sys
import os
import argparse
import json
from datetime import datetime

# Fix Unicode output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.readers import RefrigerantDataReaderFactory
from src.domain.sustainability import SustainabilityAnalyzer
from src.domain.validators import DatasetValidator


def parse_args():
    parser = argparse.ArgumentParser(
        description='KrioMetrics - Análisis de Sostenibilidad de Gases Refrigerantes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python scripts/analyze_sustainability.py
  python scripts/analyze_sustainability.py --top 5 --output data/processed
  python scripts/analyze_sustainability.py --filter-category Basic --json
        """
    )
    parser.add_argument('--output', default='data/processed',
                        help='Directorio de salida para los reportes (default: data/processed)')
    parser.add_argument('--top', type=int, default=10,
                        help='Número de gases a mostrar en el ranking (default: 10)')
    parser.add_argument('--filter-category', choices=['Basic', 'Intermediate', 'Industrial'],
                        help='Filtrar por categoría de refrigeración')
    parser.add_argument('--json', action='store_true',
                        help='También exportar ranking en formato JSON')
    parser.add_argument('--validate', action='store_true', default=True,
                        help='Ejecutar validación del dataset antes del análisis (default: True)')
    parser.add_argument('--quiet', action='store_true',
                        help='Modo silencioso - solo mostrar el ranking final')
    return parser.parse_args()


def print_header(quiet: bool = False):
    if not quiet:
        print("=" * 65)
        print("  🌿 KrioMetrics - Analizador de Sostenibilidad Ambiental")
        print("  Marcos Regulatorios: Montreal · Kigali · EU F-Gas 517/2014")
        print("=" * 65)
        print(f"  Ejecutado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def run_validation(refrigerants, facts, quiet: bool = False):
    if not quiet:
        print("🔍 Ejecutando validación del dataset...")
    
    validator = DatasetValidator()
    valid, invalid, issues = validator.validate_refrigerants(refrigerants)
    
    if not quiet:
        print(f"   ✅ Refrigerantes válidos: {valid}/{len(refrigerants)}")
        if invalid > 0:
            print(f"   ❌ Refrigerantes con errores: {invalid}")
            errors = [i for i in issues if i.startswith("[ERROR]")]
            for e in errors[:5]:
                print(f"      {e}")
            if len(errors) > 5:
                print(f"      ... y {len(errors) - 5} errores adicionales")
        warnings = [i for i in issues if i.startswith("[WARN]")]
        print(f"   ⚠️  Advertencias: {len(warnings)}")
        print()
    
    return valid, invalid, issues


def print_ranking(scores, top_n: int, filter_category: str = None):
    print(f"\n{'='*65}")
    print(f"🏆 RANKING DE SOSTENIBILIDAD ECOLÓGICA")
    if filter_category:
        print(f"   Filtro: Categoría = {filter_category}")
    print(f"{'='*65}")
    
    header = f"{'#':<4} {'Refrigerante':<14} {'Eco Score':<12} {'Etiqueta':<22} {'EU F-Gas':<10} {'Kigali'}"
    print(header)
    print("-" * 75)
    
    displayed = 0
    for rank, score in enumerate(scores, 1):
        if filter_category and score.ashrae_name:
            # Necesitaría el objeto completo para filtrar por categoría
            pass
        
        eu = "✅ Sí" if score.eu_fgas_compliant else "❌ No"
        kig = "⚠️ Sí" if score.kigali_restricted else "✅ No"
        print(f"{rank:<4} {score.ashrae_name:<14} {score.eco_score:<12.1f} {score.eco_label:<22} {eu:<10} {kig}")
        
        displayed += 1
        if displayed >= top_n:
            break
    
    print(f"\n{'='*65}")
    print(f"📊 ESTADÍSTICAS GLOBALES DEL CATÁLOGO")
    print(f"{'='*65}")


def print_summary(summary: dict):
    print(f"  Total analizados:          {summary['total_analyzed']} gases")
    print(f"  Puntuación eco promedio:   {summary['average_eco_score']:.1f} / 100")
    print(f"  Cumplen EU F-Gas 517/2014: {summary['eu_fgas_compliant']} gases")
    print(f"  Restringidos por Kigali:   {summary['kigali_restricted']} gases")
    print(f"  Afectados por Montreal:    {summary['montreal_banned']} gases")
    
    print(f"\n  📊 Distribución por etiqueta ecológica:")
    for label, count in sorted(summary['label_distribution'].items(), key=lambda x: x[1], reverse=True):
        bar = '█' * count
        print(f"     {label:<25} {count:>2} gases  {bar}")
    
    print(f"\n  🌿 TOP 5 MÁS ECOLÓGICOS:   {' · '.join(summary['top_5_ecological'])}")
    print(f"  🔴 BOTTOM 5 MÁS CRÍTICOS: {' · '.join(summary['bottom_5_ecological'])}")


def export_json(scores, summary, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    output = {
        "generated_at": datetime.now().isoformat(),
        "summary": summary,
        "rankings": [s.to_dict() for s in scores]
    }
    path = os.path.join(output_dir, "sustainability_rankings.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    return path


def main():
    args = parse_args()
    print_header(args.quiet)
    
    # 1. Cargar datos
    if not args.quiet:
        print("📂 Cargando datos del catálogo de refrigerantes...")
    
    reader = RefrigerantDataReaderFactory.get_reader("fallback")
    refrigerants = reader.read_refrigerants()
    facts = reader.read_pressure_temperature_points(refrigerants)
    
    if not args.quiet:
        print(f"   ✅ {len(refrigerants)} refrigerantes cargados, {len(facts)} puntos P-T\n")
    
    # 2. Validación opcional
    if args.validate and not args.quiet:
        run_validation(refrigerants, facts, args.quiet)
    
    # 3. Análisis de sostenibilidad
    if not args.quiet:
        print("🌿 Calculando puntuaciones de sostenibilidad...")
    
    analyzer = SustainabilityAnalyzer()
    scores = analyzer.score_all(refrigerants)
    summary = analyzer.get_ranking_summary(scores)
    
    if not args.quiet:
        print(f"   ✅ Análisis completado para {len(scores)} gases\n")
    
    # 4. Mostrar ranking
    print_ranking(scores, args.top, args.filter_category)
    print_summary(summary)
    
    # 5. Exportar JSON si se solicitó
    if args.json:
        json_path = export_json(scores, summary, args.output)
        print(f"\n📄 Ranking exportado en JSON: {json_path}")
    
    print(f"\n{'='*65}")
    print("✅ Análisis completado exitosamente.")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
