# SmartQ Model Diagnostics and Statistical Analysis

## Why this stage exists

MAE and RMSE tell us **how wrong a model is**, but they do not answer every question.

This diagnostics stage asks additional questions:

- Does the model generalise to unseen dates?
- Is it overfitting?
- How much variation does it explain?
- Which Linear Regression variables are statistically significant?
- Are some variables repeating the same information?
- Are the Linear Regression assumptions reasonable?
- Which features actually matter for XGBoost predictions?
- Where does the selected model still fail?

The important lesson is that **statistical significance, model fit, feature usefulness and predictive accuracy are related but are not the same thing**.

---

## 1. Train / validation / test model fit

| Model | Split | MAE | RMSE | R² |
|---|---|---:|---:|---:|
| Linear Regression | Train | 4.2204 | 6.4640 | 0.9515 |
| Linear Regression | Validation | 4.1146 | 6.1452 | 0.9433 |
| Linear Regression | Test | 4.0645 | 6.4606 | 0.9313 |
| Random Forest | Train | 1.8234 | 2.8922 | 0.9903 |
| Random Forest | Validation | 2.6315 | 4.4920 | 0.9697 |
| Random Forest | Test | 2.5231 | 4.6425 | 0.9645 |
| XGBoost | Train | 2.4457 | 3.9787 | 0.9816 |
| XGBoost | Validation | 2.6302 | 4.3893 | 0.9711 |
| XGBoost | Test | 2.5824 | 4.9561 | 0.9596 |

### Simple interpretation

All three models still perform well on later unseen dates, so there is no evidence of catastrophic overfitting.

Random Forest has the largest train-to-validation improvement gap:

- Train MAE: 1.82
- Validation MAE: 2.63

That shows it fits the training data more aggressively.

XGBoost has a smaller gap:

- Train MAE: 2.45
- Validation MAE: 2.63

This is one reason the XGBoost result looks more stable even though Random Forest and XGBoost are extremely close on validation accuracy.

### What is R²?

R² measures how much of the variation in waiting time the model explains.

For example, XGBoost test R² = 0.9596 means the fitted predictions explain about 96% of the variation in the synthetic test waiting times.

R² is useful, but it does not replace MAE/RMSE because customer-facing accuracy still needs to be understood in minutes.

---

## 2. Linear Regression statistical model

For statistical inference, a companion OLS Linear Regression was fitted on the training set.

The statistical version uses the same underlying predictor concepts, but categorical variables use reference-category encoding so that the coefficient matrix is identifiable.

HC3 robust standard errors are used because the residual-variance test shows heteroscedasticity.

Training statistical fit:

- R²: **0.94855**
- Adjusted R²: **0.94853**
- Training rows: **64,074**
- Estimated terms including intercept: **30**

Adjusted R² is almost identical to R², which means adding the current terms is not producing a large artificial R² increase simply from having many predictors.

---

## 3. Statistical significance

Using HC3 robust standard errors, 26 of the 30 estimated terms have p < 0.05.

Four terms are not statistically significant at the 5% threshold:

- Monday indicator
- Tuesday indicator
- Wednesday indicator
- Peak-period indicator

### Important interpretation

This does **not** mean those concepts are useless everywhere.

For example, raw EDA shows peak periods have higher average waits.

However, after the regression already controls for actual queue state such as people ahead, workload and counters, the simple peak-period flag adds little independent linear information.

That is an important distinction:

> A variable can show a raw group difference but become weak after more direct explanatory variables are included.

With more than 64,000 training observations, even very small effects can produce tiny p-values. Therefore p < 0.05 must not automatically be translated into "important for SmartQ".

Practical importance must also be examined through predictive error, effect size and feature-importance diagnostics.

---

## 4. Group significance tests and effect size

### General vs Priority

- General mean wait: 16.90 min
- Priority mean wait: 9.66 min
- Welch p-value: effectively < 0.001
- Cohen's d: **0.258**

There is a statistically clear difference, but the standardised effect size is small-to-moderate rather than enormous.

### Appointment vs Walk-in

- Appointment mean wait: 16.97 min
- Walk-in mean wait: 12.97 min
- p-value: 1.21e-74
- Cohen's d: **0.142**

The difference is statistically strong because of the large dataset, but the standardised effect is small.

### Peak vs Non-peak

- Peak mean wait: 16.97 min
- Non-peak mean wait: 14.47 min
- p-value: 3.16e-36
- Cohen's d: **0.089**

Again, statistically significant but a very small standardised effect.

### Service type

A one-way ANOVA comparing the raw waiting-time means of Collections, ID Applications and Passport Applications gives:

- F = 0.4303
- p = **0.6503**
- eta-squared ≈ **0.000009**

There is no meaningful raw overall waiting-time difference between the three service types in this generated dataset.

This is a useful reminder that a feature can still participate in a multivariable model even when its simple unadjusted group means are similar.

---

## 5. Multicollinearity and VIF

### What is multicollinearity?

Multicollinearity means multiple predictors carry very similar information.

This is mainly a problem for interpreting individual Linear Regression coefficients.

### What is VIF?

Variance Inflation Factor (VIF) measures how strongly one predictor can be explained by the other predictors.

A common rough interpretation is:

- around 1: little overlap
- 5+: notable overlap
- 10+: strong overlap

Several SmartQ engineered queue variables have very high VIF:

| Feature | VIF |
|---|---:|
| queue_pressure_index | 44.14 |
| people_ahead | 38.91 |
| serving_count | 38.76 |
| counter_utilisation | 38.54 |
| general_waiting | 35.16 |
| workload_minutes_ahead | 33.18 |
| open_general_counters | 7.79 |

### Why is this happening?

