from dash import dcc, html
import datetime
import plotly.express as px
from copy import deepcopy
from mod_dataworld import QUERY_ID, HEADERS, get_data, maa, all_data
from mod_filters import country_input, snu_input, lgu_input, maa_input

plot_data = all_data.query(
    "ma_name.isin(list(@maa['ma_name']))"
).loc[:,
    ['yearmonth', 'weight_mt']
].groupby(
    by = ['yearmonth']
).sum().reset_index()

fig = px.bar(plot_data, x = 'yearmonth', y = 'weight_mt')

plot = dcc.Graph(id = 'catches-plot', figure = fig)

update_button = html.Button(children = 'Apply filters')

plot_div = html.Div(
    [html.Label("Catches plot"), plot]
)

plot_UI = html.Div([
    update_button,
    html.Br(),
    plot_div
], style = {'width': '49%', 'float': 'right', 'display': 'inline-block'})
