"""
Script para parchar 'src/infrastructure/readers.py' añadiendo el campo 'true_replacement'
técnicamente exacto para cada uno de los 55 gases refrigerantes.
"""

import re

def patch():
    # Mapeo de Sustitutos Oficiales recomendados para cada gas
    replacements_map = {
        "R-134a": "R-1234yf (Automotriz) o R-513A (Comercial / Drop-in)",
        "R-600a": "Ninguno (Ya es el estándar ecológico natural en heladeras)",
        "R-290": "Ninguno (Ya es el estándar ecológico natural en botelleros)",
        "R-12": "R-134a (Sustituto Ecológico) o R-437A (Sustituto Drop-in compatible con aceite mineral)",
        "R-401A": "R-437A o R-134a (requiere cambio a aceite POE)",
        "R-401B": "R-437A o R-404A",
        "R-409A": "R-437A",
        "R-413A": "R-437A",
        "R-426A": "R-134a",
        "R-437A": "R-513A o R-1234yf (HFO de bajo GWP)",
        "R-600": "R-600a",
        "R-1234yf": "Ninguno (Es la HFO de ultra bajo GWP definitiva en automoción)",
        "R-415B": "R-134a",
        "R-424A": "R-427A o R-407C",
        "R-513A": "R-290 (Propano natural)",
        "R-22": "R-407C (AC con cambio de aceite POE) o R-438A (Drop-in compatible con aceite mineral)",
        "R-410A": "R-32 (Menor GWP en splits) o R-454B (Chillers de gran escala)",
        "R-404A": "R-448A / R-449A (HFO/HFC de bajo GWP) o R-744 (CO2 natural)",
        "R-407C": "R-32 o R-454B",
        "R-507A": "R-448A / R-449A",
        "R-32": "R-454B o R-290 (Alternativas de menor GWP)",
        "R-407A": "R-448A o R-449A",
        "R-407F": "R-448A",
        "R-422D": "R-427A",
        "R-427A": "R-448A",
        "R-448A": "R-744 (CO2) o R-290 (Sustituto natural definitivo)",
        "R-449A": "R-744 (CO2) o R-290 (Sustituto natural definitivo)",
        "R-452A": "R-454C",
        "R-417A": "R-427A",
        "R-422A": "R-448A",
        "R-438A": "R-427A",
        "R-453A": "R-427A",
        "R-502": "R-404A / R-507A",
        "R-454B": "R-290 (Propano natural)",
        "R-454C": "R-290 (Propano natural)",
        "R-455A": "R-290 o R-744",
        "R-458A": "R-407C",
        "R-466A": "R-32 o R-454B",
        "R-407B": "R-448A",
        "R-717": "Ninguno (Fluido natural definitivo de máxima eficiencia)",
        "R-744": "Ninguno (Fluido natural definitivo de alto rendimiento)",
        "R-123": "R-1233zd (HFO de ultra bajo GWP)",
        "R-124": "R-515B o R-1233zd",
        "R-1233zd": "Ninguno (Es la HFO definitiva para chillers centrífugos de baja presión)",
        "R-1234ze": "R-515B (no inflamable)",
        "R-508B": "R-170 (Etano natural)",
        "R-23": "R-508B o R-170",
        "R-503": "R-508B",
        "R-718": "Ninguno (Agua - Fluido natural absoluto)",
        "R-729": "Ninguno (Aire - Fluido natural absoluto)",
        "R-1150": "R-170",
        "R-1270": "R-290",
        "R-170": "Ninguno (Es el hidrocarburo natural criogénico definitivo)",
        "R-11": "R-1233zd",
        "R-113": "Fluidos fluorados inertes",
        "R-114": "Fluidos fluorados inertes"
    }

    readers_path = "src/infrastructure/readers.py"
    with open(readers_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Procesar el catálogo de raw_data
    # Reemplazaremos cada bloque de diccionario añadiendo la llave true_replacement
    def replacer(match):
        block = match.group(0)
        # Extraer el nombre de ashrae_name
        name_match = re.search(r'"ashrae_name":\s*"([^"]+)"', block)
        if name_match:
            gas_name = name_match.group(1)
            tr = replacements_map.get(gas_name, "Ninguno")
            # Añadir antes del cierre de llave del bloque
            # Buscaremos la línea de alternatives y agregaremos la nueva llave abajo
            if '"alternatives":' in block and '"true_replacement":' not in block:
                # Reemplazar la línea de alternativas añadiendo true_replacement abajo
                new_block = re.sub(
                    r'("alternatives":\s*"[^"]+")',
                    rf'\1, "true_replacement": "{tr}"',
                    block
                )
                return new_block
        return block

    # Expresión regular para encontrar cada diccionario en el catálogo
    # Cada diccionario está delimitado por llaves { ... } y contiene un ashrae_name
    pattern = r'\{[^{}]*"ashrae_name"[^{}]*\}'
    modified_content = re.sub(pattern, replacer, content)

    # También actualizar el desempaque en la línea 748 aproximadamente:
    # r_dict = r.to_dict() y mapear a Refrigerant
    # Verifiquemos cómo se crea el objeto Refrigerant en read_refrigerants():
    # alternatives=d["alternatives"] -> alternatives=d["alternatives"], true_replacement=d["true_replacement"]
    target_instantiation = 'alternatives=d["alternatives"]'
    replacement_instantiation = 'alternatives=d["alternatives"], true_replacement=d["true_replacement"]'
    if target_instantiation in modified_content and replacement_instantiation not in modified_content:
        modified_content = modified_content.replace(target_instantiation, replacement_instantiation)

    with open(readers_path, "w", encoding="utf-8") as f:
        f.write(modified_content)

    print("[OK] readers.py ha sido parchado con el campo true_replacement exitosamente!")

if __name__ == "__main__":
    patch()
