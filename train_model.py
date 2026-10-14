"""Train the credit risk model and save it for the website to use.

Run from the project folder:   python train_model.py

IMPORTANT: Right now this trains on SYNTHETIC (made-up) data so the project
works out of the box. It is only a placeholder. In step 7 you will replace
the data loading part with a real dataset (for example Kaggle's
"Give Me Some Credit" or "German Credit") loaded with pandas, and keep
everything else the same.
"""
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from core.ml import FEATURE_NAMES, MODEL_PATH, build_features


def make_synthetic_data(n=5000, seed=42):
    rng = np.random.default_rng(seed)
    monthly_income = rng.lognormal(mean=11.2, sigma=0.5, size=n)  # about PKR 70,000
    loan_amount = monthly_income * rng.uniform(2, 30, size=n)
    existing_debt = monthly_income * rng.uniform(0, 14, size=n)
    credit_history = rng.uniform(0, 15, size=n)
    missed = rng.poisson(1.0, size=n)
    employment = rng.uniform(0, 15, size=n)

    X = np.array([
        build_features(i, l, c, d, m, e)
        for i, l, c, d, m, e in zip(
            monthly_income, loan_amount, credit_history, existing_debt, missed, employment)
    ])

    # Made-up "truth": more debt and missed payments raise risk, history and job lower it
    z = (-1.0 + 1.6 * X[:, 0] - 0.12 * X[:, 1] + 0.5 * X[:, 2]
         - 0.08 * X[:, 3] + 0.5 * X[:, 4])
    probability = 1 / (1 + np.exp(-z))
    y = rng.binomial(1, probability)
    return X, y


def main():
    X, y = make_synthetic_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000)),
    ])
    model.fit(X_train, y_train)

    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    print(f"Test AUC: {auc:.3f}  (1.0 is perfect, 0.5 is random guessing)")
    print("Features used:", FEATURE_NAMES)

    Path(MODEL_PATH).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
