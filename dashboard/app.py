from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.formatting import best_candidate_table


ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "data" / "runs"

st.set_page_config(page_title="NEMO Results", layout="wide")
st.title("NEMO Results")

csv_files = sorted(RUNS_DIR.glob("*/results.csv"))
if not csv_files:
    st.warning("No run logs found. Run `nemo sample` or `nemo optimize` first.")
    st.stop()

selected = st.sidebar.selectbox(
    "Run log",
    csv_files,
    format_func=lambda path: str(path.relative_to(ROOT)),
)
metadata_path = selected.parent / "run.json"
metadata = (
    json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata_path.exists()
    else {}
)
df = pd.read_csv(selected)
part_id = str(metadata.get("part_id") or df.get("part_id", pd.Series(["bracket"])).iloc[0])
part_name = metadata.get("part_name", part_id.title())
constraints = metadata.get("constraints", {})
min_fos = float(constraints.get("min_factor_of_safety", 2.5))
max_deflection = float(constraints.get("max_deflection_mm", 0.5))

st.caption(
    f"{part_name} | {metadata.get('material', {}).get('name', 'Configured material')} | "
    f"FOS >= {min_fos:g} | deflection <= {max_deflection:g} mm"
)

ok = df[df["status"] == "ok"].copy()
if ok.empty:
    st.error("The selected run has no successful analytical evaluations.")
    st.dataframe(df, width="stretch")
    st.stop()

ok["feasible"] = (
    (ok["factor_of_safety"] >= min_fos)
    & (ok["max_deflection_mm"] <= max_deflection)
)
best_feasible = ok[ok["feasible"]].sort_values("mass_kg").head(1)
best_objective = ok.sort_values("objective_value").head(1)

metric_cols = st.columns(4)
metric_cols[0].metric("Evaluations", len(df))
metric_cols[1].metric("Successful", len(ok))
metric_cols[2].metric("Feasible", int(ok["feasible"].sum()))
metric_cols[3].metric(
    "Best mass kg",
    f"{best_feasible['mass_kg'].iloc[0]:.3f}" if not best_feasible.empty else "n/a",
)

left, right = st.columns(2)
with left:
    st.plotly_chart(
        px.line(ok, x="iteration", y="mass_kg", markers=True, title="Mass Convergence"),
        width="stretch",
    )
with right:
    st.plotly_chart(
        px.scatter(
            ok,
            x="mass_kg",
            y="max_stress_mpa",
            color="feasible",
            hover_data=["iteration", "factor_of_safety", "max_deflection_mm", "objective_value"],
            title="Stress vs Mass",
        ),
        width="stretch",
    )

left, right = st.columns(2)
with left:
    fos_figure = px.scatter(
        ok, x="mass_kg", y="factor_of_safety", color="feasible", title="FOS vs Mass"
    )
    fos_figure.add_hline(y=min_fos, line_dash="dash", line_color="red")
    st.plotly_chart(fos_figure, width="stretch")
with right:
    deflection_figure = px.scatter(
        ok,
        x="mass_kg",
        y="max_deflection_mm",
        color="feasible",
        title="Deflection vs Mass",
    )
    deflection_figure.add_hline(y=max_deflection, line_dash="dash", line_color="red")
    st.plotly_chart(deflection_figure, width="stretch")

st.subheader("Best Candidate")
candidate = best_feasible if not best_feasible.empty else best_objective
st.dataframe(best_candidate_table(candidate), width="stretch", hide_index=True)

parameter_metadata = metadata.get("parameters", [])
if parameter_metadata:
    st.subheader("Design Variables")
    st.dataframe(pd.DataFrame(parameter_metadata), width="stretch", hide_index=True)

st.subheader("Run Data")
st.dataframe(df, width="stretch")
