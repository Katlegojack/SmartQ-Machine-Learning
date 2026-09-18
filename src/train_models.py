from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "SmartQ_Synthetic_Operational_Dataset_100k.csv"
RESULTS = ROOT / "results" / "modeling"
MODELS = ROOT / "models"
RESULTS.mkdir(parents=True, exist_ok=True)
MODELS.mkdir(parents=True, exist_ok=True)

TARGET = "actual_wait_minutes"
NUMERIC_FEATURES = [
    "arrival_offset_minutes", "people_ahead", "general_waiting", "priority_waiting",
    "serving_count", "open_general_counters", "open_priority_counters",
    "effective_open_counters", "counter_utilisation", "queue_pressure_index",
    "workload_minutes_ahead", "recent_avg_service_minutes_10",
    "recent_avg_wait_minutes_10", "recent_throughput_60m",
    "service_target_minutes", "hour_of_day",
]
CATEGORICAL_FEATURES = [
    "branch_code", "service_code", "booking_source",
    "queue_type", "day_of_week", "is_peak_period",
]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

def score(y_true, y_pred):
    y_pred = np.clip(np.asarray(y_pred), 0, None)
    return (
        mean_absolute_error(y_true, y_pred),
        mean_squared_error(y_true, y_pred) ** 0.5,
    )

df = pd.read_csv(DATA, parse_dates=["scenario_date"])
completed = df[df["status"] == "COMPLETED"].copy()

dates = sorted(completed["scenario_date"].dt.normalize().unique())
n = len(dates)
train_end = pd.Timestamp(dates[int(n * 0.70) - 1])
val_start = pd.Timestamp(dates[int(n * 0.70)])
val_end = pd.Timestamp(dates[int(n * 0.85) - 1])
test_start = pd.Timestamp(dates[int(n * 0.85)])

train = completed[completed["scenario_date"] <= train_end].copy()
validation = completed[
    (completed["scenario_date"] >= val_start)
    & (completed["scenario_date"] <= val_end)
].copy()
test = completed[completed["scenario_date"] >= test_start].copy()

X_train, y_train = train[FEATURES], train[TARGET]
X_val, y_val = validation[FEATURES], validation[TARGET]
X_test, y_test = test[FEATURES], test[TARGET]

preprocessor = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
    ]), NUMERIC_FEATURES),
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ]), CATEGORICAL_FEATURES),
])

Xtr = preprocessor.fit_transform(X_train)
Xv = preprocessor.transform(X_val)
Xt = preprocessor.transform(X_test)

rows = []

def add_result(model, split, y_true, y_pred, parameters):
    mae, rmse = score(y_true, y_pred)
    rows.append({
        "model": model,
        "split": split,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "parameters": parameters,
    })

mean_wait = float(y_train.mean())
add_result("Mean baseline", "validation", y_val, np.full(len(y_val), mean_wait), f"train_mean={mean_wait:.4f}")
add_result("Mean baseline", "test", y_test, np.full(len(y_test), mean_wait), f"train_mean={mean_wait:.4f}")

add_result("SmartQ deterministic ETA", "validation", y_val, validation["baseline_eta_minutes"], "existing baseline_eta_minutes")
add_result("SmartQ deterministic ETA", "test", y_test, test["baseline_eta_minutes"], "existing baseline_eta_minutes")

linear = LinearRegression().fit(Xtr, y_train)
add_result("Linear Regression", "validation", y_val, linear.predict(Xv), "default LinearRegression; non-negative clipping")
add_result("Linear Regression", "test", y_test, linear.predict(Xt), "default LinearRegression; non-negative clipping")

rf_candidates = [
    {"n_estimators": 100, "max_depth": 18, "min_samples_leaf": 2, "max_features": 0.8},
    {"n_estimators": 150, "max_depth": 14, "min_samples_leaf": 2, "max_features": 1.0},
]
rf_trials = []
best_rf = None
best_rf_mae = float("inf")
best_rf_params = None
for params in rf_candidates:
    model = RandomForestRegressor(random_state=42, n_jobs=-1, **params)
    model.fit(Xtr, y_train)
    pred = np.clip(model.predict(Xv), 0, None)
    mae, rmse = score(y_val, pred)
    rf_trials.append({**params, "validation_mae": mae, "validation_rmse": rmse})
    if mae < best_rf_mae:
        best_rf, best_rf_mae, best_rf_params = model, mae, params.copy()

add_result("Random Forest", "validation", y_val, best_rf.predict(Xv), json.dumps(best_rf_params, sort_keys=True))
add_result("Random Forest", "test", y_test, best_rf.predict(Xt), json.dumps(best_rf_params, sort_keys=True))

xgb_candidates = [
    {"n_estimators": 150, "max_depth": 4, "learning_rate": 0.05, "subsample": 0.9, "colsample_bytree": 0.9, "reg_lambda": 1.0},
    {"n_estimators": 200, "max_depth": 5, "learning_rate": 0.08, "subsample": 0.9, "colsample_bytree": 0.9, "reg_lambda": 2.0},
]
xgb_trials = []
best_xgb = None
best_xgb_mae = float("inf")
best_xgb_params = None
for params in xgb_candidates:
    model = XGBRegressor(
        random_state=42,
        n_jobs=-1,
        objective="reg:squarederror",
        tree_method="hist",
        **params,
    )
    model.fit(Xtr, y_train)
    pred = np.clip(model.predict(Xv), 0, None)
    mae, rmse = score(y_val, pred)
    xgb_trials.append({**params, "validation_mae": mae, "validation_rmse": rmse})
    if mae < best_xgb_mae:
        best_xgb, best_xgb_mae, best_xgb_params = model, mae, params.copy()

add_result("XGBoost", "validation", y_val, best_xgb.predict(Xv), json.dumps(best_xgb_params, sort_keys=True))
add_result("XGBoost", "test", y_test, best_xgb.predict(Xt), json.dumps(best_xgb_params, sort_keys=True))

metrics = pd.DataFrame(rows)
metrics.to_csv(RESULTS / "model_metrics.csv", index=False)
pd.DataFrame(rf_trials).to_csv(RESULTS / "random_forest_tuning.csv", index=False)
pd.DataFrame(xgb_trials).to_csv(RESULTS / "xgboost_tuning.csv", index=False)

official = metrics[
    (metrics["split"] == "validation")
    & metrics["model"].isin(["Linear Regression", "Random Forest", "XGBoost"])
].sort_values("mae")
selected = official.iloc[0]["model"]

if selected == "XGBoost":
    selected_model = best_xgb
elif selected == "Random Forest":
    selected_model = best_rf
else:
    selected_model = linear

bundle = {
    "preprocessor": preprocessor,
    "model": selected_model,
    "features": FEATURES,
    "target": TARGET,
    "selected_model_name": selected,
}
joblib.dump(bundle, MODELS / "smartq_wait_time_model.joblib", compress=3)

summary = {
    "total_completed_rows": len(completed),
    "train_rows": len(train),
    "validation_rows": len(validation),
    "test_rows": len(test),
    "train_end": str(train_end.date()),
    "validation_start": str(val_start.date()),
    "validation_end": str(val_end.date()),
    "test_start": str(test_start.date()),
    "selected_model": selected,
    "best_random_forest_params": best_rf_params,
    "best_xgboost_params": best_xgb_params,
}
(RESULTS / "training_summary.json").write_text(json.dumps(summary, indent=2))

print(metrics.to_string(index=False))
print("\nSelected model:", selected)
