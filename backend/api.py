import os
import sys

import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model.predict import predict_future_months  # noqa: E402
from paths import DATA_CSV  # noqa: E402

app = Flask(__name__)
CORS(app)


@app.route("/data")
def actual_data():
    df = pd.read_csv(DATA_CSV)
    return jsonify(df.to_dict(orient="records"))


@app.route("/predict")
def predict():
    return jsonify(predict_future_months(months=6))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
