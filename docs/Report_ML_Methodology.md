# Report-Ready SmartQ Machine-Learning Methodology

## Data understanding

The SmartQ dataset contained 100,000 synthetic operational queue records representing appointments, walk-ins, General and Priority queues, multiple service types, active counters, queue-state measurements and service outcomes. Exploratory data analysis was performed to inspect record distributions, missing values, waiting-time behaviour and data-quality constraints. For the regression experiment, only the 92,655 completed visits were retained because cancelled and no-show records did not contain a genuine completed waiting-time outcome.

## Data preparation

The prediction target was `actual_wait_minutes`, defined as the time from customer check-in until the customer was called for service. Only variables available at prediction time were used as model inputs. Post-outcome variables such as call time, actual service duration and service-completion timestamps were excluded to prevent data leakage.

Numeric missing values were imputed using medians learned from the training partition, while categorical missing values used the most frequent training value. Categorical variables were converted using one-hot encoding.

The completed records were divided chronologically by whole operating dates. The training set contained 64,074 records from 2 January to 16 June 2026, the validation set contained 14,665 records from 17 June to 22 July 2026, and the test set contained 13,916 records from 23 July to 27 August 2026. This approach prevented records from the same operating day from appearing across different partitions.

## Modelling

Three regression algorithms specified in the project proposal were trained using the same prepared dataset: Linear Regression, Random Forest and XGBoost. A simple mean-waiting-time predictor was used as the required baseline. The existing deterministic SmartQ ETA was also evaluated as an additional engineering benchmark but was not used as an input to the machine-learning models.

Limited manual parameter tuning was performed for Random Forest and XGBoost. The purpose was to obtain reasonable model configurations while keeping the comparison understandable and appropriate for a third-year mini-capstone project.

## Evaluation

Models were compared using Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE). The model-selection rule was fixed in advance as the lowest validation MAE.

Validation MAE values were 4.1146 minutes for Linear Regression, 2.6315 minutes for Random Forest and 2.6302 minutes for XGBoost. XGBoost therefore achieved the lowest validation MAE and was selected for integration.

The selected XGBoost model was then evaluated on the untouched chronological test set, producing an MAE of 2.5824 minutes and RMSE of 4.9561 minutes. The mean-wait baseline produced a test MAE of 14.9850 minutes, while the existing deterministic SmartQ ETA produced a test MAE of 4.6386 minutes.

Random Forest produced a slightly lower test MAE of 2.5231 minutes. However, it was not substituted for XGBoost after the test results were observed because the final test set was not intended for model selection. Keeping XGBoost preserved the predefined validation-based evaluation process.

## Traffic-condition analysis

The selected model was additionally evaluated under low, moderate and busy synthetic queue conditions. XGBoost achieved a test MAE of approximately 1.22 minutes under low traffic, 2.95 minutes under moderate traffic and 7.94 minutes under busy conditions. This indicates that prediction becomes more difficult during heavy congestion and should be reported as a limitation.

## Interpretation and limitation

The results show that the machine-learning models can learn the operational patterns deliberately represented in the synthetic SmartQ dataset. They do not prove equivalent performance in a real government, university, clinic or commercial queue. The model should therefore be treated as a prototype demonstration until representative real operational data becomes available for external validation and retraining.
