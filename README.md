# Patient Health Record Dashboard

A Streamlit dashboard for exploring diabetes encounter and readmission data.

## Run locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Deploy

1. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub.
2. Select **Create app**, then choose `amritanshu2005/HCL-PROJECT`, branch `main`, and `app.py`.
3. Deploy. The app reads `diabetic_data.csv` from the repository root.

The dashboard displays patient-level encounter records and allows them to be downloaded. Confirm you have permission to publish and share the dataset before deploying this public repository.
