# SmartQ Model Evaluation

## Objective

The SmartQ machine-learning task is to predict customer waiting time in minutes using queue information available at check-in time.

The supervised target is `actual_wait_minutes`.

Only completed visits are used for the regression task because no-shows and cancelled visits do not have a genuine completed wait outcome.

## Data split

The 92,655 completed visits were split chronologically by whole operating days.

| Split | Rows | Date range |
|---|---:|---|
| Training | 64,074 | 2026-01-02 to 2026-06-16 |
| Validation | 14,665 | 2026-06-17 to 2026-07-22 |
| Test | 13,916 | 2026-07-23 to 2026-08-27 |

The same operating date never appears in more than one partition. This is more realistic than a random row split because SmartQ learns from earlier queue behaviour and is evaluated on later queue behaviour.

## Preprocessing

Numeric missing values are imputed using medians fitted on training data only. Categorical missing values use the most frequent training category. Categorical fields are one-hot encoded with unknown categories ignored.

The existing deterministic `baseline_eta_minutes` is not used as a model input. It is retained only as an engineering benchmark.

Post-outcome fields such as call time, actual service duration, service start/completion timestamps and the target itself are excluded from model inputs to avoid data leakage.

## Validation results

| Model | MAE (min) | RMSE (min) |
|---|---:|---:|
| Mean baseline | 15.9560 | 25.8235 |
| SmartQ deterministic ETA | 4.6871 | 6.3250 |
| Linear Regression | 4.1146 | 6.1452 |
| Random Forest | 2.6315 | 4.4920 |
| **XGBoost** | **2.6302** | **4.3893** |

The project selection rule is lowest validation MAE among Linear Regression, Random Forest and XGBoost. XGBoost therefore becomes the selected model.

The Random Forest and XGBoost validation MAEs differ by only about 0.0013 minutes, so they should be described as effectively very close rather than claiming that XGBoost is dramatically superior.

## Final test results

The untouched test set was evaluated after model selection was fixed.

| Model | MAE (min) | RMSE (min) |
|---|---:|---:|
| Mean baseline | 14.9850 | 24.8143 |
| SmartQ deterministic ETA | 4.6386 | 6.3683 |
| Linear Regression | 4.0645 | 6.4606 |
| Random Forest | 2.5231 | 4.6425 |
| **Selected XGBoost** | **2.5824** | **4.9561** |

Random Forest happens to have the lowest test MAE, but the selected model is not changed after seeing test results. Switching at this point would use the final test set for model selection and weaken the validity of the evaluation.

The selected XGBoost model beats the required simple mean-wait baseline by a large margin and also improves on the existing deterministic SmartQ ETA benchmark.

## Traffic-condition performance

Traffic scenarios are defined using `queue_pressure_index`:

- Low: below 1.0
- Moderate: 1.0 to below 2.5
- Busy: 2.5 or above

Selected XGBoost test performance:

| Traffic | Rows | MAE (min) | RMSE (min) |
|---|---:|---:|---:|
| Low | 6,216 | 1.22 | 2.40 |
| Moderate | 6,575 | 2.95 | 4.43 |
| Busy | 1,125 | 7.94 | 12.54 |

This shows an important limitation: prediction error increases substantially during heavy congestion. The result should be discussed openly in the final report.

## Service performance

XGBoost test MAE is similar across the three synthetic service types:

| Service | MAE (min) |
|---|---:|
| Collections | 2.61 |
| ID Applications | 2.54 |
| Passport Applications | 2.60 |

## Branch performance

The synthetic scenario shows different error levels by branch. The highest test MAE occurs for Centurion Service Centre at about 4.07 minutes, while Pretoria Central is about 2.00 minutes.

These branch names and results belong to the synthetic dataset. They must not be interpreted as measured performance of real service centres.

## Feature importance

The strongest XGBoost feature is `people_ahead`, followed by `queue_pressure_index` and `workload_minutes_ahead`. This is operationally sensible: a customer's wait is strongly affected by the amount of queued work and available serving capacity.

Feature importance describes how the fitted model uses the synthetic dataset; it should not be presented as causal proof.

## Selected model

**XGBoost** is the SmartQ integration candidate because it achieved the lowest validation MAE under the predeclared selection rule.

Best tested XGBoost configuration:

- n_estimators: 200
- max_depth: 5
- learning_rate: 0.08
- subsample: 0.9
- colsample_bytree: 0.9
- reg_lambda: 2.0

## Interpretation

The experiment satisfies the proposal requirement to train Linear Regression, Random Forest and XGBoost on the same prepared data and compare them using MAE and RMSE.

The results demonstrate performance on the **synthetic SmartQ operational dataset**. They do not establish guaranteed accuracy on real government, clinic, university or business queues. Real-world deployment would require validation and retraining using representative operational data.
