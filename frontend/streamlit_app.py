# frontend/streamlit_app.py
import os
import requests
import streamlit as st
import pandas as pd

API_BASE = os.getenv("API_BASE", "http://localhost:5000/api")
API_KEY = "super-simple-api-key"  # must match backend

# Simple in-memory user store (for demo only)
USERS = {
    "uploader": {"password": "upload123", "role": "uploader"},
    "viewer": {"password": "view123", "role": "viewer"},
}


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


def login_sidebar():
    """Very simple login in the sidebar using the USERS dict."""
    st.sidebar.title("Login")

    if "user" not in st.session_state:
        st.session_state["user"] = None
        st.session_state["role"] = None

    # Already logged in
    if st.session_state["user"]:
        st.sidebar.write(
            f"Logged in as **{st.session_state['user']}** "
            f"({st.session_state['role']})"
        )
        if st.sidebar.button("Log out"):
            st.session_state["user"] = None
            st.session_state["role"] = None
            # Clear cached data on logout
            fetch_summary.clear()
            fetch_sample.clear()
        return

    # Login form
    with st.sidebar.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        info = USERS.get(username)
        if info and info["password"] == password:
            st.session_state["user"] = username
            st.session_state["role"] = info["role"]
            st.sidebar.success("Login successful.")
        else:
            st.sidebar.error("Invalid username or password.")


def upload_section():
    """
    Panel visible only to uploader role.
    Sends a ZIP to the Flask backend's /api/upload_snapshot endpoint.
    """
    st.subheader("Upload New AACT Snapshot (Uploader Only)")

    uploaded_zip = st.file_uploader(
        "Upload AACT snapshot ZIP file",
        type=["zip"],
        help="Use a flatfiles snapshot from the AACT website.",
    )

    if uploaded_zip is not None:
        if st.button("Upload to Server"):
            try:
                files = {
                    "file": (
                        uploaded_zip.name,
                        uploaded_zip.getvalue(),
                        "application/zip",
                    )
                }
                headers = {"X-API-KEY": API_KEY}
                resp = requests.post(
                    f"{API_BASE}/upload_snapshot",
                    files=files,
                    headers=headers,
                )
                if resp.status_code == 200:
                    st.success("Upload successful. Data has been refreshed.")
                    # Clear caches so new data is loaded
                    fetch_summary.clear()
                    fetch_sample.clear()
                else:
                    try:
                        msg = resp.json().get("error", resp.text)
                    except Exception:
                        msg = resp.text
                    st.error(f"Upload failed: {msg}")
            except Exception as e:
                st.error(f"Error uploading file: {e}")


def main():
    st.set_page_config(page_title="Clinical Trials Dashboard", layout="wide")

    login_sidebar()

    # Require login
    if not st.session_state.get("user"):
        st.title("Clinical Trials Dashboard (AACT, Core Parameters)")
        st.info("Please log in as 'uploader' or 'viewer' in the sidebar.")
        st.stop()

    role = st.session_state.get("role", "viewer")

    st.title("Clinical Trials Dashboard (AACT, Core Parameters)")
    st.caption(f"Role: **{role}**")

    require_backend()

    # Uploader panel
    if role == "uploader":
        with st.expander("Uploader Panel", expanded=False):
            upload_section()
        st.markdown("---")

    # Load data from backend
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

    # --- Charts ---
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.subheader("Studies by Phase")
        phase_df = (
            pd.DataFrame(
                {
                    "phase": list(summary["by_phase"].keys()),
                    "count": list(summary["by_phase"].values()),
                }
            )
            .sort_values("count", ascending=False)
        )
        st.bar_chart(phase_df.set_index("phase"))

    with col_b:
        st.subheader("Studies by Study Type")
        type_df = (
            pd.DataFrame(
                {
                    "study_type": list(summary["by_study_type"].keys()),
                    "count": list(summary["by_study_type"].values()),
                }
            )
            .sort_values("count", ascending=False)
        )
        st.bar_chart(type_df.set_index("study_type"))

    with col_c:
        st.subheader("Studies by Overall Status")
        status_df = (
            pd.DataFrame(
                {
                    "status": list(summary["by_status"].keys()),
                    "count": list(summary["by_status"].values()),
                }
            )
            .sort_values("count", ascending=False)
        )
        st.bar_chart(status_df.set_index("status"))

    st.markdown("---")

    # --- Enrollment table ---
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
                {
                    "country": list(summary["top_countries"].keys()),
                    "count": list(summary["top_countries"].values()),
                }
            )
            .sort_values("count", ascending=False)
        )
        st.bar_chart(country_df.set_index("country"))
    else:
        st.info("No country information available in the current dataset.")

    st.markdown("---")

    # --- Sample grid with filters ---
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
