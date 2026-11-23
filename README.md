# Sales Prediction Model

Forecasts monthly sales value for the next 6 months and shows actual vs predicted sales on a web dashboard. Flask serves the API, and a Chart.js page draws the chart.

## How the forecast works
Sales value is roughly `quantity x effective rate`, so the forecast combines two models:
1. **XGBoost** on `quantity, eff_rate, rate_change, month_num, trend`, fed with assumed demand growth (1.5%/month), rate increase (3%/month) and a festive-season boost (Oct–Dec).
2. **Linear trends** of quantity and rate over the last 6 months, multiplied together. Tree models cannot predict beyond the range they were trained on, so this branch covers the rising trend.

The final prediction is the average of the two.

### Accuracy
Rolling-origin backtest on the 12 months of data (train on the first k months, forecast the next ones, mean absolute % error):

| Horizon | Original (XGBoost only) | Now (ensemble) |
|---|---|---|
| 1 month | 4.21% | **3.71%** |
| 3 months | 6.18% | **4.99%** |

Caveat: there are only 12 monthly data points, so these numbers are noisy and the model cannot learn real seasonality. Adding more history is the biggest improvement available. Reproduce with `python backend/model/train_model.py`.

## Project layout
```
backend/
  api.py                 Flask API: /data (actuals), /predict (next 6 months)
  paths.py               file locations
  data/monthly_agg.csv   monthly quantity, rate and sales value
  model/predict.py       forecasting logic (trains model.pkl on first use if missing)
  model/train_model.py   trains + saves the model and prints the backtest
  utils/preprocess.py    raw per-product sales -> monthly_agg.csv
  utils/extract_pdf.py   sales PDF -> sales_raw.csv (needs tabula-py)
frontend/                index.html, app.js, styles.css (Chart.js dashboard)
```

## Run
```
pip install -r requirements.txt
python backend/api.py          # API on http://127.0.0.1:5000
```
Then open `frontend/index.html` in a browser.

To print the forecast without the API: `python backend/model/predict.py`.

## API
| Endpoint | Returns |
|---|---|
| `GET /data` | monthly actuals (`month, quantity, eff_rate, value, ...`) |
| `GET /predict` | `[{ "month": "YYYY-MM-DD", "value": ... }]` for the next 6 months |
