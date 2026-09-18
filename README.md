<<<<<<< HEAD
# SmartQ-Machine-Learning
=======
# SmartQ Machine Learning

Machine-learning workspace for **SmartQ: A Machine-Learning-Assisted Queue Management System for Waiting-Time Prediction**.

## Objective

Use SmartQ queue-state information to predict customer waiting time and compare the three regression models defined in the project proposal:

- Linear Regression
- Random Forest Regressor
- XGBoost Regressor

The primary prediction target is:

`actual_wait_minutes`

Models will be compared using **MAE (Mean Absolute Error)** and **RMSE (Root Mean Squared Error)**. Model selection will use validation MAE, followed by a final evaluation on an unseen chronological test set.

## Repository structure

```text
SmartQ-Machine-Learning/
├── data/
│   └── SmartQ_Synthetic_Operational_Dataset_100k.csv
├── notebooks/
│   └── SmartQ_ML_100k_Embedded_Dataset.ipynb
├── docs/
│   └── SmartQ_100k_Synthetic_Dataset_Documentation.docx
├── models/
├── results/
├── src/
├── requirements.txt
└── README.md
```

## Dataset

The dataset contains **100,000 synthetic SmartQ operational records** generated to represent realistic queue behaviour across multiple branches and operating days.

It includes appointments, walk-ins, General/Priority lanes, early/on-time/late arrivals, no-shows, cancellations, queue position, people ahead, active counters, queue pressure, service targets, actual waiting time, actual service duration, counter assignment, and time-based operational features.

The dataset is **synthetic** and contains no real customer personal information.

## Important ML rule

For waiting-time prediction, only information available at prediction/check-in time should be used as model input.

Post-outcome fields such as `call_time`, `actual_wait_minutes`, `actual_service_minutes`, `service_started_at`, and `service_completed_at` must not be used as predictors because that would cause data leakage.

## Planned workflow

1. Data understanding and validation
2. Data preparation
3. Chronological train/validation/test split
4. Mean-wait baseline
5. Linear Regression
6. Random Forest
7. XGBoost
8. MAE/RMSE comparison
9. Selected-model test evaluation
10. Model export
11. SmartQ API integration

## Status

Dataset and initial notebook prepared. Model development follows next.
>>>>>>> 25df0ba (Initialize SmartQ machine learning project with 100k dataset)
