from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
	page_title="Patient Health Record Dashboard",
	page_icon="+",
	layout="wide",
	initial_sidebar_state="expanded",
)


BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "diabetic_data.csv"


@st.cache_data
def load_data() -> pd.DataFrame:
	frame = pd.read_csv(DATA_PATH, na_values="?", low_memory=False)
	frame["readmitted_flag"] = frame["readmitted"].ne("NO")
	frame["readmission_label"] = frame["readmitted"].map(
		{"NO": "No readmission", "<30": "Within 30 days", ">30": "After 30 days"}
	)
	return frame


def metric_delta(value: float) -> str:
	return f"{value:.1f}%"


data = load_data()

st.markdown(
	"""
	<style>
	@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
	:root { --ink:#17233f; --muted:#65718a; --cobalt:#176c82; --sky:#e5f3f4; --line:#cfe1e3; --coral:#d9654c; --leaf:#4d9a78; }
	[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #eef9f6 0%, #f7fbfa 52%, #e8f2fa 100%); }
	html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
	.stApp, .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4 { color: var(--ink) !important; }
	h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: 0; }
	.block-container { padding: 2.4rem 3.2rem 3rem; max-width: 1500px; }
	[data-testid="stSidebar"] { background: #e8f5f2; border-right: 1px solid var(--line); }
	[data-testid="stSidebar"] * { color: var(--ink) !important; }
	[data-baseweb="select"] > div { background: #f4fbff; border-color: #80b8d2; color: var(--ink); }
	[data-baseweb="select"] svg { fill: var(--cobalt); }
	[data-testid="stMetric"] { background: #f2fbf8; border: 1px solid var(--line); border-radius: 8px; padding: 1rem 1.15rem; box-shadow: 0 5px 18px rgba(23,33,38,.04); }
	[data-testid="stMetricLabel"] { color: var(--muted) !important; }
	[data-testid="stMetricValue"] { color: var(--cobalt); font-family: 'Space Grotesk', sans-serif; }
	.eyebrow { color: var(--cobalt); font-size: .75rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin-bottom: .35rem; }
	.hero { background: linear-gradient(120deg, #dff3ef 0%, #edf8f5 55%, #e3f0f8 100%); border: 1px solid var(--line); border-radius: 12px; padding: 2rem 2.2rem; margin-bottom: 1.35rem; }
	.hero h1 { font-size: clamp(2rem, 4vw, 3.4rem); line-height: 1.02; margin: 0; }
	.hero p { color: var(--muted); font-size: 1.05rem; margin: .65rem 0 0; max-width: 700px; }
	.section-title { margin: 1.8rem 0 .8rem; font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 1.2rem; }
	.note { background: var(--sky); border-left: 4px solid var(--cobalt); padding: .8rem 1rem; border-radius: 4px; color: #294b79; font-size: .9rem; }
	.cohort-strip { display: flex; gap: .65rem; flex-wrap: wrap; align-items: center; margin: .8rem 0 1rem; color: var(--muted); font-size: .88rem; }
	.cohort-pill { background: #eef9f6; border: 1px solid var(--line); border-radius: 999px; padding: .35rem .7rem; color: var(--ink); }
	.status { color: var(--muted); font-size: .85rem; padding-top: .45rem; }
	[data-testid="stDownloadButton"] button { border-color: var(--cobalt); color: var(--cobalt); }
	</style>
	""",
	unsafe_allow_html=True,
)

st.markdown(
	"""
	<div class="hero">
	  <div class="eyebrow">Clinical analytics workspace</div>
	  <h1>Patient health record dashboard</h1>
	  <p>Explore diabetes encounters, readmission patterns, and patient-level records from the available hospital dataset.</p>
	</div>
	""",
	unsafe_allow_html=True,
)

