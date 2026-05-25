"""
Script de Ejecución Principal del Pipeline ETL
Este archivo es el punto de entrada para ejecutar la canalización de datos
en Python aplicando los principios del Esquema Estrella y SOLID.
"""

import os
import sys

# Agregar el directorio actual al path de Python para resolución correcta de módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.application.pipeline import RefrigerantETLPipeline

def main():
    print("=" * 60)
    print(" PIPELINE ETL: GASES REFRIGERANTES (SOLID & STAR SCHEMA)")
    print("=" * 60)
    
    # Rutas relativas del proyecto
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "data", "processed")
    web_data_dir = os.path.join(base_dir, "web", "data")
    
    # Instanciar y ejecutar el pipeline
    # Por defecto usa 'fallback' que contiene la rica base de datos termodinámica de 55 gases
    pipeline = RefrigerantETLPipeline(
        output_dir=output_dir,
        web_data_dir=web_data_dir,
        reader_type="fallback"
    )
    
    try:
        pipeline.run()
        print("\n[OK] Proceso completado exitosamente.")
        print("[OK] Archivos CSV relacionales del modelo estrella generados en: data/processed/")
        print("[OK] Archivo JSON de analitica unificado generado en: web/data/refrigerants_dashboard.json")
        print("[OK] Reporte EDA en formato Markdown generado en: data/processed/eda_report.md")
    except Exception as e:
        print(f"\n[ERROR] Error durante la ejecucion del pipeline: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
