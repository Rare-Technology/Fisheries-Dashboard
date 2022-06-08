def get_map_data(data, maa):
    return (
        data.assign(weight_kg = lambda x: 1000*x['weight_mt'])
        .loc[:, ['ma_id', 'weight_kg']]
        .groupby('ma_id')
        .sum()
        .reset_index()
        .join(maa[['ma_id', 'ma_name', 'ma_lat', 'ma_lon']].set_index('ma_id'), on = 'ma_id')
        .query("ma_lat != 0 & ma_lon != 0")
        .reset_index(drop = False)
    )
