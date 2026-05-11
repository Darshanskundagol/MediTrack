"""
predict.py — Load trained models and run predictions on new data
"""
import os, sys
import numpy as np
import pandas as pd
import joblib

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from models.feature_engineering import engineer_features, get_feature_columns

MODELS_DIR = os.path.join(BASE, "models")


def _load_artifacts():
    expiry_model = joblib.load(os.path.join(MODELS_DIR, "expiry_model.pkl"))
    slow_model   = joblib.load(os.path.join(MODELS_DIR, "slow_moving_model.pkl"))
    scaler       = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
    return expiry_model, slow_model, scaler


def predict_from_df(df: pd.DataFrame) -> pd.DataFrame:
    """Run expiry-risk and slow-moving predictions on a processed DataFrame."""
    expiry_model, slow_model, scaler = _load_artifacts()
    FEATURES = get_feature_columns()
    df = engineer_features(df)
    X = df[FEATURES].fillna(0)
    X_s = scaler.transform(X)
    df["Predicted Risk"]    = expiry_model.predict(X_s)
    df["Slow Moving Pred"]  = slow_model.predict(X_s)
    df["Risk Probability"]  = expiry_model.predict_proba(X_s)[:, 1].round(4)
    df["Risk Level Pred"]   = df["Predicted Risk"].map({1: "High Risk", 0: "Low Risk"})
    return df


def predict_from_csv(filepath: str) -> pd.DataFrame:
    """Load CSV, run feature engineering, and return predictions."""
    df = pd.read_csv(filepath, parse_dates=["Expiry Date", "Manufacture Date"])
    return predict_from_df(df)
