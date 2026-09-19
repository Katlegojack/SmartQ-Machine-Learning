# SmartQ ML Learning Guide — Plain English

> This file is for learning, not just submission.
>
> Rule used throughout this project: whenever an ML term appears, explain what it means, why it matters, and where SmartQ uses it.

---

## 1. What machine learning is doing in SmartQ

Machine learning is not magic.

SmartQ gives a model examples of past queue situations together with the waiting time that actually happened.

Example:

- 8 people ahead
- 3 counters open
- queue pressure high
- service = ID application
- time = 10:30
- actual wait = 24 minutes

The model studies many examples like this and learns patterns.

Later, when a new customer checks in, SmartQ gives the model the current queue situation and asks:

> "Based on the patterns you learned, how long is this customer likely to wait?"

That is supervised machine learning.

### Supervised learning

**Supervised learning** means the training data contains both:

1. the inputs, and
2. the correct answer.

For SmartQ:

- inputs = queue conditions
- correct answer = actual waiting time

---

## 2. Core words you must understand

### Dataset

A **dataset** is the collection of records used for analysis and training.

SmartQ currently has 100,000 synthetic operational records.

### Row / observation

One row is one recorded queue event or customer visit.

### Feature

A **feature** is an input variable the model can use.

Examples:

- people ahead
- number of open counters
- queue pressure
- service type
- branch
- time of day

Think of features as the clues we give the model.

### Target

The **target** is the answer we want the model to predict.

SmartQ target:

`actual_wait_minutes`

### Regression

**Regression** means predicting a number.

Examples:

- waiting time = 12.4 minutes
- house price = R1.2 million
- temperature = 27.5°C

SmartQ is a regression problem because waiting time is numeric.

### Classification

**Classification** means predicting a category.

Example:

- no-show / not no-show
- fraud / not fraud
- urgent / normal

SmartQ could later build a no-show classification model.

---

## 3. Training, validation and test data

### Training set

The **training set** is what the model learns from.

Think of it as studying from textbooks and examples.

SmartQ training rows: 64,074.

### Validation set

The **validation set** is used while deciding which model or settings are best.

Think of it as a practice exam.

SmartQ validation rows: 14,665.

### Test set

The **test set** is the final unseen exam.

It should not be used to choose the winning model.

SmartQ test rows: 13,916.

### Why SmartQ uses chronological splitting

We train on earlier dates and evaluate on later dates.

That better matches real deployment:

> learn from the past -> predict the future

---

## 4. Baseline

A **baseline** is a simple reference method.

It answers:

> "Is the ML model actually better than something very simple?"

SmartQ uses two benchmarks.

### Mean baseline

Predict the same average training wait for everyone.

Very simple, but useful.

### Deterministic ETA

SmartQ already has a formula-based waiting-time estimate.

This gives us another useful comparison.

---

## 5. MAE and RMSE

### MAE

**Mean Absolute Error**

Plain English:

> On average, how many minutes wrong was the model?

If:

MAE = 2.5

then the model is about 2.5 minutes wrong on average.

Lower is better.

### RMSE

**Root Mean Squared Error**

Plain English:

> Similar to MAE, but large mistakes hurt the score more.

Why useful?

A model that is usually correct but occasionally makes huge mistakes can still have a reasonable MAE.

RMSE exposes those big failures more strongly.

Lower is better.

---

# MODEL 1 — LINEAR REGRESSION

## 6. What Linear Regression is

Linear Regression tries to create a mathematical relationship between features and the target.

Very simplified idea:

`predicted wait = base value + feature effects`

Example concept:

`wait = 3 + (2 × people_ahead) - (1.5 × open_counters)`

The actual SmartQ model has more variables, but the idea is the same.

### Coefficient

A **coefficient** is the weight Linear Regression gives to a feature.

Example:

If the coefficient for `people_ahead` is positive, increasing people ahead tends to increase the predicted wait.

If the coefficient for `open_counters` is negative, more counters may reduce predicted wait.

Do not automatically interpret coefficients as cause and effect.

---

## 7. Steps used for SmartQ Linear Regression

### Step 1 — choose valid rows

Use completed visits only.

Why?

No-shows and cancellations do not have a genuine completed wait.

