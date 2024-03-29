from dash import Dash, dcc, html, callback_context
from dash.dependencies import Input, Output, State
from mod_dataworld import get_ourfish_data, get_geo_data
from utils_filters import sync_select_all
from mod_filters import start_filters
from utils_plot import (
    get_catch_data, make_catch_fig,
    get_cpue_value_data, make_cpue_value_fig,
    get_length_data, make_length_fig,
    get_composition_data, make_composition_fig
)
from mod_plot import start_plot
from utils_map import get_map_data, make_map, mapbox_url
from mod_map import start_map
from utils_highlights import (
    create_card, get_total_weight, get_total_value, get_total_trips,
    get_fishers, get_female, get_buyers, get_highlights_data
)
from mod_highlights import start_highlights
from mod_download import start_download_button
import datetime
import io
import pandas as pd
from flask_caching import Cache
import uuid

# Importing bootstrap 4; Why 4 and not 5? The hover on v4's buttons is better! The change in color
# is actually noticeable. v5's buttons (the lighter colors) you can't even tell if there's
# a change on hover. Not great for the download button
external_stylesheets = [
    {
        'href': 'https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-xOolHFLEh07PJGoPkLv1IbcEPTNtaed2xpHsD9ESMhqIYd0nLMwNLD69Npy4HI+N',
        'crossorigin': 'anonymous'
    }
]

external_scripts = [
    {
        'src': "https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js",
        'integrity': "sha384-Fy6S3B9q64WdZWQUiU+q4/2Lc9npb8tCaSX9FK7E8HnRr0Jz8D6OP9dO5Vg3Q9ct",
        'crossorigin': "anonymous"
    }
]

