import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, html
from utils_map import make_map, mapbox_url

def start_map(map_data, comm):
    fig = make_map(map_data, mapbox_url)

    map = dcc.Graph(
        id = 'fish-map',
        figure = fig,
        config = {'displayModeBar': False},
        style = {"height": "calc(100vh)"}
    )
    legend = html.Div(
        id = "legend",
        children = [
            html.Div(
                className = "line",
                children = [
                    html.Div(className = "box green"),
                    html.Span("Subnational Government")
                ]
            ),
            html.Div(
                className = "line",
                children = [
                    html.Div(className = "box blue"),
                    html.Span("Local Government Unit")
                ]
            ),
            html.Div(
                className = "line",
                children = [
                    html.Div(className = "box red"),
                    html.Span("Established Managed Access Area")
                ]
            ),
            html.Div(
                className = "line",
                children = [
                    html.Div(className = "box grey"),
                    html.Span("Proposed Managed Access Area")
                ]
            ),
            html.Div(
                className = "line",
                children = [
                    html.Div(className = "box yellow"),
                    html.Span("Established Reserve")
                ]
            ),
            html.Div(
                className = "line",
                children = [
                    html.Div(className = "box orange"),
                    html.Span("Proposed Reserve")
                ]
            ),
            html.Div(
                className = "line",
                children = [
                    html.Div(className = "box lightblue"),
                    html.Span("Established Global MPAs")
                ]
            )
        ]
    )

    map_div = html.Div(
        [map, legend],
        style = {
            "z-index": "1",
            "width": "100%",
            "height": "100%"
        }
    )

    return map_div
