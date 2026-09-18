# SmartQ Machine Learning — Engineering Worklog and Decision Record

> **Purpose of this file:** This is the detailed internal explanation of what was done, how it was done, why each decision was made, what alternatives were considered, what trade-offs were accepted, what the results mean, and what still has to be done.
>
> This file is intentionally kept under `.project-notes/` so it does not compete with the public project `README.md`. It is written in simple English for revision, project defence, and future maintenance.

---

## 1. Where the machine-learning work currently stands

The core SmartQ machine-learning experiment is complete.

We have:

- created and validated a 100,000-row synthetic SmartQ operational dataset;
- completed Data Understanding / EDA;
- defined the waiting-time prediction target;
- removed records that are not valid for waiting-time regression;
- prevented obvious data leakage;
- prepared numeric and categorical features;
- created a chronological train / validation / test split;
- trained the required Linear Regression, Random Forest and XGBoost models;
- used MAE and RMSE to compare them;
- performed limited, documented tuning;
- selected XGBoost using the pre-declared validation-MAE rule;
- evaluated the chosen approach on later unseen dates;
- analysed performance during low, moderate and busy traffic;
- inspected feature importance;
- added reproducible training code;
- added a prediction helper for later Django integration;
- documented limitations honestly;
- added automated dataset-quality checks.

The next major engineering stage is to connect the selected model to the main SmartQ Django application and measure prediction response time.

---

## 2. The problem we are solving

SmartQ wants to answer a simple customer question:

> **"How many minutes am I likely to wait from check-in until I am called?"**

The supervised machine-learning target is:

`actual_wait_minutes`

For a completed visit, this is the time between:

`check_in_at -> call_time`

This target was chosen because it matches the user-facing problem in the project proposal: estimating waiting time before service begins.

We are **not** trying to predict total time spent inside the service centre. That would include service duration and would be a different target.

---

## 3. Why we used synthetic SmartQ data

At this stage SmartQ does not have a large, trustworthy real-world production dataset.

The project therefore uses a controlled synthetic operational dataset designed around SmartQ queue behaviour.

The dataset contains:

- 100,000 rows;
- 45 columns;
- several synthetic branches;
- appointments and walk-ins;
- General and Priority queue lanes;
- early, on-time and late arrivals;
- no-shows and cancellations;
- queue positions;
- people ahead;
- open counters;
- queue pressure;
- service targets;
- actual service durations;
- actual waiting times;
- counter assignments;
- timestamps;
- peak and non-peak periods.

### Why this was the practical choice

The project proposal explicitly allows prototype-generated and simulated queue events. Synthetic data gives us enough records to demonstrate the complete machine-learning pipeline without pretending that we already have large amounts of real customer data.

### Trade-off

Synthetic data gives us control and enough volume, but it also makes model performance easier than true deployment may be.

The model is learning patterns created by the SmartQ simulator. Real organisations can contain behaviour that the simulator does not represent: staff breaks, paperwork problems, customers changing services, counter failures, unusual surges, policy changes, missing data, and many other factors.

Therefore:

> **The current model proves the SmartQ ML methodology and prototype workflow. It does not prove guaranteed real-world accuracy.**

That statement must remain in the final report and presentation.

---

## 4. Stage 1 — Data Understanding / EDA

### Is Data Understanding the same as EDA?

Not exactly.

**EDA (Exploratory Data Analysis)** is the main practical activity inside Data Understanding.

EDA means looking at distributions, counts, averages, missing values, unusual values, relationships and graphs.

Data Understanding is slightly wider. It also asks:

- What does each column mean?
- Which records are suitable for the ML task?
- Is the target correct?
- Are there impossible records?
- Are some missing values normal?
- Which variables could leak the answer?
- Does the data behave logically enough to move to modelling?

### What we checked

The repository contains:

`notebooks/01_Data_Understanding_EDA.ipynb`

and:

`docs/EDA_Findings.md`

The EDA examined:

