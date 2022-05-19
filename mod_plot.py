from dash import dcc, html
import pandas as pd
import datetime
import plotly.express as px
from mod_dataworld import QUERY_ID, HEADERS, get_data, maa, all_data
from mod_filters import country_input, snu_input, lgu_input, maa_input

filter_data = all_data.query(
    "country.isin(@country_input.value)"
)
filter_data['date'] = filter_data['date'].apply(
    datetime.date.fromisoformat
).sort_values().apply(
    lambda x: datetime.date(x.year, x.month, 1)
)
filter_data = filter_data[['country', 'date', 'weight_mt']].groupby(
    by = ['country', 'date']
).sum().reset_index()

fig = px.bar(filter_data, x = 'date', y = 'weight_mt')
plot = dcc.Graph(id = 'catches-plot', figure = fig)

plot_div = html.Div(children = [
    html.Label("Catches plot"),
    plot
])
