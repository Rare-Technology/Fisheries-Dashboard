from dash import dcc, html
import datetime
from mod_dataworld import countries, snu, lgu, maa, all_data

##### TODO figure out how to either (1) limit the amount of selectted options displayed or
##### (2) find a different dropdown selection similar to ones on FMA tool
### Country selection
country_input = dcc.Dropdown(id = 'country-input',
    options = list(countries['country_name']),
    value = list(countries['country_name']),
    multi = True,
    clearable = False
)
country_select_all = dcc.Checklist(id = 'country-select-all',
    options = ['Select all'],
    value = ['Select all'],
    inline = True
)
country_div = html.Div(children = [
    html.Label('Country'),
    country_select_all,
    country_input
])

### Subnational selection
snu_input = dcc.Dropdown(id = 'snu-input',
    options = [],
    value = [],
    multi = True,
    clearable = False
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

### Local selection
lgu_input = dcc.Dropdown(id = 'lgu-input',
    options = [],
    value = [],
    multi = True,
    clearable = False
)
lgu_select_all = dcc.Checklist(id = 'lgu-select-all',
    options = ['Select all'],
    value = [],
    inline = True
)
lgu_div = html.Div(children = [
    html.Label('Local government unit'),
    lgu_select_all,
    lgu_input
])

### MA Selection
maa_input = dcc.Dropdown(id = 'maa-input',
    options = [],
    value = [],
    multi = True,
    clearable = False,
)
maa_select_all = dcc.Checklist(id = 'maa-select-all',
    options = ['Select all'],
    value = [],
    inline = True
)
maa_div = html.Div(children = [
    html.Label('Managed access area'),
    maa_select_all,
    maa_input
])

min_date = all_data['date'].min()
max_date = all_data['date'].max()
if max_date.month >= 6:
    start_date = datetime.date(max_date.year, max_date.month - 5, 1)
else:
    start_date = datetime.date(max_date.year - 1, max_date.month + 7, 1)

daterange_input = dcc.DatePickerRange(id='date-range-input',
        min_date_allowed = min_date,
        max_date_allowed = max_date,
        initial_visible_month = max_date,
        start_date = start_date,
        end_date = max_date,
)
daterange_div = html.Div([
    html.Label('Date range'),
    daterange_input
])

filters_UI = [
    daterange_div,
    html.Br(),
    country_div,
    html.Br(),
    snu_div,
    html.Br(),
    lgu_div,
    html.Br(),
    maa_div]

filter_inputs_div = html.Div(filters_UI,
    id = 'filter-inputs'
)

filter_inputs_toggle_div = html.Div([
        html.H3("Filters", style = {"display": "inline"}),
        html.Span(
            [html.Span(className = "Select-arrow")],
            className = "Select-arrow-zone dropdown-arrow"
        )
    ],
    id = "filter-inputs-toggle"
)

update_button = html.Button(
    children = html.H4('Apply filters'),
    id = "update-button",
    className = "btn btn-success"
)

filter_div = html.Div([
        html.Div([filter_inputs_toggle_div, filter_inputs_div], id = "filters-container"),
        update_button
])