app = Dash(__name__, external_stylesheets = external_stylesheets)
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        <div id="bars1">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
        </div>
    </body>
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</html>
"""
# To avoid using global variables, which dash does not behave well with, we use caching
# to share data between callbacks. This sets up a redis database on the server, where 
# data is cached and pulled from.
# For more details, see https://dash.plotly.com/sharing-data-between-callbacks
# We are using Ex 4, the solution for caching user-based session data on the server.
# Ex 1 can also cache user-based session data but on the client side, which for
# our audience we will not do.
cache = Cache(app.server, config={
    'CACHE_TYPE': 'redis',
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',
    'CACHE_THRESHOLD': 200 # subject to change
})

# User opens app and initial query to data.world is performed
# The query output is memoized using the session id, so each user
# will have their initial data cached.
@cache.memoize()
def query_ourfish_data(session_id):
    all_data = get_ourfish_data()
    return all_data

@cache.memoize()
def query_geo_data(session_id):
    all_data = query_ourfish_data(session_id) # from cache
    geo = get_geo_data(all_data)
    return geo

@cache.memoize()
def apply_filters(session_id, sel_maa, start_date, end_date):
    """
    Pull full cached DW dataset then filter it. Compute and return data for plots, highlights, and map.
    The output is memoized according to the unique user and filters.
    Notice we don't return the filtered data -- ultimately what we care about pulling from cache
    is not the filtered data but the numbers we get from processing that filtered data. That is
    what actually goes on the plots, map, highlights, and download file.
    """
    all_data = query_ourfish_data(session_id) # from cache
    filtered_data = all_data.query(
        "ma_id.isin(list(@sel_maa)) & \
        @start_date <= date & \
        date <= @end_date"
    )
    geo = query_geo_data(session_id) # from cache

    output_data = {}
    output_data["map"] = get_map_data(filtered_data, geo["comm"])
    output_data["catch"] = get_catch_data(filtered_data)
    output_data["cpue-value"] = get_cpue_value_data(filtered_data)
    output_data["length"] = get_length_data(filtered_data)
    output_data["composition"] = get_composition_data(filtered_data)
    output_data["highlights"] = get_highlights_data(filtered_data)

    return output_data

server = app.server
def serve_layout():
    """
    Create app layout on page load

    Query data.world to process data, giving the initial data that is displayed.
    "Initial" in this sense means the first dataset after loading the app; it is
    the past 6 months of OurFish data. We also pull the full dataset which is
    used to update components when filters are changed.

    This initial data is then used to create the first visualizations, filter settings,
    and download file.

    The outputs (divs) are only updated using dash callbacks; when this function
    runs again to create the divs, it is because the app has been rebooted.
    """
    session_id = str(uuid.uuid4())

    all_data = query_ourfish_data(session_id)
    geo = query_geo_data(session_id)
    countries = geo["country"]
    snu = geo["snu"]
    lgu = geo["lgu"]
    maa = geo["maa"]
    comm = geo["comm"]
    
    # choose start and end dates to initially show the past 6 months of data
    end_date = all_data['date'].max()
    if end_date.month >= 6:
        start_date = datetime.date(end_date.year, end_date.month - 5, 1)
    else:
        start_date = datetime.date(end_date.year - 1, end_date.month + 7, 1)
    
    output_data = apply_filters(session_id, maa["ma_id"], start_date, end_date)
    plot_data = {k: output_data[k] for k in ["catch", "cpue-value", "length", "composition"]}

    # Min/max dates to show on calendar
    min_date = all_data["date"].min()
    max_date = end_date

    map_div = start_map(output_data["map"], comm)
    filter_div = start_filters(min_date, max_date, countries)
    plot_div = start_plot(plot_data)
    download_div = start_download_button()
    highlights_div = start_highlights(output_data["highlights"])

    return html.Div([
        html.Div(session_id, id="session-id", style={"display": "none"}),
        map_div,
        filter_div,
        plot_div,
        download_div,
        highlights_div
    ])

app.layout = serve_layout

@app.callback(
    Output("country-select-all", 'value'),
    Output("country-input", 'value'),
    Input("country-select-all", 'value'),
    Input("country-input", 'value'),
    State("session-id", "children")
)
def sync_country_select_all(all_selected, sel_country, session_id):
    """
    Sync country selections with 'select all' checkbox
    """
    countries = query_geo_data(session_id)["country"]
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    all_countries = list(countries['country_name'])

    return sync_select_all(all_selected, "country-input", sel_country, all_countries, triggered_id)

@app.callback(
    Output("snu-select-all", 'value'),
    Output("snu-input", 'options'),
    Output("snu-input", 'value'),
    Input("snu-select-all", 'value'),
    Input("snu-input", 'value'),
    Input("country-input", 'value'),
    State("snu-input", 'options'),
    State("session-id", "children")
)
def update_snu(snu_all_selected, sel_snu, sel_country_names, state_opt_snu_dict, session_id):
    """
    This callback will handle the following events:

    (1) Country value changes - Update SNU options/values. Don't update values if
    the user had made changes to selections.

    (2) One of 'Select all' checkbox or SNU selections changes. This produces a
    circular callback in which:
        (a) if 'Select all' checkbox changes, update SNU selections accordingly
        (b) if SNU selections change, update 'Select all' checkbox accordingly
    """
    countries = query_geo_data(session_id)["country"]
    snu = query_geo_data(session_id)["snu"]
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    sel_country = list(countries.query("country_name.isin(@sel_country_names)")['country_id'])
    all_snu = list(snu.query("country_id.isin(@sel_country)")['snu_id'])
    all_snu_names = list(snu.query("country_id.isin(@sel_country)")['snu_name'])
    all_snu_opt_dict = [{'label': s_name, 'value': s} for s_name, s in zip(all_snu_names, all_snu)]
    state_opt_snu = [d['value'] for d in state_opt_snu_dict]

    if triggered_id == "country-input":
        # Update triggered by change to country selections
        if set(state_opt_snu) == set(sel_snu):
            # User has not removed any available SNU selections, so the new
            # SNU values will match the new SNU options
            snu_all_selected = ['Select all'] if sel_country != [] else []
            return snu_all_selected, all_snu_opt_dict, all_snu
        else:
            # The user has previously deselected SNU's. The new SNU values will keep the
            # same SNU's deselected but add any new SNU's.
            diff_snu = [s for s in state_opt_snu if s not in sel_snu] # snu's explicitly de-selected
            keep_snu = [s for s in all_snu if s not in diff_snu]
            snu_all_selected = ['Select all'] if set(keep_snu) == set(all_snu) else []
            return snu_all_selected, all_snu_opt_dict, keep_snu
    else:
        # Update triggered by change to SNU value or 'Select all' checkbox.
        # If SNU value is the trigger, update the checkbox
        # If the checkbox is the trigger, update the SNU values
        snu_all_selected, sel_snu = sync_select_all(snu_all_selected, "snu-input", sel_snu, all_snu, triggered_id)
        return snu_all_selected, all_snu_opt_dict, sel_snu

@app.callback(
    Output("lgu-select-all", 'value'),
    Output("lgu-input", 'options'),
    Output("lgu-input", 'value'),
    Input("lgu-select-all", 'value'),
    Input("lgu-input", 'value'),
    Input("snu-input", 'value'),
    State("lgu-input", 'options'),
    State("session-id", "children")
)
def update_lgu(lgu_all_selected, sel_lgu, sel_snu, state_opt_lgu_dict, session_id):
    """
    This callback will handle the following events:

    (1) SNU value changes - Update LGU options/values. Don't update values if
    the user had made changes to selections.

    (2) One of 'Select all' checkbox or LGU selections changes. This produces a
    circular callback in which:
        (a) if 'Select all' checkbox changes, update LGU selections accordingly
        (b) if LGU selections change, update 'Select all' checkbox accordingly
    """
    lgu = query_geo_data(session_id)["lgu"]
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    all_lgu = list(lgu.query("snu_id.isin(@sel_snu)")['lgu_id'])
    all_lgu_names = list(lgu.query("snu_id.isin(@sel_snu)")['lgu_name'])
    all_lgu_opt_dict = [{'label': l_name, 'value': l} for l_name, l in zip(all_lgu_names, all_lgu)]
    state_opt_lgu = [d['value'] for d in state_opt_lgu_dict]

    if triggered_id == "snu-input":
        if set(state_opt_lgu) == set(sel_lgu):
            lgu_all_selected = ['Select all'] if sel_snu != [] else []
            return lgu_all_selected, all_lgu_opt_dict, all_lgu
        else:
            # the user has made changes to the lgu selections so don't touch the selected
            # lgu's unless any of them belong to a country no longer selected. Filter those out.
            diff_lgu = [l for l in state_opt_lgu if l not in sel_lgu]
            keep_lgu = [l for l in all_lgu if l not in diff_lgu]
            lgu_all_selected = ['Select all'] if set(keep_lgu) == set(all_lgu) else []
            return lgu_all_selected, all_lgu_opt_dict, keep_lgu
    else:
        lgu_all_selected, sel_lgu = sync_select_all(lgu_all_selected, "lgu-input", sel_lgu, all_lgu, triggered_id)
        return lgu_all_selected, all_lgu_opt_dict, sel_lgu

@app.callback(
    Output("maa-select-all", 'value'),
    Output("maa-input", 'options'),
    Output("maa-input", 'value'),
    Input("maa-select-all", 'value'),
    Input("maa-input", 'value'),
    Input("lgu-input", 'value'),
    State("maa-input", 'options'),
    State("session-id", "children")
)
def update_maa(maa_all_selected, sel_maa, sel_lgu, state_opt_maa_dict, session_id):
    maa = query_geo_data(session_id)["maa"]
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    all_maa = list(maa.query("lgu_id.isin(@sel_lgu)")['ma_id'])
    all_maa_names = list(maa.query("lgu_id.isin(@sel_lgu)")['ma_name'])
    all_maa_opt_dict = [{'label': m_name, 'value': m} for m_name, m in zip(all_maa_names, all_maa)]
    state_opt_maa = [d['value'] for d in state_opt_maa_dict]

    if triggered_id == "lgu-input":
        if set(state_opt_maa) == set(sel_maa):
            maa_all_selected = ['Select all'] if sel_lgu != [] else []
            return maa_all_selected, all_maa_opt_dict, all_maa
        else:
            diff_maa = [m for m in state_opt_maa if m not in sel_maa]
            keep_maa = [m for m in all_maa if m not in diff_maa]
            maa_all_selected = ['Select all'] if set(keep_maa) == set(all_maa) else []
            return maa_all_selected, all_maa_opt_dict, keep_maa
    else:
        maa_all_selected, sel_maa = sync_select_all(maa_all_selected, "maa-input", sel_maa, all_maa, triggered_id)
        return maa_all_selected, all_maa_opt_dict, sel_maa

@app.callback(
    Output("catches-plot", 'figure'),
    Output("cpue-value-plot", 'figure'),
    Output("length-plot", 'figure'),
    Output("composition-plot", 'figure'),
    Output("highlights-container", 'children'),
    Input("update-button", 'n_clicks'),
    State("session-id", "children"),
    State("maa-input", "value"),
    State("date-range-input", "start_date"),
    State("date-range-input", "end_date"),
    prevent_initial_call = True
)
def update_plots(n_clicks, session_id, sel_maa, start_date, end_date):
    start_date = datetime.date.fromisoformat(start_date)
    end_date = datetime.date.fromisoformat(end_date)

    # I THINK this callback runs first instead of update_map, so running apply_filters
    # here will calculate the new output data then cache it.
    output_data = apply_filters(session_id, sel_maa, start_date, end_date)

    catch_fig = make_catch_fig(output_data["catch"])
    cpue_value_fig = make_cpue_value_fig(output_data["cpue-value"])
    length_fig = make_length_fig(output_data["length"])
    composition_fig = make_composition_fig(output_data["composition"])

    highlights_data = output_data["highlights"]
    highlights_children = [
        create_card(highlights_data.loc[0, 'weight'], "Total weight (mt)"),
        create_card(highlights_data.loc[0, 'value'], "Total value (USD)"),
        create_card(highlights_data.loc[0, 'trips'], "Total #trips"),
        create_card(highlights_data.loc[0, 'fishers'], "Fishers recorded"),
        create_card(highlights_data.loc[0, 'buyers'], "Total buyers"),
        create_card(highlights_data.loc[0, 'female buyers'], "Total female buyers"),
    ]

    return catch_fig, cpue_value_fig, length_fig, composition_fig, highlights_children

@app.callback(
    Output("fish-map", 'figure'),
    Input("fish-map", 'clickData'),
    Input("update-button", 'n_clicks'),
    State("session-id", "children"),
    State("maa-input", 'value'),
    State("date-range-input", 'start_date'),
    State("date-range-input", 'end_date'),
    prevent_initial_call = True
)
def update_map(mapClickData, update_clicks, session_id, sel_maa, start_date, end_date):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == "fish-map":
        # TODO update this. There used to be a map dcc.Graph object imported from mod_map that
        # would work with the code here.
        # zoom in on the point that was clicked
        sel_lat = mapClickData['points'][0]['lat']
        sel_lon = mapClickData['points'][0]['lon']

        fig = map.figure
        fig.update_layout(
            mapbox = {
                'center': {
                    'lat': sel_lat,
                    'lon': sel_lon,
                },
                'zoom': 5
            }
        )
    elif triggered_id == "update-button":
        # Update points and fit the zoom to the filtered points
        start_date = datetime.date.fromisoformat(start_date)
        end_date = datetime.date.fromisoformat(end_date)

        # Pull map data from cache; I think the update_plots callback goes first so the output data
        # has already been updated and cached.
        map_data = apply_filters(session_id, sel_maa, start_date, end_date)["map"]

        fig = make_map(map_data, mapbox_url)

    return fig

@app.callback(
    Output('filter-inputs', 'style'),
    Input('filter-inputs-toggle', 'n_clicks')
)
def toggle_filter_display(n_clicks):
    if n_clicks is None or n_clicks % 2 == 0:
        style = {"display": "none"}
    else:
        style = {"display": "block"}

    return style

@app.callback(
    Output('plot-displays', 'style'),
    Input('plots-toggle', 'n_clicks')
)
def toggle_plot_display(n_clicks):
    if n_clicks is None or n_clicks % 2 == 0:
        style = {"display": "block"}
    else:
        style = {"display": "none"}

    return style

@app.callback(
    Output('download-data', 'data'),
    Input('btn-download', 'n_clicks'),
    State("session-id", "children"),
    State("country-input", 'value'),
    State("snu-input", 'value'),
    State("lgu-input", 'value'),
    State("maa-input", 'value'),
    State("date-range-input", 'start_date'),
    State("date-range-input", 'end_date'),
    prevent_initial_call = True
)
def trigger_download(n_clicks, session_id, sel_country, sel_snu, sel_lgu, sel_maa, start_date, end_date):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine = 'xlsxwriter')

    start_date = datetime.date.fromisoformat(start_date)
    end_date = datetime.date.fromisoformat(end_date)

    # Pull the cached filtered data
    output_data = apply_filters(session_id, sel_maa, start_date, end_date)

    sheet_names = {
        "highlights": "Totals",
        "catch": "Catches",
        "cpue-value": "CPUE-Value",
        "length": "Length",
        "composition": "Catch composition",
        "map": "Communities"
    }
    
    for d in output_data.items():
        # d: ('df_name', df)
        d[1].to_excel(writer, sheet_name = sheet_names[d[0]], index = False)

    # Before finishing, we'll add metadata. And before that, we need names for geographic info,
    # not just the id's

    geo = query_geo_data(session_id)
    snu = geo["snu"]
    lgu = geo["lgu"]
    maa = geo["maa"]
    snu_names = list(snu.query("snu_id.isin(@sel_snu)")['snu_name'])
    lgu_names = list(lgu.query("lgu_id.isin(@sel_lgu)")['lgu_name'])
    maa_names = list(maa.query("ma_id.isin(@sel_maa)")['ma_name'])

    metadata = pd.DataFrame({
        'FILTER': ['country', 'snu', 'lgu', 'maa', 'start date', 'end date'],
        'VALUE': [
            ', '.join(sel_country),
            ', '.join(snu_names),
            ', '.join(lgu_names),
            ', '.join(maa_names),
            start_date, end_date
        ]
    })

    metadata.to_excel(writer, sheet_name = 'metadata', index = False)

    writer.save()
    output_data = output.getvalue()
    output.close()

    return dcc.send_bytes(output_data, 'fisheries-data.xlsx')

if __name__ == '__main__':
    app.run_server(debug=False)
