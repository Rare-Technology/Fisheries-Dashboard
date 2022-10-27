import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, html
from mod_dataworld import init_data, comm
from utils_map import get_map_data, make_map, mapbox_url

map_data = get_map_data(init_data, comm)

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
