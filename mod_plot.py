from dash import dcc, html
import datetime
from mod_dataworld import maa, init_data
from utils_plot import (
    get_catch_data, make_catch_fig,
    get_cpue_value_data, make_cpue_value_fig,
    get_length_data, make_length_fig,
    get_composition_data, make_composition_fig
)

catch_data = get_catch_data(init_data)
catch_fig = make_catch_fig(catch_data)
catch_plot = dcc.Graph(id = 'catches-plot', figure = catch_fig)

cpue_value_data = get_cpue_value_data(init_data)
cpue_value_fig = make_cpue_value_fig(cpue_value_data)
cpue_value_plot = dcc.Graph(id = 'cpue-value-plot', figure = cpue_value_fig)

length_data = get_length_data(init_data)
length_fig = make_length_fig(length_data)
length_plot = dcc.Graph(id = 'length-plot', figure = length_fig)

composition_data = get_composition_data(init_data)
composition_fig = make_composition_fig(composition_data)
composition_plot = dcc.Graph(id = 'composition-plot', figure = composition_fig)

update_button = html.Button(children = 'Apply filters', className = "btn btn-primary")

plot_UI = html.Div([
    update_button,
    html.Br(),
    html.Br(),
    html.Div([
        composition_plot,
        catch_plot
    ], style = {'width': '49%', 'float': 'left'}),
    html.Div([
        cpue_value_plot,
        length_plot
    ], style = {'width': '49%', 'float': 'right'})
], style = {'width': '100%', 'height': '400px'}
)