- dataset dimensions;
- record status counts;
- services;
- branches;
- General vs Priority traffic;
- appointments vs walk-ins;
- weekday patterns;
- peak periods;
- missing values;
- waiting-time distribution;
- waiting time by branch;
- waiting time by service;
- waiting time by queue type;
- waiting time by booking source;
- waiting time by hour;
- relationships between queue-state variables and waiting time;
- existing deterministic SmartQ ETA performance;
- data-quality rules;
- data-leakage risks.

### Main EDA result

The full dataset contains:

- 100,000 total records;
- 92,655 completed visits;
- 5,096 no-shows;
- 2,249 cancelled visits.

For completed visits:

- average wait: about 16.03 minutes;
- median wait: about 7.50 minutes;
- 95th percentile wait: about 61.73 minutes;
- maximum generated wait: about 358.10 minutes.

The large difference between the median and the maximum shows that waiting time is **right-skewed**: most customers wait much less than the worst congestion cases.

This is one reason we use both MAE and RMSE.

MAE tells us the average size of an error in easy-to-explain minutes.

RMSE punishes large errors more heavily, which helps show when a model struggles badly on extreme congestion.

---

## 5. Data-quality validation

Before modelling, we checked whether the synthetic data obeyed basic SmartQ rules.

The checks returned zero violations for:

- negative completed waiting time;
- non-positive completed service duration;
- queue position not matching people ahead + 1;
- a customer being called before service eligibility;
- service starting before the call;
- service ending before it started;
- an appointment becoming eligible before the booked time;
- walk-in eligibility not matching check-in.

Why do this before modelling?

Because a model can successfully learn bad data. A low error score is meaningless if timestamps or queue positions are logically impossible.

This is also why `src/validate_dataset.py` exists and why a GitHub Actions quality workflow was added.

---

## 6. Which rows were used for regression and why

Only rows with:

`status == COMPLETED`

are used for waiting-time regression.

That leaves:

**92,655 completed visits**

### Why exclude no-shows?

A no-show does not have a genuine completed queue wait because the customer never arrives and waits for service.

### Why exclude cancellations?

A cancelled visit also does not represent the normal check-in -> call waiting-time process.

### Alternative considered

We could have filled missing waiting-time outcomes for cancelled/no-show records with zero.

We deliberately did **not** do that.

Why?

Because zero would incorrectly mean "the customer arrived and was served immediately." That is not what cancellation or no-show means.

If SmartQ later wants to predict whether somebody will become a no-show, that should be a **separate classification model**, not forced into the waiting-time regression target.

---

## 7. Features used for modelling

The current official feature set contains information SmartQ can know at or around check-in time.

### Numeric features

- `arrival_offset_minutes`
- `people_ahead`
- `general_waiting`
- `priority_waiting`
- `serving_count`
- `open_general_counters`
- `open_priority_counters`
- `effective_open_counters`
- `counter_utilisation`
- `queue_pressure_index`
- `workload_minutes_ahead`
- `recent_avg_service_minutes_10`
- `recent_avg_wait_minutes_10`
- `recent_throughput_60m`
- `service_target_minutes`
- `hour_of_day`

### Categorical features

- `branch_code`
- `service_code`
- `booking_source`
- `queue_type`
- `day_of_week`
- `is_peak_period`

### Why these features?

They describe four things that logically affect waiting time:

1. **Demand** — how many customers are waiting.
2. **Capacity** — how many counters are available.
3. **Workload** — how much expected service work is ahead.
4. **Context** — service type, branch, queue lane and time pattern.

---

## 8. Why `people_ahead` and workload features are important

The strongest XGBoost feature is `people_ahead`.

Other strong features include:

- `queue_pressure_index`
- `workload_minutes_ahead`

This makes operational sense.

If many people are ahead of a customer, or the amount of service work ahead is high compared with open counters, the customer should usually wait longer.

### Important caution

Feature importance does **not** prove cause and effect.

It only tells us that the fitted model relied heavily on those variables in this synthetic dataset.

---

## 9. Data leakage — one of the most important decisions

