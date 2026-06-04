"""Pipeline completo para extraer datos en modo RANDOM GOLD.

Flujo:
1. Identificar 100 jugadores de Oro I (configurable)
2. Descargar 100 partidas de cada uno (configurable)
3. Extraer 10 jugadores de cada partida + estadísticas
4. Guardar en dataset_playersXpartida.csv

Salida:
- dataset_random_gold.json (partidas brutas)
- dataset_playersXpartida.csv (10 jugadores × partidas con estadísticas)
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir / 'PipeLine_API_Riot' / 'UsuarioRandom'))
sys.path.insert(0, str(root_dir / 'PipeLine_API_Riot'))

from PipeLine_API_Riot.UsuarioRandom.mainRandom import run_pipeline_random
from PipeLine_API_Riot.data_processor_random import build_dataset


def main():
    json_path = root_dir / 'PipeLine_API_Riot' / 'dataset_random_gold.json'
    csv_path = root_dir / 'PipeLine_API_Riot' / 'UsuarioRandom' / 'dataset_playersXpartida.csv'

    print('=' * 60)
    print('PIPELINE RANDOM GOLD - MODO ALEATORIO')
    print('=' * 60)
    
    print('\nPASO 1: Descargar partidas...')
    run_pipeline_random()

    print('\nPASO 2: Procesar y extraer 10 jugadores por partida...')
    build_dataset(
        input_path=json_path,
        output_path=csv_path
    )

    print('\n' + '=' * 60)
    print('✓ PIPELINE COMPLETADO')
    print('=' * 60)
    print(f'\nResultado: {csv_path}')
    print(f'Estructura: match_id, team_id, summoner_name, champion, kills, deaths, assists, ...')


if __name__ == '__main__':
    main()
