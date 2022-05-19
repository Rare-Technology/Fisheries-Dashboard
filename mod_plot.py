from dash import dcc, html
import datetime
import plotly.express as px
from copy import deepcopy
from mod_dataworld import QUERY_ID, HEADERS, get_data, maa, all_data
from mod_filters import country_input, snu_input, lgu_input, maa_input

plot_data = all_data.query(
    "ma_name.isin(list(@maa['ma_name']))"
).loc[:,
    ['Date', 'weight_mt']
].groupby(
    by = ['Date']
).sum().reset_index()

fig = px.bar(plot_data, x = 'Date', y = 'weight_mt')

plot = dcc.Graph(id = 'catches-plot', figure = fig)

plot_div = html.Div(children = [
    html.Label("Catches plot"),
    plot
])
