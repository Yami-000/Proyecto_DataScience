"""
PipelineRandom.py - Orquestador masivo para Liga Aleatoria (Extracción + Procesamiento)
"""
from __future__ import annotations

import sys
from pathlib import Path

# Configuración de rutas
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir / 'PipeLine_API_Riot' / 'UsuarioRandom'))
sys.path.insert(0, str(root_dir / 'PipeLine_API_Riot'))

# 1. Importamos el extractor (Fase 1)
from PipeLine_API_Riot.UsuarioRandom.mainRandom import run_pipeline_random

# 2. Importamos el procesador (Fase 2) 
from PipeLine_API_Riot.data_processor_random import build_dataset 


def run_random_pipeline() -> None:
    # El JSON se guarda en PipeLine_API_Riot
    json_path = root_dir / 'PipeLine_API_Riot' / 'dataset_random_gold.json'
    
    # Los CSVs se guardan en la carpeta UsuarioRandom
    players_output = root_dir / 'PipeLine_API_Riot' / 'UsuarioRandom' / 'dataset_players_random.csv'
    team_output = root_dir / 'PipeLine_API_Riot' / 'UsuarioRandom' / 'dataset_team_metrics_random.csv'

    print('=== Iniciando Pipeline Aleatorio Completo ===')
    
    print('\n[Fase 1] Descargando partidas JSON masivas...')
    # CORRECCIÓN: Le quitamos el '#' a la siguiente línea para que SÍ descargue los datos
    run_pipeline_random() 
    
    print('\n[Fase 2] Procesando partidas y generando Datasets (CSVs)...')
    # Ejecutamos el procesador que aplanará el JSON a CSVs
    build_dataset(
        input_path=json_path,
        players_output=players_output,
        team_output=team_output,
        eda_output=None
    )
    
    print('\n=== Pipeline Random Completado Exitosamente ===')
    print(f'- CSV de jugadores listo en: {players_output}')
    print(f'- CSV de equipos (para Machine Learning) listo en: {team_output}')

if __name__ == '__main__':
    run_random_pipeline()