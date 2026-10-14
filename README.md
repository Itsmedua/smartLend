# SmartLend: Explainable Credit Risk Platform

A web app for bank loan officers. The officer enters an applicant's details
and gets a default-risk score with a plain-language explanation of why.
The officer then approves, refers, or rejects, and each decision is saved.

Built with Python, Django, scikit-learn, and Bootstrap.
Final Year Project, BSCS.

## Run it on your computer (Windows)

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations core
python manage.py migrate
python manage.py createsuperuser

python train_model.py
python manage.py runserver
```

On Mac or Linux, activate with `source venv/bin/activate` instead.

Open http://127.0.0.1:8000 and log in with the superuser you created.

If you skip `python train_model.py`, the site still works using a small built-in
rule set. Running it trains a real model on made-up (synthetic) data.
Replace that data with a real dataset in step 7.

## Folder guide

| Path | What it is |
|---|---|
| `manage.py` | Command tool: runserver, migrate, createsuperuser |
| `smartlend/settings.py` | Project settings (database, apps, login redirects) |
| `smartlend/urls.py` | Top-level routes, includes login and logout |
| `core/models.py` | The `Applicant` table: inputs, risk result, decision |
| `core/forms.py` | The applicant form (built from the model) |
| `core/views.py` | The logic for each page |
| `core/urls.py` | Which address opens which view |
| `core/ml.py` | Feature building, prediction, and the "why" explanation |
| `core/admin.py` | Lets you manage applicants in /admin |
| `templates/` | All HTML pages (Bootstrap) |
| `train_model.py` | Trains and saves the model to `core/ml_model/model.joblib` |

## How one request flows

1. Officer fills the form and clicks Calculate risk.
2. `views.applicant_create` checks the form, then calls `ml.predict_risk`.
3. The result (score, label, explanation) is saved on the `Applicant` row.
4. The officer is redirected to the result page, which reads it from the database.
5. Approve, Refer, or Reject posts to `views.applicant_decide`, which saves the decision and time.

## Next steps

- Step 7: load a real dataset with Pandas, compare Logistic Regression, Random Forest, and XGBoost, then add SHAP.
- Step 8: dashboard charts with Chart.js.
- Step 9: fraud module with Isolation Forest and an alerts page.
- Step 10: user roles, audit log, PostgreSQL, Docker, and deployment.