Data leakage means accidentally giving the model information that would not really be known when the prediction is supposed to happen.

That can make a model look excellent while being useless in a real system.

We deliberately excluded post-outcome fields such as:

- `call_time`
- `actual_wait_minutes`
- `wait_variance_minutes`
- `actual_service_minutes`
- `service_variance_minutes`
- `counter_number`
- `service_started_at`
- `service_completed_at`
- status-derived outcome flags.

### Why exclude `actual_wait_minutes`?

Because that is literally the answer we are trying to predict.

### Why exclude `actual_service_minutes`?

At customer check-in, SmartQ does not yet know exactly how long future service will take.

### Why exclude the final counter number?

The exact counter that eventually serves the customer is an outcome of queue operation. Depending on how routing works, it may not be known at initial prediction time.

---

## 10. Why the existing SmartQ deterministic ETA was NOT used as an ML input

The dataset contains:

`baseline_eta_minutes`

We deliberately do not feed it into Linear Regression, Random Forest or XGBoost.

Instead, we use it as an **extra benchmark**.

### Why?

If we gave the baseline ETA directly to the ML model, the model could mainly learn to correct the existing formula.

That can be a valid future engineering technique, but it makes the academic comparison less clean.

For this capstone we want to answer:

> Can the ML models learn waiting time from queue conditions themselves?

Therefore the comparison remains:

- simple mean baseline;
- existing SmartQ deterministic ETA benchmark;
- Linear Regression;
- Random Forest;
- XGBoost.

### Trade-off

Excluding the baseline ETA may sacrifice some possible predictive performance.

The benefit is a clearer, easier-to-defend experiment.

A later production experiment can test a **hybrid residual model** where ML predicts the error of the deterministic ETA.

That was considered as a future option, but it was not added to the official experiment because the proposal specifies the three regression models and we want to keep scope controlled.

---

## 11. Missing values and how they were handled

The important missing values inside completed visits occur mainly in:

- `recent_avg_service_minutes_10`
- `recent_avg_wait_minutes_10`

This happens early in a day when there may not yet be enough previous completed/called customers to calculate recent averages.

These records are not bad records.

### Decision

Numeric missing values are filled using the **median calculated from the training set only**.

Categorical missing values use the most frequent value from the training set.

### Why median?

The waiting-time data and some queue features can be skewed.

The median is less sensitive to extreme congestion than the mean.

### Why not delete those rows?

Deleting them would throw away valid early-day visits and could make the model weaker exactly when the system has little recent history.

### Why fit the imputer only on training data?

If we used the validation or test data to calculate the median, information from the future evaluation data would influence preprocessing.

That is a subtle form of leakage.

---

## 12. Why categorical variables were one-hot encoded

Algorithms cannot directly understand labels such as:

`PTC1`, `IDAPP`, `GENERAL`, `Monday`

So categorical variables are converted into binary indicator columns using one-hot encoding.

Example:

`queue_type = GENERAL / PRIORITY`

becomes separate machine-readable indicators.

### Why `handle_unknown="ignore"`?

If a later dataset contains a category that was not present in training, the preprocessing pipeline should not crash immediately.

### Alternative approaches considered

Ordinal encoding was not appropriate because branch codes and service codes do not have a natural numeric order.

Target encoding was not used because it is more complex and can easily leak target information if not implemented carefully.

For this dataset, one-hot encoding is simple, transparent and small enough to be practical.

---

## 13. Why we did not standardise every numeric feature

We did not add StandardScaler to the official preprocessing pipeline.

### Why?

Random Forest and XGBoost tree models do not need standardised numeric scales.

Ordinary Linear Regression can work without feature scaling; scaling changes coefficient size and numerical conditioning, but not the basic linear fit in the same way it affects distance-based or gradient-sensitive algorithms.

The current numeric ranges are manageable, and avoiding another transformation keeps the pipeline easier to explain.

### Trade-off

Standardisation could make Linear Regression coefficients easier to compare and can improve numerical conditioning in some datasets.

