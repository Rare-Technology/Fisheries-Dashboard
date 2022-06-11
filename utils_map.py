import plotly.graph_objects as go
import configparser

cfg = configparser.ConfigParser(interpolation = None)
cfg.read('secret.ini')
mapbox_url = cfg.get('mapbox', 'URL')

def get_map_data(data, comm):
    return (
        data.loc[:, [
            'community_id',
            'population',
            'est_fishers',
            'est_buyers',
            'weight_mt',
            'total_price_usd'
        ]].groupby('community_id')
        .sum()
        .reset_index()
        .join(comm[['community_id', 'community_name', 'community_lat', 'community_lon']].set_index('community_id'), on = 'community_id')
        .reset_index(drop = True)
    )

def make_map(map_data, mapbox_url):
    hovertext_list = [
        "Community: {}<br> \
        Population: {}<br> \
        Estimated fishers: {}<br> \
        Estimated buyers: {}<br> \
        Total catch weight (mt): {}<br> \
        Total catch value (USD): {}<br> \
        ".format(comm_name, pop, n_fisher, n_buyer, catch_weight, catch_value) \
        for comm_name, pop, n_fisher, n_buyer, catch_weight, catch_value \
        in map_data[['community_name', 'population', 'est_fishers', 'est_buyers', 'weight_mt', 'total_price_usd']].apply(tuple, axis = 1)
    ]

    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(
        lat = map_data['community_lat'], lon = map_data['community_lon'],
        mode = 'markers',
        marker = go.scattermapbox.Marker(
            size = 15,
            color = '#6fbcc3'
        ),
        hoverinfo = 'none'
    ))
    fig.add_trace(go.Scattermapbox(
        lat = map_data['community_lat'], lon = map_data['community_lon'],
        mode = 'markers',
        marker = go.scattermapbox.Marker(
            size = 10,
            color = '#99f2e8'
        ),
        hoverinfo = 'text',
        hovertext = hovertext_list,
    ))
    fig.update_layout(
        mapbox_style = 'white-bg',
        mapbox_layers = [
            {
                'below': 'traces',
                'sourcetype': 'raster',
                'sourceattribution': 'OpenStreetMap',
                'source': [mapbox_url]
            }
        ],
        showlegend = False,
        margin = {
            't': 0,
            'r': 0,
            'b': 0,
            'l': 0
        },
        height = 600
    )

    return fig
