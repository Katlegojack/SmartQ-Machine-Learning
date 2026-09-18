# Models

The selected SmartQ waiting-time model is **XGBoost**, chosen because it achieved the lowest validation MAE among the three proposal models.

Validation MAE: **2.6302 minutes**  
Final test MAE: **2.5824 minutes**  
Final test RMSE: **4.9561 minutes**

The binary model bundle is generated reproducibly by:

```bash
python src/train_models.py
```

That command writes `models/smartq_wait_time_model.joblib`, containing both the fitted preprocessing transformer and selected model.

The binary is generated rather than treated as source code; the reproducible training pipeline, exact parameters, split definition and metrics are version-controlled in this repository.
