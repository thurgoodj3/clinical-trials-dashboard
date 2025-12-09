Clinical Trials Dashboard

This project is a lightweight web application for exploring clinical trial data using a small set of core fields. It includes a Flask API backend, a Streamlit-based dashboard frontend, and a PostgreSQL database hosted on Render. The application supports two roles—Viewer and Uploader—allowing basic access control for browsing or updating the dataset.

Features
Dashboard

View study counts by phase, study type, and recruitment status

Enrollment statistics by phase

Top countries represented across trials

Filterable table of study records

Built with Streamlit for a simple, interactive user experience

Role-Based Access

Viewer: Can browse the dashboard and run data queries

Uploader: Can upload new AACT snapshot files, which trigger backend processing and database refresh

Backend

Flask API deployed on Render

Endpoints for summary statistics, sample data, and snapshot uploads

Data stored in a Render-managed PostgreSQL instance

Tech Stack

Frontend: Streamlit
Backend: Flask (REST API)
Database: PostgreSQL (Render)
Deployment: Render (backend + frontend)

Core Data Fields

To keep the application efficient and easy to maintain, the backend stores fewer than ten key fields from each trial:

nct_id

brief_title

overall_status

study_type

phase

enrollment

all_countries

all_id_information

These fields are derived from AACT snapshot files and then written to the PostgreSQL database.

Application Structure
clinical-trials-dashboard/
│
├── backend/
│   ├── api.py                  # Flask API
│   └── data_loader.py          # Loads data from AACT and writes to PostgreSQL
│
├── frontend/
│   └── streamlit_app.py        # Streamlit dashboard application
│
├── data/                       # Used only for local development
│   └── aact/                   # Optional: AACT flatfiles for testing
│
└── requirements.txt

Running the App Locally
1. Clone the repository
git clone https://github.com/<your-username>/clinical-trials-dashboard.git
cd clinical-trials-dashboard

2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.\.venv\Scripts\activate       # Windows

3. Install dependencies
pip install -r requirements.txt

4. Set environment variables

Create a .env file with:

DATABASE_URL=<your Render PostgreSQL connection URL>
API_KEY=<your uploader API key>

5. Run the backend (Flask)
cd backend
python api.py

6. Run the frontend (Streamlit)
cd frontend
streamlit run streamlit_app.py

Deployment (Render)
Backend

Flask app is deployed as a Render Web Service

Connected to the Render PostgreSQL database

Automatically reloads new data when an uploader sends a ZIP file

Frontend

Streamlit is deployed as a separate Render Web Service

Communicates with the Flask backend over HTTPS

Uploader Instructions

Log in as uploader

Open the Uploader Panel

Upload an official AACT snapshot ZIP

The backend processes the snapshot and updates the PostgreSQL database

The dashboard automatically reflects the new data

Viewer Instructions

Log in as viewer

Browse charts, tables, and statistics

Optionally filter studies by phase, type, or status

Extending the Project

Possible future enhancements include:

Adding more AACT fields (conditions, interventions)

User authentication backed by the database instead of hardcoded values

Automated scheduled updates from AACT

Deployment behind a custom domain
