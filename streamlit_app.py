from __future__ import annotations

import sqlite3

import pandas as pd
import streamlit as st

from abcd1.db import connect

st.set_page_config(page_title="ABCD1 Research Registry", layout="wide")
st.title("ABCD1 research registry")
st.caption("Public-data computational registry. This interface is planning/support tooling, not validated therapy evidence.")

db_path = st.sidebar.text_input("SQLite database", "data/abcd1.sqlite3")
try:
    conn = connect(db_path)
except sqlite3.Error as exc:
    st.error(f"Database unavailable: {exc}")
    st.stop()

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
