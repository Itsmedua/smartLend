"""Credit risk prediction helper.

This file has NO Django code in it on purpose, so train_model.py can reuse
the same feature engineering and the web app can call predict_risk().

How it works:
1. build_features() turns the form values into numbers the model understands.
2. If you trained a model (python train_model.py), we load core/ml_model/model.joblib.
   Otherwise we use a small hand-made fallback so the site still works.
3. Because the model is a Logistic Regression, each feature's push on the
   score is simply: coefficient x scaled value. That gives us the
   "why this score" explanation. (In step 7 you can replace this with SHAP.)
"""
from functools import lru_cache
from pathlib import Path

import numpy as np

MODEL_PATH = Path(__file__).resolve().parent / "ml_model" / "model.joblib"

# The order matters: the model expects the features in exactly this order.
FEATURE_NAMES = [
    "debt_to_income",
    "credit_history_years",
    "missed_payments",
    "employment_years",
    "loan_to_income",
]

FEATURE_LABELS = {
    "debt_to_income": "Existing debt vs yearly income",
    "credit_history_years": "Length of credit history",
    "missed_payments": "Missed payments",
    "employment_years": "Years in current job",
    "loan_to_income": "Loan amount vs yearly income",
}

# Used only when no trained model file exists yet.
FALLBACK = {
    "means": np.array([0.5, 5.0, 1.0, 4.0, 0.8]),
    "scales": np.array([0.4, 4.0, 1.5, 4.0, 0.6]),
    "coefs": np.array([1.0, -0.6, 0.8, -0.4, 0.7]),
    "intercept": -0.3,
}


def build_features(monthly_income, loan_amount, credit_history_years,
                   existing_debt, missed_payments, employment_years):
    """Turn raw form values into the list of numbers the model uses."""
    annual_income = max(float(monthly_income) * 12, 1.0)
    return [
        float(existing_debt) / annual_income,
        float(credit_history_years),
        float(missed_payments),
        float(employment_years),
        float(loan_amount) / annual_income,
    ]


@lru_cache(maxsize=1)
def _load_params():
    """Load model parameters once. Returns (params, source_name)."""
    if MODEL_PATH.exists():
        import joblib

        pipeline = joblib.load(MODEL_PATH)
        scaler = pipeline.named_steps["scaler"]
        clf = pipeline.named_steps["clf"]
        params = {
            "means": scaler.mean_,
            "scales": scaler.scale_,
            "coefs": clf.coef_[0],
            "intercept": float(clf.intercept_[0]),
        }
        return params, "trained model"
    return FALLBACK, "fallback rules (train a model to replace this)"


def _format_value(name, value):
    if name in ("debt_to_income", "loan_to_income"):
        return f"{value * 100:.0f}% of yearly income"
    if name == "missed_payments":
        return f"{value:.0f}"
    return f"{value:.1f} yrs"


def _risk_label(probability):
    if probability >= 0.60:
        return "High risk"
    if probability >= 0.35:
        return "Medium risk"
    return "Low risk"


def predict_risk(monthly_income, loan_amount, credit_history_years,
                 existing_debt, missed_payments, employment_years):
    """Return the default probability, a label, and a 'why' explanation."""
    params, source = _load_params()
    x = np.array(build_features(monthly_income, loan_amount, credit_history_years,
                                existing_debt, missed_payments, employment_years))

    scaled = (x - params["means"]) / params["scales"]
    contributions = params["coefs"] * scaled
    z = params["intercept"] + contributions.sum()
    probability = float(1 / (1 + np.exp(-z)))

    biggest = float(np.abs(contributions).max()) or 1.0
    explanation = []
    for name, value, effect in zip(FEATURE_NAMES, x, contributions):
        explanation.append({
            "label": FEATURE_LABELS[name],
            "value": _format_value(name, value),
            "effect": round(float(effect), 3),
            "raises_risk": bool(effect > 0),
            "width": int(round(abs(effect) / biggest * 100)),
        })
    explanation.sort(key=lambda item: abs(item["effect"]), reverse=True)

    return {
        "probability": round(probability, 4),
        "label": _risk_label(probability),
        "explanation": explanation,
        "source": source,
    }