with st.sidebar:
	st.markdown("### Filters")
	st.caption("Refine the cohort shown across the dashboard.")
	selected_gender = st.multiselect("Gender", sorted(data["gender"].dropna().unique()), default=[])
	selected_race = st.multiselect("Race", sorted(data["race"].dropna().unique()), default=[])
	selected_readmission = st.multiselect(
		"Readmission outcome",
		["No readmission", "Within 30 days", "After 30 days"],
		default=[],
	)
	selected_age = st.multiselect("Age group", sorted(data["age"].dropna().unique()), default=[])
	selected_diabetes_med = st.multiselect("Diabetes medication", sorted(data["diabetesMed"].dropna().unique()), default=[])
	stay_range = st.slider("Length of stay (days)", 1, int(data["time_in_hospital"].max()), (1, int(data["time_in_hospital"].max())))
	st.divider()
	st.markdown("**Dataset**")
	st.caption(f"{len(data):,} encounters · {data['patient_nbr'].nunique():,} patients")
	st.info("This dashboard presents descriptive analytics from the supplied patient encounter dataset. Predictive model scoring is not enabled.")

filtered = data.copy()
if selected_gender:
	filtered = filtered[filtered["gender"].isin(selected_gender)]
if selected_race:
	filtered = filtered[filtered["race"].isin(selected_race)]
if selected_readmission:
	filtered = filtered[filtered["readmission_label"].isin(selected_readmission)]
if selected_age:
	filtered = filtered[filtered["age"].isin(selected_age)]
if selected_diabetes_med:
	filtered = filtered[filtered["diabetesMed"].isin(selected_diabetes_med)]
filtered = filtered[filtered["time_in_hospital"].between(*stay_range)]

if filtered.empty:
	st.error("No encounters match the selected filters. Adjust the sidebar to continue.")
	st.stop()

total_encounters = len(filtered)
readmission_rate = filtered["readmitted_flag"].mean() * 100
avg_stay = filtered["time_in_hospital"].mean()
avg_medications = filtered["num_medications"].mean()

first_row = st.columns(4)
first_row[0].metric("Encounters", f"{total_encounters:,}")
first_row[1].metric("Readmission rate", metric_delta(readmission_rate))
first_row[2].metric("Average stay", f"{avg_stay:.1f} days")
first_row[3].metric("Average medications", f"{avg_medications:.1f}")

st.markdown(
	f'<div class="cohort-strip"><span>Showing the filtered cohort from <strong>{DATA_PATH.name}</strong></span><span class="cohort-pill">{total_encounters:,} encounters</span><span class="cohort-pill">{filtered["patient_nbr"].nunique():,} unique patients</span><span class="cohort-pill">{filtered["readmission_label"].notna().sum():,} classified outcomes</span></div>',
	unsafe_allow_html=True,
)

tab_overview, tab_patient, tab_records = st.tabs(["Overview", "Patient profile", "Records"])

with tab_overview:
	st.markdown('<div class="section-title">Readmission and utilization patterns</div>', unsafe_allow_html=True)
	chart_left, chart_right = st.columns(2)
	with chart_left:
		outcome_counts = filtered["readmission_label"].value_counts().reindex(
			["No readmission", "After 30 days", "Within 30 days"], fill_value=0
		)
		st.caption("Readmission outcomes")
		st.bar_chart(outcome_counts, color="#2457a6", height=280)
	with chart_right:
		age_readmission = (
			filtered.groupby("age", observed=False)["readmitted_flag"].mean().mul(100)
			.reindex(["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)", "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"])
			.dropna()
		)
		st.caption("Readmission rate by age group")
		st.line_chart(age_readmission, color="#d9654c", height=280)

	st.markdown('<div class="section-title">Clinical workload</div>', unsafe_allow_html=True)
	workload = filtered.groupby("time_in_hospital").agg(
		Encounters=("encounter_id", "count"),
		Readmission_rate=("readmitted_flag", "mean"),
	)
	workload["Readmission_rate"] *= 100
	workload_left, workload_right = st.columns(2)
	with workload_left:
		st.caption("Encounter volume by length of stay")
		st.bar_chart(workload["Encounters"], color="#2457a6", height=250)
	with workload_right:
		st.caption("Readmission rate by length of stay")
		st.line_chart(workload["Readmission_rate"], color="#d9654c", height=250)

	st.download_button(
		"Download cohort summary",
		workload.reset_index().to_csv(index=False),
		"filtered_cohort_summary.csv",
		"text/csv",
	)

