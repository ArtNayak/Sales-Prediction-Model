"""Aggregate raw per-product sales (backend/data/sales_raw.csv) into monthly_agg.csv."""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from paths import DATA_CSV, RAW_CSV  # noqa: E402


def preprocess():
    df = pd.read_csv(RAW_CSV)
    df.columns = ["product", "quantity", "eff_rate", "value", "month"]
    df["month"] = pd.to_datetime(df["month"])

    monthly = df.groupby(df["month"].dt.to_period("M")).agg(
        quantity=("quantity", "sum"),
        eff_rate=("eff_rate", "mean"),
        value=("value", "sum"),
    ).reset_index()

    monthly["month"] = monthly["month"].dt.to_timestamp()
    monthly["rate_change"] = monthly["eff_rate"].pct_change().fillna(0)
    monthly["month_num"] = monthly["month"].dt.month
    monthly["trend"] = range(len(monthly))
    monthly.to_csv(DATA_CSV, index=False)


if __name__ == "__main__":
    preprocess()
