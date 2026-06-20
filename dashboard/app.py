from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "data" / "runs"


st.set_page_config(page_title="NEMO Results", layout="wide")
st.title("NEMO Results Dashboard")

csv_files = sorted(RUNS_DIR.glob("*/results.csv"))
if not csv_files:
    st.warning("No run logs found. Run `nemo sample` or `nemo optimize` first.")
    st.stop()

selected = st.sidebar.selectbox(
    "Run log",
    csv_files,
    format_func=lambda path: str(path.relative_to(ROOT)),
)

df = pd.read_csv(selected)
ok = df[df["status"] == "ok"].copy()
if ok.empty:
    st.error("The selected run has no successful evaluations.")
    st.dataframe(df)
    st.stop()

ok["feasible"] = (
    (ok["factor_of_safety"] >= 2.5)
    & (ok["max_deflection_mm"] <= 0.5)
)

best_feasible = ok[ok["feasible"]].sort_values("mass_kg").head(1)
best_objective = ok.sort_values("objective_value").head(1)

metric_cols = st.columns(4)
metric_cols[0].metric("Evaluations", len(df))
metric_cols[1].metric("Successful", len(ok))
metric_cols[2].metric("Feasible", int(ok["feasible"].sum()))
metric_cols[3].metric("Best mass kg", f"{best_feasible['mass_kg'].iloc[0]:.3f}" if not best_feasible.empty else "n/a")

left, right = st.columns(2)
with left:
    fig = px.line(
        ok,
        x="iteration",
        y="mass_kg",
        markers=True,
        title="Mass Convergence",
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.scatter(
        ok,
        x="mass_kg",
        y="max_stress_mpa",
        color="feasible",
        hover_data=[
            "iteration",
            "factor_of_safety",
            "max_deflection_mm",
            "objective_value",
        ],
        title="Stress vs Mass",
    )
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    fig = px.scatter(
        ok,
        x="mass_kg",
        y="factor_of_safety",
        color="feasible",
        title="FOS vs Mass",
    )
    fig.add_hline(y=2.5, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.scatter(
        ok,
        x="mass_kg",
        y="max_deflection_mm",
        color="feasible",
        title="Deflection vs Mass",
    )
    fig.add_hline(y=0.5, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Best Candidate")
candidate = best_feasible if not best_feasible.empty else best_objective
st.dataframe(candidate.T, use_container_width=True)

st.subheader("Run Data")
st.dataframe(df, use_container_width=True)
