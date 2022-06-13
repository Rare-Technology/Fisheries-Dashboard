from dash import html
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
    total_value = data['total_price_usd'].sum()
    out = format_number(total_value)
    return out

def get_total_trips(data):
    # Idea: A buyer may have multiple transactions with a fisher in one day (for each
    # species of fish caught). So one trip can be identified by a fisher on a given day.
    # So to get the total # trips, count the number of unique fishers per day then take the sum
    num_trips = data.groupby('date')['fisher_id'].nunique().sum()
    out = format_number(num_trips)
    return out

def get_fishers(data):
    num_fishers = data['fisher_id'].nunique()
    out = format_number(num_fishers)
    return out

def get_female(data):
    num_female = data.query("gender.isin(['f', 'F'])")['fisher_id'].nunique()
    out = format_number(num_female)
    return out

def get_buyers(data):
    num_buyers = data['buyer_id'].nunique()
    out = format_number(num_buyers)
    return out
