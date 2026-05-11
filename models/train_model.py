"""
train_model.py — Train and evaluate expiry risk ML models, save with joblib
Run: python models/train_model.py
"""
import os, sys, json, warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

# ── path setup ──────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from models.preprocessing import load_datasets, clean_inventory, clean_sales, aggregate_daily_sales, get_restocking_frequency
from models.feature_engineering import merge_datasets, engineer_features, get_feature_columns

MODELS_DIR = os.path.join(BASE, "models")
STATIC_IMG = os.path.join(BASE, "static", "images")
os.makedirs(STATIC_IMG, exist_ok=True)


def train():
    print("📦 Loading datasets...")
    inv, sales, purchase, product = load_datasets()
    inv = clean_inventory(inv)
    sales = clean_sales(sales)

    sales_agg = aggregate_daily_sales(sales)
    restock = get_restocking_frequency(purchase)

    print("🔧 Engineering features...")
    df = merge_datasets(inv, sales_agg, restock, product)
    df = engineer_features(df)

    FEATURES = get_feature_columns()
    # Drop rows with NaN in features
    model_df = df[FEATURES + ["Risk Label", "Slow Moving"]].dropna()

    X = model_df[FEATURES]
    y_expiry = model_df["Risk Label"]
    y_slow = model_df["Slow Moving"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_expiry, test_size=0.25, random_state=42, stratify=y_expiry
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # ── Train three models ──────────────────────────────────────────────────
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced"),
        "Logistic Regression": LogisticRegression(max_iter=500, random_state=42, class_weight="balanced"),
        "Decision Tree": DecisionTreeClassifier(max_depth=6, random_state=42, class_weight="balanced"),
    }

    results = {}
    best_model, best_f1, best_name = None, 0, ""

    print("\n📊 Model Evaluation Results")
    print("=" * 55)
    for name, clf in models.items():
        clf.fit(X_train_s, y_train)
        preds = clf.predict(X_test_s)
        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        f1 = f1_score(y_test, preds, zero_division=0)
        results[name] = {"accuracy": round(acc,4), "precision": round(prec,4),
                         "recall": round(rec,4), "f1": round(f1,4)}
        print(f"\n🔹 {name}")
        print(f"   Accuracy={acc:.3f} | Precision={prec:.3f} | Recall={rec:.3f} | F1={f1:.3f}")
        if f1 > best_f1:
            best_f1, best_model, best_name = f1, clf, name

    print(f"\n✅ Best Model: {best_name} (F1={best_f1:.3f})")

    # ── Save artefacts ──────────────────────────────────────────────────────
    joblib.dump(best_model, os.path.join(MODELS_DIR, "expiry_model.pkl"))
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))

    # Slow-moving model
    X_train_s2, X_test_s2, y_train2, y_test2 = train_test_split(
        X, y_slow, test_size=0.25, random_state=42
    )
    X_train_s2 = scaler.transform(X_train_s2)
    X_test_s2  = scaler.transform(X_test_s2)
    sm_clf = RandomForestClassifier(n_estimators=80, random_state=42, class_weight="balanced")
    sm_clf.fit(X_train_s2, y_train2)
    joblib.dump(sm_clf, os.path.join(MODELS_DIR, "slow_moving_model.pkl"))

    # Save metrics
    json.dump(results, open(os.path.join(MODELS_DIR, "metrics.json"), "w"), indent=2)

    # ── Plots ───────────────────────────────────────────────────────────────
    _plot_confusion(best_model, X_test_s, y_test, best_name)
    _plot_feature_importance(best_model, FEATURES)
    _plot_risk_dist(df)
    _plot_category_risk(df)

    # Save processed dataset
    df.to_csv(os.path.join(BASE, "dataset", "processed_inventory.csv"), index=False)
    print("\n🎉 Training complete. All artefacts saved.")
    return results


def _plot_confusion(model, X_test, y_test, name):
    cm = confusion_matrix(y_test, model.predict(X_test))
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="RdYlGn", ax=ax,
                xticklabels=["Low Risk", "High Risk"],
                yticklabels=["Low Risk", "High Risk"])
    ax.set_title(f"Confusion Matrix — {name}", fontsize=12, fontweight="bold")
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
    plt.tight_layout()
    plt.savefig(os.path.join(STATIC_IMG, "confusion_matrix.png"), dpi=100)
    plt.close()


def _plot_feature_importance(model, features):
    if not hasattr(model, "feature_importances_"):
        return
    imp = pd.Series(model.feature_importances_, index=features).sort_values()
    fig, ax = plt.subplots(figsize=(7, 4))
    imp.plot(kind="barh", color="#2196F3", ax=ax)
    ax.set_title("Feature Importances", fontweight="bold")
    ax.set_xlabel("Importance")
    plt.tight_layout()
    plt.savefig(os.path.join(STATIC_IMG, "feature_importance.png"), dpi=100)
    plt.close()


def _plot_risk_dist(df):
    counts = df["Risk Level"].value_counts()
    colors = {"High Risk": "#E53935", "Medium Risk": "#FB8C00", "Low Risk": "#43A047"}
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(counts.values, labels=counts.index,
           colors=[colors.get(l, "#90CAF9") for l in counts.index],
           autopct="%1.1f%%", startangle=140, wedgeprops=dict(linewidth=2, edgecolor="white"))
    ax.set_title("Expiry Risk Distribution", fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(STATIC_IMG, "risk_distribution.png"), dpi=100)
    plt.close()


def _plot_category_risk(df):
    cat_risk = df.groupby(["Category", "Risk Level"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 5))
    cat_risk.plot(kind="bar", ax=ax,
                  color={"High Risk": "#E53935", "Medium Risk": "#FB8C00", "Low Risk": "#43A047"})
    ax.set_title("Risk by Category", fontweight="bold")
    ax.set_xlabel("Category"); ax.set_ylabel("Count")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(STATIC_IMG, "category_risk.png"), dpi=100)
    plt.close()


if __name__ == "__main__":
    train()
