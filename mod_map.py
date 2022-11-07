import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, html
from utils_map import get_map_data, make_map, mapbox_url

def start_map(data, comm):
    map_data = get_map_data(data, comm)

    fig = make_map(map_data, mapbox_url)

    map = dcc.Graph(
        id = 'fish-map',
        figure = fig,
        config = {'displayModeBar': False},
        style = {"height": "calc(100vh)"}
    )
    map_div = html.Div(
        [map],
        style = {
            "z-index": "1",
            "width": "100%",
            "height": "100%"
        }
    )

    return map_div