It was not necessary for the main prediction comparison.

If interpretation of standardised linear coefficients becomes a report requirement, a second analysis can be added without changing the main model-selection process.

---

## 14. Chronological train / validation / test split

This is one of the strongest methodological decisions in the project.

Instead of randomly mixing all rows, we split by **whole operating dates**.

The completed visits were divided as follows:

| Split | Rows | Date range |
|---|---:|---|
| Training | 64,074 | 2026-01-02 to 2026-06-16 |
| Validation | 14,665 | 2026-06-17 to 2026-07-22 |
| Test | 13,916 | 2026-07-23 to 2026-08-27 |

The split is roughly 70% / 15% / 15%.

### Why chronological instead of random?

SmartQ will normally learn from past queue behaviour and make predictions on future queue behaviour.

A chronological split copies that situation better.

It also prevents records from the same simulated operating day from being spread across training and testing.

### What problem can random splitting create?

Customers from the same day share:

- staffing level;
- traffic pattern;
- branch conditions;
- queue build-up;
- recent service history.

If some customers from the same day are in training and others are in testing, the evaluation can become unrealistically easy.

### Trade-off

A chronological split can expose changes between earlier and later periods, which may make performance look worse than a random split.

That is actually useful because it is closer to deployment.

### Alternative considered

Time-series cross-validation / rolling-window validation would provide a more thorough estimate across multiple future periods.

We did not use it because:

- the proposal asks for a clear train / validation / test comparison;
- the project deadline is tight;
- the current whole-day chronological split is easier to explain;
- the main goal is a third-year capstone, not exhaustive model research.

Rolling validation is a good future improvement.

---

## 15. Why we have both a validation set and a test set

The validation set is used to make modelling decisions.

The test set is the final exam.

### Validation set

Used for:

- comparing Linear Regression, Random Forest and XGBoost;
- selecting limited hyperparameters;
- selecting the winning model using validation MAE.

### Test set

Used only after the model-selection rule was fixed.

After selection, we also calculated post-selection test metrics for the other models for diagnostic comparison. Those extra test scores were **not used to change the selected model**.

This distinction is important.

The test set must not become a second validation set.

---

## 16. Baselines — why we need them

A machine-learning score means little without something simple to compare against.

### Baseline 1 — mean waiting time

The required simple baseline predicts the training-set mean wait for every customer.

This is intentionally simple.

If a complex ML model cannot beat this, the model is not useful.

### Baseline 2 — existing deterministic SmartQ ETA

SmartQ already has a formula-style ETA.

We keep it as an engineering benchmark.

It is not one of the three proposal ML models.

### Why two baselines?

The mean baseline answers:

> Does ML beat a very simple guess?

The deterministic ETA answers:

> Does ML improve on the queue logic SmartQ already has?

---

## 17. Models trained

The proposal requires:

1. Linear Regression
2. Random Forest Regressor
3. XGBoost Regressor

We trained all three on the same prepared training data.

They were compared using the same validation data and the same MAE / RMSE metrics.

This keeps the comparison fair.

---

## 18. Why these three models make sense

### Linear Regression

Purpose:

- simple;
- transparent;
- fast;
- gives us a useful lower-complexity reference.

Weakness:

Queue relationships are not perfectly linear.

For example, congestion can change sharply when counter capacity becomes insufficient. Linear Regression may struggle with those nonlinear effects.

### Random Forest

Purpose:

- models nonlinear relationships;
- handles interactions naturally;
- robust and strong on tabular operational data;
- requires little preprocessing.

Weakness:

- larger model;
- can be slower;
- may overfit if trees are too deep;
- predictions come from averaging trees rather than a simple interpretable formula.

### XGBoost

Purpose:

- strong algorithm for structured/tabular data;
- captures nonlinear relationships;
- builds trees sequentially to correct earlier errors;
- offers useful regularisation and tuning controls.

Weakness:

- more complex than Linear Regression;
- easier to overtune if we search too many parameters;
- feature importance still needs careful interpretation.

---

