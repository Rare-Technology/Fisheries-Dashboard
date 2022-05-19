import requests
import configparser
import pandas as pd
import json
import time

cfg = configparser.ConfigParser(interpolation = None)
cfg.read('secret.ini')
dw_key = cfg.get('dw', 'API_KEY')

HEADERS = {
    'Authorization': 'Bearer ' + dw_key,
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:99.0) Gecko/20100101 Firefox/99.0'
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
    'join_ourfish_footprint_fishbase': "63cec79b-14de-4197-85f0-ee83f9ce16c0",
    'join_fishbase_focal_species': '9315ae27-8978-4525-b77e-e2072fdc10f9'
}


def get_data(query_file_name, endpoint, request_method, params = None):
    """
    Make a REST API request to data.world to retrieve data.

    ===== Keyword Arguments =====
    query_name: a key from QUERY_ID or a file name
    endpoint: 'query' or 'file'
    request_method: "GET" or "POST"
    params: Parameters for a "POST" query. Dict in the form of {param: value, ...}.
        This function handles formatting the parameter payload properly.

    returns: Query/download results as a pd.DataFrame
    """
    if endpoint == 'query':
        query_id = QUERY_ID[query_file_name]
        url = 'https://api.data.world/v0/queries/' + query_id + '/results'

        if request_method == "GET":
            response = requests.request("GET", url, headers = HEADERS)
        elif request_method == "POST":
            payload = json.dumps({'parameters': params})
            response = requests.request("POST", url, data = payload, headers = HEADERS)
    elif endpoint == 'file':
        url = 'https://api.data.world/v0/file_download/rare/fisheries-dashboard/' + query_file_name
        response = requests.request("GET", url, headers = HEADERS)

    data = response.json()
    data = pd.json_normalize(data)

    return data

countries = get_data('countries', 'query', 'GET')
# >>> countries.head()
#    country_id                    country_name
# 0           1                          Brazil
# 1          15  Federated States of Micronesia
# 2           4                       Guatemala
# 3           3                        Honduras
# 4           5                       Indonesia

snu = get_data('subnational_units', 'query', 'GET')
# >>> snu.head()
#    country_id  snu_id         snu_name
# 0           6     145          Antique
# 1           3      19        Atlántida
# 2           6     149  Camarines Norte
# 3           6     148    Camarines Sur
# 4           6     142             Cebu

lgu = get_data('local_government_units', 'query', 'GET')
# >>> lgu.head()
#    country_id  snu_id  lgu_id        lgu_name
# 0           6     147     331          Alicia
# 1           6     142     320      Aloguinsan
# 2           6     143     280           Amlan
# 3           1      10     343  Augusto Corrêa
# 4           6     143     285         Ayungon

maa = get_data('managed_access_areas', 'query', 'GET')
# >>> maa.head()
#    country_id  snu_id  lgu_id  ma_id     ma_name
# 0           6     147     331  195.0      Alicia
# 1           6     142     320    4.0  Aloguinsan
# 2           5      15     105    5.0       Amdui
# 3           6     143     280    6.0       Amlan
# 4           5      15     105    7.0      Arawai
maa = maa.dropna()
maa['ma_id'] = maa['ma_id'].astype(int)

all_data = get_data('join_ourfish_footprint_fishbase', 'query', 'GET')
# >>> all_data.head()
#                                      id        date  country_id  snu_id  ...  is_focal         a         b        lmax
# 0  a1b2aa7d-e07d-4284-a0fc-47956e66578e  2020-01-07           5      14  ...         0  0.027600  2.920000   45.700001
# 1  b32fb39a-4ae6-4c85-a946-50ed01c59748  2020-01-12           5      14  ...         1  0.024838  2.908650   69.699997
# 2  ab716c01-63dc-4d8d-8025-e072219683cf  2021-06-22           5      14  ...         1  4.030300  2.255100         NaN
# 3  2b2770e4-2a1c-4280-8ab4-a7278b018a14  2019-08-23           5      14  ...         1  0.010241  2.951254  104.000000
# 4  4459de6a-03ab-413c-bb3c-81f45156ea4f  2020-10-29           5      14  ...         0  0.026400  2.860000   46.000000
# >>> all_data.columns
# Index(['id', 'date', 'country_id', 'snu_id', 'lgu_id', 'community_id',
#        'country', 'snu_name', 'lgu_name', 'community_name', 'buyer_id',
#        'fisher_id', 'gear_type', 'ma_id', 'ma_name', 'ma_lat', 'ma_lon',
#        'population', 'community_lat', 'community_lon', 'est_buyers',
#        'est_fishers', 'label', 'buying_unit', 'fishbase_id', 'weight_mt',
#        'count', 'total_price_usd', 'family_scientific', 'family_local',
#        'species_scientific', 'species_local', 'is_focal', 'a', 'b', 'lmax'],
#       dtype='object')
# Takes approx 15s to get the query result
# 
# all_data['date'] = all_data['date'].apply(
#     datetime.date.fromisoformat
# ).sort_values().apply(
#     lambda x: x.strftime("%b %Y")
# )
# all_data = all_data[['country', 'date', 'weight_mt']].groupby(
#     by = ['country', 'date']
# ).sum().reset_index()
