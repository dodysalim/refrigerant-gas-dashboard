import os
import json

def scan_refrigerants():
    base_dir = "images/Gases_Refrigerantes"
    categories = [
        "01_Refrigeracion_Domestica",
        "02_Refrigeracion_Intermedia",
        "03_Refrigeracion_Industrial"
    ]
    
    mapping = {}
    
    for cat in categories:
        cat_path = os.path.join(base_dir, cat)
        if not os.path.exists(cat_path):
            continue
            
        # Listar subcarpetas de gases
        for folder in os.listdir(cat_path):
            folder_path = os.path.join(cat_path, folder)
            if not os.path.isdir(folder_path):
                continue
                
            # Extraer el nombre ASHRAE de la carpeta (e.g. R_134a -> R-134a, R_404A -> R-404A)
            # Reemplazar primer guión bajo por guión medio, o buscar el patrón R_[0-9]+[a-zA-Z]*
            parts = folder.split('_')
            ashrae_raw = parts[0] + "_" + parts[1] # e.g. R_134a
            ashrae_name = ashrae_raw.replace('_', '-') # e.g. R-134a
            
            # Buscar archivos de imagen en la carpeta
            images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            
            if images:
                # Tomar la primera imagen encontrada
                # Preferir nombres más cortos o limpios si es posible, o solo la primera
                first_img = sorted(images)[0]
                
                # Guardar la ruta relativa desde la carpeta base del dashboard
                # En streamlit, la ruta es relative a la raíz: images/Gases_Refrigerantes/...
                # En JS, la ruta es relative a web: images/Gases_Refrigerantes/...
                streamlit_path = f"images/Gases_Refrigerantes/{cat}/{folder}/{first_img}"
                web_path = f"images/Gases_Refrigerantes/{cat}/{folder}/{first_img}"
                
                mapping[ashrae_name] = {
                    "streamlit": streamlit_path,
                    "web": web_path,
                    "folder": folder,
                    "img_name": first_img
                }
                
    # Imprimir resumen de mapeos encontrados
    print(f"Total gases mapeados con éxito: {len(mapping)}/55")
    
    # Escribir el mapeo a un archivo JSON para leerlo en el pipeline o dashboards
    with open("data/refrigerants_images_map.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    print("Mapeo guardado exitosamente en data/refrigerants_images_map.json")

if __name__ == "__main__":
    scan_refrigerants()
