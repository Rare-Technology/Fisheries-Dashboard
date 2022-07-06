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
catch_plot = dcc.Graph(
    id = 'catches-plot',
    className = "mb-4",
    figure = catch_fig,
    config = {
        'modeBarButtonsToRemove': ['select', 'lasso2d'],
        'displaylogo': False
    }
)

cpue_value_data = get_cpue_value_data(init_data)
cpue_value_fig = make_cpue_value_fig(cpue_value_data)
cpue_value_plot = dcc.Graph(
    id = 'cpue-value-plot',
    className = "mb-4",
    figure = cpue_value_fig,
    config = {
        'modeBarButtonsToRemove': ['select', 'lasso2d'],
        'displaylogo': False
    }
)

length_data = get_length_data(init_data)
length_fig = make_length_fig(length_data)
length_plot = dcc.Graph(
    id = 'length-plot',
    # className = "pretty_container",
    figure = length_fig,
    config = {
        'modeBarButtonsToRemove': ['select', 'lasso2d'],
        'displaylogo': False
    }
)

composition_data = get_composition_data(init_data)
composition_fig = make_composition_fig(composition_data)
composition_plot = dcc.Graph(
    id = 'composition-plot',
    className = "mb-4",
    figure = composition_fig,
    config = {
        'displaylogo': False
    }
)

plot_toggle_div = html.Div(
    id = "plots-toggle",
    children = [
        html.H3("Charts", style = {"display": "inline"}),
        html.Span(
            [html.Span(className = "Select-arrow")],
            className = "Select-arrow-zone dropdown-arrow"
        )
    ]
)

plot_displays_div = html.Div(
    id = "plot-displays",
    children = [
        composition_plot,
        catch_plot,
        cpue_value_plot,
        length_plot
    ]
)

plot_div = html.Div(
    id = "plots-container",
    children = [plot_toggle_div, plot_displays_div]
)
