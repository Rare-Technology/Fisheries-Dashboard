import requests
import os
import pandas as pd
import numpy as np
import json
import datetime

### TODO:
# Compile list of demo accounts (typically buyers I think)
# Filter out transactions with these accounts
# demoMAR

def process_init_data():
    # TODO figure out what needs to be returned and how to make the other files
    # that import from here work (mod_higlights, mod_plot, mod_filters, mod_map)
    # Pull data from data.world and clean it a bit. Will have to call this
    # on every page load, so probably will go into serve_layout() from app.py

    fishers = pd.read_csv('https://query.data.world/s/q4i5ndlwyhoqkcjpfee5buncfu5icn')
    fishers = fishers[['fisher_id', 'gender']].drop_duplicates()
    # >>> fishers.head()
    #            fisher_id gender
    # 0  CN-MR-001978-2015      m
    # 1  CN-MR-001965-2015      m
    # 2  CN-MR-001967-2015      m
    # 3  CN-MR-001972-2015      m
    # 4  CN-MR-001962-2015      f

    all_data = pd.read_csv('https://query.data.world/s/43qwgxsrhlmxvpumqqb3wifgfmawsa')
    # all_data = pd.read_csv('all_data.csv')
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

    # The next few lines trigger this warning
    #   A value is trying to be set on a copy of a slice from a DataFrame.
    #   Try using .loc[row_indexer,col_indexer] = value instead
    # Even though I'm following their instructions?? Stack overflow said to use
    # df.assign() but that increased memory usage a little bit
    # These column assignments aren't causing any issue right now, so we're just
    # going to hush the warnings so that the logs aren't clogged.
    pd.set_option('mode.chained_assignment', None)
    all_data.loc[:, 'date'] = all_data.loc[:,'date'].apply(datetime.date.fromisoformat)
    all_data.loc[:,'yearmonth'] = all_data.loc[:,'date'].apply(lambda x: datetime.date(x.year, x.month, 1))
    all_data.loc[:,'ma_id'] = all_data.loc[:,'ma_id'].astype(int)

    all_data = all_data.join(fishers.set_index('fisher_id'), on = 'fisher_id')

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
    maa = maa.dropna()

    comm = all_data[['country_id', 'snu_id', 'lgu_id', 'ma_id', 'community_id', 'community_name', 'community_lat', 'community_lon', 'population']].drop_duplicates().reset_index(drop = True)
    comm = comm.query("~community_lat.isna() & ~community_lon.isna()")

    # choose start and end dates to initially show the past 6 months of data
    end_date = all_data['date'].max()
    if end_date.month >= 6:
        start_date = datetime.date(end_date.year, end_date.month - 5, 1)
    else:
        start_date = datetime.date(end_date.year - 1, end_date.month + 7, 1)
    init_data = all_data.query(
        "ma_id.isin(list(@maa['ma_id'])) & \
        @start_date <= date & \
        date <= @end_date"
    )

    return countries, snu, lgu, maa, comm, all_data, init_data
