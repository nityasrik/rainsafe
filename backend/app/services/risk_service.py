"""
Risk assessment service
"""

import asyncio
from typing import Dict, Any
from app.utils.database import db
from config.settings import RISK_THRESHOLDS


class RiskAssessmentService:
    """Service for flood risk assessment"""
    
    def __init__(self):
        self.thresholds = RISK_THRESHOLDS
    
    async def check_thresholds(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Check if location meets risk thresholds based on user reports and weather
        """
        try:
            reports_collection = db.get_collection("reports")
            
            # Find recent reports near the location (within ~1km radius)
            # Using simple bounding box for demo (in production, use proper geospatial queries)
            nearby_reports = await reports_collection.find({
                "latitude": {"$gte": lat - 0.01, "$lte": lat + 0.01},
                "longitude": {"$gte": lon - 0.01, "$lte": lon + 0.01}
            }).to_list(length=10)
            
            user_reports_found = len(nearby_reports)
            
            # Check for high water level reports
            high_risk_reports = [
                report for report in nearby_reports 
                if report.get("water_level") in self.thresholds["HIGH_WATER_LEVEL"]
            ]
            
            # Determine risk level
            if high_risk_reports:
                risk_level = "High"
                trigger = "High water level reported"
            elif user_reports_found > 0:
                risk_level = "Medium"
                trigger = "Recent reports found"
            else:
                risk_level = "Low"
                trigger = "No recent reports"
            
            # Check weather data availability
            weather_collection = db.get_collection("weather_data")
            recent_weather = await weather_collection.find_one({
                "fetched_at": {"$gte": "2025-10-01"}  # Recent weather data
            })
            weather_data_found = recent_weather is not None
            
            return {
                "risk": risk_level,
                "details": {
                    "user_reports_found": user_reports_found,
                    "weather_data_found": weather_data_found,
                    "trigger": trigger
                }
            }
            
        except Exception as e:
            print(f"Error in threshold check: {e}")
            return {
                "risk": "Unknown",
                "details": {"error": str(e)}
            }
    
    async def gather_features_for_prediction(self, lat: float, lon: float) -> list:
        """
        Gather features for ML prediction
        This is a simplified version - in production, you'd gather more comprehensive features
        """
        try:
            # Get recent reports count
            reports_collection = db.get_collection("reports")
            recent_reports_count = await reports_collection.count_documents({
                "latitude": {"$gte": lat - 0.01, "$lte": lat + 0.01},
                "longitude": {"$gte": lon - 0.01, "$lte": lon + 0.01}
            })
            
            # Get weather data (simplified features)
            weather_collection = db.get_collection("weather_data")
            recent_weather = await weather_collection.find_one({
                "fetched_at": {"$gte": "2025-10-01"}
            })
            
            if recent_weather:
                current_weather = recent_weather.get("current_weather", {})
                features = [
                    current_weather.get("temp", 25),
                    current_weather.get("humidity", 50),
                    current_weather.get("rain_1h_mm", 0),
                    current_weather.get("pressure", 1013),
                    recent_reports_count
                ]
            else:
                # Default features if no weather data
                features = [25, 50, 0, 1013, recent_reports_count]
            
            return features
            
        except Exception as e:
            print(f"Error gathering features: {e}")
            # Return default features
            return [25, 50, 0, 1013, 0]


# Global service instance
risk_service = RiskAssessmentService()