## 19. Limited tuning — what was actually explored

We did **not** run a huge hyperparameter search.

That was deliberate.

The proposal says tuning should be limited and documented.

### Random Forest configurations actually tested

Candidate 1:

- `n_estimators = 100`
- `max_depth = 18`
- `min_samples_leaf = 2`
- `max_features = 0.8`

Validation MAE: about **2.6347 minutes**

Candidate 2:

- `n_estimators = 150`
- `max_depth = 14`
- `min_samples_leaf = 2`
- `max_features = 1.0`

Validation MAE: about **2.6315 minutes**

Candidate 2 was retained.

### XGBoost configurations actually tested

Candidate 1:

- `n_estimators = 150`
- `max_depth = 4`
- `learning_rate = 0.05`
- `subsample = 0.9`
- `colsample_bytree = 0.9`
- `reg_lambda = 1.0`

Validation MAE: about **2.7754 minutes**

Candidate 2:

- `n_estimators = 200`
- `max_depth = 5`
- `learning_rate = 0.08`
- `subsample = 0.9`
- `colsample_bytree = 0.9`
- `reg_lambda = 2.0`

Validation MAE: about **2.6302 minutes**

Candidate 2 was retained.

### Why not use GridSearchCV over hundreds of combinations?

Because that would:

- increase computation;
- increase the chance of overfitting our validation set;
- make the project harder to explain;
- go beyond what the proposal requires;
- create a lot of complexity for almost no academic benefit at this stage.

The goal is to demonstrate sound ML engineering, not to win a benchmark competition.

---

## 20. Metrics and what they mean

### MAE — Mean Absolute Error

MAE answers:

> On average, how many minutes away from the true wait was the prediction?

Example:

MAE = 2.58 minutes

means the prediction is off by about 2.58 minutes on average in absolute terms on that evaluation set.

### RMSE — Root Mean Squared Error

RMSE penalises large mistakes more strongly.

If a model is usually accurate but occasionally makes very large errors, RMSE exposes that more strongly than MAE.

### Why validation MAE is the model-selection rule

The proposal explicitly uses MAE and RMSE and states that the integrated model should have the lowest validation error.

MAE is also very easy to explain in customer-waiting-time units.

Therefore we fixed:

> **Lowest validation MAE = selected model**

before using final test results for the decision.

---

## 21. Validation results

| Model | Validation MAE | Validation RMSE |
|---|---:|---:|
| Mean baseline | 15.9560 | 25.8235 |
| SmartQ deterministic ETA | 4.6871 | 6.3250 |
| Linear Regression | 4.1146 | 6.1452 |
| Random Forest | 2.6315 | 4.4920 |
| **XGBoost** | **2.6302** | **4.3893** |

According to the declared rule, XGBoost wins.

### Very important detail

Random Forest and XGBoost are almost tied.

Difference in validation MAE:

about **0.0013 minutes**

That is tiny.

We must **not** tell a lecturer that XGBoost destroyed Random Forest.

A correct statement is:

> Random Forest and XGBoost performed almost identically on validation MAE, with XGBoost narrowly achieving the lowest value and therefore being selected under the predeclared rule.

That is more scientifically honest.

---

## 22. Final test results

After selection was fixed:

| Model | Test MAE | Test RMSE |
|---|---:|---:|
| Mean baseline | 14.9850 | 24.8143 |
| SmartQ deterministic ETA | 4.6386 | 6.3683 |
| Linear Regression | 4.0645 | 6.4606 |
| Random Forest | 2.5231 | 4.6425 |
| **Selected XGBoost** | **2.5824** | **4.9561** |

### Why didn't we change to Random Forest after seeing this?

Random Forest happens to have a slightly lower test MAE.

But the test set is not supposed to choose the model.

If we switch models because we like the final-test result better, we have started tuning against the test set.

That weakens the experiment.

Therefore XGBoost stays selected because it won the **validation** rule.

### Trade-off

This means we keep a model whose final test MAE is about 0.059 minutes worse than Random Forest.

