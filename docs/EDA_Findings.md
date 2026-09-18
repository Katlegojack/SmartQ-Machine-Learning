# SmartQ Data Understanding / EDA Findings

## Purpose

This document records the first exploratory analysis of the 100,000-row synthetic SmartQ operational dataset before machine-learning model training.

## Dataset population

- Total records: **100,000**
- Columns: **45**
- Completed visits: **92,655 (92.66%)**
- No-shows: **5,096**
- Cancelled visits: **2,249**
- Regression modelling population: **completed visits only**

## Waiting-time target

The machine-learning target is `actual_wait_minutes`.

For completed visits:

- Mean wait: **16.03 minutes**
- Median wait: **7.50 minutes**
- 95th percentile: **61.73 minutes**
- Maximum: **358.10 minutes**

The difference between the mean and median shows that waiting time is right-skewed: most waits are relatively short, but some congested cases are much longer.

## Service-time profile

- Mean actual service time: **16.00 minutes**
- Median actual service time: **15.10 minutes**
- 95th percentile: **27.30 minutes**

## Important operational patterns

Average completed-visit wait by queue lane:

- General: **16.90 minutes**
- Priority: **9.66 minutes**

Average completed-visit wait by booking source:

- Appointment: **16.97 minutes**
- Walk-in: **12.97 minutes**

Average completed-visit wait during peak periods:

- Peak: **16.97 minutes**
- Non-peak: **14.47 minutes**

Average wait also differs across branches. Centurion has the highest observed mean wait (**26.99 minutes**) and Johannesburg Central the lowest (**8.66 minutes**) in this synthetic scenario. These are properties of the generated dataset and must not be presented as claims about real branches.

Friday has the highest mean weekday wait (**21.40 minutes**) in the generated data. Hourly analysis shows congestion rising through parts of the morning and afternoon, with the highest average around 15:00 (**22.21 minutes**).

## Missing values

Within completed visits, the main expected missing values are:

- `appointment_at`: **21,864** rows, because walk-ins do not have appointment times.
- `recent_avg_service_minutes_10`: **2,775** rows, mainly where insufficient completed history exists early in an operating day.
- `recent_avg_wait_minutes_10`: **313** rows, mainly where insufficient called-customer history exists.

These history-feature gaps should be handled during preprocessing rather than treating the records as invalid.

## Data-quality checks

The following validation checks returned **zero violations**:

- negative actual waiting time
- non-positive service duration
- queue position inconsistent with people ahead
- customer called before service eligibility
- service started before call time
- service completed before service start
- appointment becoming eligible before booked appointment time
- walk-in eligibility not matching check-in

## Existing SmartQ ETA benchmark

The existing deterministic SmartQ ETA produces approximately:

- MAE: **4.72 minutes**
- RMSE: **6.56 minutes**

This is an additional engineering benchmark. The proposal's official model comparison will still use Linear Regression, Random Forest and XGBoost, and will also include the required simple mean-wait baseline.

## Data-leakage rule

For a prediction made at check-in, post-outcome fields must not be used as predictors. This includes fields such as `call_time`, `actual_wait_minutes`, `actual_service_minutes`, `service_started_at`, and `service_completed_at`.

## Next step

Proceed to Data Preparation:

1. Finalise the pre-outcome feature list.
2. Handle the two recent-history missing-value features.
3. Encode categorical variables.
4. Create a chronological train/validation/test split.
5. Build the simple mean-wait baseline before training the three required regression models.
