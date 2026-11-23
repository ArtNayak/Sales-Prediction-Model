import os

BACKEND = os.path.dirname(os.path.abspath(__file__))
DATA_CSV = os.path.join(BACKEND, "data", "monthly_agg.csv")
RAW_CSV = os.path.join(BACKEND, "data", "sales_raw.csv")
MODEL_PKL = os.path.join(BACKEND, "model", "model.pkl")
