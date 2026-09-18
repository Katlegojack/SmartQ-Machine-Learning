# SmartQ Modelling Results

This folder stores reproducible outputs from the SmartQ waiting-time prediction experiment.

- `data_preparation_summary.json`: chronological split, feature list and selected hyperparameters.
- `model_metrics.csv`: MAE/RMSE for the mean baseline, deterministic SmartQ ETA, Linear Regression, Random Forest and XGBoost.
- `random_forest_tuning.csv`: limited Random Forest validation tuning.
- `xgboost_tuning.csv`: limited XGBoost validation tuning.
- `feature_importance.csv`: fitted selected-model feature importance.
- `scenario_performance.csv`: selected XGBoost performance under Low, Moderate and Busy traffic.
- `service_performance.csv`: selected-model performance by service.
- `branch_performance.csv`: selected-model performance by synthetic branch.
- `peak_performance.csv`: selected-model performance during peak and non-peak periods.

The official model is selected using **validation MAE**, not final test performance. XGBoost is retained as the selected model even though Random Forest happens to achieve a slightly lower test MAE, because changing the model after observing the final test results would contaminate the evaluation process.
