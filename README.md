# Protocol Monitor - Take Home

Hi, here is my submission for the Protocol Monitor assignment.

I implemented the monitoring pipeline using Python (FastAPI) and used SQLite for the database to keep the setup simple and easy to run without needing an external Postgres instance.

## Overview
The system does three main things:
1.  **Ingests Data**: I wrote a script (`ingest.py`) that mimics fetching data from Felix and HLP. Since I didn't have access to live robust APIs for these specific metrics, I mocked the data generators to prove the anomaly detection logic works.
2.  **Detects Anomalies**: The system flags alerts if:
    -   TVL drops by more than 20% (Critical)
    -   APY drops below 2% (Warning)
    -   Utilization goes above 95% (Warning)
3.  **API**: You can query the current health and history via the REST API.

## How to Run

First, install the requirements:
```bash
pip install -r requirements.txt
```

### 1. Setup Database
Initialize the SQLite database:
```bash
python database.py
```

### 2. Run Ingestion (Mock Data)
Run the ingestion script. You can run this multiple times to generate more history:
```bash
python ingest.py
```
*Note: I added some randomization in the mock data so you might see alerts pop up occasionally.*

### 3. Start the API
Start the server:
```bash
python api.py
```
Then open your browser to:
-   **Health Check**: [http://localhost:8000/protocols](http://localhost:8000/protocols)
-   **Alerts**: [http://localhost:8000/alerts](http://localhost:8000/alerts)

## Docker (Optional)
If you prefer running with Docker, I included a Dockerfile.
```bash
docker build -t protocol-monitor .
docker run -p 8000:8000 protocol-monitor
```

## Notes
-   I used `SQLite` instead of Postgres to make this submission portable.
-   The anomaly detection relies on comparing the *current* fetch vs the *last* snapshot.
