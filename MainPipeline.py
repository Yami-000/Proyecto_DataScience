"""Main pipeline para ejecutar toda la lógica de extracción y preparación de datos.

Este script se ejecuta desde la raíz del proyecto y genera:
- dataset_specific_user.json
- dataset_players.csv
- dataset_team_metrics.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir / '1_PipeLine_API_Riot' / 'UsuarioPersonalizado'))
sys.path.insert(0, str(root_dir / '1_PipeLine_API_Riot'))

from UsuarioPersonalizado.mainUP import run_pipeline
from UsuarioPersonalizado.configUP import SETTINGS
from data_processor import build_dataset


def run_main_pipeline() -> None:
    json_path = root_dir / '1_PipeLine_API_Riot' / 'dataset_specific_user.json'
    players_output = root_dir / '1_PipeLine_API_Riot' / 'dataset_players.csv'
    team_output = root_dir / '1_PipeLine_API_Riot' / 'dataset_team_metrics.csv'

    print('=== Iniciando MainPipeline ===')
    print('1) Descargando partidas del usuario específico...')
    run_pipeline()

    print('2) Preparando datasets para análisis...')
    build_dataset(
        input_path=json_path,
        target_name=SETTINGS['TARGET_NAME'],
        target_tag=SETTINGS['TARGET_TAG'],
        players_output=players_output,
        team_output=team_output,
        eda_output=None,
    )

    print('=== MainPipeline completado ===')
    print(f'- JSON de partidas: {json_path}')
    print(f'- CSV de jugadores: {players_output}')
    print(f'- CSV de métricas de equipo: {team_output}')


if __name__ == '__main__':
    run_main_pipeline()
