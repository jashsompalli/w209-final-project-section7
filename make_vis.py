import os
import flet
from flet import *
import numpy as np
import pandas as pd
import altair as alt
from pathlib import Path
from vega_datasets import data

STATES = alt.topo_feature(data.us_10m.url, 'states')

DATASET = Path('./fema_disaster_with_noaa_monthly_temp_combined.csv')

def make_frame(data_loc):
    '''
        Make some changes to the raw data in order to make the column names
        a bit more manageable for analysis. Return the frame that we need.
        Input -> location of csv file.
        Output -> Cleaned dataframe + One computed column
    '''
    data = pd.read_csv(data_loc, low_memory = False)
    columns_to_keep = [
            'declaration_type', 'fy_declared',
            'incident_type', 'declaration_title', 'State',
            'average_temp', 'monthly_mean_from_1901_to_2000',
            'centroid_lon', 'centroid_lat'
            ]
    data = data[columns_to_keep]
    data = data.rename(columns = {
        'declaration_type' : 'type',
        'incident_type' : 'incident',
        'declaration_title' : 'title',
        'State' : 'state',
        'fy_declared' : 'year',
        'monthly_mean_from_1901_to_2000' : 'historical_temps',
        'centroid_lon' : 'longitude',
        'centroid_lat' : 'latitude'
        })
    data = data.dropna()

    data['diff_current_hist'] = data['average_temp'] - data['historical_temps']
    data['title'] = data['title'].apply(lambda x: x.lower())
    return data
    
def get_census_ansi_codes():
    ansi = pd.read_csv('https://www2.census.gov/geo/docs/reference/state.txt', sep='|')
    ansi.columns = ['id', 'abbr', 'state', 'statens']
    ansi = ansi[['id', 'abbr', 'state']]
    state_id_map = dict(zip(ansi['state'].tolist(), ansi['id'].tolist()))
    return state_id_map

def state_summary_frame(data, disaster = 'all'):
    if disaster == 'all':
        out = pd.DataFrame(data['state'].value_counts()).reset_index()
        out = out.rename(columns = {
            'index' : 'state',
            'state' : 'count'
            })
        out['id'] = out['state'].apply(lambda x: state_id_map[x])
        return out
    else:
        data = data[data['title'].str.contains(disaster)]
        out = pd.DataFrame(data['state'].value_counts()).reset_index()
        out = out.rename(columns = {
            'index' : 'state',
            'state' : 'count'
            })
        out['id'] = out['state'].apply(lambda x: state_id_map[x])
        return out

def make_chart(raw_data, incident):
    dataset_1 = make_frame(raw_data)
    dataset_1 = state_summary_frame(dataset_1, incident)

    from vega_datasets import data
    states = alt.topo_feature(data.us_10m.url, 'states')

    base = alt.Chart(states).mark_geoshape(fill='lightgray', stroke='white')

    chart = alt.Chart(states).mark_geoshape(stroke='black').encode(
        color = alt.Color('count:Q', scale=alt.Scale(scheme='yelloworangered'))
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(dataset_1, 'id', list(dataset.columns))
    ).properties(
        width=1000,
        height=500,
        title=f'Count of {incident} FEMA Reports'
    ).project('albersUsa')

    return (base + chart).show()

state_id_map = get_census_ansi_codes() 
dataset = make_frame(DATASET)
dataset = state_summary_frame(dataset)

def main(page):
    def btn_click(e):
        if not txt_name.value:
            txt_name.error_text = "Enter a Disaster"
            page.update()
        else:
            name = txt_name.value
            name = name.lower()
            page.clean()
            make_chart(DATASET, name)
            page.add(Text(f"Showing {name}!"))

    txt_name = TextField(label="Enter a Disaster")

    page.add(txt_name, ElevatedButton("Explore!", on_click=btn_click))

if __name__ == '__main__':
     #state_id_map = get_census_ansi_codes()
     #dataset = make_frame(DATASET)
     #dataset = state_summary_frame(dataset)
     #make_chart(DATASET, 'earthquake')
    flet.app(target=main, view=flet.WEB_BROWSER)

    

