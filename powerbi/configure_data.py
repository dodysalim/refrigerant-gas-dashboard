"""Actualiza únicamente el parámetro DataFolder a la carpeta local data."""
import json
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    folder = str(root / "data") + ("\\" if __import__("os").name == "nt" else "/")
    quoted = '"' + folder.replace('"', '""') + '"'
    path = root / "Analytics.SemanticModel" / "definition" / "expressions.tmdl"
    path.write_text('expression DataFolder = ' + quoted + ' meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n\tkind: m\n', encoding="utf-8")
    print("DataFolder configurado:", folder)

if __name__ == "__main__":
    main()
