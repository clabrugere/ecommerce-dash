from datetime import datetime

import numpy as np
import pandas as pd

from . import config


def consolidate_dataset():
    '''helper function to generate the dataset. It is not used in the application.
    '''
    # load datasets
    df_order = pd.read_csv(config.get_raw_filename(config.DATA_FILES['order']))
    df_order_item = pd.read_csv(config.get_raw_filename(config.DATA_FILES['order_item']))
    df_order_payment = pd.read_csv(config.get_raw_filename(config.DATA_FILES['order_payment']))
    df_order_review = pd.read_csv(config.get_raw_filename(config.DATA_FILES['order_review']))

    df_customer = pd.read_csv(config.get_raw_filename(config.DATA_FILES['customer']))
    df_product = pd.read_csv(config.get_raw_filename(config.DATA_FILES['product']))
    df_product_category_translation = pd.read_csv(
        config.get_raw_filename(config.DATA_FILES['product_category_translation']))
    df_seller = pd.read_csv(config.get_raw_filename(config.DATA_FILES['seller']))
    df_states = pd.read_csv(config.STATES)

    # filter data to keep only 2018
    df_order = df_order[(df_order['order_purchase_timestamp'] >= '2018-01-01') & (df_order['order_purchase_timestamp'] <= '2018-08-09')]
    df_order_item = df_order_item[df_order_item['order_id'].isin(df_order['order_id'].unique())]
    df_order_payment = df_order_payment[df_order_payment['order_id'].isin(df_order['order_id'].unique())]
    df_order_review = df_order_review[df_order_review['order_id'].isin(df_order['order_id'].unique())]

    df_customer = df_customer[df_customer['customer_id'].isin(df_order['customer_id'].unique())]
    df_customer = df_customer.drop('customer_unique_id', axis=1)

    df_order_review = df_order_review[['order_id', 'review_score']]
    df_product = df_product[df_product['product_id'].isin(df_order_item['product_id'].unique())]
    df_product = df_product.loc[:, ['product_id', 'product_category_name']]
    df_product['product_category_name'] = df_product['product_category_name'].map(
        pd.Series(df_product_category_translation['product_category_name_english'].values,
                  index=df_product_category_translation['product_category_name']).to_dict())

    df_seller = df_seller[df_seller['seller_id'].isin(df_order_item['seller_id'].unique())]

    # merge to one dataset
    df_order = df_order.merge(df_customer, how='left', on='customer_id')
    df_order = df_order.merge(df_order_payment, how='left', on='order_id')
    df_order = df_order.merge(df_order_item, how='left', on='order_id')
    df_order = df_order.merge(df_order_review, how='left', on='order_id')
    df_order = df_order.merge(df_product, how='left', on='product_id')
    df_order = df_order.merge(df_seller, how='left', on='seller_id')
    df_order = df_order.merge(df_states, how='left', left_on='customer_state', right_on='state_code',
                              suffixes=('', '_customer'))

    df_order = df_order.dropna(subset=['payment_type', 'product_category_name', 'seller_state', 'customer_state'])
    df_order.to_csv(config.get_processed_filename(config.DATA_FILES['order']), index=False)


def filter_dataframe(df, start_date, end_date, payment_type, product_category, customer_state):
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    dff = df[
        (df['order_purchase_timestamp'].dt.date >= start_date) &
        (df['order_purchase_timestamp'].dt.date <= end_date) &
        (df['payment_type'].isin(payment_type)) &
        (df['product_category_name'].isin(product_category)) &
        (df['state_name'].isin(customer_state))
        ]

    return dff


# controls
def min_date(df):
    return df['order_purchase_timestamp'].min().date()


def max_date(df):
    return df['order_purchase_timestamp'].max().date()


def values_to_options(values):
    return [{'label': v, 'value': v} for v in values]


def payment_types(df):
    return df['payment_type'].unique()


def payment_types(df):
    return df['payment_type'].unique()


def product_categories(df):
    return df['product_category_name'].unique()


def states(df):
    return df['state_name'].unique()


# KPIS
def revenue(df):
    df = df[df['order_status'].isin(config.ORDER_STATUS_CONSO)]
    return df['payment_value'].sum()


def aov(df):
    df = df[df['order_status'].isin(config.ORDER_STATUS_CONSO)]
    revenue = df['payment_value'].sum()
    n_order = df['order_id'].nunique()

    if n_order == 0:
        aov = 0.
    else:
        aov = revenue / n_order

    return aov


def abandonment_rate(df):
    n_completed = df.loc[df['order_status'].isin(config.ORDER_STATUS_CONSO), 'order_id'].nunique()
    n_order = df['order_id'].nunique()

    if n_order == 0:
        abandonment_rate = 0.
    else:
        abandonment_rate = 100. * (1. - n_completed / n_order)

    return abandonment_rate


def order_satisfaction(df):
    df = df[~df['review_score'].isna()]
    n_statisfied = df.loc[df['review_score'] >= 4, 'order_id'].nunique()
    n_review = df['order_id'].nunique()

    if n_review == 0:
        order_statisfaction = 0.
    else:
        order_statisfaction = 100 * n_statisfied / n_review

    return order_statisfaction