That is only about 3.5 seconds difference in average absolute error.

The methodological benefit of keeping the selection process honest is more important than chasing that tiny test-set difference.

---

## 23. Why XGBoost is the current integration candidate

XGBoost is not being called "universally best."

It is the integration candidate because:

- it is one of the three proposal models;
- it achieved the lowest validation MAE;
- it achieved the lowest validation RMSE of the three ML models;
- its final test performance is strong;
- it beats the simple mean baseline by a large margin;
- it improves on the current deterministic SmartQ ETA benchmark;
- it can be packaged and called quickly from a web backend.

This is the best decision **for the current declared project methodology**.

It is not a claim that XGBoost would always beat Random Forest on every future real dataset.

---

## 24. Busy-traffic analysis — an important weakness

We did not stop at one overall MAE.

The selected XGBoost model was also checked under synthetic traffic conditions.

Traffic bands use `queue_pressure_index`:

- Low: below 1.0
- Moderate: 1.0 to below 2.5
- Busy: 2.5 or above

Results:

| Traffic | Rows | MAE | RMSE |
|---|---:|---:|---:|
| Low | 6,216 | 1.22 | 2.40 |
| Moderate | 6,575 | 2.95 | 4.43 |
| Busy | 1,125 | 7.94 | 12.54 |

### What this tells us

The model is much less accurate during severe congestion.

That matters because busy queues are exactly when waiting-time prediction is most useful.

### Why not hide this?

Because it is a real limitation of the model and dataset.

A strong project should show where the model fails, not only where it looks good.

### Likely future improvement

Collect more genuinely busy operational examples and retrain with richer congestion signals.

Potential future features could include:

- counter downtime / pause status;
- staff changeovers;
- service mix of customers ahead;
- time since last counter completion;
- queue growth rate;
- recent arrival rate;
- rolling throughput trend;
- counter-specific service speed.

These are future improvements, not current model inputs.

---

## 25. Why we did not use neural networks

Neural networks were deliberately not added to the official model experiment.

Reasons:

- the proposal explicitly keeps deep learning out of scope;
- the data is structured/tabular, where tree models are often very strong;
- neural networks would add tuning complexity;
- the project deadline is tight;
- adding another model would weaken focus rather than strengthen the declared methodology.

A neural network could be explored later as an extension, but it is not needed to satisfy the current capstone.

---

## 26. Why we did not turn this into a time-series forecasting problem

SmartQ predicts the waiting time for an individual customer using the queue state at prediction time.

That is naturally a supervised regression problem.

A separate time-series project could forecast:

- queue length 30 minutes from now;
- branch demand later today;
- expected arrivals next hour.

That is useful, but it is a different problem.

We kept the current ML component focused on the proposal's waiting-time prediction task.

---

## 27. Why we did not remove all extreme waits

The dataset contains long waiting-time cases, including some severe congestion.

We did not automatically delete them just because they are inconvenient for the model.

Why?

Because long waits are operationally important.

Deleting every large value would make the dataset cleaner but could hide exactly the situations SmartQ is supposed to help manage.

### Trade-off

Keeping extremes increases RMSE and makes busy-period prediction harder.

That is acceptable if the records are logically valid.

Outliers should be removed only when there is evidence that they are invalid data, not merely because the model dislikes them.

---

## 28. Why no-shows and cancellations remain in the master dataset

They are excluded from the waiting-time regression subset, but they remain in the master dataset.

Why?

Because they are still valid SmartQ operational events.

They may be useful later for:

- no-show prediction;
- appointment adherence analysis;
- branch analytics;
- demand planning;
- operational reporting.

Keeping the raw/master data richer is better than deleting information simply because one ML task does not use it.

---

## 29. Reproducibility — how somebody can repeat the work

Important repository files:

### Data

`data/SmartQ_Synthetic_Operational_Dataset_100k.csv`

### EDA

`notebooks/01_Data_Understanding_EDA.ipynb`

`docs/EDA_Findings.md`

### Data preparation