### Step 2 — choose valid features

Use information known at check-in time.

Why?

The model must only use information that would really exist when the prediction is made.

### Step 3 — handle missing values

Numeric missing values are filled with the training-set median.

Why?

Some recent-history features are naturally missing early in the day.

### Step 4 — encode categories

Branch, service, queue type and similar text values are one-hot encoded.

Why?

Linear Regression needs numeric inputs.

### Step 5 — fit the model

The model calculates coefficients that reduce prediction error on training data.

### Step 6 — evaluate on validation data

We calculate MAE and RMSE.

SmartQ Linear Regression validation:

- MAE: about 4.11 minutes
- RMSE: about 6.15 minutes

### Step 7 — compare against other models

Linear Regression is simple and useful, but tree models performed better.

---

## 8. Why keep Linear Regression if it loses?

Because it teaches us something.

It is:

- simple
- fast
- interpretable
- a useful benchmark
- good for statistical diagnostics

If a complex model only slightly beats Linear Regression, the complex model may not be worth the extra complexity.

---

## 9. Linear Regression diagnostics we should understand

### R²

**R-squared**

Plain English:

> How much of the variation in waiting time does the model explain?

Example:

R² = 0.70

means the model explains about 70% of the variation in the target.

Higher is usually better, but a high R² does not guarantee good predictions.

### Adjusted R²

Similar to R², but it penalises adding useless variables.

Useful when comparing Linear Regression models with different numbers of features.

### Residual

A **residual** is:

`actual value - predicted value`

Example:

actual wait = 20

predicted wait = 16

residual = 4 minutes

Residual analysis helps us see where the model fails.

### p-value

A **p-value** is used in statistical testing.

Very simplified meaning:

> "If there were really no relationship here, how surprising would this result be?"

A small p-value can suggest that a coefficient is statistically distinguishable from zero.

Common threshold:

`p < 0.05`

But this does NOT automatically mean the feature is practically important.

With 90,000+ rows, tiny effects can become statistically significant.

### Confidence interval

A **confidence interval** gives a plausible range for a coefficient estimate.

Example:

people_ahead coefficient:

1.2 to 1.5 minutes

This shows uncertainty around the estimated effect.

### VIF

**Variance Inflation Factor**

Plain English:

> Are some input variables basically repeating the same information?

High VIF can indicate multicollinearity.

### Multicollinearity

This means two or more features are strongly related to each other.

Example:

- queue_position
- people_ahead

These may contain nearly the same information.

This makes Linear Regression coefficients harder to interpret.

---

# MODEL 2 — RANDOM FOREST

## 10. What a Decision Tree is first

Random Forest is built from decision trees.

A tree asks a series of questions.

Example:

> Are there more than 5 people ahead?

If yes -> go one way.

If no -> go another way.

Then:

> Are fewer than 3 counters open?

Then another split.

Eventually the tree arrives at a predicted wait.

A single tree can easily overfit.

---

## 11. What Random Forest is

A **Random Forest** builds many decision trees instead of trusting one tree.

Each tree sees a slightly different version of the data/features.

Then the forest averages their predictions.

Simple picture:

```text
Tree 1 predicts 12 min
Tree 2 predicts 15 min
Tree 3 predicts 13 min
Tree 4 predicts 14 min

Forest prediction ≈ average
```

This makes the model more stable than one tree.

---

## 12. Random Forest terms

### n_estimators

Number of trees.

More trees usually improve stability but cost more computation.

SmartQ selected:

150 trees.

### max_depth

Maximum number of decision levels in a tree.

Too deep:

tree may memorise training data.

Too shallow:

tree may miss useful patterns.

### min_samples_leaf

Minimum number of training examples allowed in a final leaf.

Larger values can reduce overfitting.

### max_features

How many features each split is allowed to consider.

Randomness between trees helps make the forest diverse.

---

## 13. Steps used for SmartQ Random Forest

1. Use the same completed customer rows.
2. Use the same feature set.
3. Use the same train/validation/test split.
4. Apply the same preprocessing.
5. Train a small number of candidate configurations.
6. Compare validation MAE/RMSE.
7. Keep the best validation configuration.
8. Compare it with Linear Regression and XGBoost.

Selected Random Forest validation:

