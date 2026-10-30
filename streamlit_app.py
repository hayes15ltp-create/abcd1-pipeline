from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="ABCD1 Research Registry", layout="wide")
st.title("ABCD1 research registry")
st.caption("Public-data computational registry. This interface is planning/support tooling, not validated therapy evidence.")

db_path = st.sidebar.text_input("SQLite database", "data/verify.sqlite3")
database_file = Path(db_path)

if not database_file.is_file():
    st.error(f"Database unavailable: {database_file} was not found.")
    st.stop()

try:
    conn = sqlite3.connect(f"file:{database_file.resolve()}?mode=ro", uri=True, timeout=30)
    conn.row_factory = sqlite3.Row
except sqlite3.Error as exc:
    st.error(f"Database unavailable: {exc}")
    st.stop()

with database_file.open("rb") as file:
    st.sidebar.download_button(
        "Download SQLite database",
        data=file.read(),
        file_name=database_file.name,
        mime="application/vnd.sqlite3",
    )

st.subheader("Active Pathogenic-only cohort")
members = conn.execute(
    """
    SELECT v.hgvs, v.assembly, v.transcript, cm.row_reference
    FROM cohorts c
    JOIN cohort_memberships cm ON cm.cohort_id=c.id
    JOIN variants v ON v.id=cm.variant_id
    WHERE c.active=1 AND cm.state='included'
    ORDER BY v.hgvs
    """
).fetchall()
st.metric("Eligible variants", len(members))
st.dataframe(pd.DataFrame([dict(row) for row in members]), use_container_width=True)

st.subheader("Logical runs by status")
runs = conn.execute(
    """
    SELECT lr.id, lr.status, lr.attempt, lr.reason, rs.fingerprint, rs.tool_name, rs.tool_version
    FROM logical_runs lr JOIN run_specs rs ON rs.id=lr.spec_id
    ORDER BY lr.id DESC
    """
).fetchall()
st.dataframe(pd.DataFrame([dict(row) for row in runs]), use_container_width=True)

st.subheader("Delivery-method summary")
methods = conn.execute(
    """
    SELECT dm.id, dm.family, dm.name, dm.version, COUNT(DISTINCT sm.study_id) AS linked_studies
    FROM delivery_methods dm LEFT JOIN study_methods sm ON sm.method_id=dm.id
    GROUP BY dm.id, dm.family, dm.name, dm.version
    ORDER BY dm.family, dm.name
    """
).fetchall()
st.dataframe(pd.DataFrame([dict(row) for row in methods]), use_container_width=True)

st.subheader("Database browser")
table_names = [
    row["name"]
    for row in conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    )
]
selected_table = st.selectbox("Table", table_names)
limit = st.number_input("Rows to display", min_value=1, max_value=10000, value=100, step=100)
table_rows = conn.execute(
    f'SELECT * FROM "{selected_table.replace(chr(34), chr(34) * 2)}" LIMIT ?',
    (limit,),
).fetchall()
st.caption(f"{len(table_rows)} row(s) shown from {selected_table}")
st.dataframe(pd.DataFrame([dict(row) for row in table_rows]), use_container_width=True)
