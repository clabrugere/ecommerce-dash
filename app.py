from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output
from src import config, data, plot, model

# Create app
app = dash.Dash(
    __name__,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width'}]
)
server = app.server
app.config.suppress_callback_exceptions = True

# load data
df = pd.read_csv(
    config.get_processed_filename(config.DATA_FILES['order'])
)
df[config.COLUMN_DATE] = df[config.COLUMN_DATE].apply(pd.to_datetime)

# -------------------------------------------------------------------------------
# layout
# -------------------------------------------------------------------------------
app.layout = html.Div([

    html.Div(id='output-clientside'),

    # title
    html.Div([
        html.H1('Sales overview')
    ]),

    # main container
    html.Div([

        # left panel
        html.Div([
            # date filter
            html.P(
                'Filter by order date',
                className='control_label'
            ),
            dcc.DatePickerRange(
                id='date_slider',
                display_format='D/M/Y',
                min_date_allowed=data.min_date(df),
                max_date_allowed=data.max_date(df),
                initial_visible_month=data.max_date(df),
                start_date=data.min_date(df),
                end_date=data.max_date(df),
                className='dcc_control'
            ),

            # payment type
            html.P(
                'Payment type',
                className='control_label'
            ),
            dcc.Dropdown(
                id='payment_type',
                options=data.values_to_options(data.payment_types(df)),
                multi=True,
                value=data.payment_types(df),
                className='dcc_control',
            ),

            # states
            html.P(
                'State',
                className='control_label'
            ),
            dcc.Dropdown(
                id='state',
                options=data.values_to_options(data.states(df)),
                multi=True,
                value=data.states(df),
                className='dcc_control',
            ),

            # product category
            html.P(
                'Product category',
                className='control_label'
            ),
            dcc.Dropdown(
                id='product_category',
                options=data.values_to_options(data.product_categories(df)),
                multi=True,
                value=data.product_categories(df),
                className='dcc_control',
            ),

        ],
            className='filters_container'),

        # right panel
        html.Div([

            # KPI container
            html.Div([
                # YTD sales
                html.Div(
                    [html.H2(id='kpi_sales_value'), html.H5('Revenue')],
                    id='kpi_sales', className='mini_container',
                ),
                # Average order value
                html.Div(
                    [html.H2(id='kpi_aov_value'), html.H5('Average order value')],
                    id='kpi_aov', className='mini_container',
                ),
                # Abandonment rate
                html.Div(
                    [html.H2(id='kpi_abandonment_value'), html.H5('Abandonment rate')],
                    id='kpi_abandonment', className='mini_container',
                ),
                # Customer lifetime value
                html.Div(
                    [html.H2(id='kpi_order_statisfaction'), html.H5('Orders satisfaction')],
                    id='kpi_order_satisfaction', className='mini_container',
                ),
            ],
                className='kpi_container'),

            dcc.Loading(
                id='loading',
                type='graph',
                children=[
                    # timeserie
                    html.Div([
                        html.H3('Sales'),
                        dcc.Graph(id='time_serie')
                    ],
                        className='graph_container'),

                    # sellers
                    html.Div([
                        html.H3('Sellers'),
                        dcc.Graph(id='sellers')
                    ],
                        className='graph_container'),

                    # states
                    html.Div([
                        dcc.Graph(id='states')
                    ],
                        className='graph_container'),

                    # products
                    html.Div([
                        html.H3('Product categories'),
                        html.Div(id='product_table'),
                    ],
                        className='graph_container'),
                ])
        ],
            className='right_panel')

    ],
        style={'display': 'flex', 'flex-direction': 'row'}),

])


# -------------------------------------------------------------------------------
# callbacks
# -------------------------------------------------------------------------------

# KPIs
@app.callback(
    Output('kpi_sales_value', 'children'),
    [
        Input('date_slider', 'start_date'),
        Input('date_slider', 'end_date'),
        Input('payment_type', 'value'),
        Input('product_category', 'value'),
        Input('state', 'value'),
    ],
)
def update_kpi_revenue(start_date, end_date, payment_type, product_category, state):
    dff = data.filter_dataframe(df, start_date, end_date, payment_type, product_category, customer_state=state)
    return f'R$ {data.revenue(dff):,.0f}'


@app.callback(
    Output('kpi_aov_value', 'children'),
    [
        Input('date_slider', 'start_date'),
        Input('date_slider', 'end_date'),
        Input('payment_type', 'value'),
        Input('product_category', 'value'),
        Input('state', 'value'),
    ],
)
def update_kpi_aov(start_date, end_date, payment_type, product_category, state):
    dff = data.filter_dataframe(df, start_date, end_date, payment_type, product_category, customer_state=state)
    aov = data.aov(dff)

    return f'R$ {aov:.0f}'


@app.callback(
    Output('kpi_abandonment_value', 'children'),
    [
        Input('date_slider', 'start_date'),
        Input('date_slider', 'end_date'),
        Input('payment_type', 'value'),
        Input('product_category', 'value'),
        Input('state', 'value'),
    ],
)
def update_kpi_abandonment(start_date, end_date, payment_type, product_category, state):
    dff = data.filter_dataframe(df, start_date, end_date, payment_type, product_category, customer_state=state)
    abandonment_rate = data.abandonment_rate(dff)

    return f'{abandonment_rate:.2f}%'


