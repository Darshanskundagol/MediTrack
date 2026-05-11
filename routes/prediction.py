"""routes/prediction.py — CSV upload & expiry risk prediction blueprint"""
import os, sys
import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

prediction_bp = Blueprint("prediction", __name__)

ALLOWED = {"csv", "xlsx"}


def _allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED


@prediction_bp.route("/prediction", methods=["GET", "POST"])
@login_required
def prediction():
    results = None
    summary = None
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file uploaded.", "danger")
            return redirect(request.url)
        f = request.files["file"]
        if f.filename == "" or not _allowed(f.filename):
            flash("Please upload a valid CSV or XLSX file.", "danger")
            return redirect(request.url)

        upload_dir = os.path.join(BASE, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        filename = secure_filename(f.filename)
        filepath = os.path.join(upload_dir, filename)
        f.save(filepath)

        try:
            if filename.endswith(".xlsx"):
                df = pd.read_excel(filepath)
            else:
                df = pd.read_csv(filepath)

            # Normalise column names
            df.columns = [c.strip() for c in df.columns]

            # Ensure Expiry Date column present
            if "Expiry Date" not in df.columns:
                flash("File must contain an 'Expiry Date' column.", "warning")
                return redirect(request.url)

            df["Expiry Date"] = pd.to_datetime(df["Expiry Date"], errors="coerce")
            if "Manufacture Date" in df.columns:
                df["Manufacture Date"] = pd.to_datetime(df["Manufacture Date"], errors="coerce")

            # Add missing columns with defaults
            for col, default in [("Avg Daily Sales", 5), ("Stock Quantity", 100),
                                   ("Restock Count", 2), ("Shelf Life (days)", 365)]:
                if col not in df.columns:
                    df[col] = default

            from models.predict import predict_from_df
            df = predict_from_df(df)

            summary = {
                "total": len(df),
                "high_risk": int((df["Risk Level Pred"] == "High Risk").sum()),
                "slow_moving": int(df["Slow Moving Pred"].sum()),
                "avg_risk_score": round(df["Expiry Risk Score"].mean(), 1),
            }

            cols = ["Medicine ID", "Medicine Name", "Category", "Expiry Date",
                    "Stock Quantity", "Avg Daily Sales", "Days to Expiry",
                    "Expiry Risk Score", "Risk Level Pred", "Est Wastage", "Slow Moving Pred"]
            cols = [c for c in cols if c in df.columns]
            results = df[cols].head(50).to_dict("records")

            # Log to DB
            try:
                from extensions import db
                from models_db import PredictionLog
                log = PredictionLog(
                    user_id=current_user.id,
                    filename=filename,
                    total_records=summary["total"],
                    high_risk=summary["high_risk"],
                    slow_moving=summary["slow_moving"],
                )
                db.session.add(log); db.session.commit()
            except Exception:
                pass

            flash(f"Prediction complete! Found {summary['high_risk']} high-risk medicines.", "success")

        except Exception as e:
            flash(f"Error processing file: {str(e)}", "danger")

    return render_template("prediction.html", results=results, summary=summary)
