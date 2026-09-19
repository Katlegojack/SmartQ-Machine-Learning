# SmartQ Diagnostics Results

This directory contains the machine-readable outputs from the model-diagnostics and statistical-understanding stage.

Files:

- `model_fit_by_split.csv` — MAE, RMSE and R² for each official model across training, validation and test data.
- `residual_summary.csv` — residual bias/spread and raw negative-prediction counts.
- `linear_ols_hc3_coefficients.csv` — Linear Regression coefficients, HC3 robust standard errors, p-values and confidence intervals.
- `linear_assumption_tests.csv` — heteroscedasticity, normality, autocorrelation indicator and R² diagnostics.
- `vif_numeric_features.csv` — Variance Inflation Factor for numeric predictors.
- `group_significance_tests.csv` — Welch tests and Cohen's d for selected EDA comparisons.
- `service_anova.csv` — overall service-type ANOVA and eta-squared.
- `permutation_importance.csv` — change in XGBoost test MAE after each original feature is shuffled.
- `shap_importance.csv` — mean absolute XGBoost TreeSHAP contribution on a fixed 5,000-row test sample.

The goal of these files is not to create more metrics for their own sake. They document **why the model behaves the way it does and where its limitations are**.