with tab_patient:
	st.markdown('<div class="section-title">Find an encounter</div>', unsafe_allow_html=True)
	patient_ids = sorted(filtered["patient_nbr"].dropna().astype(int).astype(str).unique().tolist())
	selected_patient = st.selectbox("Patient number", patient_ids, label_visibility="collapsed")
	patient_encounters = filtered[filtered["patient_nbr"].astype(int).astype(str) == selected_patient]
	selected_encounter = st.selectbox(
		"Encounter",
		patient_encounters["encounter_id"].astype(int).astype(str).tolist(),
		format_func=lambda encounter_id: f"Encounter {int(encounter_id):,}",
	)
	patient = patient_encounters[patient_encounters["encounter_id"].astype(int).astype(str) == selected_encounter].iloc[0]
	st.markdown(
		f'<div class="note">Encounter <strong>{int(patient["encounter_id"]):,}</strong> · outcome: <strong>{patient["readmission_label"]}</strong></div>',
		unsafe_allow_html=True,
	)
	profile_left, profile_right = st.columns(2)
	with profile_left:
		st.markdown("**Demographics**")
		st.dataframe(pd.DataFrame({"Field": ["Age", "Gender", "Race", "Weight"], "Value": [str(patient["age"]), str(patient["gender"]), str(patient["race"]), str(patient["weight"]) if pd.notna(patient["weight"]) else "Not recorded"]}), hide_index=True, use_container_width=True)
	with profile_right:
		st.markdown("**Encounter details**")
		st.dataframe(pd.DataFrame({"Field": ["Length of stay", "Lab procedures", "Procedures", "Medications", "Diabetes medication"], "Value": [f"{patient['time_in_hospital']} days", str(patient["num_lab_procedures"]), str(patient["num_procedures"]), str(patient["num_medications"]), str(patient["diabetesMed"])]}), hide_index=True, use_container_width=True)
	st.markdown("**Cohort context**")
	st.progress(int(readmission_rate), text=f"Filtered cohort readmission rate: {readmission_rate:.1f}%")
	st.caption("The rate is descriptive: it is calculated directly from the currently filtered CSV rows, not from a predictive model.")

with tab_records:
	st.markdown('<div class="section-title">Encounter records</div>', unsafe_allow_html=True)
	display_columns = ["encounter_id", "patient_nbr", "age", "gender", "race", "time_in_hospital", "num_lab_procedures", "num_medications", "readmission_label"]
	st.dataframe(filtered[display_columns].rename(columns={"readmission_label": "readmission"}), hide_index=True, use_container_width=True, height=520)
	st.download_button("Download filtered records", filtered[display_columns].to_csv(index=False), "filtered_patient_records.csv", "text/csv")

	with st.expander("Data quality and definitions"):
		quality = pd.DataFrame(
			{
				"Field": ["encounter_id", "patient_nbr", "readmitted", "weight", "medical_specialty"],
				"Meaning": ["Hospital encounter identifier", "Patient identifier", "Raw CSV readmission outcome", "Patient weight; ? is treated as missing", "Recorded specialty; ? is treated as missing"],
				"Missing in cohort": [filtered["encounter_id"].isna().sum(), filtered["patient_nbr"].isna().sum(), filtered["readmitted"].isna().sum(), filtered["weight"].isna().sum(), filtered["medical_specialty"].isna().sum()],
			}
		)
		st.dataframe(quality, hide_index=True, use_container_width=True)
		st.caption(f"Source: {DATA_PATH.name} · {len(data):,} source rows loaded · filters affect every metric, chart, profile, and download above.")
