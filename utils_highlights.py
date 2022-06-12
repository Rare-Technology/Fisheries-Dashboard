from dash import html
from mod_dataworld import fishers_data, init_data
from utils_map import format_number

def create_card(value, title):
    return html.Div(
        className = "card mx-2",
        children = [
            html.Div(
                className = "card-body",
                children = [
                    html.H5(value, className = "card-title"),
                    html.H6(title, className = "card-subtitle")
                ]
            )
        ]
    )

def get_total_weight(data):
    total_weight = data['weight_mt'].sum()
    out = format_number(total_weight)
    return out

def get_total_value(data):
    pass

def get_total_trips(data):
    pass

def get_fishers(data):
    pass

def get_female(data):
    pass

def get_buyers(data):
    pass
