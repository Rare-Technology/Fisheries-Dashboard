from dash import dcc, html
import datetime
from mod_dataworld import maa, all_data
from utils_plot import (
    get_catch_data, make_catch_fig,
    get_cpue_value_data, make_cpue_value_fig,
    get_length_data, make_length_fig,
    get_composition_data, make_composition_fig
)
# choose start and end dates to initially show the past 6 months of data
end_date = all_data['date'].max()
if end_date.month >= 6:
    start_date = datetime.date(end_date.year, end_date.month - 5, 1)
else:
    start_date = datetime.date(end_date.year - 1, end_date.month + 7, 1)

init_data = all_data.query(
    "ma_id.isin(list(@maa['ma_id'])) & \
    @start_date <= date & \
    date <= @end_date"
)

catch_data = get_catch_data(init_data)
catch_fig = make_catch_fig(catch_data)
catch_plot = dcc.Graph(id = 'catches-plot', figure = catch_fig)

cpue_value_data = get_cpue_value_data(init_data)
cpue_value_fig = make_cpue_value_fig(cpue_value_data)
cpue_value_plot = dcc.Graph(id = 'cpue-value-plot', figure = cpue_value_fig)

### Uncomment once these functions are written out
length_data = get_length_data(init_data)
length_fig = make_length_fig(length_data)
length_plot = dcc.Graph(id = 'length-plot', figure = length_fig)
#
# composition_data = get_composition_data(init_data)
# composition_fig = make_composition_fig(composition_data)
# composition_plot = dcc.Graph(id = 'composition-plot', figure = composition_fig)

update_button = html.Button(children = 'Apply filters', className = "btn btn-primary")

plot_UI = html.Div([
    update_button,
    html.Br(),
    html.Br(),
    catch_plot,
    html.Br(),
    cpue_value_plot,
    html.Br(),
    length_plot,
    # html.Br(),
    # composition_plot
], style = {'width': '49%', 'float': 'right', 'display': 'inline-block', 'height': '600px', 'overflow-y': 'scroll'}
)
