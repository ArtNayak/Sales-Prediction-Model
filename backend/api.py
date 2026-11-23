import os
import sys

import pandas as pd
from flask import Flask, jsonify, send_from_directory

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model.predict import predict_future_months  # noqa: E402
from paths import DATA_CSV  # noqa: E402

FRONTEND = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

# the dashboard is served from the same origin as the API, so no CORS is needed
app = Flask(__name__, static_folder=FRONTEND, static_url_path="")


@app.route("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


@app.route("/data")
def actual_data():
    df = pd.read_csv(DATA_CSV)
    return jsonify(df.to_dict(orient="records"))


@app.route("/predict")
def predict():
    return jsonify(predict_future_months(months=6))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