@app.callback(
    Output('kpi_order_statisfaction', 'children'),
    [
        Input('date_slider', 'start_date'),
        Input('date_slider', 'end_date'),
        Input('payment_type', 'value'),
        Input('product_category', 'value'),
        Input('state', 'value'),
    ],
)
def update_kpi_order_statisfaction(start_date, end_date, payment_type, product_category, state):
    dff = data.filter_dataframe(df, start_date, end_date, payment_type, product_category, customer_state=state)
    order_satisfaction = data.order_satisfaction(dff)

    return f'{order_satisfaction:.0f}%'


@app.callback(
    Output('time_serie', 'figure'),
    [
        Input('date_slider', 'start_date'),
        Input('date_slider', 'end_date'),
        Input('payment_type', 'value'),
        Input('product_category', 'value'),
        Input('state', 'value'),
    ],
)
def make_timeserie(start_date, end_date, payment_type, product_category, state):
    dff = data.filter_dataframe(df, start_date, end_date, payment_type, product_category, customer_state=state)
    
    if dff.equals(df):
        make_predictions = True
    else:
        make_predictions = False
    
    dff = dff[dff['order_status'].isin(config.ORDER_STATUS_CONSO)]
    dff = dff.groupby(pd.Grouper(key='order_purchase_timestamp', freq='1D')).agg({
        'payment_value': 'sum',
        'order_id': 'nunique'
    }).reset_index()
    
    if make_predictions:
        predictions = model.predict(dff['order_purchase_timestamp'], dff['payment_value'], look_ahead=15)

    fig = plot.sales_timeserie(dff, predictions)

    return fig


@app.callback(
    Output('states', 'figure'),
    [
        Input('date_slider', 'start_date'),
        Input('date_slider', 'end_date'),
        Input('payment_type', 'value'),
        Input('product_category', 'value'),
        Input('state', 'value'),
    ],
)
def make_states(start_date, end_date, payment_type, product_category, state):
    dff = data.filter_dataframe(df, start_date, end_date, payment_type, product_category, customer_state=state)
    dff_map = dff.groupby(['customer_state', 'state_name', 'lat', 'long'])['payment_value'].sum().reset_index()
    dff_map['text'] = dff_map['state_name'] + ': ' + dff_map['payment_value'].apply(lambda x: f'R$ {x:,.0f}')

    dff_time = dff.groupby(['customer_state', 'state_name', pd.Grouper(key='order_purchase_timestamp', freq='1M')])[
        'payment_value'].sum().reset_index()

    fig = plot.sales_map(dff_map, dff_time)

    return fig


@app.callback(
    Output('product_table', 'children'),
    [
        Input('date_slider', 'start_date'),
        Input('date_slider', 'end_date'),
        Input('payment_type', 'value'),
        Input('product_category', 'value'),
        Input('state', 'value'),
    ],
)
def make_product_categories(start_date, end_date, payment_type, product_category, state):
    dff = data.filter_dataframe(df, start_date, end_date, payment_type, product_category, customer_state=state)
    dff = dff[dff['order_status'].isin(config.ORDER_STATUS_CONSO)]

    dff = dff.groupby('product_category_name').agg(
        total_order_value=('payment_value', 'sum'),
        mean_order_value=('payment_value', 'mean'),
        n_customer=('customer_id', 'nunique'),
        n_order=('order_id', 'nunique'),
        n_seller=('seller_id', 'nunique'),
    ).reset_index().sort_values('total_order_value', ascending=False)

    dff['percentage_total'] = 100 * dff['total_order_value'] / dff['total_order_value'].sum()

    dff = dff.rename({
        'product_category_name': 'Product category',
        'total_order_value': 'Total order value',
        'mean_order_value': 'Mean order value',
        'n_customer': 'Number of customers',
        'n_order': 'Number of orders',
        'n_seller': 'Number of sellers'
    }, axis=1)
    dff = dff.round(2)

    datatable = dt.DataTable(
        columns=[
            {'name': i, 'id': i, 'deletable': False, 'selectable': True} for i in dff.columns
        ],
        data=dff.to_dict('records'),
        filter_action='native',
        sort_action='native',
        sort_mode='multi',
        page_current=0,
        style_cell={'fontSize': 12}
    )

    return datatable


@app.callback(
    Output('sellers', 'figure'),
    [
        Input('date_slider', 'start_date'),
        Input('date_slider', 'end_date'),
        Input('payment_type', 'value'),
        Input('product_category', 'value'),
        Input('state', 'value'),
    ],
)
def make_sellers(start_date, end_date, payment_type, product_category, state):
    dff = data.filter_dataframe(df, start_date, end_date, payment_type, product_category, customer_state=state)
    dff = dff[dff['order_status'].isin(config.ORDER_STATUS_CONSO)]

    df_seller_rank = dff.groupby('seller_id')['payment_value'].sum().reset_index().sort_values('payment_value',
                                                                                               ascending=False).head(10)

    df_seller_month = dff.loc[:, ['order_purchase_timestamp', 'seller_id', 'payment_value']]
    df_seller_month['month_no'] = df_seller_month['order_purchase_timestamp'].dt.month
    df_seller_month['month_name'] = df_seller_month['order_purchase_timestamp'].dt.month_name()
    df_seller_month = df_seller_month = df_seller_month.groupby(['month_no', 'month_name']).agg({
        'seller_id': 'nunique',
        'payment_value': 'mean'
    }).reset_index()

    fig = plot.sellers(df_seller_rank, df_seller_month)

    return fig


# -------------------------------------------------------------------------------
# main
# -------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
