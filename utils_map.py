import plotly.graph_objects as go
import numpy as np
import os

### Dumb issue... we need the mapbox url which is saved as an environment variable
# On production server (heroku) this is no problem, just call os.environ['MAPBOX_URL']
# On development, my conda env does not export the environment variable correctly.
# This is because of the equals sign. So, the mapbox url is split in two and the
# equals sign is manually added (see else block below)
# I tried the following:
# - Escape with \
# - Escape with ^
# - Use single quotation marks instead of double
# - Setting up (de)activate.d w/ env_vars.sh in conda env (see https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html#macos-and-linux)
# Nothing worked and I don't want to waste any more time on this issue
is_production = os.environ['IS_PRODUCTION']
if is_production == 'True':
    mapbox_url = os.environ['MAPBOX_URL']
else:
    mapbox_url = os.environ['MAPBOX_URL1'] + '=' + os.environ['MAPBOX_URL2']

def format_number(x):
    """
    Format numbers for map display purposes (highlight, hover info).

    Examples:
    123456 -> 123K
    1234567 -> 1.23M
    12.34 -> 12.3
    0.123456 -> 0.12 (preference of no more than 2 decimal places)
    """
    units = {
        0: '',
        3: 'K',
        6: 'M',
        9: 'B' # currently nothing at this order of magnitude
    }
    orders = np.array(list(units.keys()))

    ### Special cases
    if np.isnan(x):
        # mostly for NA populations
        return 'Not available'
    elif x == 0:
        # x = 0 -> log error in a few lines
        return '0'
    elif x < 1:
        # 0.123456 -> 0.12
        return f'{x:.2f}'

    log = np.log10(x)
    log_floor = int(np.floor(log))
    highest_order = orders[orders <= log_floor].max()
    rounding = highest_order - log_floor + 2

    sigfigs = f'{(x / 10**highest_order):.3g}'
    # if highest_order == 0 or np.log10(sigfigs) >= 2:
    #     # 1.0 -> 1 (highest_order )
    #     # 12.0 -> 12
    #     # 123.0 -> 123
    #     sigfigs = int(sigfigs)
    unit = units[highest_order]
    out = '{}{}'.format(sigfigs, unit)

    return out


def get_map_data(data, comm):
    return (
        data.loc[:, [
            'community_id',
            'est_fishers',
            'est_buyers',
            'weight_mt',
            'total_price_usd'
        ]].groupby('community_id')
        .sum()
        .reset_index()
        .join(comm[['community_id', 'community_name', 'community_lat', 'community_lon', 'population']].set_index('community_id'), on = 'community_id')
        .reset_index(drop = True)
    )

def make_map(map_data, mapbox_url):
    map_data[['population', 'est_fishers', 'est_buyers', 'weight_mt', 'total_price_usd']] = map_data[['population', 'est_fishers', 'est_buyers', 'weight_mt', 'total_price_usd']].applymap(format_number)
    hovertext_list = [
        "Community: {}<br>\
Population: {}<br>\
Estimated fishers: {}<br>\
Estimated buyers: {}<br>\
Total catch weight (mt): {}<br>\
Total catch value (USD): {}<br>\
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
        height = 1000
    )

    return fig
