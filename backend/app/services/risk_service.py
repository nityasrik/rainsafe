"""
Risk assessment and NLP analysis service (with non-blocking NLP)
"""

import asyncio
import spacy
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone # Import for time filtering
from app.utils.database import db
from config.settings import RISK_THRESHOLDS

# Load the spaCy model once when the service is initialized
try:
    nlp = spacy.load("en_core_web_sm")
    print("✅ Successfully loaded spaCy model 'en_core_web_sm'")
except OSError:
    print("❌ spaCy model not found. Please run 'python -m spacy download en_core_web_sm'")
    nlp = None

def _run_spacy_analysis(description: str) -> Dict[str, Any]:
    """
    A synchronous wrapper for the CPU-bound spaCy analysis.
    This function will be run in a separate thread.
    """
    if not nlp:
        return {"severity_from_text": "unknown", "extracted_locations": [], "actionable_words": []} # Fixed key name
    
    doc = nlp(description.lower())
    
    entities = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC", "FAC"]]
    
    severity = "low"
    actionable_words = []
    
    high_risk_lemmas = ["stick", "submerge", "block", "trap", "enter", "dangerous", "impassable", "wash", "collapsed"]
    medium_risk_lemmas = ["rise", "overflow", "waterlog", "struggle", "difficult", "stagnant"]

    for token in doc:
        if token.lemma_ in high_risk_lemmas:
            severity = "high"
            actionable_words.append(token.text)
        elif token.lemma_ in medium_risk_lemmas and severity != "high":
            severity = "medium"
            actionable_words.append(token.text)
            
    return {
        "severity_from_text": severity,
        "extracted_locations": list(set(entities)),
        "actionable_words": list(set(actionable_words))
    }

class RiskAssessmentService:
    """Service for flood risk assessment and NLP-based report analysis."""

    def __init__(self, database):
        """The database connection is now injected for better testability."""
        self.db = database
        self.thresholds = RISK_THRESHOLDS

    async def analyze_description_with_nlp(self, description: str) -> Dict[str, Any]:
        """
        Asynchronously analyzes a user's description without blocking the server.
        """
        # Run the synchronous, CPU-bound function in a separate thread
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, _run_spacy_analysis, description)
        return result

    async def check_thresholds(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Check if a location meets risk thresholds based on recent user reports.
        Returns a dictionary with 'risk' and 'details' including 'user_reports_found'
        """
        try:
            reports_collection = self.db.get_collection("reports")
            
            # Define a time window for recent reports (e.g., last 24 hours)
            time_window_start = datetime.now(timezone.utc) - timedelta(hours=24)

            # Query for nearby and recent reports
            nearby_reports = await reports_collection.find({
                "latitude": {"$gte": lat - 0.01, "$lte": lat + 0.01}, # Adjust radius as needed
                "longitude": {"$gte": lon - 0.01, "$lte": lon + 0.01},
                "created_at": {"$gte": time_window_start} 
            }).to_list(length=50) # Limit the list size for performance

            user_reports_count = len(nearby_reports)
            high_risk_reports = [r for r in nearby_reports if r.get("water_level") in self.thresholds.get("HIGH_WATER_LEVEL", [])]
            
            # Prepare details for the risk assessment
            details_output = {"user_reports_found": user_reports_count}
            risk_level = "Low"
            
            if high_risk_reports:
                risk_level = "High"
                details_output["trigger"] = "High water level reported by users" # Still keep 'trigger' for internal logic
            elif user_reports_count > 0:
                risk_level = "Medium"
                details_output["trigger"] = f"{user_reports_count} recent user reports" # Still keep 'trigger' for internal logic
            else:
                details_output["trigger"] = "No recent user reports" # Still keep 'trigger' for internal logic
            
            return {"risk": risk_level, "details": details_output}
            
        except Exception as e:
            print(f"Error in check_thresholds: {e}")
            return {"risk": "Unknown", "details": {"error": str(e), "user_reports_found": 0}}


    async def gather_features_for_prediction(self, lat: float, lon: float) -> Dict[str, Any]: # Changed return type to Dict for clarity
        """Gather enhanced features for the ML model."""
        try:
            reports_collection = self.db.get_collection("reports")
            weather_collection = self.db.get_collection("weather_data")

            # Define a recent time window for weather data and user reports for ML
            time_window_start_ml = datetime.now(timezone.utc) - timedelta(hours=3) # More recent for ML
            
            reports_in_vicinity = await reports_collection.count_documents({
                "latitude": {"$gte": lat - 0.01, "$lte": lat + 0.01},
                "longitude": {"$gte": lon - 0.01, "$lte": lon + 0.01},
                "created_at": {"$gte": time_window_start_ml}
            })

            # Fetch the most recent weather data, within a reasonable time frame
            recent_weather = await weather_collection.find_one(
                {"fetched_at": {"$gte": time_window_start_ml}},
                sort=[("fetched_at", -1)]
            )
            
            # Default features in case data is missing
            temp = 25.0
            humidity = 50
            rain_1h_mm = 0.0
            pressure = 1013
            rainfall_next_3_hours = 0.0
            weather_data_was_found = False

            if recent_weather:
                weather_data_was_found = True
                current = recent_weather.get("current_weather", {})
                forecast = recent_weather.get("forecast_data", [])
                
                temp = current.get("temp", temp)
                humidity = current.get("humidity", humidity)
                rain_1h_mm = current.get("rain_1h_mm", rain_1h_mm)
                pressure = current.get("pressure", pressure)
                
                # Sum rainfall for the next 3 hours from forecast
                # Assuming forecast_data has elements with 'dt_txt' and 'rain.3h'
                now = datetime.now(timezone.utc)
                for item in forecast:
                    # Parse dt_txt to datetime object if it's a string
                    if 'dt_txt' in item:
                        forecast_time_str = item['dt_txt']
                        # Example format: "2023-10-28 12:00:00"
                        forecast_time = datetime.strptime(forecast_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                        
                        if now <= forecast_time <= (now + timedelta(hours=3)):
                            rainfall_next_3_hours += item.get("rain", {}).get("3h", 0)

            return {
                "features": [temp, humidity, rain_1h_mm, pressure, reports_in_vicinity, rainfall_next_3_hours],
                "weather_data_found": weather_data_was_found
            }
            
        except Exception as e:
            print(f"Error gathering features: {e}")
            return {
                "features": [25.0, 50, 0.0, 1013, 0, 0.0],
                "weather_data_found": False
            }