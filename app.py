# -*- coding: utf-8 -*-
from dash import Dash, dcc, html, callback_context
from dash.dependencies import Input, Output, State
from mod_filters import (
    country_input, country_select_all, snu_input, snu_select_all, lgu_input,
    lgu_select_all, maa_input, maa_select_all, daterange_input, filters_UI
)
from mod_plot import catch_plot, cpue_value_plot, length_plot, composition_plot, update_button, plot_UI
from utils_plot import (
    get_catch_data, make_catch_fig,
    get_cpue_value_data, make_cpue_value_fig,
    get_length_data, make_length_fig,
    get_composition_data, make_composition_fig
)
from mod_map import map_UI
from mod_text import output, text_UI
from mod_dataworld import countries, snu, lgu, maa, all_data
from utils_filters import sync_select_all
import datetime


external_scripts = [
    {
        'src': "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js",
        'integrity': "sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p",
        'crossorigin': "anonymous"
    }
]
external_stylesheets = [
    {
        'href': 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3',
        'crossorigin': 'anonymous'
    }
]

app = Dash(__name__, external_stylesheets = external_stylesheets)

app.layout = html.Div([
    map_UI,
    html.Div(
        filters_UI + text_UI,
        style = {'width': '49%', 'display': 'inline-block', 'height': '600px', 'overflow-y': 'scroll'}
    ),
    plot_UI
])

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
def update_snu(snu_all_selected, sel_snu, sel_country, state_opt_snu):
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
    sel_country_id = countries.query("country_name.isin(@sel_country)")['country_id']
    all_snu = list(snu.query("country_id.isin(@sel_country_id)")['snu_name'])

    if triggered_id == country_input.id:
        if set(state_opt_snu) == set(sel_snu):
            snu_all_selected = ['Select all'] if sel_country != [] else []
            return snu_all_selected, all_snu, all_snu
        else:
            # the user has made changes to the snu selections so don't touch the selected
            # snu's unless any of them belong to a country no longer selected. Filter those out.
            diff_snu = [s for s in state_opt_snu if s not in sel_snu] # snu's explicitly de-selected
            keep_snu = [s for s in all_snu if s not in diff_snu]
            snu_all_selected = ['Select all'] if set(keep_snu) == set(all_snu) else []
            return snu_all_selected, all_snu, keep_snu
    else:
        snu_all_selected, sel_snu = sync_select_all(snu_all_selected, snu_input, sel_snu, all_snu, triggered_id)
        return snu_all_selected, all_snu, sel_snu

@app.callback(
    Output(lgu_select_all, 'value'),
    Output(lgu_input, 'options'),
    Output(lgu_input, 'value'),
    Input(lgu_select_all, 'value'),
    Input(lgu_input, 'value'),
    Input(snu_input, 'value'),
    State(lgu_input, 'options'),
)
def update_lgu(lgu_all_selected, sel_lgu, sel_snu, state_opt_lgu):
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
    sel_snu_id = snu.query("snu_name.isin(@sel_snu)")['snu_id']
    all_lgu = list(lgu.query("snu_id.isin(@sel_snu_id)")['lgu_name'])

    if triggered_id == snu_input.id:
        if set(state_opt_lgu) == set(sel_lgu):
            lgu_all_selected = ['Select all'] if sel_snu != [] else []
            return lgu_all_selected, all_lgu, all_lgu
        else:
            # the user has made changes to the lgu selections so don't touch the selected
            # lgu's unless any of them belong to a country no longer selected. Filter those out.
            diff_lgu = [l for l in state_opt_lgu if l not in sel_lgu]
            keep_lgu = [l for l in all_lgu if l not in diff_lgu]
            lgu_all_selected = ['Select all'] if set(keep_lgu) == set(all_lgu) else []
            return lgu_all_selected, all_lgu, keep_lgu
    else:
        lgu_all_selected, sel_lgu = sync_select_all(lgu_all_selected, lgu_input, sel_lgu, all_lgu, triggered_id)
        return lgu_all_selected, all_lgu, sel_lgu

@app.callback(
    Output(maa_select_all, 'value'),
    Output(maa_input, 'options'),
    Output(maa_input, 'value'),
    Input(maa_select_all, 'value'),
    Input(maa_input, 'value'),
    Input(lgu_input, 'value'),
    State(maa_input, 'options')
)
def update_maa(maa_all_selected, sel_maa, sel_lgu, state_opt_maa):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    sel_lgu_id = lgu.query("lgu_name.isin(@sel_lgu)")['lgu_id']
    all_maa = list(maa.query("lgu_id.isin(@sel_lgu_id)")['ma_id'])
    all_maa_names = list(maa.query("lgu_id.isin(@sel_lgu_id)")['ma_name'])
    all_maa_opt_dict = [{'label': m_name, 'value': m} for m_name, m in zip(all_maa_names, all_maa)]
    state_opt_maa_values = [d['value'] for d in state_opt_maa]

    if triggered_id == lgu_input.id:
        if set(state_opt_maa_values) == set(sel_maa):
            maa_all_selected = ['Select all'] if sel_lgu != [] else []
            return maa_all_selected, all_maa_opt_dict, all_maa
        else:
            diff_maa = [m for m in state_opt_maa_values if m not in sel_maa]
            keep_maa = [m for m in all_maa if m not in diff_maa]
            maa_all_selected = ['Select all'] if set(keep_maa) == set(all_maa) else []
            return maa_all_selected, all_maa_opt_dict, keep_maa
    else:
        maa_all_selected, sel_maa = sync_select_all(maa_all_selected, maa_input, sel_maa, all_maa, triggered_id)
        return maa_all_selected, all_maa_opt_dict, sel_maa

@app.callback(
    Output(catch_plot, 'figure'),
    Output(cpue_value_plot, 'figure'),
    Output(length_plot, 'figure'),
    Output(composition_plot, 'figure'),
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

    catch_data = get_catch_data(filter_data)
    catch_fig = make_catch_fig(catch_data)

    cpue_value_data = get_cpue_value_data(filter_data)
    cpue_value_fig = make_cpue_value_fig(cpue_value_data)

    length_data = get_length_data(filter_data)
    length_fig = make_length_fig(length_data)

    composition_data = get_composition_data(filter_data)
    composition_fig = make_composition_fig(composition_data)

    return catch_fig, cpue_value_fig, length_fig, composition_fig
if __name__ == '__main__':
    app.run_server(debug=True)
