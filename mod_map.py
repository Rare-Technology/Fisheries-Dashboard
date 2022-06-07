import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, html
from mod_dataworld import init_data, maa
from utils_map import get_map_data

map_data = get_map_data(init_data, maa)

# fig = go.Figure(go.Scattermapbox(mode = 'markers', fill = 'toself', marker = {'size': 10, 'color': 'orange'}))
fig = px.scatter_mapbox(map_data, lat = 'ma_lat', lon = 'ma_lon', hover_name = 'ma_name', hover_data = ['weight_mt'])
fig.update_layout(
    mapbox_style = 'white-bg',
    mapbox_layers = [
        {
            'below': 'traces',
            'sourcetype': 'raster',
            'sourceattribution': 'OpenStreetMap',
            'source': ['https://api.mapbox.com/styles/v1/stoyleg/ckog2kkao0o5j1amjvgizilp2/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1Ijoic3RveWxlZyIsImEiOiJjaWZ5ZXN1YXQwMmh4dDBtN2lidWZpb3AwIn0.h_bxYt64qWi6PIBeJ1bqPA']
        }
    ]
)

map = dcc.Graph(id = 'fish-map', figure = fig)
map_UI = html.Div([map])
