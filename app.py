# -*- coding: utf-8 -*-
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from mod_filters import (
    country_input, country_select_all,  snu_input, lgu_input, maa_input, apply_button, filters_UI
)
from mod_text import output, text_UI
from mod_dataworld import countries, snu, lgu, maa

external_stylesheets = [
    {
        'src': 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
        'integrity': 'sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3',
        'crossorigin': 'anonymous'
    }
]

app = Dash(__name__, external_stylesheets = external_stylesheets)

app.layout = html.Div(
    filters_UI +
    text_UI
)

### TODO Finish this callback for making a 'select all' checkbox  for country dropdown
# @app.callback(
#     Output(country_select_all, 'value'),
#     Output(country_input, 'value'),
#     Input(country_select_all, 'value'),
#     Input(country_input, 'value')
# )
# def sync_country_select_all(all_countries, sel_country):
#     ctx = callback_context
#     triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
#     if triggered_id == country_select_all.id:
#

@app.callback(
    Output(snu_input, 'options'),
    Output(snu_input, 'value'),
    Input(country_input, 'value'),
    State(snu_input, 'options'),
    State(snu_input, 'value')
)
def update_snu_options(sel_country, state_opt_snu, state_sel_snu):
    sel_country_id = countries.query("country_name.isin(@sel_country)")['country_id']
    sel_snu = list(snu.query("country_id.isin(@sel_country_id)")['snu_name'])

    print('options: ', state_opt_snu)
    print('selected: ', state_sel_snu)
    if set(state_opt_snu) == set(state_sel_snu):
        return sel_snu, sel_snu
    else:
        # the user has made changes to the snu selections so don't touch the selected
        # snu's unless any of them belong to a country no longer selected. Filter those out.
        keep_snu = [s for s in state_sel_snu if s in sel_snu]
        return sel_snu, keep_snu

# @app.callback(
#     Output(snu_input, 'value'),
#     Input(snu_input, 'options'),
#     State(country_input, 'value')
# )
# def update_snu_value(snu_opt, sel_country):
#     sel_country_ud = countries.query("country_name.isin(@sel_country)")['country_id']
#     sel_snu = snu.query("country_id.isin(@sel_country_id)")['snu_name']
#     if set() == set(sel_snu): #
#     return snu_options


if __name__ == '__main__':
    app.run_server(debug=True)