`notebooks/02_Data_Preparation.ipynb`

### Model training and evaluation

`notebooks/03_Model_Training_Evaluation.ipynb`

`src/train_models.py`

### Prediction interface

`src/predict.py`

### Dataset validation

`src/validate_dataset.py`

### Model evaluation documentation

`docs/Model_Evaluation.md`

`docs/Model_Card.md`

### Integration plan

`docs/SmartQ_Integration_Guide.md`

### Report wording

`docs/Report_ML_Methodology.md`

### Machine-readable results

`results/eda/`

`results/modeling/`

The training script is designed so the selected model bundle can be regenerated rather than relying on an unexplained binary file.

---

## 30. Why the binary trained model is generated instead of treated like source code

The current `.gitignore` excludes generated model binaries such as `.joblib`.

The reproducible source of truth is:

- dataset;
- preprocessing code;
- model parameters;
- split rules;
- random seed;
- training script;
- result files.

Running:

`python src/train_models.py`

generates:

`models/smartq_wait_time_model.joblib`

### Why do this?

Binary model files can change when library versions change and are not easy to review in Git.

The code and parameters are more informative and reproducible.

### Trade-off

A fresh clone must run the training script before `src/predict.py` can load the model bundle.

If final deployment requires a prebuilt artifact, we can later package a fixed release model separately.

---

## 31. Prediction interface added for integration

`src/predict.py`

defines a stable prediction function:

`predict_wait_minutes(observation)`

It:

- validates required input fields;
- loads the fitted preprocessing + model bundle;
- applies the same preprocessing used during training;
- predicts waiting time;
- clips negative predictions to zero.

### Why clip at zero?

Negative waiting time is not meaningful to a customer.

A regression model can mathematically output a negative value, especially near very short waits.

The customer-facing value must therefore be constrained to a sensible lower bound.

---

## 32. Planned fallback behaviour in the real SmartQ app

When we integrate with Django, ML should not become a single point of failure.

If the ML predictor fails for any reason, SmartQ should fall back to the existing deterministic ETA.

Why?

The queue application must continue working even if:

- the model file is missing;
- a feature is unavailable;
- a Python/model error occurs;
- the model version is incompatible.

This is a software-engineering decision, not just a machine-learning decision.

---

## 33. Things considered but deliberately not made part of the official experiment

The following ideas were considered as possible alternatives or future improvements, but were not used as official project methods:

- random train/test splitting;
- large GridSearchCV / RandomizedSearchCV sweeps;
- neural networks;
- LSTM/time-series modelling;
- target encoding;
- using baseline ETA as an ML feature;
- residual learning on top of the deterministic ETA;
- deleting all long-wait outliers;
- training waiting-time regression on no-shows/cancellations;
- adding sensitive personal attributes;
- using post-service fields to improve apparent accuracy;
- choosing the final model using test-set results.

Most were rejected because they either create leakage, complicate the third-year scope, weaken evaluation discipline, or answer a different research question.

---

## 34. Main trade-offs made

| Decision | What we gain | What we give up |
|---|---|---|
| Synthetic 100k dataset | Enough data and controlled experiments | Real-world validity is not proven |
| Completed visits only | Clean waiting-time target | No-show/cancel behaviour not modelled |
| Chronological split | More realistic future prediction test | Can score worse than random split |
| Whole-day separation | Reduces same-day leakage | Slightly uneven row percentages |
| Median imputation | Keeps valid early-day records | Imputed history is only an estimate |
| One-hot encoding | Simple and transparent | More columns than compact encodings |
| No baseline ETA as feature | Cleaner independent ML comparison | May leave some predictive performance unused |
| Limited tuning | Easier to defend, less overfitting risk | May not find absolute best hyperparameters |
| Validation MAE selection | Honest predefined decision rule | Keeps XGBoost even though RF test MAE is slightly lower |
| Keep extreme valid waits | Honest congestion representation | Higher RMSE and harder busy-case modelling |
| No deep learning | Scope control and explainability | No comparison with neural approaches |
| Generated model artifact | Reproducible source-controlled workflow | Model must be regenerated before local prediction |

