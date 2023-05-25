import requests
import os
import pandas as pd
import numpy as np
import json
import datetime

def get_ourfish_data():
    """
    Pull full OurFish data from data.world. Return the OF data.

    Data source: join_ourfish_footprint_fishbase from https://data.world/rare/ourfish
    """
    all_data = pd.read_csv('https://query.data.world/s/mlrbseaz6qipapni2wh7bp6m6eqkv2?dws=00000')
    # >>> all_data.head()
    #                                          id        date  country_id  snu_id  ...         a         b   lmax hide
    # 0  8be7aa9a-58ef-4972-950d-dd33cff6cd1c  2020-03-17           6     143  ...  0.004262  3.325280    7.6  NaN
    # 1  02910cce-7508-4a92-9d20-d68af3321f9f  2020-03-02           6     143  ...       NaN       NaN    NaN  NaN
    # 2  3a0d62c8-672d-413a-a652-a7a78a7c28dd  2021-04-11           6     145  ...  0.024523  2.949499   69.0  NaN
    # 3  56a6ed9c-5dcf-46f8-bb0c-4957f46942e8  2022-09-19           7      25  ...  0.010241  2.951254  104.0  NaN
    # 4  0d4787fd-aed8-41d9-a683-090d2b9c7885  2022-11-28           7      25  ...  0.010241  2.951254  104.0  NaN    # >>> all_data.columns
    # [5 rows x 39 columns]
    # >>> all_data.columns
    # Index(['id', 'date', 'country_id', 'snu_id', 'lgu_id', 'community_id',
    #    'country', 'snu_name', 'lgu_name', 'community_name', 'ma_id', 'ma_name',
    #    'ma_lat', 'ma_lon', 'population', 'community_lat', 'community_lon',
    #    'est_buyers', 'est_fishers', 'buyer_id', 'buyer_name', 'buyer_gender',
    #    'fisher_id', 'buying_unit', 'fishbase_id', 'weight_kg', 'weight_lbs',
    #    'count', 'total_price_local', 'total_price_usd', 'family_scientific',
    #    'family_local', 'species_scientific', 'species_local', 'is_focal', 'a',
    #    'b', 'lmax', 'hide'],
    #   dtype='object')   
    # Takes approx 15s to get the query result

    # The next few lines trigger this warning
    #   A value is trying to be set on a copy of a slice from a DataFrame.
    #   Try using .loc[row_indexer,col_indexer] = value instead
    # Even though I'm following their instructions?? Stack overflow said to use
    # df.assign() but that increased memory usage a little bit
    # These column assignments aren't causing any issue right now, so we're just
    # going to hush the warnings so that the logs aren't clogged.
    pd.set_option('mode.chained_assignment', None)
    all_data = all_data.query("~date.isna()")
    all_data.loc[:, 'date'] = all_data.loc[:,'date'].apply(datetime.date.fromisoformat)
    all_data.loc[:,'yearmonth'] = all_data.loc[:,'date'].apply(lambda x: datetime.date(x.year, x.month, 1))
    # Thu May 25 2023
    # Using a new table now but it has 742 missing ma_id's that were not in the previous dataset.
    # George looking into this, for now we are taking these out but ideally this next line won't be needed after
    all_data = all_data.query("~ma_id.isna()") 
    all_data.loc[:,'ma_id'] = all_data.loc[:,'ma_id'].astype(int)

    all_data["weight_mt"] = all_data.loc[:, "weight_kg"]/1e3

    return all_data

def get_geo_data(all_data):
    """
    Use `all_data` to return a dictionary of tables related to geography:

    - countries
    - snu: Subnational units
    - lgu: Local government units
    - maa: Managed access areas
    - comm: Communities
    """
    countries = all_data[['country_id', 'country']].drop_duplicates().rename(
        {'country': 'country_name'}, axis = 1
    ).reset_index(drop = True)

    snu = all_data[['country_id', 'snu_id', 'snu_name']].drop_duplicates().reset_index(drop = True)

    lgu = all_data[['country_id', 'snu_id', 'lgu_id', 'lgu_name']].drop_duplicates().reset_index(drop = True)

    ### May 19 2022
    # There are 2695 records with a blank ma. Some communities just haven't been assigned one
    # in the MA+R tracker; it is up to country teams to complete their data management.
    maa = all_data[['country_id', 'snu_id', 'lgu_id', 'ma_id', 'ma_name', 'ma_lat', 'ma_lon']].drop_duplicates().reset_index(drop = True)
    maa['ma_lat'] = maa['ma_lat'].fillna(0)
    maa['ma_lon'] = maa['ma_lon'].fillna(0)
    maa["ma_name"] = maa["ma_name"].fillna("Unspecified")
    maa = maa.dropna()

    comm = all_data[['country_id', 'snu_id', 'lgu_id', 'ma_id', 'community_id', 'community_name', 'community_lat', 'community_lon', 'population']].drop_duplicates().reset_index(drop = True)
    comm = comm.query("~community_lat.isna() & ~community_lon.isna()")

    tables = {
        "country": countries,
        "snu": snu,
        "lgu": lgu,
        "maa": maa,
        "comm": comm
    }
    
    return tables