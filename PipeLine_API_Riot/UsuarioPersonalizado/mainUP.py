# mainUP.py
from riot_engineUP import get_puuid_by_riot_id, get_matches_data
from configUP import SETTINGS
from pathlib import Path
import json

def run_pipeline():
    all_matches_dataset = []
    name = SETTINGS['NAME_PLAYER']
    tag = SETTINGS['TAG_PLAYER']
    limit = SETTINGS['NUMBER_MATCHES']

    print(f"--- MODO USUARIO ESPECÍFICO: {name}#{tag} ---")

    puuid = get_puuid_by_riot_id(name, tag)
    if not puuid:
        print("ERROR: No se pudo obtener el PUUID del usuario específico.")
        return

    print(f"PUUID encontrado. Descargando {limit} partidas...")
    all_matches_dataset.extend(get_matches_data(puuid, limit))

    output_dir = Path(__file__).resolve().parent.parent
    output_path = output_dir / "dataset_specific_user.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_matches_dataset, f)

    print(f"--- Proceso finalizado. Archivo creado: {output_path} ---")

if __name__ == "__main__":
    run_pipeline()