# -*- coding: utf-8 -*-
from dash import Dash, dcc, html, callback_context
from dash.dependencies import Input, Output, State
from mod_dataworld import countries, snu, lgu, maa, comm, all_data
from utils_filters import sync_select_all
from mod_filters import (
    country_input, country_select_all, snu_input, snu_select_all, lgu_input,
    lgu_select_all, maa_input, maa_select_all, daterange_input, update_button, filter_div
)
from utils_plot import (
    get_catch_data, make_catch_fig,
    get_cpue_value_data, make_cpue_value_fig,
    get_length_data, make_length_fig,
    get_composition_data, make_composition_fig
)
from mod_plot import (
    init_catch_data, init_cpue_value_data, init_length_data, init_composition_data,
    catch_plot, cpue_value_plot, length_plot, composition_plot, plot_div
)
from utils_map import get_map_data, make_map, mapbox_url
from mod_map import map, map_div
from utils_highlights import (
    create_card, get_total_weight, get_total_value, get_total_trips,
    get_fishers, get_female, get_buyers, get_highlights_data
)
from mod_highlights import highlights_div, init_highlights_data
from mod_download import download_div
import datetime
import io
import pandas as pd

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
server = app.server
app.layout = html.Div([
    map_div,
    filter_div,
    plot_div,
    download_div,
    highlights_div
])

data = {
    'Totals': init_highlights_data,
    'Catch': init_catch_data,
    'CPUE-Value': init_cpue_value_data,
    'Length': init_length_data,
    'Composition': init_composition_data
}

@app.callback(
    Output(country_select_all, 'value'),
    Output(country_input, 'value'),
    Input(country_select_all, 'value'),
    Input(country_input, 'value')
)
def sync_country_select_all(all_selected, sel_country):
    """
    Sync country selections with 'select all' checkbox
    """
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    all_countries = list(countries['country_name'])

    return sync_select_all(all_selected, country_input, sel_country, all_countries, triggered_id)

@app.callback(
    Output(snu_select_all, 'value'),
    Output(snu_input, 'options'),
    Output(snu_input, 'value'),
    Input(snu_select_all, 'value'),
    Input(snu_input, 'value'),
    Input(country_input, 'value'),
    State(snu_input, 'options'),
)
def update_snu(snu_all_selected, sel_snu, sel_country_names, state_opt_snu_dict):
    """
    This callback will handle the following events:

    (1) Country value changes - Update SNU options/values. Don't update values if
    the user had made changes to selections.

    (2) One of 'Select all' checkbox or SNU selections changes. This produces a
    circular callback in which:
        (a) if 'Select all' checkbox changes, update SNU selections accordingly
        (b) if SNU selections change, update 'Select all' checkbox accordingly
    """
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    sel_country = list(countries.query("country_name.isin(@sel_country_names)")['country_id'])
    all_snu = list(snu.query("country_id.isin(@sel_country)")['snu_id'])
    all_snu_names = list(snu.query("country_id.isin(@sel_country)")['snu_name'])
    all_snu_opt_dict = [{'label': s_name, 'value': s} for s_name, s in zip(all_snu_names, all_snu)]
    state_opt_snu = [d['value'] for d in state_opt_snu_dict]

    if triggered_id == country_input.id:
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
        snu_all_selected, sel_snu = sync_select_all(snu_all_selected, snu_input, sel_snu, all_snu, triggered_id)
        return snu_all_selected, all_snu_opt_dict, sel_snu

@app.callback(
    Output(lgu_select_all, 'value'),
    Output(lgu_input, 'options'),
    Output(lgu_input, 'value'),
    Input(lgu_select_all, 'value'),
    Input(lgu_input, 'value'),
    Input(snu_input, 'value'),
    State(lgu_input, 'options'),
)
def update_lgu(lgu_all_selected, sel_lgu, sel_snu, state_opt_lgu_dict):
    """
    This callback will handle the following events:

    (1) SNU value changes - Update LGU options/values. Don't update values if
    the user had made changes to selections.

    (2) One of 'Select all' checkbox or LGU selections changes. This produces a
    circular callback in which:
        (a) if 'Select all' checkbox changes, update LGU selections accordingly
        (b) if LGU selections change, update 'Select all' checkbox accordingly
    """
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    all_lgu = list(lgu.query("snu_id.isin(@sel_snu)")['lgu_id'])
    all_lgu_names = list(lgu.query("snu_id.isin(@sel_snu)")['lgu_name'])
    all_lgu_opt_dict = [{'label': l_name, 'value': l} for l_name, l in zip(all_lgu_names, all_lgu)]
    state_opt_lgu = [d['value'] for d in state_opt_lgu_dict]

    if triggered_id == snu_input.id:
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
        lgu_all_selected, sel_lgu = sync_select_all(lgu_all_selected, lgu_input, sel_lgu, all_lgu, triggered_id)
        return lgu_all_selected, all_lgu_opt_dict, sel_lgu

