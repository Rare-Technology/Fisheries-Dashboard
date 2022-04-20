from dash import dcc, html
from mod_dataworld import countries, snu, lgu, maa

country_input = dcc.Dropdown(
    countries['country_name'],
    countries['country_name'],
    multi = True
)

country_select_all = dcc.Checklist(['Select all'])

country_div = html.Div(children = [
    html.Label('Country'),
    country_select_all
    country_input
])


snu_input = dcc.Dropdown(
    snu['snu_name'],
    snu['snu_name'],
    multi = True
)

snu_div = html.Div(children = [
    'Subnational Unit',
    snu_input
])

lgu_input = dcc.Dropdown(
    lgu['lgu_name'],
    lgu['lgu_name'],
    multi = True
)

lgu_div = html.Div(children = [
    html.Label('Local government unit'),
    lgu_input
])

maa_input = dcc.Dropdown(
    maa['ma_name'],
    maa['ma_name'],
    multi = True
)

maa_div = html.Div(children = [
    html.Label('Managed access area'),
    maa_input
])

apply_button = html.Button(children = 'Apply filters')

filters_UI = [country_div, snu_div, lgu_div, maa_div, apply_button]
