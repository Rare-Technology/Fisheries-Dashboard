from dash import dcc, html

def create_card(value, title):
    return html.Div(
        className = "card mx-2",
        children = [
            html.Div(
                className = "card-body",
                children = [
                    html.H4(value, className = "card-title"),
                    html.H6(title, className = "card-subtitle")
                ]
            )
        ]
    )

biomass_card = create_card("123", "Total weight (mt)")
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
