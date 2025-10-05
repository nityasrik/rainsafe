# RainSafe Backend Architecture

## Core Components

- **Backend Framework:** FastAPI (Python)  
- **Database:** MongoDB Atlas  
- **Machine Learning:** Scikit-learn (RandomForestClassifier)  
- **Deployment:** Docker & Docker Compose  
- **Automation:** cron for scheduled data fetching  

---

## Project Structure

```bash
rainsafe-backend/
├── app/
│   ├── main.py                 # FastAPI app & API endpoints
│   ├── models/
│   │   ├── schemas.py          # Pydantic data models
│   │   └── flood_predictor.py  # The ML predictor class
│   └── services/
│       └── risk_service.py     # Core risk logic
├── data/
│   ├── ml_artifacts/           # ML model & scaler (.pkl) files
│   └── flood_risk_dataset_india.csv
├── scripts/
│   └── fetch_weather.py        # Weather fetching script
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## How It Works: The Data Flow

### Automated Data Collection
- A cron job automatically runs `scripts/fetch_weather.py` every 30 minutes.  
- This script fetches the latest weather and forecast data from the OpenWeatherMap API and stores it in MongoDB.

### User Reporting
- The frontend can send a user’s flood observation (location, water level, description, etc.) via `POST /report`.  
- The backend saves this report with a timestamp to the database.

### Hybrid Risk Assessment
When the frontend requests a risk level via `GET /risk`:

1. **Threshold Check:**  
   - Quick rule-based check for immediate danger using recent high-risk user reports (e.g., "Knee-deep" water).

2. **ML Prediction:**  
   - Gathers the latest weather data, prepares it using `scaler.pkl`, and feeds it to `model.pkl` for predictive risk assessment.

3. **Final Decision:**  
   - Combines both results and reports the **highest risk level** as the final, authoritative answer.

---

## Core API Endpoints

- **POST /report:** Submits a new user flood report.  
- **GET /risk:** Returns the hybrid risk assessment for a specific location.  
- **GET /dashboard-data:** Provides recent high-risk reports for the frontend map.  
- **POST /alerts:** Logs a triggered alert to the database (MVP version).  
