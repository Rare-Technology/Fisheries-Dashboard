import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

COLORS = {
    'rare-blue': '#005BBB',
    'rare-green': '#008542',
    'rare-gray': '#5E6A71',
    'secondary-red': '#AA1948',
    'secondary-blue': '#00AFD8',
    'secondary-orange': '#F58233'
}

pretty_template = {
    'layout': {
        'paper_bgcolor': '#e5f7fa',
        'plot_bgcolor': '#e5f7fa',
        'yaxis': {
            'gridcolor': COLORS['rare-gray']
        },
        'xaxis': {
            'gridcolor': COLORS['rare-gray']
        }
    }
}

def get_catch_data(data):
    """
    Monthly catch weight

    Example output:
         yearmonth   weight_mt
    0   2019-01-01    0.101200
    1   2019-02-01    0.582100
    2   2019-03-01    3.852917
    3   2019-04-01    8.212560
    4   2019-05-01   17.535412
    """
    return (data
        .loc[:, ['yearmonth', 'weight_mt']]
        .groupby('yearmonth')
        .sum()
        .reset_index())

def get_cpue_value_data(data):
    """
    Calculate CPUE and "VPUE" (value per unit effort)
    Our current working definition of unit effort is a boat (a group of fishers)
    
    (monthly) CPUE = (monthly catch weight) / (num boats) = mean(monthly catch weight per boat)
    (monthly) VPUE = (monthly catch value) / (num boats) = mean(monthly catch value per boat)
                   
    where a boat is represented by a unique fisher_id. So first we find how much each boat caught each month,
    then take the average within each month.

    Example output:
         yearmonth  cpue_kg_boat  ste_cpue_kg_boat  avg_catch_value_usd  ste_catch_value_usd
    0   2019-01-01     12.650000          6.527469            52.696180            29.298693
    1   2019-02-01     22.388462          5.458381            82.476161            15.578747
    2   2019-03-01     25.182462          2.339142            64.142291             6.472819
    3   2019-04-01     40.257645          6.780494            94.859590            18.729878
    4   2019-05-01     56.023681          5.858671           116.990813            15.688032
    """
    return (data
    .assign(weight_kg = lambda x: 1e3*x['weight_mt'])
    .loc[:, [
        'yearmonth',
        'fisher_id',
        'weight_kg',
        'total_price_usd'
    ]].groupby(
        by = ['yearmonth', 'fisher_id'],
        dropna = False # do not remove rows where one of the grouping variables is NA
    ).sum()
    .groupby('yearmonth')
    .agg(
        # Take averages and standard errors across boats each month
        cpue_kg_boat = ('weight_kg', 'mean'),
        ste_cpue_kg_boat = ('weight_kg', 'sem'),
        avg_catch_value_usd = ('total_price_usd', 'mean'),
        ste_catch_value_usd = ('total_price_usd', 'sem')
    ).reset_index())

def get_length_data(data):
    """
    Extract length information using the weight-length relation, then create dataframes
    for calculating average lengths and proportion of mature population using the Froese-Binohlan relations.
    Return the join of these two datasets.

    The weight-length relation is

    W = a*L^b ---> L = (W/a)^(1/b)

    where L in in cm and W is in g. Since each sample accounts for multiple fish, we will
    have to normalize the weight using the `count` column.

    The Froese-Binohlan relations are

    Linf = 10^(0.044 + 0.9841*log10(Lmax))
    Lmat = 10^(0.8979*log10(Linf) - 0.0782)

    Example output:
        yearmonth    avg_length  Pmat
    0   2019-01-01   25.201645   5.190311
    1   2019-02-01   21.532064  17.983193
    2   2019-03-01   13.597551   5.436279
    3   2019-04-01   20.008063   9.200271
    4   2019-05-01   24.545225  24.774686
    """
    lengths = (data
    .query(
        "count > 0 & \
        a > 0 & \
        b > 0 & \
        weight_mt > 0"
    ).assign(
        # 1e6 to go from mt to g
        length_cm = lambda x: np.power(1e6*x['weight_mt']/x['count']/x['a'], 1/x['b'])
    ).loc[:, [
        'date',
        'yearmonth',
        'ma_id',
        'fishbase_id',
        'length_cm',
        'count',
        'lmax'
    ]].query( "~length_cm.isna()"))

    avg_length = (lengths
    .assign(weighted_length = lambda x: x['length_cm'] * x['count'])
    .groupby('yearmonth')
    .agg(
        weighted_length = ('weighted_length', 'sum'),
        count = ('count', 'sum')
    ).assign(avg_length = lambda x: x['weighted_length'] / x['count'])
    .loc[:, ['avg_length']])

    lengths = lengths.query("lmax > 0")

    prop_mature = (lengths
    .assign(
        linf = lambda x: np.power(10, 0.044 + 0.9841*np.log10(x['lmax'])),
        lmat = lambda x: np.power(10, 0.8979*np.log10(x['linf']) - 0.0782),
        count_mature = lambda x: x['count'] * (x['length_cm'] > x['lmat'])
    ).groupby('yearmonth')
    .agg(
        count = ('count', 'sum'),
        count_mature = ('count_mature', 'sum')
    ).assign(Pmat = lambda x: 100 * x['count_mature'] / x['count'])
    .loc[:, ['Pmat']])

    length_data = avg_length.join(prop_mature, how='outer').reset_index()

    return length_data

