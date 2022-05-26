# Import Libraries
from datetime import datetime
import plotly.graph_objects as go
import requests
import json
import pandas as pd


# Import A350 Dataset & Create List Of Unique A350 HEX Codes (https://opensky-network.org/datasets/metadata/)
a350_data = pd.read_csv("a350_data.csv")
a350 = a350_data['icao24'].tolist()


# Query OpenSky Network Via Rest API
user_name = ''
password = ''
url_data = 'https://'+user_name+':'+password+'@opensky-network.org/api/states/all?'
response = requests.get(url_data).json()


# Load Response Into Data Frame
column_names = ['icao24','callsign','origin_country','time_position','last_contact','long','lat','baro_altitude','on_ground','velocity',       
'true_track','vertical_rate','sensors','geo_altitude','squawk','spi','position_source','dummy']
flight_data = pd.DataFrame(response['states'],columns = column_names)


# Join Datasets To Identify A350s & Tail Details
flight_data_a350 = pd.merge(flight_data, a350_data, on = 'icao24')


# Create Column Containing Relevant A/C Info For The Labels
flight_data_a350['text'] = flight_data_a350['registration'] + ' (' + flight_data_a350['model'] + ') - ' + flight_data_a350['operatorplain']

# Plot Locations Of Each A/C
fig = go.Figure(data=go.Scattergeo(
        lon = flight_data_a350['long'],
        lat = flight_data_a350['lat'],
        text = flight_data_a350['text'],
        mode = 'markers',
        marker = dict(
            size = 8,
            opacity = 0.8,
            reversescale = True,
            symbol = 'circle',
            line = dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            colorscale = 'Aggrnyl',
            cmin = 0,
            color = flight_data_a350['baro_altitude'],
            cmax = flight_data_a350['baro_altitude'].max(),
            colorbar_title="Alititude",
            showscale = False,
            showlegend = False,
        )))

fig.update_layout(
        geo_scope = 'world',
        showscale = False,
        showlegend = False,
        )


# Prepare Dataset For Export
data_export = flight_data_a350[['registration','model','serialnumber','operatorplain','on_ground']]
data_export['serialnumber'] = data_export['serialnumber'].astype(str).apply(lambda x: x.replace('.0',''))
data_export['Export'] = datetime.today().strftime('%d/%m/%Y - %H:%M')
data_export.rename(columns = {'registration': 'A/C', 'model': 'Type', 'operatorplain': 'Operator', 'on_ground': 'Grounded', 'serialnumber': 'MSN'}, inplace=True)


# Export Data
data_export.to_csv('_data/flight_data_a350.csv', index=False)
fig.write_html("_data/flight_data_a350.html")
fig.write_image("flight_data_a350.png", width=1280, height=720)
