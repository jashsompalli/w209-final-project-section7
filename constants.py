import os
from pathlib import Path
import altair as alt
from vega_datasets import data

# states geo map
STATES = alt.topo_feature(data.us_10m.url, 'states')
CWD = os.getcwd()
# Data paths
DATASET = f'{CWD}/data/fema_disaster_with_noaa_monthly_temp_combined.csv'# if os.getenv('ENVIRONMENT') == 'PROD' else Path('./data/fema_disaster_with_noaa_monthly_temp_combined.csv')
TEMPERATURE_DATASET =  f'{CWD}/data/average_monthly_temperature_by_state_1950-2022.csv'# if os.getenv('ENVIRONMENT') == 'PROD' else Path('./data/average_monthly_temperature_by_state_1950-2022.csv')

WIDTH_MULTIPLIER = .85 # chart should take up WIDTH_MULTIPLIER*100 % of the viewport width
HEIGHT_MULTIPLIER = .5 # chart should take up HEIGHT_MULTIPLIER*100 % of the viewport height
