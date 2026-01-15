# Video Submission Script (2-3 Minutes)

**Preparation:**
1.  Open VS Code with your project files (`api.py`, `ingest.py`, `database.py`) visible.
2.  Open a Terminal in VS Code.
3.  Open a Browser tab to `http://localhost:8000/protocols`.

---

### **1. Introduction (0:00 - 0:30)**
*   **Action**: Start with your face or the VS Code editor on screen.
*   **Say**:
    > "Hi, I'm [Your Name]. This is my walkthrough for the Data Engineer Protocol Monitor assignment.
    >
    > My goal was to build a robust pipeline that monitors DeFi protocols like Felix and HLP. I focused on creating a clean, modular architecture that handles data ingestion, anomaly detection, and serving the results via an API."

### **2. Architecture Overview (0:30 - 1:00)**
*   **Action**: Click on `ingest.py` file.
*   **Say**:
    > "For the core logic, I built this ingestion service. I decided to mock the data sources here to ensure we could reliably test the anomaly detection—for example, simulating a sudden 20% TVL drop to trigger a critical alert.
    >
    > This script fetches the data, checks against my defined thresholds (like the 20% drop rule), and then persists everything to the database."

*   **Action**: Click on `database.py` very briefly.
*   **Say**:
    > "For storage, I chose SQLite using SQLAlchemy. I went with SQLite for this specific assignment to make it portable—you can run the whole thing locally without needing to spin up a Docker container for Postgres, although migrating to Postgres would just be a one-line config change."

### **3. Live Demo (1:00 - 1:45)**
*   **Action**: Open the Terminal. Run `python ingest.py`.
*   **Say**:
    > "Let me show you it running. Here I'm running the ingestion script manually..."
    > *(Wait for 'Successfully processed' logs)*
    > "You can see it processed the snapshots and checked for alerts."

*   **Action**: Run `python api.py` (if not running) or switch to the already running terminal. Then Switch to the **Browser**.
*   **Say**:
    > "Now, here is the API. I built this using FastAPI."
    > *(Refresh `http://localhost:8000/protocols`)*
    > "This endpoint returns the latest health status. You can see Felix and HLP are currently showing as 'healthy'. If an anomaly was detected, this status field would update to 'warning' or 'critical' automatically."

### **4. Conclusion (1:45 - 2:00)**
*   **Action**: Switch back to VS Code or camera.
*   **Say**:
    > "That's the high-level overview. The code is modular, type-safe with Pydantic, and ready to be containerized with the included Dockerfile. Thanks for your time!"
