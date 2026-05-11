"""routes/dashboard.py — Main dashboard blueprint"""
import os, json
import pandas as pd
from flask import Blueprint, render_template, jsonify
from flask_login import login_required

dashboard_bp = Blueprint("dashboard", __name__)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_CSV = os.path.join(BASE, "dataset", "processed_inventory.csv")
METRICS_JSON  = os.path.join(BASE, "models", "metrics.json")


def _load_inventory():
    if os.path.exists(PROCESSED_CSV):
        return pd.read_csv(PROCESSED_CSV)
    # fallback: run feature engineering on raw data
    import sys; sys.path.insert(0, BASE)
    from models.preprocessing import load_datasets, clean_inventory, clean_sales, aggregate_daily_sales, get_restocking_frequency
    from models.feature_engineering import merge_datasets, engineer_features
    inv, sales, purchase, product = load_datasets()
    inv = clean_inventory(inv)
    sales = clean_sales(sales)
    df = merge_datasets(inv, aggregate_daily_sales(sales), get_restocking_frequency(purchase), product)
    df = engineer_features(df)
    df.to_csv(PROCESSED_CSV, index=False)
    return df


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    df = _load_inventory()
    risk_col = "Risk Level" if "Risk Level" in df.columns else None

    stats = {
        "total_medicines": int(df["Medicine ID"].nunique()),
        "total_batches": len(df),
        "high_risk": int((df["Risk Level"] == "High Risk").sum()) if risk_col else 0,
        "medium_risk": int((df["Risk Level"] == "Medium Risk").sum()) if risk_col else 0,
        "low_risk": int((df["Risk Level"] == "Low Risk").sum()) if risk_col else 0,
        "slow_moving": int(df["Slow Moving"].sum()) if "Slow Moving" in df.columns else 0,
        "total_wastage": int(df["Est Wastage"].sum()) if "Est Wastage" in df.columns else 0,
        "expiring_soon": int((df["Days to Expiry"] <= 90).sum()) if "Days to Expiry" in df.columns else 0,
    }

    # Top 5 high-risk items
    high_risk_items = []
    if "Risk Level" in df.columns:
        hr = df[df["Risk Level"] == "High Risk"].sort_values("Expiry Risk Score", ascending=False).head(5)
        high_risk_items = hr[["Medicine ID", "Medicine Name", "Category", "Days to Expiry",
                               "Stock Quantity", "Expiry Risk Score"]].to_dict("records")

    # Category breakdown
    cat_data = {}
    if "Category" in df.columns and "Risk Level" in df.columns:
        cat_data = df.groupby(["Category", "Risk Level"]).size().unstack(fill_value=0).to_dict()

    # Load model metrics
    metrics = {}
    if os.path.exists(METRICS_JSON):
        metrics = json.load(open(METRICS_JSON))

    return render_template(
        "dashboard.html",
        stats=stats,
        high_risk_items=high_risk_items,
        metrics=metrics,
    )


@dashboard_bp.route("/api/chart/risk-distribution")
@login_required
def api_risk_distribution():
    df = _load_inventory()
    counts = df["Risk Level"].value_counts().to_dict() if "Risk Level" in df.columns else {}
    return jsonify(counts)


@dashboard_bp.route("/api/chart/category-risk")
@login_required
def api_category_risk():
    df = _load_inventory()
    if "Category" not in df.columns or "Risk Level" not in df.columns:
        return jsonify({})
    result = df.groupby(["Category", "Risk Level"]).size().unstack(fill_value=0)
    return jsonify(result.to_dict())


@dashboard_bp.route("/api/chart/expiry-timeline")
@login_required
def api_expiry_timeline():
    df = _load_inventory()
    if "Days to Expiry" not in df.columns:
        return jsonify({})
    bins = {"0-30 days": 0, "31-60 days": 0, "61-90 days": 0, "91-180 days": 0, "180+ days": 0}
    for d in df["Days to Expiry"].dropna():
        if d <= 30: bins["0-30 days"] += 1
        elif d <= 60: bins["31-60 days"] += 1
        elif d <= 90: bins["61-90 days"] += 1
        elif d <= 180: bins["91-180 days"] += 1
        else: bins["180+ days"] += 1
    return jsonify(bins)


@dashboard_bp.route("/api/chart/wastage-by-category")
@login_required
def api_wastage_by_category():
    df = _load_inventory()
    if "Category" not in df.columns or "Est Wastage" not in df.columns:
        return jsonify({})
    result = df.groupby("Category")["Est Wastage"].sum().round(0).astype(int).to_dict()
    return jsonify(result)
