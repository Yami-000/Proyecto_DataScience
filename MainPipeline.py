"""Main pipeline para ejecutar toda la lógica de extracción y preparación de datos.

Este script se ejecuta desde la raíz del proyecto y genera:
- dataset_random_gold_timeline.json
- dataset_team_metrics_early_<EARLY_GAME_MINUTE>min.csv
"""
from __future__ import annotations
from PipeLine_API_Riot.UsuarioRandom.mainRandom import run_pipeline_random
from PipeLine_API_Riot.UsuarioRandom.configRandom import SETTINGS
from PipeLine_API_Riot.data_processor_early import build_early_team_dataset
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir / 'PipeLine_API_Riot' / 'UsuarioRandom'))
sys.path.insert(0, str(root_dir / 'PipeLine_API_Riot'))

def run_main_pipeline() -> None:
    minute = int(SETTINGS.get('EARLY_GAME_MINUTE', 10))
    json_path = root_dir / 'PipeLine_API_Riot' / 'dataset_random_gold_timeline.json'
    team_output = root_dir / 'PipeLine_API_Riot' / f'dataset_team_metrics_early_{minute}min.csv'

    print('=== Iniciando MainPipeline RANDOM ===')
    print(f'1) Descargando partidas random + timelines (minuto {minute})...')
    run_pipeline_random()

    print('2) Preparando dataset de métricas early-game...')
    build_early_team_dataset(
        input_path=json_path,
        output_path=team_output,
    )

    print('=== MainPipeline completado ===')
    print(f'- JSON de partidas: {json_path}')
    print(f'- CSV temprano: {team_output}')


if __name__ == '__main__':
    run_main_pipeline()