def get_composition_data(data):
    """
    Get top 10 species by catch weight

    Example output:
               species_scientific  is_focal                                      species_local   weight_mt
    378         Thunnus albacares         0  Balangkuni/Bankulis/Bantalaan/Thaninga/Tuna/Tu...  104.234600
    52          Carassius auratus         0                     Caxuxo/Chipandavuma/Salamuamba  102.214500
    90      Decapterus macarellus         1                                         Galunggong   79.778600
    155        Katsuwonus pelamis         1                                              Bulis   75.813680
    40    Carangoides malabaricus         0         Bubara/Cepa/Cheleua/Enthare/Ninthare/Xereu   69.117400
    """
    return (data
    .loc[:, [
        "species_local",
        "is_focal",
        "species_scientific",
        "weight_mt"
    ]].groupby("species_scientific")
    .agg({
        "is_focal": "max", # basically, the identity; is_focal is unique per species
        "species_local": lambda x: "/".join(np.unique(x)),
        "weight_mt": "sum"
    }).reset_index()
    .sort_values(
        by = 'weight_mt',
        axis = 0,
        ascending = False
    ).iloc[:10,])

def make_catch_fig(catch_data):
    """
    Put catch data on a bar plot
    """
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x = catch_data['yearmonth'],
        y = catch_data['weight_mt'],
        marker_color = COLORS['rare-blue']
    ))

    fig.update_layout(
        title = "Total Catch per Month (metric tons)",
        xaxis_title = "",
        height = 400
    )

    fig.update_xaxes(fixedrange = True)
    fig.update_yaxes(fixedrange = True)

    return fig

def make_cpue_value_fig(cpue_value_data):
    """
    Put CPUE/value data on a line plot
    """
    fig = make_subplots(specs = [[{'secondary_y': True}]])
    fig.add_trace(
        go.Scatter(
            x = cpue_value_data['yearmonth'],
            y = cpue_value_data['cpue_kg_boat'],
            name = 'CPUE (kg/boat)',
            marker_color = COLORS['rare-blue'],
            yaxis = 'y'
        ), secondary_y = False
    )
    fig.add_trace(
        go.Scatter(
            x = cpue_value_data['yearmonth'],
            y = cpue_value_data['avg_catch_value_usd'],
            name = 'Catch Value (USD/boat)',
            marker_color = COLORS['secondary-red'],
            yaxis = 'y2'
        ), secondary_y = True
    )
    fig.update_layout(
        title = 'CPUE and Catch Value per Boat',
        xaxis_title = '',
        yaxis = {
            'titlefont': {
                'color': COLORS['rare-blue']
            },
            'tickfont': {
                'color': COLORS['rare-blue']
            },
            'nticks': 4
        },
        yaxis2 = {
            'titlefont': {
                'color': COLORS['secondary-red']
            },
            'tickfont': {
                'color': COLORS['secondary-red']
            },
            'nticks': 4
        },
        legend = {
            'orientation': 'h'
        },
        height = 400
    )

    fig.update_xaxes(fixedrange = True)
    fig.update_yaxes(fixedrange = True)

    return fig

def make_length_fig(length_data):
    """
    Put length data on a line plot
    """
    fig = make_subplots(specs = [[{'secondary_y': True}]])
    fig.add_trace(
        go.Scatter(
            x = length_data['yearmonth'],
            y = length_data['avg_length'],
            name = 'Average length (cm)',
            marker_color = COLORS['rare-blue']
        ), secondary_y = False
    )
    fig.add_trace(
        go.Scatter(
            x = length_data['yearmonth'],
            y = length_data['Pmat'],
            name = '% Mature',
            marker_color = COLORS['secondary-red']
        ), secondary_y = True
    )
    fig.update_layout(
        title = 'Average Length and % Mature',
        xaxis_title = '',
        xaxis = {
            'zerolinecolor': '#ffffff'
        },
        yaxis = {
            'titlefont': {
                'color': COLORS['rare-blue']
            },
            'tickfont': {
                'color': COLORS['rare-blue']
            }
        },
        yaxis2 = {
            'titlefont': {
                'color': COLORS['secondary-red']
            },
            'tickfont': {
                'color': COLORS['secondary-red']
            },
        },
        legend = {'orientation': 'h'},
        height = 400
    )

    fig.update_xaxes(fixedrange = True)
    fig.update_yaxes(fixedrange = True)

    return fig

def make_composition_fig(comp_data):
    """
    Put composition data on a pie chart
    """
    fig = go.Figure(data = [go.Pie(
        labels = comp_data['species_scientific'],
        values = comp_data['weight_mt'],
        hole = 0.5,
    )])

    fig.update_traces(
        hoverinfo = 'label+value',
        textinfo = 'percent',
        marker = dict(
            line = dict(
                color = '#e5f7fa',
                width = 2
            )
        )
    )

    fig.update_layout(title = "Catch Composition (Top 10, metric tons)")

    return fig
