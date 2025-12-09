import os
from functools import lru_cache

import pandas as pd
from sqlalchemy import create_engine

# Read DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Make sure it's in your .env "
        "locally and configured in Render for the backend service."
    )

engine = create_engine(DATABASE_URL)


@lru_cache(maxsize=1)
def load_core_trials() -> pd.DataFrame:
    """
    Load and merge the core trial dataset using < 10 parameters:
      - nct_id
      - brief_title
      - overall_status
      - study_type
      - phase
      - enrollment
      - all_countries
      - all_id_information
    """

    # --- studies table ---
    studies_query = """
        SELECT
            nct_id,
            brief_title,
            overall_status,
            study_type,
            phase,
            enrollment
        FROM studies
    """
    studies = pd.read_sql(studies_query, engine)

    # clean enrollment
    studies["enrollment"] = pd.to_numeric(
        studies["enrollment"].replace("", pd.NA),
        errors="coerce",
    )

    studies["overall_status"] = studies["overall_status"].fillna("Unknown")
    studies["study_type"] = studies["study_type"].fillna("Unknown")
    studies["phase"] = studies["phase"].fillna("Unknown")

    # --- countries table -> all_countries ---
    countries_query = """
        SELECT
            nct_id,
            name
        FROM countries
    """
    countries = pd.read_sql(countries_query, engine)

    countries["name"] = countries["name"].fillna("Unknown")

    countries_agg = (
        countries.groupby("nct_id")["name"]
        .apply(lambda s: "; ".join(sorted(s.dropna().unique())))
        .reset_index(name="all_countries")
    )

    # --- id_information table -> all_id_information ---
    id_query = """
        SELECT
            nct_id,
            id_information
        FROM id_information
    """
    id_info = pd.read_sql(id_query, engine)

    id_info["id_information"] = id_info["id_information"].fillna("")

    id_agg = (
        id_info.groupby("nct_id")["id_information"]
        .apply(lambda s: "; ".join(sorted(s.dropna().unique())))
        .reset_index(name="all_id_information")
    )

    # --- merge everything on nct_id ---
    df = studies.merge(countries_agg, on="nct_id", how="left")
    df = df.merge(id_agg, on="nct_id", how="left")

    df["all_countries"] = df["all_countries"].fillna("Unknown")
    df["all_id_information"] = df["all_id_information"].fillna("")

    return df


def reload_core_trials_cache():
    """Clear cache so next call reads fresh data."""
    load_core_trials.cache_clear()