These variables are deliberately related.

For example:

- queue pressure depends on waiting demand and available capacity;
- workload ahead is strongly related to people ahead;
- counter utilisation is related to serving count and counters.

### Decision

We do **not** remove these variables from XGBoost or Random Forest solely because of high VIF.

Tree models can still use overlapping signals for prediction.

However, we must be careful when interpreting individual Linear Regression coefficients. With severe multicollinearity, coefficient signs and sizes can become unstable even when overall prediction remains good.

A reduced Linear Regression could be explored later if the main research goal becomes coefficient interpretation rather than prediction.

---

## 6. Linear Regression assumption checks

### Heteroscedasticity

Breusch-Pagan test:

- LM statistic ≈ 13,674.78
- p-value ≈ 0

This indicates **heteroscedasticity**: the amount of prediction error changes across different queue conditions.

That is not surprising because severe congestion produces much larger errors than quiet conditions.

### Residual normality

Jarque-Bera test:

- statistic ≈ 163,042
- p-value ≈ 0
- residual skewness ≈ 0.85
- residual kurtosis ≈ 10.63

The residuals are not normally distributed.

With 64,000+ observations, formal normality tests are extremely sensitive, but the high kurtosis also confirms heavy error tails.

### Durbin-Watson

Durbin-Watson ≈ **1.91**.

A value near 2 does not show obvious strong first-order residual autocorrelation in the fitted row order.

This is not a complete time-dependence analysis; chronological splitting remains the main protection against unrealistic temporal leakage.

### Decision

Because heteroscedasticity is present, robust HC3 standard errors are used for the Linear Regression p-values and confidence intervals.

The predictive model is still judged primarily on unseen validation/test performance, not on perfect satisfaction of classical OLS assumptions.

---

## 7. Negative raw predictions

Regression algorithms can mathematically predict values below zero even though negative waiting time makes no operational sense.

On the test set:

- Linear Regression produced 2,192 raw negative predictions.
- XGBoost produced 962 raw negative predictions.
- Random Forest produced 0 raw negative predictions.

For XGBoost the negatives are generally small:

- minimum raw prediction ≈ -1.04 min
- median among negative predictions ≈ -0.10 min

### Decision

Customer-facing predictions are clipped at zero:

`max(0, prediction)`

This rule is already present in the SmartQ prediction helper.

This is transparent post-processing based on a real-world constraint, not hidden model manipulation.

---

## 8. Permutation importance

### What is permutation importance?

Take one feature and randomly shuffle it.

If model MAE becomes much worse, that feature contained useful predictive information.

Selected XGBoost test MAE before shuffling:

**2.5824 min**

Largest MAE increases after shuffling:

| Feature | MAE increase |
|---|---:|
| workload_minutes_ahead | +7.54 min |
| people_ahead | +4.15 min |
| arrival_offset_minutes | +3.30 min |
| effective_open_counters | +2.70 min |
| queue_pressure_index | +0.54 min |
| open_general_counters | +0.31 min |
| counter_utilisation | +0.22 min |
| queue_type | +0.20 min |

This gives strong evidence that workload, position in the queue and effective serving capacity are genuinely useful to XGBoost prediction.

Small negative permutation values for a few low-importance features should be interpreted as noise/redundancy, not proof that those variables are harmful.

---

## 9. SHAP explanation

### What is SHAP?

SHAP estimates how much each feature pushes a model prediction up or down.

For a single customer it can answer:

> "Why did the model predict this waiting time?"

Using XGBoost TreeSHAP on a fixed 5,000-row test sample, the strongest average absolute contributions are:

| Feature | Mean absolute SHAP contribution |
|---|---:|
| workload_minutes_ahead | 7.10 |
| people_ahead | 5.74 |
| arrival_offset_minutes | 3.88 |
| effective_open_counters | 2.59 |
| queue_pressure_index | 1.47 |
| open_general_counters | 0.76 |

SHAP and permutation importance tell a consistent story: the amount of work ahead and the capacity available to process it are the main prediction signals.

---

## 10. Is the selected model a good fit?

For the current **synthetic SmartQ dataset**, yes, with important limitations.

Evidence supporting a useful predictive fit:

- XGBoost validation MAE ≈ 2.63 min.
- XGBoost test MAE ≈ 2.58 min.
- XGBoost test R² ≈ 0.960.
- Validation and test performance are close.
- It strongly beats the simple mean baseline.
- It improves on the existing deterministic ETA.
- Permutation importance and SHAP identify operationally sensible features.

Reasons not to overclaim:

- all training/evaluation data is synthetic;
- busy-traffic MAE is much worse;
- engineered queue features are strongly correlated;
- raw XGBoost can produce small negative values before clipping;
- model performance on a real deployment is still unknown.

Therefore the correct conclusion is:

> XGBoost is a strong prototype fit for the synthetic SmartQ operational dataset and a reasonable integration candidate, but real-world accuracy still requires representative live data and external validation.

---

## 11. What changed because of this diagnostics stage?

The selected model did **not** change.

Why?

The new diagnostics do not show a methodological reason to override the predefined validation-MAE selection rule.

Instead, this stage improved our understanding:

- XGBoost generalises well on the generated later dates.
- Random Forest fits training data more aggressively.
- Several Linear Regression coefficients are difficult to interpret because of multicollinearity.
- Classical OLS constant-variance/normal-error assumptions do not hold perfectly.
- HC3 robust inference is therefore more appropriate.
- Statistical significance is not the same as practical importance.
- workload, people ahead and effective counter capacity are genuinely important predictive signals.
- busy conditions and non-negative prediction handling remain important limitations.

That is exactly what diagnostics are supposed to do: improve understanding rather than blindly force a model change.
