"""routes/reports.py — Reports, alerts, and CSV export blueprint"""
import os, sys, io
import pandas as pd
from flask import Blueprint, render_template, send_file, Response
from flask_login import login_required

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

reports_bp = Blueprint("reports", __name__)

PROCESSED = os.path.join(BASE, "dataset", "processed_inventory.csv")


def _df():
    return pd.read_csv(PROCESSED) if os.path.exists(PROCESSED) else pd.DataFrame()


@reports_bp.route("/reports")
@login_required
def reports():
    df = _df()
    report_data = {}
    if not df.empty and "Risk Level" in df.columns:
        report_data["category_summary"] = (
            df.groupby(["Category", "Risk Level"]).size().unstack(fill_value=0).reset_index().to_dict("records")
        )
        report_data["risk_summary"] = df["Risk Level"].value_counts().to_dict()
        report_data["top_wastage"] = (
            df.nlargest(10, "Est Wastage")[
                ["Medicine ID", "Medicine Name", "Category", "Est Wastage", "Risk Level", "Days to Expiry"]
            ].to_dict("records")
            if "Est Wastage" in df.columns else []
        )
    return render_template("reports.html", report_data=report_data)


@reports_bp.route("/alerts")
@login_required
def alerts():
    df = _df()
    alerts_data = {"expiring_soon": [], "high_risk": [], "slow_moving": []}
    if not df.empty:
        if "Days to Expiry" in df.columns:
            soon = df[df["Days to Expiry"] <= 90].sort_values("Days to Expiry")
            alerts_data["expiring_soon"] = soon[
                ["Medicine ID", "Medicine Name", "Category", "Expiry Date",
                 "Days to Expiry", "Stock Quantity", "Risk Level"]
            ].head(20).to_dict("records")

        if "Risk Level" in df.columns:
            hr = df[df["Risk Level"] == "High Risk"].sort_values("Expiry Risk Score", ascending=False)
            alerts_data["high_risk"] = hr[
                ["Medicine ID", "Medicine Name", "Category", "Expiry Risk Score",
                 "Est Wastage", "Days to Expiry"]
            ].head(20).to_dict("records")

        if "Slow Moving" in df.columns:
            sm = df[df["Slow Moving"] == 1]
            alerts_data["slow_moving"] = sm[
                ["Medicine ID", "Medicine Name", "Category", "Avg Daily Sales",
                 "Stock Quantity", "Days to Expiry"]
            ].head(20).to_dict("records")

    return render_template("alerts.html", alerts_data=alerts_data)


@reports_bp.route("/export/csv")
@login_required
def export_csv():
    df = _df()
    if df.empty:
        return "No data available", 404
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=meditrack_risk_report.csv"},
    )


@reports_bp.route("/export/alerts-csv")
@login_required
def export_alerts_csv():
    df = _df()
    if df.empty or "Days to Expiry" not in df.columns:
        return "No data", 404
    soon = df[df["Days to Expiry"] <= 90].sort_values("Days to Expiry")
    output = io.StringIO()
    soon.to_csv(output, index=False)
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=meditrack_alerts.csv"},
    )