- MAE ≈ 2.6315
- RMSE ≈ 4.4920

That is much better than Linear Regression.

Why?

Queue behaviour is not perfectly linear.

Random Forest can learn patterns such as:

> "When queue pressure is high AND counters are low AND people ahead is high, waiting time increases sharply."

Linear Regression struggles more with this kind of interaction.

---

# MODEL 3 — XGBOOST

## 14. What boosting means

Random Forest builds many trees mostly independently and averages them.

**Boosting** works differently.

It builds trees one after another.

Each new tree focuses on correcting mistakes made by the previous trees.

Simple example:

Tree 1 makes rough predictions.

Then we look at its mistakes.

Tree 2 learns how to correct some of those mistakes.

Tree 3 corrects more remaining mistakes.

And so on.

---

## 15. What XGBoost is

**XGBoost** stands for:

Extreme Gradient Boosting.

It is a highly optimised boosting algorithm.

It is especially popular for structured/tabular data like SmartQ.

---

## 16. XGBoost terms

### n_estimators

Number of boosting trees.

SmartQ:

200.

### learning_rate

How strongly each new tree is allowed to change the current prediction.

Smaller learning rates usually learn more slowly and may require more trees.

SmartQ:

0.08.

### max_depth

Maximum tree depth.

Controls model complexity.

SmartQ:

5.

### subsample

Fraction of training rows used for each tree.

SmartQ:

0.9 = 90%.

This adds randomness and can reduce overfitting.

### colsample_bytree

Fraction of features available to each tree.

SmartQ:

0.9.

Again, this adds randomness and can improve generalisation.

### reg_lambda

Regularisation strength.

Regularisation discourages the model from becoming unnecessarily complex.

SmartQ:

2.0.

---

## 17. Steps used for SmartQ XGBoost

1. Start with the exact same training population.
2. Use the same features.
3. Apply the same preprocessing.
4. Train candidate XGBoost configurations.
5. Predict validation waiting times.
6. Calculate MAE and RMSE.
7. Keep the candidate with the lower validation MAE.
8. Compare against Random Forest and Linear Regression.
9. Select the official model using the predefined rule.

SmartQ XGBoost validation:

- MAE ≈ 2.6302
- RMSE ≈ 4.3893

This narrowly beat Random Forest validation MAE.

That is why XGBoost became the selected integration model.

---

## 18. Why XGBoost and Random Forest are so close

Both are tree-based nonlinear models.

Both can understand complex interactions that Linear Regression cannot model directly.

So it is not surprising that their results are similar.

The difference is mainly how the trees are built:

### Random Forest

Many trees learn independently -> predictions averaged.

### XGBoost

Trees learn sequentially -> each tree tries to correct previous mistakes.

Neither method is universally better.

Their performance depends on the dataset.

---

# MODEL QUALITY

## 19. Good fit

"Good fit" can mean several things.

For prediction, the strongest evidence is:

- low error on unseen data;
- performance better than baseline;
- similar validation and test behaviour;
- no obvious leakage;
- errors understood across subgroups;
- no extreme train-vs-test collapse.

Do not judge model quality using training accuracy alone.

A model can memorise training data and fail on new customers.

---

## 20. Overfitting

**Overfitting** means:

> The model learned the training data too specifically and does not generalise well.

Simple analogy:

A student memorises the exact answers in the revision sheet instead of understanding the topic.

They score 100% on that sheet but fail a different exam.

Signs:

- extremely good training score;
- much worse validation/test score.

---

## 21. Underfitting

**Underfitting** means the model is too simple to capture the real patterns.

Example:

Using a straight line when the relationship is strongly curved.

Linear Regression can underfit nonlinear queue behaviour.

---

## 22. Generalisation

**Generalisation** means:

> Can the model work well on new data it did not train on?

This is one of the main goals of ML.

Our chronological validation/test design is meant to measure generalisation.

---

# FEATURE QUALITY

## 23. Feature importance

Tree models can estimate which features they relied on most.

SmartQ XGBoost currently relies strongly on:

- people ahead;
- queue pressure;
- workload minutes ahead.

This makes operational sense.

But feature importance does not prove causality.

---

## 24. Permutation importance

A useful future diagnostic.

