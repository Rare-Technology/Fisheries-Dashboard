from dash import dcc, html
from utils_highlights import (
    create_card, get_total_weight, get_total_value, get_total_trips,
    get_fishers, get_female, get_buyers, get_highlights_data
)

def start_highlights(init_data):
    highlights_data = get_highlights_data(init_data)

    biomass_card = create_card(highlights_data.loc[0, 'weight'], "Catch weight (tonnes)")
    value_card = create_card(highlights_data.loc[0, 'value'], "Catch value (USD)")
    trips_card = create_card(highlights_data.loc[0, 'trips'], "Fishing trips")
    fishers_card = create_card(highlights_data.loc[0, 'fishers'], "Fishers recorded")
    buyers_card = create_card(highlights_data.loc[0, 'buyers'], "Buyers")
    female_card = create_card(highlights_data.loc[0, 'female buyers'], "Female buyers")

    highlights_div = html.Div(
        className = "card-group",
        id = "highlights-container",
        children = [
            biomass_card,
            value_card,
            trips_card,
            fishers_card,
            buyers_card,
            female_card
        ]
    )

    return highlights_div, highlights_data