---

## 35. What makes the current approach a good decision for this capstone

The approach is good because it balances:

- correctness;
- simplicity;
- reproducibility;
- proposal compliance;
- time available;
- ability to explain the work in a viva;
- ability to integrate the result into SmartQ.

We are not trying to build the most complicated possible ML system.

We are trying to build a defensible one.

A lecturer should be able to ask:

> Why did you split the data that way?

and get a clear answer.

They should be able to ask:

> Why didn't you use the test set to choose the model?

and get a clear answer.

They should be able to ask:

> Why is your model accurate?

and we should answer with measured MAE/RMSE while also explaining that the data is synthetic.

That is stronger engineering than blindly adding more algorithms.

---

## 36. What we must NOT claim

Do not say:

- "XGBoost is always the best queue model."
- "The model will be 2.58 minutes accurate at Home Affairs."
- "The 100,000 rows are real customers."
- "The model proves production readiness."
- "Feature importance proves causation."
- "Random Forest failed."
- "The test set selected XGBoost."

Correct wording:

- XGBoost narrowly achieved the lowest validation MAE in the current synthetic SmartQ experiment.
- The selected model achieved 2.5824-minute MAE on the held-out synthetic test period.
- Real-world performance requires live representative data and external validation.
- Random Forest performed almost identically and even achieved a slightly lower post-selection test MAE.

---

## 37. Current next steps

The remaining ML engineering work should proceed in this order:

1. Integrate the selected model bundle into the SmartQ Django backend.
2. Build live model features from the real SmartQ queue state.
3. Add safe deterministic-ETA fallback behaviour.
4. Add an API response field for predicted waiting time.
5. Measure prediction latency and confirm it is below the proposal's two-second requirement.
6. Add integration tests.
7. Log predictions and later actual waits for future real-data evaluation.
8. Produce final report charts/tables and presentation material.
9. Keep the synthetic-data limitation explicit.
10. If time allows, run a small sanity evaluation using the earlier SmartQ live simulation records as a separate demonstration dataset, without pretending those few records are enough to retrain the model.

---

## 38. One-minute explanation for the lecturer

If asked to explain the entire ML approach simply:

> "I created a synthetic SmartQ operational dataset because the prototype did not yet have enough real production data. I first explored and validated the data, then used only completed visits because cancelled and no-show records do not have a real waiting-time outcome. I removed fields that would leak future information. I split the data chronologically so the models learned from earlier dates and were evaluated on later dates. Numeric missing history values were filled using training-set medians, and categorical variables were one-hot encoded. I trained Linear Regression, Random Forest and XGBoost because those are the models defined in the proposal. I compared them using MAE and RMSE and selected the model with the lowest validation MAE. XGBoost narrowly beat Random Forest on validation and was therefore selected. On the later test period it achieved about 2.58 minutes MAE. I also found that the model is less accurate during heavy congestion, so I document that as a limitation. Because all training data is synthetic, I treat the result as a prototype demonstration rather than proof of real-world production accuracy."

---

## 39. Engineering lesson from this stage

The biggest lesson is that the model itself is only one part of machine learning.

Most of the important work happened before the final model:

- defining the right target;
- making sure the data is valid;
- avoiding leakage;
- creating a realistic split;
- using a baseline;
- choosing metrics;
- controlling tuning;
- preserving the test set;
- documenting limitations;
- making the work reproducible.

A slightly better metric is not worth destroying the credibility of the experiment.

---

## 40. Documentation policy going forward

Every meaningful ML change should leave evidence in at least one of these places:

- notebook for exploration;
- `src/` for reusable code;
- `results/` for machine-readable outputs;
- `docs/` for formal project documentation;
- this `.project-notes/README.md` for the plain-English engineering worklog and decision history.

This file should be updated whenever we make a major decision, change preprocessing, change the selected model, add integration behaviour, discover a limitation, or change the evaluation procedure.