Method:

1. measure normal model performance;
2. randomly scramble one feature;
3. measure performance again.

If performance becomes much worse, that feature was useful.

Why useful?

It measures importance using prediction performance rather than only internal tree structure.

---

## 25. SHAP

**SHAP** is an explainability method.

Plain English:

> It estimates how much each feature pushed an individual prediction up or down.

Example:

Predicted wait = 25 minutes.

SHAP may show:

- many people ahead: +10 min
- high queue pressure: +8 min
- many counters open: -4 min
- priority lane: -3 min

SHAP is useful for understanding individual predictions and overall feature behaviour.

It is more advanced, so it should be added only after the core diagnostics are understood.

---

# STATISTICAL SIGNIFICANCE VS PREDICTIVE USEFULNESS

## 26. They are not the same thing

A feature can be statistically significant but barely improve prediction.

Example:

With 90,000 rows, Friday may have a very small but statistically detectable effect.

But if removing Friday changes MAE by only 0.001 minutes, it may not be practically important.

So ask two questions:

1. Is the relationship statistically credible?
2. Does the variable meaningfully help prediction?

---

# WHY OUR WORKFLOW IS ORDERED THIS WAY

## 27. Correct sequence

```text
Understand the problem
        ↓
Understand the data
        ↓
Validate the data
        ↓
Define the target
        ↓
Remove leakage
        ↓
Choose features
        ↓
Split train / validation / test
        ↓
Fit preprocessing on training only
        ↓
Build simple baseline
        ↓
Train Linear Regression
        ↓
Train Random Forest
        ↓
Train XGBoost
        ↓
Compare validation MAE/RMSE
        ↓
Select model
        ↓
Final test evaluation
        ↓
Diagnostics
        ↓
Integration
        ↓
Monitoring and retraining
```

Skipping earlier steps can make later model results misleading.

---

# SMARTQ RESULTS IN PLAIN ENGLISH

## 28. What the current scores mean

Validation:

- Linear Regression: about 4.11 min MAE
- Random Forest: about 2.63 min MAE
- XGBoost: about 2.63 min MAE

XGBoost narrowly wins validation.

Final selected XGBoost test:

- MAE ≈ 2.58 minutes
- RMSE ≈ 4.96 minutes

This means:

> On the synthetic test period, XGBoost was about 2.6 minutes wrong on average, while RMSE shows that some larger errors still exist.

---

## 29. Important weakness

Busy traffic:

MAE ≈ 7.94 minutes.

This tells us the model is much less reliable in heavy congestion.

This is useful knowledge.

A good ML project does not only ask:

> "How accurate is the average?"

It also asks:

> "When does the model fail?"

---

# QUESTIONS YOU SHOULD BE ABLE TO ANSWER

## 30. Why regression?

Because waiting time is a number.

## 31. Why not include no-shows?

Because they do not have a genuine completed wait outcome.

## 32. Why chronological split?

Because deployment predicts future queue conditions from past data.

## 33. Why validation data?

To choose models/settings without touching the final test exam.

## 34. Why test data?

To estimate final generalisation after model selection.

## 35. Why MAE?

Easy to explain in minutes.

## 36. Why RMSE?

It punishes big prediction errors more strongly.

## 37. Why Linear Regression?

Simple baseline model and useful statistical interpretation.

## 38. Why Random Forest?

Captures nonlinear interactions using many trees.

## 39. Why XGBoost?

Captures nonlinear patterns and sequentially corrects errors; strong for tabular data.

## 40. Why XGBoost selected?

It achieved the lowest validation MAE under the predefined rule.

## 41. Why not switch to Random Forest after test results?

Because the test set should not be used for model selection.

## 42. Why synthetic data?

Not enough real production records yet; the proposal allows simulated prototype data.

## 43. Biggest limitation?

Synthetic-only training and weaker performance under severe congestion.

---

# LEARNING POLICY FOR THIS PROJECT

From this point onward, whenever a new ML term is introduced, documentation should include:

1. **Term**
2. **Simple definition**
3. **Why it matters**
4. **How SmartQ uses it**
5. **Trade-off or limitation where relevant**

The goal is not only to finish SmartQ.

The goal is for the developer to understand why the system was built this way.
