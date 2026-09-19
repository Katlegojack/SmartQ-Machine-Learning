import json
from pathlib import Path

NOTEBOOK = Path("notebooks/SmartQ_ML_100k_Embedded_Dataset.ipynb")

replacements = {
    0: """# My SmartQ Self-Contained Machine-Learning Notebook

**Project:** SmartQ — Machine-Learning-Assisted Queue Management System  
**Dataset:** 100,000-row synthetic SmartQ operational dataset  
**Purpose:** I use this notebook as a portable, self-contained copy of my ML dataset setup.

I embedded the complete SmartQ CSV inside this notebook in compressed form so I can keep one portable notebook that can recreate the dataset when needed.

I keep this notebook mainly as a safe, self-contained data copy. My current EDA, data-preparation, model-training and diagnostics work lives in the numbered notebooks in the same folder.

> I use synthetic SmartQ operational data here. I do not present these rows as real customer records.
""",
    1: """## My machine-learning roadmap

When I started this notebook, my planned workflow was:

1. I extract and load the embedded dataset.
2. I understand and validate the data.
3. I prepare the modelling dataset.
4. I create chronological train/validation/test splits.
5. I build a simple mean-wait baseline.
6. I train Linear Regression.
7. I train Random Forest.
8. I train XGBoost.
9. I compare MAE and RMSE.
10. I select the model using validation MAE.
11. I evaluate the selected model on the later test period.
12. I save the final model for SmartQ integration.

I later expanded this work into separate numbered notebooks because I wanted each ML stage to be easier to understand, review and reproduce.
""",
    2: """## My embedded dataset details

I embedded the following dataset inside this notebook:

- **Rows:** 100,000
- **Columns:** 45
- **CSV name:** `SmartQ_Synthetic_Operational_Dataset_100k.csv`
- **Original CSV size:** 33.53 MB
- **Compressed payload size:** 4.37 MB
- **SHA-256:** `616a25c43475fa44c0e8c17521a1156603aab99aea22802a319542b50b374b3e`

I use the SHA-256 value as an integrity check so I can confirm that the extracted CSV matches the dataset I originally embedded.
""",
    7: """## My most important modelling rule

My prediction target is:

`actual_wait_minutes`

For waiting-time regression, I use **completed visits only**.

I exclude fields such as `call_time`, `actual_wait_minutes`, `wait_variance_minutes`, `actual_service_minutes`, `service_started_at`, and `service_completed_at` from model inputs.

I do this because those fields contain information from after the prediction point or directly contain the answer.

If I used them, I would create **data leakage**, which would make the model look unrealistically accurate.
""",
    9: """## Where I continued the work

I no longer use this self-contained notebook as the main modelling notebook.

I split the real ML work into clearer stages:

- `01_Data_Understanding_EDA.ipynb`
- `02_Data_Preparation.ipynb`
- `03_Model_Training_Evaluation.ipynb`
- `04_Model_Diagnostics_Statistical_Analysis.ipynb`

I did this because I wanted each stage to have one clear purpose and enough explanation for me to understand what I was doing instead of hiding the whole project inside one very large notebook.
""",
}

with NOTEBOOK.open("r", encoding="utf-8") as handle:
    notebook = json.load(handle)

for index, text in replacements.items():
    notebook["cells"][index]["source"] = [
        line + "\n" for line in text.strip().split("\n")
    ]

with NOTEBOOK.open("w", encoding="utf-8", newline="\n") as handle:
    json.dump(notebook, handle, ensure_ascii=False, indent=1)
    handle.write("\n")

print(f"Rewrote first-person narrative in {NOTEBOOK}")
