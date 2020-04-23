import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import config


# TODO moving average as principal line
def sales_timeserie(df, predictions, plot_predictions=False):
    df_rolling_mean = df.set_index('order_purchase_timestamp')[['payment_value', 'order_id']].rolling(
        30).mean().dropna().reset_index()
    df_rolling_mean = df_rolling_mean.round(2)
    df = df.round(2)

    fig = make_subplots(specs=[[{'secondary_y': True}]])

    fig.add_trace(
        go.Bar(
            x=df['order_purchase_timestamp'], y=df['order_id'],
            name='Orders',
            marker_color='lightslategray',
            marker_opacity=.3,
        ),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(
            x=df['order_purchase_timestamp'], y=df['payment_value'],
            mode='lines',
            marker_opacity=.3,
            name='Revenue'
        ),
        secondary_y=False,
    )
    
    if plot_predictions:
        fig.add_trace(
            go.Scatter(
                x=predictions['date'], y=predictions['ci_high'],
                mode='lines',
                fill=None,
                line_width=0,
                name='Forecast 95% CI',
                showlegend=False,
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=predictions['date'], y=predictions['ci_low'],
                mode='lines',
                fill='tonexty',
                fillcolor='rgba(173,216,230,0.2)',
                line_width=0,
                name='Forecast 95% CI',
                showlegend=False,
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=predictions['date'], y=predictions['forecast'],
                mode='lines',
                line_color='#add8e6',
                line_dash='dot',
                marker_opacity=.5,
                name='15 days forecast'
            ),
            secondary_y=False,
        )
        
    fig.add_trace(
        go.Scatter(
            x=df_rolling_mean['order_purchase_timestamp'], y=df_rolling_mean['payment_value'],
            mode='lines',
            line_width=4,
            name='Moving mean (30 days)'
        ),
        secondary_y=False,
    )

    fig.update_layout(
        hovermode='x unified',
        autosize=True,
        margin=dict(
            l=30,
            r=30,
            b=20,
            t=40
        ),
        legend_orientation='h',
        plot_bgcolor='#F9F9F9',
        paper_bgcolor='#F9F9F9',
    )
    fig.update_yaxes(title_text='Revenue', secondary_y=False)
    fig.update_yaxes(title_text='Orders', secondary_y=True)

    return fig


# TODO orders on the map second
def sales_map(df_map, df_time):
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.3, 0.6],
        specs=[[{'type': 'scattergeo'}, {'type': 'scatter'}]],
    )

    fig.add_trace(
        go.Scattergeo(
            lat=df_map['lat'],
            lon=df_map['long'],
            text=df_map['text'],
            marker=dict(
                size=df_map['payment_value'],
                sizeref=df_map['payment_value'].min(),
                sizemode='area',
                color=df_map['state_name'].astype('category').cat.codes
            ),
            name='Map',
        ),
        row=1, col=1
    )

    for s in df_time['state_name'].unique():
        _df = df_time[df_time['state_name'] == s]

        fig.add_trace(
            go.Scatter(
                x=_df['order_purchase_timestamp'], y=_df['payment_value'],
                mode='markers',
                marker_opacity=.6,
                name=f'{s}',
            ),
        )

    fig.update_layout(
        showlegend=True,
        hovermode='closest',
        geo=dict(
            scope='south america',
            projection_type='equirectangular',
            showland=True,
            showocean=True,
            oceancolor='#F9F9F9',
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)',
        ),
        autosize=True,
        margin=dict(
            l=30,
            r=30,
            b=20,
            t=40
        ),
        plot_bgcolor='#F9F9F9',
        paper_bgcolor='#F9F9F9',
    )

    return fig


# top sellers and number of sellers per month in a radarplot (sales)
def sellers(df_seller_rank, df_seller_month):
    df_seller_rank = df_seller_rank.sort_values('payment_value')

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'bar'}, {'type': 'barpolar'}]],
    )

    fig.add_trace(
        go.Bar(
            x=df_seller_rank['payment_value'].round(),
            y=df_seller_rank['seller_id'],
            orientation='h',
            name='Revenues from top sellers',
            text=df_seller_rank['payment_value'].round(),
            textposition='auto',
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Barpolar(
            r=df_seller_month['seller_id'].round(),
            theta=df_seller_month['month_name'],
            name='Number of sellers'
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Barpolar(
            r=df_seller_month['payment_value'].round(2),
            theta=df_seller_month['month_name'],
            name='Mean revenue per seller'
        ),
        row=1, col=2
    )

    fig.update_layout(
        legend_orientation='h',
        autosize=True,
        margin=dict(
            l=30,
            r=30,
            b=20,
            t=40
        ),
        hovermode='closest',
        plot_bgcolor='#F9F9F9',
        paper_bgcolor='#F9F9F9',
    )

    return fig
