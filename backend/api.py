# backend/api.py
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# -------------------------------------------------
# Load .env (one level above backend/)
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

# Now that env vars are loaded, we can import data_loader
from data_loader import load_core_trials

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("API_KEY", "super-simple-api-key")


# -------------------------------------------------
# Root route for Render health check
# -------------------------------------------------
@app.route("/")
def root():
    return jsonify({
        "status": "ok",
        "message": "clinical-trials backend running"
    }), 200


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"}), 200


# -------------------------------------------------
# /api/studies/summary with FULL DEBUG LOGGING
# -------------------------------------------------
@app.route("/api/studies/summary")
def studies_summary():
    print(">>> [SUMMARY] endpoint called")

    try:
        # Load data
        df = load_core_trials()
        print(">>> Loaded dataframe:", df.shape)
        print(">>> Columns:", df.columns.tolist())

        # Required columns check
        required_cols = [
            "phase",
            "study_type",
            "overall_status",
            "enrollment",
            "all_countries",
            "nct_id"
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            print(">>> MISSING COLUMNS:", missing)
            return jsonify({"error": "Missing columns", "missing": missing}), 500

        # Ensure enrollment is numeric
        print(">>> Cleaning enrollment column...")
        df["enrollment"] = (
            df["enrollment"]
            .apply(lambda x: None if x in ["", "NA", None] else x)
        )
        df["enrollment"] = (
            df["enrollment"]
            .apply(lambda x: float(x) if str(x).replace(".", "", 1).isdigit() else None)
        )
        df["enrollment"] = df["enrollment"].fillna(0)

        print(">>> Enrollment cleaned. Example:", df["enrollment"].head().tolist())

        # ------------------------------------------
        # Aggregations
        # ------------------------------------------
        print(">>> Computing aggregates...")

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

        print(">>> Enrollment aggregated by phase")

        # ------------------------------------------
        # Countries
        # ------------------------------------------
        print(">>> Processing countries...")

        country_counts = {}
        for countries in df["all_countries"].dropna():
            for c in str(countries).split(";"):
                name = c.strip()
                if not name or name == "Unknown":
                    continue
                country_counts[name] = country_counts.get(name, 0) + 1

        top_countries = dict(
            sorted(country_counts.items(), key=lambda kv: kv[1], reverse=True)[:10]
        )

        print(">>> Countries processed:", len(country_counts))

        # ------------------------------------------
        # Final JSON Output
        # ------------------------------------------
        result = {
            "total_studies": int(df["nct_id"].nunique()),
            "by_phase": by_phase,
            "by_study_type": by_study_type,
            "by_status": by_status,
            "enrollment_by_phase": enrollment_by_phase,
            "top_countries": top_countries,
        }

        print(">>> Final summary ready:", result.keys())

        return jsonify(result)

    except Exception as e:
        print(">>> ERROR in /api/studies/summary:", e)
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------
# Sample endpoint (kept unchanged except logs)
# -------------------------------------------------
@app.route("/api/studies/sample")
def studies_sample():
    print(">>> [SAMPLE] endpoint called")

    try:
        df = load_core_trials()
        print(">>> Loaded dataframe:", df.shape)

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
        print(">>> Sample size:", len(sample))

        return jsonify({"rows": sample})

    except Exception as e:
        print(">>> ERROR in /api/studies/sample:", e)
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------
# Local development entrypoint (Render uses gunicorn)
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f">>> Running locally on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)

