from flask import Flask, jsonify
from flask_cors import CORS
from data_loader import load_core_trials

app = Flask(__name__)
CORS(app)  # allow Streamlit (different port) to call this API


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/studies/summary")
def studies_summary():
    """
    Returns:
      - total_studies
      - counts by phase
      - counts by study_type
      - counts by overall_status
      - enrollment stats by phase
      - top countries (by number of trials)
    """
    df = load_core_trials()

    by_phase = df["phase"].value_counts().to_dict()
    by_study_type = df["study_type"].value_counts().to_dict()
    by_status = df["overall_status"].value_counts().to_dict()

    enrollment_by_phase = (
        df.groupby("phase")["enrollment"]
        .agg(["count", "median", "mean"])
        .fillna(0)
        .round(1)
        .to_dict(orient="index")
    )

    # simple country count: each trial may have multiple countries (split on ";")
    country_counts = {}
    for countries in df["all_countries"].dropna():
        for c in str(countries).split(";"):
            name = c.strip()
            if not name or name == "Unknown":
                continue
            country_counts[name] = country_counts.get(name, 0) + 1

    # take top 10
    top_countries = dict(
        sorted(country_counts.items(), key=lambda kv: kv[1], reverse=True)[:10]
    )

    return jsonify(
        {
            "total_studies": int(df["nct_id"].nunique()),
            "by_phase": by_phase,
            "by_study_type": by_study_type,
            "by_status": by_status,
            "enrollment_by_phase": enrollment_by_phase,
            "top_countries": top_countries,
        }
    )


@app.route("/api/studies/sample")
def studies_sample():
    """
    Returns a small sample of rows with our < 10 parameters.
    """
    df = load_core_trials()
    cols = [
        "nct_id",
        "brief_title",
        "overall_status",
        "study_type",
        "phase",
        "enrollment",
        "all_countries",
        "all_id_information",
    ]
    sample = df[cols].head(200).to_dict(orient="records")
    return jsonify({"rows": sample})


if __name__ == "__main__":
    # Run Flask API on port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
