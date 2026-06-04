"""Main pipeline para ejecutar toda la lógica de extracción y preparación de datos.

Este script se ejecuta desde la raíz del proyecto y genera:
- dataset_random_gold.json
- dataset_playersXpartida.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir / 'PipeLine_API_Riot' / 'UsuarioRandom'))
sys.path.insert(0, str(root_dir / 'PipeLine_API_Riot'))

from PipeLine_API_Riot.UsuarioRandom.mainRandom import run_pipeline_random
from PipeLine_API_Riot.data_processor_random import build_dataset


def run_main_pipeline() -> None:
    json_path = root_dir / 'PipeLine_API_Riot' / 'dataset_random_gold.json'
    players_output = root_dir / 'PipeLine_API_Riot' / 'dataset_playersXpartida.csv'

    print('=== Iniciando MainPipeline RANDOM ===')
    print('1) Descargando partidas random...')
    run_pipeline_random()

    print('2) Preparando dataset players por partida...')
    build_dataset(
        input_path=json_path,
        output_path=players_output,
    )

    print('=== MainPipeline completado ===')
    print(f'- JSON de partidas: {json_path}')
    print(f'- CSV de jugadores por partida: {players_output}')


if __name__ == '__main__':
    run_main_pipeline()