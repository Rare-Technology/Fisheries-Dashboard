from dash import dcc, html
import datetime
from utils_plot import (
    make_catch_fig,
    make_cpue_value_fig,
    make_length_fig,
    make_composition_fig
)

def start_plot(plot_data):
    catch_fig = make_catch_fig(plot_data["catch"])
    catch_plot = dcc.Graph(
        id = 'catches-plot',
        className = "mb-4",
        figure = catch_fig,
        config = {
            'modeBarButtonsToRemove': ['select', 'lasso2d'],
            'displaylogo': False
        }
    )

    cpue_value_fig = make_cpue_value_fig(plot_data["cpue-value"])
    cpue_value_plot = dcc.Graph(
        id = 'cpue-value-plot',
        className = "mb-4",
        figure = cpue_value_fig,
        config = {
            'modeBarButtonsToRemove': ['select', 'lasso2d'],
            'displaylogo': False
        }
    )

    length_fig = make_length_fig(plot_data["length"])
    length_plot = dcc.Graph(
        id = 'length-plot',
        # className = "pretty_container",
        figure = length_fig,
        config = {
            'modeBarButtonsToRemove': ['select', 'lasso2d'],
            'displaylogo': False
        }
    )

    composition_fig = make_composition_fig(plot_data["composition"])
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

    return plot_div
