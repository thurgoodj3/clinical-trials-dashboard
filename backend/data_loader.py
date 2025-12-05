import os
import pandas as pd
from functools import lru_cache

# Base folder where AACT flatfiles live
DATA_DIR = "/Users/jameswalton/Desktop/clinical-trials-dashboard/data/aact"

STUDIES_FILE = os.path.join(DATA_DIR, "studies.txt")
COUNTRIES_FILE = os.path.join(DATA_DIR, "countries.txt")
ID_INFO_FILE = os.path.join(DATA_DIR, "id_information.txt")

def _check_file(path: str, label: str):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing {label} file at {path}. "
            f"Make sure the file exists in your AACT data folder."
        )


@lru_cache(maxsize=1)
def load_core_trials():
    """
    Load and merge the core trial dataset using < 10 parameters:
      - nct_id
      - brief_title
      - overall_status
      - study_type
      - phase
      - enrollment
      - all_countries        (aggregated from countries.txt)
      - all_id_information   (aggregated from id_information.txt)
    """

    # --- studies.txt ---
    _check_file(STUDIES_FILE, "studies.txt")

    studies_usecols = [
        "nct_id",
        "brief_title",
        "overall_status",
        "study_type",
        "phase",
        "enrollment",
    ]

    studies = pd.read_csv(
        STUDIES_FILE,
        sep="|",
        dtype=str,
        usecols=lambda c: c in studies_usecols,
        low_memory=False,
    )

    # Clean numeric enrollment
    studies["enrollment"] = (
        studies["enrollment"]
        .replace("", pd.NA)
        .astype("float")
    )

    studies["overall_status"] = studies["overall_status"].fillna("Unknown")
    studies["study_type"] = studies["study_type"].fillna("Unknown")
    studies["phase"] = studies["phase"].fillna("Unknown")

    # --- countries.txt -> all_countries ---
    _check_file(COUNTRIES_FILE, "countries.txt")

    countries = pd.read_csv(
        COUNTRIES_FILE,
        sep="|",
        dtype=str,
        low_memory=False,
    )

    # In AACT, the country name column is usually "name"
    if "name" not in countries.columns:
        raise ValueError(
            "Expected 'name' column in countries.txt. "
            "Check the file or adjust the column name in data_loader.py."
        )

    countries["name"] = countries["name"].fillna("Unknown")

    countries_agg = (
        countries.groupby("nct_id")["name"]
        .apply(lambda s: "; ".join(sorted(s.dropna().unique())))
        .reset_index(name="all_countries")
    )

    # --- id_information.txt -> all_id_information ---
    _check_file(ID_INFO_FILE, "id_information.txt")

    id_info = pd.read_csv(
        ID_INFO_FILE,
        sep="|",
        dtype=str,
        low_memory=False,
    )

    # In AACT, id_information.txt usually has an "id_value" column
    id_value_col = "id_value" if "id_value" in id_info.columns else None
    if id_value_col is None:
        raise ValueError(
            "Expected 'id_value' column in id_information.txt. "
            "Check the file or adjust the column name in data_loader.py."
        )

    id_info[id_value_col] = id_info[id_value_col].fillna("")

    id_agg = (
        id_info.groupby("nct_id")[id_value_col]
        .apply(lambda s: "; ".join(sorted(set(filter(None, s)))))
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