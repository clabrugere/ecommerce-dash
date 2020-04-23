import glob
import os

from pathlib2 import Path

DIR_ROOT = str(Path(os.path.abspath(__file__)).parents[1])
DIR_DATA = os.path.join(DIR_ROOT, 'data/')
DIR_DATA_RAW = os.path.join(DIR_DATA, 'raw/')
DIR_DATA_PROCESSED = os.path.join(DIR_DATA, 'processed/')

DATA_FILES = {
    'customer': 'olist_customers_dataset.csv',
    'geolocation': 'olist_geolocation_dataset.csv',
    'order': 'olist_orders_dataset.csv',
    'order_item': 'olist_order_items_dataset.csv',
    'order_payment': 'olist_order_payments_dataset.csv',
    'order_review': 'olist_order_reviews_dataset.csv',
    'product': 'olist_products_dataset.csv',
    'seller': 'olist_sellers_dataset.csv',
    'product_category_translation': 'product_category_name_translation.csv',
}

COLUMN_DATE = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]

STATES = os.path.join(DIR_DATA_RAW, 'states.csv')

ORDER_STATUS_CONSO = [
    'delivered',
    'shipped',
    'invoiced',
]


def get_raw_filename(name):
    return os.path.join(DIR_DATA_RAW, name)


def get_processed_filename(name):
    return os.path.join(DIR_DATA_PROCESSED, name)
