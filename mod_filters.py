from dash import dcc, html
from mod_dataworld import countries, snu, lgu, maa

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
    clearable = False
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
