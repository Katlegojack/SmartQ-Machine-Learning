# SmartQ EDA Visual Analysis — Plain English

The EDA notebook now contains additional visual comparisons and significance checks so the data-understanding stage is easier to learn from and easier to present.

## Added visuals

The notebook now includes visual comparisons for:

- General vs Priority waiting time;
- Appointment vs Walk-in waiting time;
- Peak vs Non-peak waiting time;
- waiting time by service type;
- missing values among completed visits;
- correlation between selected queue-state variables.

These are in addition to the existing:

- waiting-time histogram;
- branch waiting-time comparison;
- hourly waiting-time trend;
- weekday waiting-time comparison;
- queue-pressure vs waiting-time scatter plot.

## What the new charts show

### General vs Priority

Average completed wait:

- General: **16.90 min**
- Priority: **9.66 min**

Priority customers wait less in the generated data, which is consistent with SmartQ's separate priority-lane design.

This does not prove a universal real-world effect. It describes the synthetic scenario.

### Appointment vs Walk-in

Average completed wait:

- Appointment: **16.97 min**
- Walk-in: **12.97 min**

Appointments have a higher raw mean wait in this generated dataset.

This should not automatically be interpreted as "appointments are worse". The groups can arrive under different queue conditions.

### Peak vs Non-peak

Average completed wait:

- Peak: **16.97 min**
- Non-peak: **14.47 min**

Peak periods are worse on average, but the difference is not huge relative to the overall spread of waiting times.

### Service type

Average completed wait:

- Collections: **16.11 min**
- ID Applications: **16.05 min**
- Passport Applications: **15.90 min**

The service means are extremely similar.

The one-way ANOVA p-value is **0.6503**, so there is no statistically detectable overall raw service-type difference in waiting time in this synthetic dataset.

### Missing values

The main missing values among completed visits are:

- `appointment_at`: 21,864 rows — expected because walk-ins do not have appointments;
- `recent_avg_service_minutes_10`: 2,775 rows — expected early-day history gaps;
- `recent_avg_wait_minutes_10`: 313 rows — expected early-day history gaps.

The chart is useful because it separates **expected missingness** from corrupted data.

### Correlation matrix

The correlation visual shows that several engineered queue variables carry similar information.

Examples include:

- people ahead and workload ahead;
- general waiting and queue pressure;
- serving count and counter utilisation.

That observation led directly to the later VIF/multicollinearity analysis.

## Why this improves the EDA

A good EDA should not just produce charts.

Each chart should answer a question.

The updated EDA now covers:

1. What does the target distribution look like?
2. Do branches/time periods differ?
3. Does queue pressure relate to waiting time?
4. Do operational groups differ?
5. Where are values missing?
6. Which variables are related to each other?
7. Are observed group differences statistically detectable?
8. Are statistically detectable differences also practically large?

That is a much stronger Data Understanding stage than simply plotting a few graphs.
