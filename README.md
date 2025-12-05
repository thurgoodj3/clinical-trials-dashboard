Clinical Trials Dashboard (Flask + Streamlit + AACT Dataset)

A lightweight, scalable clinical trials analytics dashboard built using:

Flask for backend API

Streamlit for the interactive frontend

AACT flatfiles as the dataset source

Role-based access (Uploader/Viewer)

<10 core parameters for simplicity and performance

This project allows users to explore global clinical trial activity and enables authorized users to upload a new AACT dataset snapshot.

⭐ Features
Viewer Role

Access interactive dashboards

Visualize:

Studies by Phase

Studies by Study Type

Studies by Overall Status

Enrollment distributions

Top countries

Filterable sample table of trials

No permission to upload data

Uploader Role

All viewer capabilities plus:

Upload a new AACT snapshot (.zip) through the Streamlit UI

Backend automatically extracts new files and refreshes dataset cache

