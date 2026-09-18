# SmartQ ML Integration Guide

## Purpose

This guide defines how the selected SmartQ XGBoost waiting-time model should be connected to the main Django/DRF SmartQ application.

The ML repository remains responsible for model training and evaluation. The main SmartQ application remains responsible for collecting live queue state and presenting predictions to users.

## Model artifact

Run:

```bash
python src/train_models.py
```

This creates:

```text
models/smartq_wait_time_model.joblib
```

The bundle contains both the fitted preprocessing transformer and the selected XGBoost model.

## Prediction contract

The integration layer must build one observation using information known at prediction time.

Required inputs:

```text
arrival_offset_minutes
people_ahead
general_waiting
priority_waiting
serving_count
open_general_counters
open_priority_counters
effective_open_counters
counter_utilisation
queue_pressure_index
workload_minutes_ahead
recent_avg_service_minutes_10
recent_avg_wait_minutes_10
recent_throughput_60m
service_target_minutes
hour_of_day
branch_code
service_code
booking_source
queue_type
day_of_week
is_peak_period
```

The helper in `src/predict.py` validates this contract and always returns a non-negative waiting-time estimate.

## Django integration shape

The SmartQ backend should calculate the current queue-state features from its own database and queue services, pass them to the predictor, and return the prediction through the existing API layer.

Conceptually:

```python
observation = build_live_queue_features(ticket)
predicted_minutes = predict_wait_minutes(observation)
```

The API response can expose a field such as:

```json
{
  "predicted_wait_minutes": 12.7,
  "prediction_model": "xgboost",
  "model_status": "active"
}
```

The exact response shape should be adapted to the existing SmartQ API rather than creating a second unrelated API.

## Important engineering rules

1. The model must never receive post-outcome fields such as actual wait or service completion time.
2. The model should be loaded once per application process where possible rather than reloaded from disk for every HTTP request.
3. If prediction fails, SmartQ should fall back safely to the existing deterministic ETA instead of breaking the customer queue experience.
4. The prediction should be rounded for customer display while retaining the raw numeric value for evaluation/logging.
5. Prediction latency should be measured against the proposal's two-second requirement.
6. Prediction observations and later actual waits should be logged so real operational data can eventually replace synthetic-only training.

## Current limitation

The selected model was trained on synthetic SmartQ data. Integration proves the end-to-end ML workflow, but a real deployment would require validation and retraining using representative live operational data.
