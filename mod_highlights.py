from dash import dcc, html
from utils_highlights import (
    create_card, get_total_weight, get_total_value, get_total_trips,
    get_fishers, get_female, get_buyers, get_highlights_data
)
from mod_dataworld import init_data

init_highlights_data = get_highlights_data(init_data)

biomass_card = create_card(init_highlights_data.loc[0, 'weight'], "Total weight (mt)")
value_card = create_card(init_highlights_data.loc[0, 'value'], "Total value (USD)")
trips_card = create_card(init_highlights_data.loc[0, 'trips'], "Total #trips")
fishers_card = create_card(init_highlights_data.loc[0, 'fishers'], "Fishers recorded")
female_card = create_card(init_highlights_data.loc[0, 'female buyers'], "Total female buyers")
buyers_card = create_card(init_highlights_data.loc[0, 'buyers'], "Total buyers")

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
