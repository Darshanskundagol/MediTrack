"""
feature_engineering.py — Build ML features for expiry risk prediction
"""
import pandas as pd
import numpy as np
from datetime import datetime


REFERENCE_DATE = datetime.today()


def merge_datasets(inv, sales_agg, restock_freq, product):
    df = inv.copy()
    df = df.merge(sales_agg, on="Medicine ID", how="left")
    df = df.merge(restock_freq, on="Medicine ID", how="left")
    df = df.merge(
        product[["Medicine ID", "Shelf Life (days)"]].rename(
            columns={"Shelf Life (days)": "Product Shelf Life"}
        ),
        on="Medicine ID",
        how="left",
    )
    df["Avg Daily Sales"] = df["Avg Daily Sales"].fillna(0)
    df["Restock Count"] = df["Restock Count"].fillna(1)
    return df


def engineer_features(df):
    df = df.copy()
    ref = REFERENCE_DATE

    # Days to expiry
    df["Days to Expiry"] = (df["Expiry Date"] - ref).dt.days

    # Days of coverage: how many days stock will last
    df["Days Cover"] = np.where(
        df["Avg Daily Sales"] > 0,
        df["Stock Quantity"] / df["Avg Daily Sales"],
        df["Stock Quantity"] * 999,  # very slow-moving
    )

    # Sales velocity label
    velocity_thresh = df["Avg Daily Sales"].quantile(0.33)
    df["Velocity"] = np.where(df["Avg Daily Sales"] <= velocity_thresh, "Low", "Normal")

    # Wastage estimate: surplus stock that can't be sold before expiry
    df["Est Wastage"] = np.where(
        df["Avg Daily Sales"] > 0,
        np.maximum(
            df["Stock Quantity"] - df["Days to Expiry"] * df["Avg Daily Sales"], 0
        ),
        df["Stock Quantity"],
    ).round(0)

    # Stock turnover ratio
    df["Stock Turnover"] = np.where(
        df["Stock Quantity"] > 0,
        df.get("Total Sold", 0) / df["Stock Quantity"],
        0,
    ).round(4)

    # Expiry risk score (0–100)
    df["Expiry Risk Score"] = _compute_risk_score(df)

    # Binary risk label: 1 = High Risk
    df["Risk Label"] = np.where(df["Expiry Risk Score"] >= 60, 1, 0)

    # Human-readable risk level
    df["Risk Level"] = pd.cut(
        df["Expiry Risk Score"],
        bins=[-1, 30, 59, 100],
        labels=["Low Risk", "Medium Risk", "High Risk"],
    )

    # Slow-moving flag
    df["Slow Moving"] = np.where(
        (df["Avg Daily Sales"] <= velocity_thresh) & (df["Stock Quantity"] > 50), 1, 0
    )

    return df


def _compute_risk_score(df):
    """Composite score based on days to expiry, cover, and velocity."""
    # Normalised components (0–1 each, higher = worse)
    max_dte = 730
    dte_score = np.clip(1 - df["Days to Expiry"] / max_dte, 0, 1)  # nearer expiry → higher

    cover_score = np.where(
        df["Avg Daily Sales"] > 0,
        np.clip(df["Days Cover"] / np.maximum(df["Days to Expiry"], 1) - 1, 0, 1),
        1,
    )

    wastage_ratio = np.where(
        df["Stock Quantity"] > 0,
        np.clip(df["Est Wastage"] / df["Stock Quantity"], 0, 1),
        0,
    )

    score = (0.40 * dte_score + 0.35 * wastage_ratio + 0.25 * cover_score) * 100
    return score.round(2)


def get_feature_columns():
    return [
        "Days to Expiry",
        "Avg Daily Sales",
        "Days Cover",
        "Stock Quantity",
        "Restock Count",
        "Est Wastage",
        "Stock Turnover",
        "Shelf Life (days)",
    ]
