# RainSafe Monorepo

Basic structure prepared for backend and frontend.

## Structure

```
backend/   # FastAPI backend (existing app moved here)
frontend/  # Placeholder for future frontend (devcontainer + Dockerfile)
```

## Backend (FastAPI)

- Change into backend directory and run with your existing commands.

```
cd backend
source ../venv/bin/activate
python main.py
```

Swagger UI: http://localhost:8000/docs

## Frontend (Placeholder)

- Open in devcontainer: `.devcontainer/devcontainer.json` provided under `frontend/`.
- Dockerfile is minimal and keeps the container running for development.
- Add your framework (Next.js / Vite) later.

# RainSafe Backend

A Flask/FastAPI backend for flood risk assessment and real-time weather monitoring system.

## Features

- 🌤️ **Weather Data Fetching**: Automated weather data collection for major Indian cities
- 🚨 **Flood Risk Assessment**: ML-powered risk prediction with hybrid analysis
- 📊 **Real-time Reports**: User-submitted flood reports with location tracking
- 📈 **Dashboard Data**: API endpoints for frontend dashboard integration
- 🔄 **Automated Scheduling**: Cron jobs for regular weather data updates

## API Endpoints

### Core Endpoints
- `GET /` - Health check
- `POST /report` - Submit flood reports
- `GET /risk?lat={lat}&lon={lon}` - Get flood risk assessment
- `GET /dashboard-data` - Get dashboard data for frontend
- `POST /alerts` - Send flood alerts

### Data Models
- **Report**: User-submitted flood reports with location and severity
- **Alert**: Flood alerts with risk levels and notifications
- **Weather**: Real-time weather data for risk assessment

## Setup Instructions

### Prerequisites
- Python 3.8+
- MongoDB Atlas account
- OpenWeather API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rainsafe-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file with:
   ```bash
   OPENWEATHER_API_KEY=your_openweather_api_key
   MONGO_URI=your_mongodb_atlas_connection_string
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## Automated Weather Data Collection

The system automatically fetches weather data every 30 minutes using cron jobs.

### Manual Weather Data Fetch
```bash
python fetch_weather.py
```

### Cron Setup
The system includes automated cron job setup:
```bash
*/30 * * * * /path/to/run_weather_cron.sh
```

## MongoDB Collections

- **reports**: User-submitted flood reports
- **weather_data**: Historical weather data
- **alerts**: System-generated alerts

## ML Model

The system uses a trained ML model for flood risk prediction based on:
- Historical weather patterns
- User reports
- Geographic data
- Real-time conditions

## Development

### Running Tests
```bash
python test_api.py
```

### API Documentation
Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Deployment

### Production Considerations
- Set up proper MongoDB Atlas IP whitelisting
- Configure environment variables securely
- Set up monitoring and logging
- Implement rate limiting
- Add authentication/authorization

### Docker Support
```bash
docker-compose up
```

## Troubleshooting

See `MONGODB_TROUBLESHOOTING.md` for common MongoDB connection issues.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request