@app.callback(
    Output(maa_select_all, 'value'),
    Output(maa_input, 'options'),
    Output(maa_input, 'value'),
    Input(maa_select_all, 'value'),
    Input(maa_input, 'value'),
    Input(lgu_input, 'value'),
    State(maa_input, 'options')
)
def update_maa(maa_all_selected, sel_maa, sel_lgu, state_opt_maa_dict):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    all_maa = list(maa.query("lgu_id.isin(@sel_lgu)")['ma_id'])
    all_maa_names = list(maa.query("lgu_id.isin(@sel_lgu)")['ma_name'])
    all_maa_opt_dict = [{'label': m_name, 'value': m} for m_name, m in zip(all_maa_names, all_maa)]
    state_opt_maa = [d['value'] for d in state_opt_maa_dict]

    if triggered_id == lgu_input.id:
        if set(state_opt_maa) == set(sel_maa):
            maa_all_selected = ['Select all'] if sel_lgu != [] else []
            return maa_all_selected, all_maa_opt_dict, all_maa
        else:
            diff_maa = [m for m in state_opt_maa if m not in sel_maa]
            keep_maa = [m for m in all_maa if m not in diff_maa]
            maa_all_selected = ['Select all'] if set(keep_maa) == set(all_maa) else []
            return maa_all_selected, all_maa_opt_dict, keep_maa
    else:
        maa_all_selected, sel_maa = sync_select_all(maa_all_selected, maa_input, sel_maa, all_maa, triggered_id)
        return maa_all_selected, all_maa_opt_dict, sel_maa

@app.callback(
    Output(map, 'figure'),
    Output(catch_plot, 'figure'),
    Output(cpue_value_plot, 'figure'),
    Output(length_plot, 'figure'),
    Output(composition_plot, 'figure'),
    Output(highlights_div, 'children'),
    Input(update_button, 'n_clicks'),
    State(maa_input, 'value'),
    State(daterange_input, 'start_date'),
    State(daterange_input, 'end_date'),
    prevent_initial_call = True
)
def update_plots(n_clicks, sel_maa, start_date, end_date):
    start_date = datetime.date.fromisoformat(start_date)
    end_date = datetime.date.fromisoformat(end_date)

    filter_data = all_data.query(
        "ma_id.isin(list(@sel_maa)) & \
        @start_date <= date & \
        date <= @end_date"
    )

    map_data = get_map_data(filter_data, comm)
    map_fig = make_map(map_data, mapbox_url)

    catch_data = get_catch_data(filter_data)
    catch_fig = make_catch_fig(catch_data)

    cpue_value_data = get_cpue_value_data(filter_data)
    cpue_value_fig = make_cpue_value_fig(cpue_value_data)

    length_data = get_length_data(filter_data)
    length_fig = make_length_fig(length_data)

    composition_data = get_composition_data(filter_data)
    composition_fig = make_composition_fig(composition_data)

    highlights_data = get_highlights_data(filter_data)

    highlights_children = [
        create_card(highlights_data.loc[0, 'weight'], "Total weight (mt)"),
        create_card(highlights_data.loc[0, 'value'], "Total value (USD)"),
        create_card(highlights_data.loc[0, 'trips'], "Total #trips"),
        create_card(highlights_data.loc[0, 'fishers'], "Fishers recorded"),
        create_card(highlights_data.loc[0, 'female buyers'], "Total female buyers"),
        create_card(highlights_data.loc[0, 'buyers'], "Total buyers"),
    ]

    data['Totals'] = highlights_data
    data['Catch'] = catch_data
    data['CPUE-Value'] = cpue_value_data
    data['Length'] = length_data
    data['Composition'] = composition_data

    return map_fig, catch_fig, cpue_value_fig, length_fig, composition_fig, highlights_children

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
    State(country_input, 'value'),
    State(snu_input, 'value'),
    State(lgu_input, 'value'),
    State(maa_input, 'value'),
    State(daterange_input, 'start_date'),
    State(daterange_input, 'end_date'),
    prevent_initial_call = True
)
def trigger_download(n_clicks, sel_country, sel_snu, sel_lgu, sel_maa, start_date, end_date):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine = 'xlsxwriter')

    for d in data.items():
        # d: ('df_name', df)
        d[1].to_excel(writer, sheet_name = d[0], index = False)

    # Before finishing, we'll add metadata. And before that, we need names for geographic info,
    # not just the id's

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
