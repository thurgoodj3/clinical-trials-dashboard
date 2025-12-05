import requests
import streamlit as st
import pandas as pd

API_BASE = "http://localhost:5000/api"


@st.cache_data(show_spinner=False)
def fetch_summary():
    resp = requests.get(f"{API_BASE}/studies/summary")
    resp.raise_for_status()
    return resp.json()


@st.cache_data(show_spinner=False)
def fetch_sample():
    resp = requests.get(f"{API_BASE}/studies/sample")
    resp.raise_for_status()
    data = resp.json()["rows"]
    return pd.DataFrame(data)


def require_backend():
    try:
        health = requests.get(f"{API_BASE}/health").json()
        if health.get("status") != "ok":
            st.warning("Backend reachable but not healthy.")
    except Exception:
        st.error("Cannot reach Flask backend. Make sure `python api.py` is running.")
        st.stop()


def main():
    st.set_page_config(page_title="Clinical Trials Dashboard", layout="wide")
    st.title("Clinical Trials Dashboard (AACT, Core Parameters)")

    require_backend()

    summary = fetch_summary()
    sample_df = fetch_sample()

    # --- Top metrics ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total studies", f"{summary['total_studies']:,}")
    with col2:
        st.metric("Distinct phases", len(summary["by_phase"]))
    with col3:
        st.metric("Distinct statuses", len(summary["by_status"]))

    st.markdown("---")

    # --- Charts: by phase, by study type, by status ---
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.subheader("Studies by Phase")
        phase_df = (
            pd.DataFrame(
                {"phase": list(summary["by_phase"].keys()),
                 "count": list(summary["by_phase"].values())}
            )
            .sort_values("count", ascending=False)
        )
        st.bar_chart(phase_df.set_index("phase"))

    with col_b:
        st.subheader("Studies by Study Type")
        type_df = (
            pd.DataFrame(
                {"study_type": list(summary["by_study_type"].keys()),
                 "count": list(summary["by_study_type"].values())}
            )
            .sort_values("count", ascending=False)
        )
        st.bar_chart(type_df.set_index("study_type"))

    with col_c:
        st.subheader("Studies by Overall Status")
        status_df = (
            pd.DataFrame(
                {"status": list(summary["by_status"].keys()),
                 "count": list(summary["by_status"].values())}
            )
            .sort_values("count", ascending=False)
        )
        st.bar_chart(status_df.set_index("status"))

    st.markdown("---")

    # --- Enrollment by phase table ---
    st.subheader("Enrollment by Phase")
    enroll_df = pd.DataFrame.from_dict(summary["enrollment_by_phase"], orient="index")
    enroll_df.index.name = "phase"
    st.dataframe(enroll_df)

    st.markdown("---")

    # --- Top countries ---
    st.subheader("Top Countries by Number of Trials")
    if summary["top_countries"]:
        country_df = (
            pd.DataFrame(
                {"country": list(summary["top_countries"].keys()),
                 "count": list(summary["top_countries"].values())}
            )
            .sort_values("count", ascending=False)
        )
        st.bar_chart(country_df.set_index("country"))
    else:
        st.info("No country information available in the current dataset.")

    st.markdown("---")

    # --- Sample table with filters ---
    st.subheader("Sample of Trials (Core Parameters)")

    phases = ["All"] + sorted(sample_df["phase"].dropna().unique().tolist())
    statuses = ["All"] + sorted(sample_df["overall_status"].dropna().unique().tolist())
    types = ["All"] + sorted(sample_df["study_type"].dropna().unique().tolist())

    col_p, col_s, col_t = st.columns(3)
    with col_p:
        phase_filter = st.selectbox("Filter by phase", phases)
    with col_s:
        status_filter = st.selectbox("Filter by status", statuses)
    with col_t:
        type_filter = st.selectbox("Filter by study type", types)

    df_filtered = sample_df.copy()
    if phase_filter != "All":
        df_filtered = df_filtered[df_filtered["phase"] == phase_filter]
    if status_filter != "All":
        df_filtered = df_filtered[df_filtered["overall_status"] == status_filter]
    if type_filter != "All":
        df_filtered = df_filtered[df_filtered["study_type"] == type_filter]

    st.dataframe(
        df_filtered[
            [
                "nct_id",
                "brief_title",
                "overall_status",
                "study_type",
                "phase",
                "enrollment",
                "all_countries",
                "all_id_information",
            ]
        ]
    )


if __name__ == "__main__":
    main()
