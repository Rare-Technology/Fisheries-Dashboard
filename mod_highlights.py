from dash import dcc, html
from utils_highlights import (
    create_card, get_total_weight, get_total_value, get_total_trips,
    get_fishers, get_female, get_buyers
)
from mod_dataworld import init_data

biomass_card = create_card(get_total_weight(init_data), "Total weight (mt)")
value_card = create_card("456.2K", "Total value (USD)")
trips_card = create_card("2.3K", "Total #trips")
fishers_card = create_card("1.5K", "Fishers recorded")
female_card = create_card("7", "Total female fishers")
buyers_card = create_card("234", "Total buyers")

highlights_div = html.Div(
    className = "card-group",
    id = "highlights-container",
    children = [
        biomass_card,
        value_card,
        trips_card,
        fishers_card,
        female_card,
        buyers_card
    ]
)
