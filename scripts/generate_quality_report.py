"""
KrioMetrics - Generador de Reporte de Calidad de Datos
Script ejecutable para validar el dataset completo de gases refrigerantes
y generar un reporte de calidad de datos en formato Markdown.

Uso:
    python scripts/generate_quality_report.py
    python scripts/generate_quality_report.py --output data/processed/custom_report.md
    python scripts/generate_quality_report.py --verbose
"""

import sys
import os
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.readers import RefrigerantDataReaderFactory
from src.domain.validators import DatasetValidator


def parse_args():
    parser = argparse.ArgumentParser(
        description='KrioMetrics - Generador de Reporte de Calidad de Datos',
    )
    parser.add_argument('--output', default='data/processed/data_quality_report.md',
                        help='Ruta del archivo de salida (default: data/processed/data_quality_report.md)')
    parser.add_argument('--verbose', action='store_true',
                        help='Mostrar todos los problemas encontrados')
    parser.add_argument('--fail-on-errors', action='store_true',
                        help='Retornar código de error si se encuentran errores de validación')
    return parser.parse_args()


def main():
    args = parse_args()
    
    print("=" * 60)
    print("  📊 KrioMetrics - Generador de Reporte de Calidad")
    print("=" * 60)
    print(f"  Ejecutado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Cargar datos
    print("📂 Cargando datos del catálogo...")
    reader = RefrigerantDataReaderFactory.get_reader("fallback")
    refrigerants = reader.read_refrigerants()
    facts = reader.read_pressure_temperature_points(refrigerants)
    print(f"   ✅ {len(refrigerants)} refrigerantes, {len(facts):,} puntos P-T cargados\n")
    
    # 2. Ejecutar validación completa
    print("🔍 Ejecutando validación de datos...")
    validator = DatasetValidator()
    
    ref_valid, ref_invalid, ref_issues = validator.validate_refrigerants(refrigerants)
    fact_valid, fact_invalid, fact_issues = validator.validate_facts(facts, refrigerants)
    
    # 3. Mostrar resumen
    print(f"\n{'─'*40}")
    print(f"  RESUMEN DE VALIDACIÓN")
    print(f"{'─'*40}")
    print(f"  Refrigerantes válidos:    {ref_valid:>4} / {len(refrigerants)}")
    print(f"  Refrigerantes inválidos:  {ref_invalid:>4} / {len(refrigerants)}")
    print(f"  Hechos P-T válidos:       {fact_valid:>6,} / {len(facts):,}")
    print(f"  Hechos P-T inválidos:     {fact_invalid:>6,} / {len(facts):,}")
    
    all_errors = [i for i in ref_issues + fact_issues if i.startswith("[ERROR]")]
    all_warnings = [i for i in ref_issues + fact_issues if i.startswith("[WARN]")]
    
    print(f"\n  Errores totales:    {len(all_errors)}")
    print(f"  Advertencias total: {len(all_warnings)}")
    
    quality = (ref_valid / len(refrigerants)) * 100 if refrigerants else 0
    quality_symbol = "✅" if quality == 100 else ("⚠️" if quality >= 90 else "❌")
    print(f"\n  {quality_symbol} Índice de Calidad: {quality:.1f}%")
    
    if args.verbose and all_errors:
        print(f"\n{'─'*40}")
        print("  ERRORES ENCONTRADOS:")
        print(f"{'─'*40}")
        for err in all_errors[:20]:
            print(f"  🔴 {err}")
        if len(all_errors) > 20:
            print(f"  ... y {len(all_errors) - 20} errores adicionales")
    
    if args.verbose and all_warnings:
        print(f"\n  ADVERTENCIAS:")
        for warn in all_warnings[:10]:
            print(f"  🟡 {warn}")
    
    # 4. Generar reporte
    print(f"\n📝 Generando reporte de calidad...")
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    validator.generate_quality_report(refrigerants, facts, args.output)
    print(f"   ✅ Reporte guardado: {args.output}")
    
    print(f"\n{'='*60}")
    print("✅ Proceso completado.")
    print(f"{'='*60}\n")
    
    # Exit code para CI/CD
    if args.fail_on_errors and ref_invalid > 0:
        print(f"❌ Se encontraron {ref_invalid} errores de validación. Saliendo con código 1.")
        sys.exit(1)


if __name__ == "__main__":
    main()
