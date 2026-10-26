"""
Script de Ejecución Principal del Pipeline ETL - KrioMetrics
Punto de entrada para el pipeline de datos con validación integrada,
análisis de sostenibilidad y generación de reportes automáticos.

Uso:
    python run_etl.py                     # Ejecución normal
    python run_etl.py --validate          # Con validación de datos
    python run_etl.py --report            # Genera reporte de análisis completo
    python run_etl.py --validate --report # Validación + reporte completos
"""

import os
import sys
import argparse
import time
from datetime import datetime

# Fix Unicode output on Windows terminals
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from src.application.pipeline import RefrigerantETLPipeline


def parse_args():
    parser = argparse.ArgumentParser(
        description='KrioMetrics ETL Pipeline - Gases Refrigerantes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python run_etl.py                       # Pipeline básico
  python run_etl.py --validate            # + validación de calidad
  python run_etl.py --report              # + reporte de análisis
  python run_etl.py --validate --report   # Pipeline completo
        """
    )
    parser.add_argument('--validate', action='store_true',
                        help='Ejecutar validación de calidad del dataset')
    parser.add_argument('--report', action='store_true',
                        help='Generar reporte integral de análisis')
    parser.add_argument('--sustainability', action='store_true',
                        help='Exportar ranking de sostenibilidad en JSON')
    parser.add_argument('--reader', default='fallback',
                        choices=['fallback'],
                        help='Tipo de lector de datos (default: fallback)')
    return parser.parse_args()


def print_banner():
    print("\n" + "=" * 65)
    print("  ❄️  KrioMetrics — Pipeline ETL de Gases Refrigerantes")
    print("  Arquitectura: Clean Architecture | SOLID | Star Schema")
    print("=" * 65)
    print(f"  Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def run_pipeline(args, base_dir: str, output_dir: str, web_data_dir: str):
    """Ejecuta el pipeline ETL principal."""
    print("🚀 [PASO 1/4] Ejecutando pipeline ETL (Extracción → Transformación → Carga)...")
    t0 = time.time()

    pipeline = RefrigerantETLPipeline(
        output_dir=output_dir,
        web_data_dir=web_data_dir,
        reader_type=args.reader
    )
    pipeline.run()

    elapsed = time.time() - t0
    print(f"\n✅ Pipeline ETL completado en {elapsed:.2f}s")
    print(f"   📁 CSVs del Esquema Estrella → data/processed/")
    print(f"   💾 SQLite (Star Schema)      → data/processed/refrigerants_star_schema.db")
    print(f"   📊 JSON para dashboard       → web/data/refrigerants_dashboard.json")
    print(f"   📝 Reporte EDA               → data/processed/eda_report.md")

    return pipeline


def run_validation(refrigerants, facts, output_dir: str):
    """Ejecuta la validación completa del dataset."""
    from src.domain.validators import DatasetValidator

    print("\n🔍 [PASO 2/4] Validando calidad del dataset...")
    t0 = time.time()

    validator = DatasetValidator()
    ref_valid, ref_invalid, ref_issues = validator.validate_refrigerants(refrigerants)
    fact_valid, fact_invalid, fact_issues = validator.validate_facts(facts, refrigerants)

    elapsed = time.time() - t0
    quality = (ref_valid / len(refrigerants)) * 100 if refrigerants else 0
    symbol = "✅" if quality == 100 else ("⚠️" if quality >= 90 else "❌")

    print(f"   {symbol} Calidad del dataset: {quality:.1f}%")
    print(f"   📦 Refrigerantes válidos: {ref_valid}/{len(refrigerants)}")
    print(f"   📊 Hechos P-T válidos:    {fact_valid:,}/{len(facts):,}")

    all_errors = [i for i in ref_issues + fact_issues if i.startswith("[ERROR]")]
    all_warns = [i for i in ref_issues + fact_issues if i.startswith("[WARN]")]
    if all_errors:
        print(f"   ❌ Errores de validación: {len(all_errors)}")
        for e in all_errors[:3]:
            print(f"      {e}")
        if len(all_errors) > 3:
            print(f"      ... y {len(all_errors) - 3} más")
    if all_warns:
        print(f"   ⚠️  Advertencias: {len(all_warns)}")

    # Generar reporte de calidad
    quality_report_path = os.path.join(output_dir, "data_quality_report.md")
    validator.generate_quality_report(refrigerants, facts, quality_report_path)
    print(f"   📝 Reporte de calidad     → data/processed/data_quality_report.md")
    print(f"   Validación completada en {elapsed:.2f}s")


def run_full_report(refrigerants, facts, output_dir: str):
    """Genera el reporte integral de análisis."""
    from src.application.reporter import generate_full_report

    print("\n📊 [PASO 3/4] Generando reporte integral de análisis...")
    t0 = time.time()

    paths = generate_full_report(refrigerants, facts, output_dir)

    elapsed = time.time() - t0
    print(f"   📝 Reporte Markdown → data/processed/full_analysis_report.md")
    print(f"   🔢 Reporte JSON     → data/processed/full_analysis_report.json")
    print(f"   Reporte generado en {elapsed:.2f}s")


def run_sustainability_export(refrigerants, output_dir: str):
    """Exporta el ranking de sostenibilidad."""
    import json
    from src.domain.sustainability import SustainabilityAnalyzer

    print("\n🌿 [PASO 4/4] Exportando ranking de sostenibilidad...")
    t0 = time.time()

    analyzer = SustainabilityAnalyzer()
    scores = analyzer.score_all(refrigerants)
    summary = analyzer.get_ranking_summary(scores)

    output = {
        "generated_at": datetime.now().isoformat(),
        "summary": summary,
        "rankings": [s.to_dict() for s in scores]
    }

    path = os.path.join(output_dir, "sustainability_rankings.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - t0
    print(f"   🌿 Top 5 ecológicos: {' · '.join(summary['top_5_ecological'])}")
    print(f"   📄 Ranking JSON     → data/processed/sustainability_rankings.json")
    print(f"   Export en {elapsed:.2f}s")


def print_summary(args, output_dir: str):
    """Imprime resumen final de archivos generados."""
    print("\n" + "=" * 65)
    print("  ✅ PIPELINE COMPLETADO EXITOSAMENTE")
    print("=" * 65)

    generated_files = [
        ("data/processed/dim_refrigerant.csv",           "Dimensión Refrigerantes"),
        ("data/processed/dim_temperature.csv",            "Dimensión Temperatura"),
        ("data/processed/dim_state.csv",                  "Dimensión Estado"),
        ("data/processed/fact_pressure_temperature.csv",  "Hechos Presión-Temperatura"),
        ("data/processed/refrigerants_star_schema.db",    "Base de Datos SQLite"),
        ("data/processed/refrigerants_consolidated.json", "JSON Consolidado"),
        ("data/processed/eda_report.md",                  "Reporte EDA"),
        ("web/data/refrigerants_dashboard.json",          "JSON Dashboard HTML"),
        ("web/data/refrigerants_images_map.js",           "Mapping de Imágenes"),
    ]

    if args.validate:
        generated_files.append(("data/processed/data_quality_report.md", "Reporte de Calidad"))
    if args.report:
        generated_files.append(("data/processed/full_analysis_report.md", "Reporte Integral MD"))
        generated_files.append(("data/processed/full_analysis_report.json", "Reporte Integral JSON"))
    if args.sustainability:
        generated_files.append(("data/processed/sustainability_rankings.json", "Ranking Sostenibilidad"))

    print("\n  Archivos generados:")
    for rel_path, description in generated_files:
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path)
        exists = "✅" if os.path.exists(full_path) else "⏳"
        size = f"({os.path.getsize(full_path) // 1024} KB)" if os.path.exists(full_path) else ""
        print(f"  {exists} {description:<35} {size}")

    print("\n  Próximos pasos:")
    print("  → streamlit run dashboard.py    (Iniciar dashboard científico)")
    print("  → python -m pytest tests/ -v    (Ejecutar suite de tests)")
    print("  → open web/index.html           (Abrir dashboard HTML)\n")


def main():
    args = parse_args()
    print_banner()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "data", "processed")
    web_data_dir = os.path.join(base_dir, "web", "data")

    total_start = time.time()

    try:
        # Paso 1: ETL Pipeline (siempre se ejecuta)
        pipeline = run_pipeline(args, base_dir, output_dir, web_data_dir)

        # Extraer datos para pasos opcionales
        refrigerants = None
        facts = None

        if args.validate or args.report or args.sustainability:
            from src.infrastructure.readers import RefrigerantDataReaderFactory
            reader = RefrigerantDataReaderFactory.get_reader(args.reader)
            refrigerants = reader.read_refrigerants()
            facts = reader.read_pressure_temperature_points(refrigerants)

        # Paso 2: Validación (opcional)
        if args.validate:
            run_validation(refrigerants, facts, output_dir)

        # Paso 3: Reporte completo (opcional)
        if args.report:
            run_full_report(refrigerants, facts, output_dir)

        # Paso 4: Sostenibilidad (opcional)
        if args.sustainability:
            run_sustainability_export(refrigerants, output_dir)

        total_elapsed = time.time() - total_start
        print_summary(args, output_dir)
        print(f"  ⏱️  Tiempo total: {total_elapsed:.2f}s\n")

    except Exception as e:
        print(f"\n❌ Error durante la ejecución del pipeline: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
