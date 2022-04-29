import requests
import configparser
import pandas as pd
import json

cfg = configparser.ConfigParser(interpolation = None)
cfg.read('secret.ini')
dw_key = cfg.get('dw', 'API_KEY')

HEADERS = {
    'Authorization': 'Bearer ' + dw_key,
    'Content-Type': 'application/json'
}

QUERY_ID = {
    'countries': "8ba90f2c-9eac-40dd-947a-e9024109df02",
    'subnational_units': "c94b2d19-e1e9-4c34-9a6b-315cf01d25af",
    'local_government_units': "46dda9e4-a491-4b64-a21f-69aae131d134",
    'managed_access_areas': "3c735ba2-21c0-4dfa-bb37-16eb412b2c4b",
    'communities': "fa3c4d1b-036d-4232-93b2-ada2d07008b9",
    'catch_totals_by_ma': "d860383a-70fd-4776-a4f5-8cfda377f565", # 5_catch_totals_by_ma
    'total_fishers_male_female': "696fa988-42e2-4021-a21e-b478a3b3c2e5", # 6_total_fishers_male_female
    'catch_composition_top10': "ceb6388b-fe2e-47d8-9a00-dbee4cece385",
    'total_catch_per_month': "e0b091b3-8123-4b9a-b889-200e3f2e3812",
    'avg_catch_value_cpue': "e563dd85-f8b7-497b-b661-5b9f07b51d3d",
    'median_length_catch': "62602629-e3d8-4a3d-98ae-db341b1259ab",
    'export_catch': "b64b8866-308a-417d-8b79-41f3568eec89",
    'join_fishbase_focal_species': '9315ae27-8978-4525-b77e-e2072fdc10f9'
}

def get_query(query_name, request_method, params = None):
    """
    Make a REST API request to data.world to retrieve data.

    ===== Keyword Arguments =====
    query_name: a key from QUERY_ID
    request_method: "GET" or "POST"
    params: Parameters for a "POST" query. Dict in the form of {param: value, ...}.
        This function handles formatting the parameter payload properly.

    returns: Query results as a pd.DataFrame
    """
    query_id = QUERY_ID[query_name]
    url = 'https://api.data.world/v0/queries/' + query_id + '/results'

    if request_method == "GET":
        response = requests.request("GET", url, headers = HEADERS)
    elif request_method == "POST":
        payload = json.dumps({'parameters': params})
        response = requests.request("POST", url, data = payload, headers = HEADERS)

    data = response.json()
    data = pd.json_normalize(data)

    return data

countries = get_query('countries', 'GET')
# >>> countries.head()
#    country_id                    country_name
# 0           1                          Brazil
# 1          15  Federated States of Micronesia
# 2           4                       Guatemala
# 3           3                        Honduras
# 4           5                       Indonesia

snu = get_query('subnational_units', 'GET')
# >>> snu.head()
#    country_id  snu_id         snu_name
# 0           6     145          Antique
# 1           3      19        Atlántida
# 2           6     149  Camarines Norte
# 3           6     148    Camarines Sur
# 4           6     142             Cebu

lgu = get_query('local_government_units', 'GET')
# >>> lgu.head()
#    country_id  snu_id  lgu_id        lgu_name
# 0           6     147     331          Alicia
# 1           6     142     320      Aloguinsan
# 2           6     143     280           Amlan
# 3           1      10     343  Augusto Corrêa
# 4           6     143     285         Ayungon

maa = get_query('managed_access_areas', 'GET')
# >>> maa.head()
#    country_id  snu_id  lgu_id  ma_id     ma_name
# 0           6     147     331  195.0      Alicia
# 1           6     142     320    4.0  Aloguinsan
# 2           5      15     105    5.0       Amdui
# 3           6     143     280    6.0       Amlan
# 4           5      15     105    7.0      Arawai
maa = maa.dropna()
maa['ma_id'] = maa['ma_id'].astype(int)

fish = get_query('join_fishbase_focal_species', 'GET')
# >>> fish.head()
#    country_id  fishbase_id                species species_local_name  ... is_focal   a   b  lmax
# 0         NaN         6205  Galaxias tanycephalus               None  ...        0 NaN NaN   NaN
# 1         NaN        11050      Galaxias zebratus               None  ...        0 NaN NaN   NaN
# 2         NaN        65787      Galeichthys trowi               None  ...        0 NaN NaN   NaN
# 3         NaN          808         Galeus murinus               None  ...        0 NaN NaN   NaN
# 4         NaN        27641        Gambusia beebei               None  ...        0 NaN NaN  5.53
