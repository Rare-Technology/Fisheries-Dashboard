def get_map_data(data, maa):
    return (
        data[['ma_id', 'weight_mt']]
        .groupby('ma_id')
        .sum()
        .reset_index()
        .join(maa[['ma_id', 'ma_name', 'ma_lat', 'ma_lon']].set_index('ma_id'), on = 'ma_id')
    )
