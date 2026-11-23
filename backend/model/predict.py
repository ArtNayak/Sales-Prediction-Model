"""Forecast monthly sales value with an ensemble of two models.

1. XGBoost on (quantity, eff_rate, rate_change, month_num, trend), driven by assumed growth.
2. Linear trend of quantity x linear trend of effective rate over the last 6 months
   (sales value = quantity x rate, and trees cannot extrapolate beyond the training range).

A rolling-origin backtest on the 12 months of data (see train_model.py) gave lower
error for the ensemble than either model alone.
"""
import os
import sys

import joblib
import numpy as np
import pandas as pd
from xgboost import XGBRegressor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from paths import DATA_CSV, MODEL_PKL  # noqa: E402

FEATURES = ["quantity", "eff_rate", "rate_change", "month_num", "trend"]
DEMAND_GROWTH = 0.015   # monthly quantity growth assumed by the XGBoost branch
RATE_INCREMENT = 0.03   # monthly rate increase assumed by the XGBoost branch
FESTIVE_MONTHS = (10, 11, 12)
FESTIVE_BOOST = 1.05
LINEAR_WINDOW = 6


def make_model():
    return XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=4, random_state=42)


def load_data():
    return pd.read_csv(DATA_CSV, parse_dates=["month"])


def load_model():
    """Load the saved model, training it first if model.pkl does not exist yet."""
    if not os.path.exists(MODEL_PKL):
        df = load_data()
        joblib.dump(make_model().fit(df[FEATURES], df["value"]), MODEL_PKL)
    # model.pkl is produced locally by this module and gitignored; never load one from an untrusted source
    return joblib.load(MODEL_PKL)


def _linear(y, steps):
    t = np.arange(len(y))
    slope, intercept = np.polyfit(t, y, 1)
    return slope * np.arange(len(y), len(y) + steps) + intercept


def forecast(df, model, months=6):
    """Forecast `months` values after the last row of df using a fitted XGBoost `model`."""
    last = df.iloc[-1]
    q, r = last["quantity"], last["eff_rate"]
    xgb = []
    for i in range(1, months + 1):
        q *= 1 + DEMAND_GROWTH
        r *= 1 + RATE_INCREMENT
        month_num = (int(last["month_num"]) + i - 1) % 12 + 1
        if month_num in FESTIVE_MONTHS:
            q *= FESTIVE_BOOST
        x = pd.DataFrame([[q, r, RATE_INCREMENT, month_num, int(last["trend"]) + i]], columns=FEATURES)
        xgb.append(model.predict(x)[0])

    recent = df.tail(LINEAR_WINDOW)
    linear = _linear(recent["quantity"].values, months) * _linear(recent["eff_rate"].values, months)
    return (np.array(xgb) + linear) / 2


def predict_future_months(months=6):
    """Return [{"month": "YYYY-MM-DD", "value": float}, ...] for the next `months` months."""
    df = load_data()
    values = forecast(df, load_model(), months)
    start = df["month"].iloc[-1] + pd.offsets.MonthBegin(1)
    dates = pd.date_range(start, periods=months, freq="MS")
    return [{"month": d.strftime("%Y-%m-%d"), "value": round(float(v), 2)} for d, v in zip(dates, values)]


if __name__ == "__main__":
    print("Predicted Monthly Sales:")
    for p in predict_future_months(6):
        print(f"{p['month'][:7]}: Rs {p['value']:,.2f}")
