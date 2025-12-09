📊 Clinical Trials Dashboard

A lightweight web application for exploring clinical trial data using a curated set of core fields. The system includes:

Flask API backend (deployed on Render)

Streamlit dashboard frontend (also deployed on Render)

PostgreSQL database hosted on Render

Role-based access for dataset control (Viewer / Uploader)

🚀 Features
👀 Viewer Capabilities

Interactive dashboard

Counts by phase, study type, and recruitment status

Enrollment statistics

Top countries for trial locations

Filterable trial table

🔐 Uploader Capabilities

All viewer features plus the ability to upload new AACT snapshot ZIP files

Upload triggers data ingestion and refresh in the Render PostgreSQL database

🧱 Tech Stack
Layer	Technology
Frontend	Streamlit
Backend	Flask REST API
Database	PostgreSQL (Render)
Deployment	Render Web Services
📁 Project Structure
clinical-trials-dashboard/
│
├── backend/
│   ├── api.py                  # Flask API service
│   └── data_loader.py          # Data extraction and DB ingestion
│
├── frontend/
│   └── streamlit_app.py        # Streamlit dashboard UI
│
├── data/                       # Used for local development only
│   └── aact/                   # Optional: AACT flatfiles
│
└── requirements.txt

🗂️ Core Data Fields (Under 10)

To keep the dashboard simple and performant, only the following fields are stored in the database:

Field	Description
nct_id	Primary trial identifier
brief_title	Study title
overall_status	Recruiting, Completed, etc.
study_type	Interventional, Observational
phase	Phase 1–4
enrollment	Enrollment counts
all_countries	Aggregated locations
all_id_information	Aggregated registry/sponsor IDs
🧰 Local Development Setup
1. Clone the repository
git clone https://github.com/<your-username>/clinical-trials-dashboard.git
cd clinical-trials-dashboard

2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.\.venv\Scripts\activate       # Windows

3. Install dependencies
pip install -r requirements.txt

4. Create a .env file
DATABASE_URL=<Render PostgreSQL connection string>
API_KEY=<secret uploader key>

5. Start backend
cd backend
python api.py

6. Start frontend
cd frontend
streamlit run streamlit_app.py

🌐 Deployment (Render)
Backend

Deployed as a Render Web Service

Connects to Render PostgreSQL

Handles summary endpoints and file upload endpoint

Frontend

Streamlit deployed as a separate Render Web Service

Communicates with Flask API over HTTPS

🔑 Login Credentials
Role	Username	Password	Permissions
Uploader	uploader	upload123	Uploads new dataset snapshots
Viewer	viewer	view123	Read-only access
📤 Uploading New AACT Data (Uploader Only)

Log in as uploader

Open the Uploader Panel

Upload an AACT snapshot ZIP

Backend extracts the ZIP and loads the data into PostgreSQL

Dashboard reflects updated data after reload

📈 Future Enhancements

Additional AACT tables (conditions, interventions, outcomes)

Database-backed authentication

Scheduled automatic updates

Deployment behind a custom domain

CI/CD integration
