import pandas as pd
from dash.dependencies import Input, Output
from app import app
from src import config, data

from datetime import datetime

# -------------------------------------------------------------------------------------------
# KPIs
# -------------------------------------------------------------------------------------------
@app.callback(
    Output("kpi_sales_value", "children"),
    [
        Input('payment_type', 'value'),
        Input('product_category', 'value'),
        Input('state', 'value'),
    ],
)
def update_kpi_sales(payment_type, product_category, state):
    #dff = data.filter_dataframe(df, start_date, end_date, payment_type, product_category, customer_state=state)
    return "test"
    #return data.compute_revenue(df)


@app.callback(
    Output("kpi_aov_value", "children"),
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
    aov = data.compute_aov(dff)
    
    return aov


@app.callback(
    Output("kpi_abandonment_value", "children"),
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
    abandonment_rate = data.compute_abandonment_rate(dff)
    
    return abandonment_rate


@app.callback(
    Output("kpi_purchase_freq_value", "children"),
    [
        Input('date_slider', 'start_date'),
        Input('date_slider', 'end_date'),
        Input('payment_type', 'value'),
        Input('product_category', 'value'),
        Input('state', 'value'),
    ],
)
def update_kpi_kpi_purchase_freq(start_date, end_date, payment_type, product_category, state):
    dff = data.filter_dataframe(df, start_date, end_date, payment_type, product_category, customer_state=state)
    purchase_freq = data.purchase_freq(dff)
    
    return purchase_freq


