import datadotworld as dw

data = dw.load_dataset('rare/fisheries-dashboard', auto_update = True)
# LazyLoadedDict( 'join_fishbase_focal_species': LazyLoadedValue(<pandas.DataFrame>), 'join_fishers_footprint': LazyLoadedValue(<pandas.DataFrame>), 'join_footprint_ma': LazyLoadedValue(<pandas.DataFrame>), 'join_ourfish_footprint': LazyLoadedValue(<pandas.DataFrame>), 'join_ourfish_footprint_fishbase': LazyLoadedValue(<pandas.DataFrame>), 'local_government_units': LazyLoadedValue(<pandas.DataFrame>), 'managed_access_areas': LazyLoadedValue(<pandas.DataFrame>), 'mature_in_catch': LazyLoadedValue(<pandas.DataFrame>), 'ourfish_focal': LazyLoadedValue(<pandas.DataFrame>), 'subnational_units': LazyLoadedValue(<pandas.DataFrame>)})


countries = data.dataframes['countries']
# >>> data.dataframes['countries'].head()
#    country_id                    country_name
# 0           1                          Brazil
# 1          15  Federated States of Micronesia
# 2           4                       Guatemala
# 3           3                        Honduras
# 4           5                       Indonesia

snu = data.dataframes['subnational_units']
# >>> data.dataframes['subnational_units'].head()
#    country_id  snu_id         snu_name
# 0           6     145          Antique
# 1           3      19        Atlántida
# 2           6     149  Camarines Norte
# 3           6     148    Camarines Sur
# 4           6     142             Cebu

lgu = data.dataframes['local_government_units']
# >>> data.dataframes['local_government_units'].head()
#    country_id  snu_id  lgu_id        lgu_name
# 0           6     147     331          Alicia
# 1           6     142     320      Aloguinsan
# 2           6     143     280           Amlan
# 3           1      10     343  Augusto Corrêa
# 4           6     143     285         Ayungon

maa = data.dataframes['managed_access_areas']
# >>> data.dataframes['managed_access_areas'].head()
#    country_id  snu_id  lgu_id  ma_id     ma_name
# 0           6     147     331  195.0      Alicia
# 1           6     142     320    4.0  Aloguinsan
# 2           5      15     105    5.0       Amdui
# 3           6     143     280    6.0       Amlan
# 4           5      15     105    7.0      Arawai
