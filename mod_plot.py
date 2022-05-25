from dash import dcc, html
import datetime
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from copy import deepcopy
from mod_dataworld import QUERY_ID, HEADERS, get_data, maa, all_data
from mod_filters import country_input, snu_input, lgu_input, maa_input

# choose start and end dates to initially show the past 6 months of data
end_date = all_data['date'].max()
if end_date.month >= 6:
    start_date = datetime.date(end_date.year, end_date.month - 5, 1)
else:
    start_date = datetime.date(end_date.year - 1, end_date.month + 7, 1)

catch_data = all_data.query(
    "ma_id.isin(list(@maa['ma_id'])) & \
    @start_date <= date & \
    date <= @end_date"
).loc[:,
    ['yearmonth', 'weight_mt']
].groupby(
    by = ['yearmonth']
).sum().reset_index()

cpue_value_data = all_data.query(
    "ma_id.isin(list(@maa['ma_id'])) & \
    @start_date <= date & \
    date <= @end_date"
).assign(
    weight_kg = lambda x: 1000*x['weight_mt']
).loc[:, [
    'date',
    'yearmonth',
    'fisher_id',
    'ma_id', # restructure ma filtering to use id's -> use less memory, increase speed?
    'fishbase_id',
    'weight_kg',
    'total_price_usd'
]].groupby(
    by = ['yearmonth', 'date', 'fisher_id', 'ma_id', 'fishbase_id'],
    dropna = False # do not remove rows where one of the grouping variables is NA
).sum().groupby(
    by = ['yearmonth'],
).agg(
    avg_cpue_kg_trip = ('weight_kg', 'median'), # numbers differ slightly from old dashboard bc the query it pulls from uses SQL's APPROX_MEDIAN
    ste_cpue_kg_trip = ('weight_kg', 'sem'), # DataFrame.std() uses bias corrected stddev, pd.std does not
    avg_catch_value_usd = ('total_price_usd', 'median'),
    ste_catch_value_usd = ('total_price_usd', 'sem')
).reset_index()

catch_fig = px.bar(catch_data, x = 'yearmonth', y = 'weight_mt')
catch_plot = dcc.Graph(id = 'catches-plot', figure = catch_fig)

cpue_value_fig = make_subplots(specs = [[{'secondary_y': True}]])
cpue_value_fig.add_trace(
    go.Scatter(x = cpue_value_data['yearmonth'], y = cpue_value_data['avg_cpue_kg_trip']),
    secondary_y = False
)
cpue_value_fig.add_trace(
    go.Scatter(x = cpue_value_data['yearmonth'], y = cpue_value_data['avg_catch_value_usd']),
    secondary_y = True
)
cpue_value_plot = dcc.Graph(id = 'cpue-value-plot', figure = cpue_value_fig)

# catch_plot_div = html.Div(
#     [html.Label("Total Catch per Month (metric tons)"), catch_plot]
# )
# cpue_value_plot_div = html.Div(
#     [html.Label("Average CPUE and average catch value"), cpue_value_plot]
# )

update_button = html.Button(children = 'Apply filters')

plot_UI = html.Div([
    update_button,
    html.Br(),
    catch_plot,
    html.Br(),
    cpue_value_plot
], style = {'width': '49%', 'float': 'right', 'display': 'inline-block'})
