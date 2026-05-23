# PipeLine_API_Riot

Pipeline de procesamiento de datos para League of Legends usando la API de Riot.

## Objetivo

Este proyecto extrae datos de partidas de `MATCH-V5`, identifica el equipo aliado del usuario objetivo (`Vanitas`), y convierte esos datos en un formato plano apto para análisis y modelos de machine learning.

## Estructura principal

- `data_processor.py`: pipeline modular que carga un JSON de partidas, selecciona los 5 jugadores del equipo aliado del usuario objetivo, limpia los datos y genera un CSV de jugadores y otro de métricas de equipo.
- `feature_factory.py`: funciones auxiliares para extracción de features y análisis de correlación.
- `mainUP.py`, `riot_engineUP.py`, `configUP.py`: lógica de descarga de datos de la API de Riot y configuración para el modo de usuario personalizado.
- `dataset_specific_user.json`: dataset de partidas descargado desde la API de Riot.

## Uso

1. Coloca `dataset_specific_user.json` en la raíz del proyecto.
2. Ejecuta:

```bash
python data_processor.py --input dataset_specific_user.json --players-output dataset_players.csv --team-output dataset_team_metrics.csv
```

3. Para omitir la generación de gráficos de EDA:

```bash
python data_processor.py --input dataset_specific_user.json --no-eda
```

## Salidas

- `dataset_players.csv`: datos a nivel de jugador para el equipo aliado.
- `dataset_team_metrics.csv`: métricas agregadas del equipo aliado por partida.
- `eda_outputs/`: gráficos de análisis exploratorio si no se usa `--no-eda`.

## Requisitos

- Python 3.10+ (probado con 3.14)
- Paquetes:
  - `pandas`
  - `numpy`
  - `matplotlib`
  - `seaborn`

## Consideraciones

- El pipeline asume que el JSON de entradas está en formato MATCH-V5 de Riot.
- El usuario objetivo se identifica por `summonerName` o por `riotIdGameName`+`riotIdTagline`.
- El script está diseñado para extraer únicamente el equipo aliado de la cuenta objetivo y preparar datos listos para modelos de clasificación de win/loss.
