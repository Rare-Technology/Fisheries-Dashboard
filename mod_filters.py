from dash import dcc, html
from mod_dataworld import countries, snu, lgu, maa

country_input = dcc.Dropdown(id = 'country-input',
    options = countries['country_name'],
    value = countries['country_name'],
    multi = True
)

country_select_all = dcc.Checklist(id = 'country-select-all',
    options = ['Select all'],
    value = [],
    inline = True
)

country_div = html.Div(children = [
    html.Label('Country'),
    country_select_all,
    country_input
])

snu_input = dcc.Dropdown(id = 'snu-input',
    options = snu['snu_name'],
    value = snu['snu_name'],
    multi = True
)

snu_select_all = dcc.Checklist(id = 'snu-select-all',
    options = ['Select all'],
    value = [],
    inline = False
)

snu_div = html.Div(children = [
    'Subnational Unit',
    snu_select_all,
    snu_input
])

lgu_input = dcc.Dropdown(id = 'lgu-input',
    options = lgu['lgu_name'],
    value = lgu['lgu_name'],
    multi = True
)

lgu_div = html.Div(children = [
    html.Label('Local government unit'),
    lgu_input
])

maa_input = dcc.Dropdown(id = 'maa-input',
    options = maa['ma_name'],
    value = maa['ma_name'],
    multi = True
)

maa_div = html.Div(children = [
    html.Label('Managed access area'),
    maa_input
])

apply_button = html.Button(children = 'Apply filters')

filters_UI = [
    country_div,
    html.Br(),
    snu_div,
    html.Br(),
    lgu_div,
    html.Br(),
    maa_div,
    apply_button]
