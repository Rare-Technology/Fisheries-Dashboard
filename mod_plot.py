from dash import dcc, html
import pandas as pd
import plotly.express as px
from mod_dataworld import QUERY_ID, HEADERS, get_query, maa, fish
from mod_filters import country_input, snu_input, lgu_input, maa_input

# There's something like 30k unique fish. Using the whole list always ends in a
# 504 timeout error. DW may still be a bottleneck on dash
sel_fish = list(fish['fishbase_id'].astype('str').unique())[150:500]

catch_params = {
    'ma_ids': ','.join(list(maa['ma_id'].astype('str'))),
    'fishbase_ids': ','.join(sel_fish),
    'start': '2021-01-01',
    'end': '2021-12-31'
}
catch = get_query('total_catch_per_month', 'POST', catch_params)

# Check the prints... for some reason not all months of 2021 are being captured even though
# many tests up to this point showed all months. inconsistent responses from API call
print(catch)
fig = px.bar(catch, x = 'month', y = 'sum_weight_mt')

plot = dcc.Graph(id = 'catches-plot', figure = fig)

plot_div = html.Div(children = [
    html.Label("Catches plot"),
    plot
])
