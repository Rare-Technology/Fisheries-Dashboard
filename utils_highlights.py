from dash import html
from utils_map import format_number
import pandas as pd

def create_card(value, title):
    return html.Div(
        className = "card mx-2",
        children = [
            html.Div(
                className = "card-body",
                children = [
                    html.H5(format_number(value), className = "card-title"),
                    html.H6(title, className = "card-subtitle")
                ]
            )
        ]
    )

def get_total_weight(data):
    return data['weight_mt'].sum()

def get_total_value(data):
    return data['total_price_usd'].sum()

def get_total_trips(data):
    # Idea: A buyer may have multiple transactions with a fisher in one day (for each
    # species of fish caught). So one trip can be identified by a fisher on a given day.
    # So to get the total # trips, count the number of unique fishers per day then take the sum
    return data.groupby('date')['fisher_id'].nunique().sum()

def get_fishers(data):
    return data['fisher_id'].nunique()


def get_female(data):
    return data.query("gender.isin(['f', 'F'])")['buyer_id'].nunique()


def get_buyers(data):
    return data['buyer_id'].nunique()

def get_highlights_data(data):
    return pd.DataFrame({
        'weight': [get_total_weight(data)],
        'value': [get_total_value(data)],
        'trips': [get_total_trips(data)],
        'fishers': [get_fishers(data)],
        'female buyers': [get_female(data)],
        'buyers': [get_buyers(data)]
    })
