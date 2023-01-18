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
    return data.loc[:,
        ['yearmonth', 'weight_mt']
    ].groupby(
        by = ['yearmonth']
    ).sum().reset_index()

def get_cpue_value_data(data):
    """
    Calculate CPUE and "VPUE" (value per unit effort)
    Unit effort is a boat (a group of fishers)
    
    (monthly) CPUE = (monthly catch weight) / (num boats)
    (monthly) VPUE = (monthly catch value) / (num boats)
                   
    where a boat is represented by a unique fisher_id
    """
    return data.assign(
        weight_kg = lambda x: 1e3*x['weight_mt']
    ).loc[:, [
        'yearmonth',
        'fisher_id',
        'weight_kg',
        'total_price_usd'
    ]].groupby(
        by = ['yearmonth', 'fisher_id'],
        dropna = False # do not remove rows where one of the grouping variables is NA
    ).sum().groupby(
        by = ['yearmonth'],
    ).agg(
        # Take averages and standard errors across boats each month
        cpue_kg_boat = ('weight_kg', 'mean'),
        ste_cpue_kg_boat = ('weight_kg', 'sem'), # DataFrame.std() uses bias corrected stddev, pd.std does not
        avg_catch_value_usd = ('total_price_usd', 'mean'),
        ste_catch_value_usd = ('total_price_usd', 'sem')
    ).reset_index()

def get_length_data(data):
    """
    Extract length information using weight and ecological factors, then create dataframes
    for calculating average lengths and proportion of mature population. Return the join of
    these two datasets.
    """
    lengths = data.query(
        "~count.isna() & \
        count != 0 & \
        ~a.isna() & \
        a != 0 & \
        ~b.isna() & \
        b != 0 & \
        weight_mt != 0"
    ).assign(
        length_cm = lambda x: np.exp(np.log(1e6*x['weight_mt']/x['count']/x['a'])/x['b'])
    ).loc[:, [
        'date',
        'yearmonth',
        'ma_id',
        'fishbase_id',
        'length_cm',
        'count',
        'lmax'
    ]].query(
        "~length_cm.isna()"
    ).reset_index(drop = True)

    avg_length_data = lengths.assign(
        weighted_length = lambda x: x['length_cm'] * x['count']
    ).groupby(
        by = ['yearmonth']
    ).agg(
        weighted_length = ('weighted_length', 'sum'),
        count = ('count', 'sum')
    ).assign(
        avg_length = lambda x: x['weighted_length'] / x['count']
    )

    lengths = lengths.query("~lmax.isna()").reset_index(drop = True)

    prop_mature = lengths.assign(
        linf = lambda x: np.power(10, 0.044 + 0.9841*np.log10(x['lmax'])),
        lmat = lambda x: np.power(10, 0.8979*np.log10(x['linf']) - 0.0782),
        count_mature = lambda x: x['count'] * (x['length_cm'] > x['lmat'])
    ).groupby(
        by = ['yearmonth']
    ).agg(
        count = ('count', 'sum'),
        count_mature = ('count_mature', 'sum')
    ).assign(
        Pmat = lambda x: 100 * x['count_mature'] / x['count']
    ).loc[:, ['Pmat']]

    length_data = prop_mature.join(avg_length_data['avg_length'], how = 'inner').reset_index()

    return length_data

def get_composition_data(data):
    # The plot numbers look different from the old dashboard because the old dashboard
    # has a bug in the SQL code that double counts the weight any species that are non-focal
    return (data
        .loc[:, [
            "family_scientific", # for later...
            "species_local",
            "is_focal",
            "species_scientific",
            "weight_mt"
        ]]
        .groupby(["species_scientific"])
        .agg({
            "is_focal": "max", # basically, the identity; is_focal is unique per species
            "species_local": lambda x: "/".join(np.unique(x)),
            "weight_mt": "sum"
        })
        .reset_index()
        .sort_values(
            by = ['weight_mt'],
            axis = 0,
            ascending = False
        )
        .iloc[:10,]
    )

def make_catch_fig(catch_data):
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
