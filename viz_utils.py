import os
# import flet
# from flet import *
import numpy as np
import pandas as pd
import altair as alt

from constants import *

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

def make_combined_frame_filtered(disaster_data_loc, temperature_data_loc, begin_date, end_date, disaster_type):
    begin_year, begin_month, begin_day = [int(i) for i in begin_date.split('-')]
    end_year, end_month, end_day = [int(i) for i in end_date.split('-')]

    data_df = pd.read_csv(disaster_data_loc, index_col=0)
    data_df['date'] = pd.to_datetime(data_df[['year', 'month']].assign(DAY=1))
    fema_df = data_df[['date','incident_type','disaster_number','state_disaster','average_temp']].drop_duplicates('disaster_number', keep='first')
    fema_df = fema_df.loc[(begin_date <= data_df['date']) & (data_df['date'] < end_date)]
    fema_df['year'] = pd.DatetimeIndex(fema_df['date']).year

    # All is a special case to include all disasters
    if disaster_type != 'All':
        fema_df = fema_df.loc[(fema_df['incident_type'] == disaster_type)]

    temp_df = pd.read_csv(temperature_data_loc, index_col=0)
    temp_df['date'] = pd.to_datetime(data_df[['year', 'month']].assign(DAY=1))
    temp_year_df = temp_df.groupby('year', as_index=False).mean().drop(columns='month')
    temp_year_df = temp_year_df[['year', 'average_temp']]

    # merged dataset should already subsetted the disaster types
    fema_temp_years_df = pd.merge(fema_df, temp_year_df, how='outer')
    fema_temp_years_df = fema_temp_years_df.loc[(begin_year <= fema_temp_years_df['year']) & (fema_temp_years_df['year'] < end_year)]
    return fema_df

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

def make_search_chart(raw_data,
                        incident,
                        height,
                        width,
                        json=False):
    dataset_1 = make_frame(raw_data)
    dataset_1 = state_summary_frame(dataset_1, incident)

    from vega_datasets import data
    states = alt.topo_feature(data.us_10m.url, 'states')
    base = alt.Chart(states).mark_geoshape(fill='lightgray', stroke='white')

    chart = alt.Chart(states).mark_geoshape(stroke='black').encode(
        color = alt.Color('count:Q', scale=alt.Scale(scheme='yelloworangered')),
        tooltip=["state:N", "count:Q"]
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(dataset_1, 'id', list(dataset.columns))
    ).properties(
        width=width,
        height=height,
        title=f'Count of {incident} FEMA Reports'
    ).project('albersUsa')

    if json:
        return (base + chart).to_json()
    return (base + chart).show()

def make_deepdive_chart(domain,
                        height,
                        width,
                        disaster_type="Hurricane",
                        json=False,
                        ):
    source = make_combined_frame_filtered(disaster_data_loc=DATASET,
                                        temperature_data_loc=TEMPERATURE_DATASET,
                                        begin_date=domain[0],
                                        end_date=domain[1],
                                        disaster_type=disaster_type)

    # Base encoding the X-axis
    base = alt.Chart(source).encode(
        x = alt.X('date:T', title='Year', scale=alt.Scale(domain=domain))
    ).properties(
        title=f'Average Temp and {disaster_type}',
        width=width,
        height=height
    )

    # Line chart for average temperatures
    temperatures = base.mark_line(color="lightgray", strokeWidth=1).encode(
        y = alt.Y('average(average_temp):Q', title='Average Temperature (deg. F)')
    )

    # Regression line for average temperatures
    temp_regression = temperatures + temperatures.transform_regression('date','average_temp').mark_line(color='red').encode(
        y = alt.Y('average(average_temp):Q', axis=None)
    )

    # Stacked bar chart for top 3 incidents
    disasters = base.mark_bar().encode(
        y = alt.Y('count(incident_type):Q', title='Number of Hurricanes'),
        color = alt.Color('incident_type:N', title='Incident', scale=alt.Scale(scheme='category10'))
    )

    # Graph containing actual data only (using independent scales)
    temp_disaster = (temperatures + disasters).resolve_scale(y='independent')
    if json:
        return (temp_disaster + temp_regression).to_json()
    return (temp_disaster + temp_regression)

state_id_map = get_census_ansi_codes()
dataset = make_frame(DATASET)
dataset = state_summary_frame(dataset)

def get_unique_disaster_types():
    return ['All'] + sorted(make_frame(DATASET).incident.unique())

def determine_chart_dimensions(args):
    width = round(int(args.get('width'))*WIDTH_MULTIPLIER)
    height = round(int(args.get('height'))*HEIGHT_MULTIPLIER)
    return width, height
# def main(page):
#     def btn_click(e):
#         if not txt_name.value:
#             txt_name.error_text = "Enter a Disaster"
#             page.update()
#         else:
#             name = txt_name.value
#             name = name.lower()
#             page.clean()
#             make_chart(DATASET, name)
#             page.add(Text(f"Showing {name}!"))
#
#     txt_name = TextField(label="Enter a Disaster")
#
#     page.add(txt_name, ElevatedButton("Explore!", on_click=btn_click))

# if __name__ == '__main__':
#      #state_id_map = get_census_ansi_codes()
#      #dataset = make_frame(DATASET)
#      #dataset = state_summary_frame(dataset)
#      #make_chart(DATASET, 'earthquake')
#     flet.app(target=main, view=flet.WEB_BROWSER)
