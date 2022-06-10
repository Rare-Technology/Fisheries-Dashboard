import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

pretty_template = {
    'layout': {
        'paper_bgcolor': '#e5f7fa',
        'plot_bgcolor': '#e5f7fa',
        'yaxis': {
            'gridcolor': '#5E6A71'
        },
        'xaxis': {
            'gridcolor': '#5E6A71'
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
    return data.assign(
        weight_kg = lambda x: 1e3*x['weight_mt']
    ).loc[:, [
        'date',
        'yearmonth',
        'fisher_id',
        'ma_id', # restructure ma filtering to use id's -> use less memory, increase speed?
        'fishbase_id',
        'weight_kg',
        'total_price_usd'
    ]].groupby(
        by = ['yearmonth', 'date', 'fisher_id', 'ma_id', 'fishbase_id'],
        dropna = False # do not remove rows where one of the grouping variables is NA
    ).sum().groupby(
        by = ['yearmonth'],
    ).agg(
        avg_cpue_kg_trip = ('weight_kg', 'median'), # numbers differ slightly from old dashboard bc the query it pulls from uses SQL's APPROX_MEDIAN
        ste_cpue_kg_trip = ('weight_kg', 'sem'), # DataFrame.std() uses bias corrected stddev, pd.std does not
        avg_catch_value_usd = ('total_price_usd', 'median'),
        ste_catch_value_usd = ('total_price_usd', 'sem')
    ).reset_index()

def get_length_data(data):
    """
    Extract length information using weight and ecological factors, then create dataframes
    for calculating median lengths and proportion of mature population. Return the join of
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

    median_length_data = lengths.take(
        lengths.index.repeat(
            lengths['count']
        )
    ).groupby(
        by = ['yearmonth']
    ).agg(
        med_length_cm = ('length_cm', 'median')
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

    length_data = prop_mature.join(median_length_data, how = 'inner').reset_index()

    return length_data

def get_composition_data(data):
    # The plot numbers look different from the old dashboard because the old dashboard
    # has a bug in the SQL code that double counts the weight any species that are non-focal
    return (data
        .loc[:, [
            'family_scientific', # for later...
            'species_local',
            'is_focal',
            'species_scientific',
            'weight_mt'
        ]]
        .groupby(['is_focal', 'species_local', 'species_scientific']).sum()
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
        marker_color = '#005BBB'
    ))

    fig.update_layout(
        title = "Total Catch per Month (metric tons)",
        xaxis_title = "",
        template = pretty_template
    )

    fig.update_xaxes(fixedrange = True)
    fig.update_yaxes(fixedrange = True)

    return fig

def make_cpue_value_fig(cpue_value_data):
    fig = make_subplots(specs = [[{'secondary_y': True}]])
    fig.add_trace(
        go.Scatter(
            x = cpue_value_data['yearmonth'],
            y = cpue_value_data['avg_cpue_kg_trip'],
            name = 'CPUE',
            marker_color = '#5cb9ea'
        ), secondary_y = False
    )
    fig.add_trace(
        go.Scatter(
            x = cpue_value_data['yearmonth'],
            y = cpue_value_data['avg_catch_value_usd'],
            name = 'Catch Value',
            marker_color = '#f47762'
        ), secondary_y = True
    )
    fig.update_layout(
        title = 'Average CPUE per Trip and Average Catch Value',
        xaxis_title = '',
        yaxis = {
            'title': 'CPUE (kg/trip)',
            'titlefont': {
                'color': '#5cb9ea'
            },
            'tickfont': {
                'color': '#5cb9ea'
            }
        },
        yaxis2 = {
            'title': 'Catch Value (USD)',
            'titlefont': {
                'color': '#f47762'
            },
            'tickfont': {
                'color': '#f47762'
            }
        },
        template = pretty_template
    )

    fig.update_xaxes(fixedrange = True)
    fig.update_yaxes(fixedrange = True)

    return fig

def make_length_fig(length_data):
    fig = make_subplots(specs = [[{'secondary_y': True}]])
    fig.add_trace(
        go.Scatter(
            x = length_data['yearmonth'],
            y = length_data['med_length_cm'],
            name = 'Median length',
            marker_color = '#5cb9ea'
        ), secondary_y = False
    )
    fig.add_trace(
        go.Scatter(
            x = length_data['yearmonth'],
            y = length_data['Pmat'],
            name = '% Mature',
            marker_color = '#f47762'
        ), secondary_y = True
    )
    fig.update_layout(
        title = 'Median Length and Proportion of Mature Catch',
        xaxis_title = '',
        yaxis = {
            'title': 'Median Length (cm)',
            'titlefont': {
                'color': '#5cb9ea'
            },
            'tickfont': {
                'color': '#5cb9ea'
            }
        },
        yaxis2 = {
            'title': '% Mature',
            'titlefont': {
                'color': '#f47762'
            },
            'tickfont': {
                'color': '#f47762'
            }
        },
        template = pretty_template
    )

    fig.update_xaxes(fixedrange = True)
    fig.update_yaxes(fixedrange = True)

    return fig

def make_composition_fig(comp_data):
    fig = px.pie(
        comp_data,
        names = 'species_scientific',
        values = 'weight_mt',
        hole = 0.5,
        title = "Catch Composition (Top 10, metric tons)"
    )

    fig.update_layout(template = pretty_template)

    return fig
