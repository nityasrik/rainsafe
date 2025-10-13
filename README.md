# RainSafe - Flood Risk Assessment API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

RainSafe is a FastAPI-based backend for a flood risk assessment and real-time weather monitoring system. It provides core functionalities for submitting user reports, assessing flood risk using hybrid analysis (thresholds + ML), fetching real-time weather, and serving data to a frontend dashboard.

## 🌟 Features

* **🌤️ Weather Data Fetching**: Automated collection of real-time weather and forecast data for key locations (e.g., major Indian cities).
* **🚨 Flood Risk Assessment**: Hybrid risk prediction combining:
    * Threshold-based analysis from recent user reports.
    * ML-powered prediction using current weather and historical data.
* **📊 Real-time User Reports**: API for users to submit flood conditions with location and severity.
* **📈 Dashboard Data**: Endpoints designed to feed interactive frontend dashboards with map points and aggregated insights.
* **🔄 Automated Scheduling**: Cron job for regular weather data updates to ensure fresh data for predictions.

## 🚀 Getting Started

These instructions will get your backend up and running for development and testing.

### Prerequisites

Before you begin, ensure you have the following:

* **Python 3.8+**
* **Docker & Docker Compose** (for containerized setup)
* **MongoDB Atlas Account**: You'll need a connection string.
* **OpenWeather API Key**: For fetching weather data.
* **(Optional) WSL2 / Ubuntu**: Recommended for consistent development environment on Windows.

### 🛠️ Installation & Setup (Docker Compose Recommended)

The easiest way to get the entire backend stack (FastAPI + MongoDB) running is with Docker Compose.

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/nityasrik/rainsafe.git](https://github.com/nityasrik/rainsafe.git)
    cd rainsafe
    ```

2.  **Create `.env` file:**
    Navigate to the `backend/` directory and create a `.env` file with your credentials:

    ```bash
    cd backend
    touch .env # Create the .env file
    ```

    Then, edit `.env` and add:

    ```ini
    OPENWEATHER_API_KEY=your_openweather_api_key_here
    MONGO_URI=your_mongodb_atlas_connection_string_here
    ```

    *Replace placeholders with your actual keys.*

3.  **Build and Run with Docker Compose:**
    From the `backend/` directory:

    ```bash
    docker compose up --build -d
    ```

    *The `-d` flag runs containers in detached mode.*

4.  **Verify Services:**
    Check container logs to ensure everything started successfully:

    ```bash
    docker compose logs -f
    ```

    Look for messages like `RainSafe API is running!`, `MongoDB connected.`, and `Flood predictor (ML) model loaded successfully.`

### 🌐 Accessing the API

Once running, your FastAPI application will be accessible at:

* **API Root:** `http://localhost:8000/`
* **Interactive API Docs (Swagger UI):** `http://localhost:8000/docs`
* **Alternative Docs (Redoc):** `http://localhost:8000/redoc`

Use the Swagger UI (`/docs`) to interact with and test all API endpoints directly in your browser.

## 🗺️ API Endpoints

### Core Endpoints

* `GET /`: Health check (returns `{"status": "RainSafe API is running!"}`)
* `POST /report`: Submit a new flood report.
* `GET /risk?lat={lat}&lon={lon}`: Get a hybrid flood risk assessment for a given location.
* `GET /dashboard-data`: Retrieve recent flood reports and risk levels for dashboard visualization.
* `POST /alerts`: Send and log flood alerts.

### Data Models

* **Report**: User-submitted flood conditions (location, description, water level, NLP analysis).
* **Alert**: System-generated alerts (location, risk level, recipient, timestamp).
* **Weather**: Real-time and forecasted weather data.

## 🗃️ MongoDB Collections

The application utilizes the following collections in MongoDB:

* `reports`: Stores user-submitted flood reports.
* `weather_data`: Stores historical and real-time weather information.
* `alerts`: Logs all system-generated and dispatched alerts.

## 🤖 ML Model

The system incorporates an ML model (`app/models/flood_predictor.py`) for enhanced flood risk prediction. It leverages:

* Real-time weather data
* Recent user reports
* Geographic features (implicitly through location)
* Historical patterns

**Note**: The `FloodPredictor` is designed to be easily swappable with your trained model. A dummy implementation is provided for initial setup.

## ⚙️ Automated Weather Data Collection

Weather data is automatically fetched and updated in the `weather_data` collection via a cron job.

### Manual Fetch (for testing)

To manually trigger a weather data fetch:

```bash
docker compose exec backend python fetch_weather.py
