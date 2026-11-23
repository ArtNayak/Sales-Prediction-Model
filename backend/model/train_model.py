"""Train the XGBoost model, save it, and print a rolling-origin backtest."""
import os
import sys

import joblib
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from model.predict import FEATURES, forecast, load_data, make_model  # noqa: E402
from paths import MODEL_PKL  # noqa: E402

MIN_TRAIN = 6


def backtest(df, horizon):
    """Mean absolute % error of the ensemble when forecasting `horizon` months ahead."""
    errors = []
    for k in range(MIN_TRAIN, len(df) - horizon + 1):
        train = df.iloc[:k]
        model = make_model().fit(train[FEATURES], train["value"])
        actual = df["value"].values[k:k + horizon]
        errors.append(np.mean(np.abs(forecast(train, model, horizon) - actual) / actual))
    return 100 * np.mean(errors)


if __name__ == "__main__":
    df = load_data()
    joblib.dump(make_model().fit(df[FEATURES], df["value"]), MODEL_PKL)
    print(f"Saved model to {MODEL_PKL}")
    for h in (1, 3):
        print(f"Backtest MAPE, {h}-month horizon: {backtest(df, h):.2f}%")
