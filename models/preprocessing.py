"""
preprocessing.py — Data loading and cleaning for Meditrack ML pipeline
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET = os.path.join(BASE, "dataset")


def load_datasets():
    inv = pd.read_csv(os.path.join(DATASET, "inventory_data.csv"), parse_dates=["Expiry Date", "Manufacture Date"])
    sales = pd.read_csv(os.path.join(DATASET, "sales_data.csv"), parse_dates=["Date"])
    purchase = pd.read_csv(os.path.join(DATASET, "purchase_data.csv"), parse_dates=["Order Date", "Received Date"])
    product = pd.read_csv(os.path.join(DATASET, "product_info.csv"))
    return inv, sales, purchase, product


def clean_inventory(inv):
    inv = inv.copy()
    inv.drop_duplicates(inplace=True)
    inv["Stock Quantity"] = pd.to_numeric(inv["Stock Quantity"], errors="coerce").fillna(0)
    inv["Shelf Life (days)"] = pd.to_numeric(inv["Shelf Life (days)"], errors="coerce").fillna(365)
    inv["Expiry Date"] = pd.to_datetime(inv["Expiry Date"], errors="coerce")
    inv["Manufacture Date"] = pd.to_datetime(inv["Manufacture Date"], errors="coerce")
    return inv


def clean_sales(sales):
    sales = sales.copy()
    sales["Qty Sold"] = pd.to_numeric(sales["Qty Sold"], errors="coerce").fillna(0)
    return sales


def aggregate_daily_sales(sales):
    """Compute avg daily sales per Medicine ID."""
    agg = (
        sales.groupby("Medicine ID")["Qty Sold"]
        .agg(total_sold="sum", days_active=pd.Series.nunique)
        .reset_index()
    )
    agg.columns = ["Medicine ID", "Total Sold", "Active Days"]
    agg["Avg Daily Sales"] = (agg["Total Sold"] / agg["Active Days"]).round(2)
    return agg


def get_restocking_frequency(purchase):
    """Compute restocking frequency per Medicine ID."""
    freq = purchase.groupby("Medicine ID").size().reset_index(name="Restock Count")
    return freq
