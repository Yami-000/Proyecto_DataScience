from riot_engineUP import get_puuid_by_riot_id, get_matches_data
from configUP import SETTINGS
import json

name = SETTINGS['TARGET_NAME']
tag = SETTINGS['TARGET_TAG']
print(f"Test quick fetch para {name}#{tag}")
puuid = get_puuid_by_riot_id(name, tag)
if not puuid:
    print('No se encontró puuid')
    exit(1)

matches = get_matches_data(puuid, count=5)
print(f'Descargadas {len(matches)} partidas')
with open('dataset_specific_user_small.json', 'w', encoding='utf-8') as f:
    json.dump(matches, f)
print('Archivo creado: dataset_specific_user_small.json')
