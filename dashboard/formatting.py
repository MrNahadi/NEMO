"""Display helpers for the Streamlit dashboard."""

from __future__ import annotations

from numbers import Number

import pandas as pd


def best_candidate_table(candidate: pd.DataFrame) -> pd.DataFrame:
    """Return one candidate as a homogeneous field/value display table."""
    if candidate.empty:
        return pd.DataFrame({"Field": [], "Value": []}, dtype=str)

    row = candidate.iloc[0]
    return pd.DataFrame(
        {
            "Field": [str(field) for field in row.index],
            "Value": [_format_value(value) for value in row],
        }
    )


def _format_value(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, Number):
        return f"{float(value):.6g}"
    return str(value)
