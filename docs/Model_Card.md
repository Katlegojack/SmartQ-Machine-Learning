# SmartQ Waiting-Time Model Card

## Model

Selected model: **XGBoost Regressor**

Purpose: predict `actual_wait_minutes` at customer check-in.

## Training population

92,655 completed synthetic SmartQ visits.

- Train: 64,074
- Validation: 14,665
- Test: 13,916

## Selection rule

Lowest validation MAE among Linear Regression, Random Forest and XGBoost.

Selected XGBoost validation MAE: **2.6302 minutes**.

Final test MAE: **2.5824 minutes**.  
Final test RMSE: **4.9561 minutes**.

## Intended inputs

Queue-state and operational information known at prediction time, including people ahead, queue pressure, workload ahead, active counters, recent operational averages, service type, branch, booking source, queue lane and time features.

## Excluded inputs

Post-outcome information such as call time, actual wait, actual service duration and completion timestamps is excluded to prevent data leakage.

The existing deterministic SmartQ ETA is also excluded from the official ML feature set.

## Important limitations

The model is trained entirely on synthetic SmartQ operational data. It is suitable for demonstrating the capstone methodology and prototype integration, not for claiming production accuracy on a real organisation.

Prediction error is substantially larger under very busy queue conditions. Real deployment would require representative live data, monitoring and retraining.
