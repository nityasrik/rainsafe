"""
RainSafe Backend - Working Version
"""

import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List, Optional

import motor.motor_asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# from app.models.flood_predictor import FloodPredictor

# Load environment variables
load_dotenv()

# --- Data Models ---
class Report(BaseModel):
    latitude: float
    longitude: float
    description: str
    water_level: Optional[str] = None


class Alert(BaseModel):
    location_name: str
    risk_level: str
    recipient: str


class RiskResponse(BaseModel):
    risk_level: str
    source: str
    details: dict


# --- Lifespan function for startup and shutdown ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    print("🚀 Starting RainSafe API...")
    
    # Connect to MongoDB
    try:
        app.state.mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
        app.state.mongodb = app.state.mongodb_client.rainsafe_db
        
        # Test connection
        await app.state.mongodb_client.admin.command('ping')
        print("✅ Successfully connected to MongoDB")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise RuntimeError("Database connection failed")
    
    # Initialize ML predictor
    try:
        # predictor = FloodPredictor()
        app.state.predictor = None
        print("⚠️ ML predictor disabled for now")
    except Exception as e:
        print(f"⚠️ ML predictor initialization failed: {e}")
        app.state.predictor = None
    
    print("✅ RainSafe API startup complete!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down RainSafe API...")
    app.state.mongodb_client.close()
    print("🔒 RainSafe API shutdown complete")


# Initialize FastAPI with lifespan manager
app = FastAPI(
    title="RainSafe API",
    version="1.0.0",
    description="Flood risk assessment and weather monitoring API",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Helper Functions ---
async def check_thresholds(request: Request, lat: float, lon: float):
    """Check if location meets risk thresholds based on user reports and weather"""
    try:
        reports_collection = request.app.state.mongodb.reports
        
        # Find recent reports near the location (within ~1km radius)
        nearby_reports = await reports_collection.find({
            "latitude": {"$gte": lat - 0.01, "$lte": lat + 0.01},
            "longitude": {"$gte": lon - 0.01, "$lte": lon + 0.01}
        }).to_list(length=10)
        
        user_reports_found = len(nearby_reports)
        
        # Check for high water level reports
        high_risk_reports = [
            report for report in nearby_reports 
            if report.get("water_level") in ["Knee-deep", "Waist-deep", "Chest-deep", "Above head"]
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
        weather_collection = request.app.state.mongodb.weather_data
        recent_weather = await weather_collection.find_one({
            "fetched_at": {"$gte": "2025-10-01"}
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


async def gather_features_for_prediction(request: Request, lat: float, lon: float):
    """Gather features for ML prediction"""
    try:
        # Get recent reports count
        reports_collection = request.app.state.mongodb.reports
        recent_reports_count = await reports_collection.count_documents({
            "latitude": {"$gte": lat - 0.01, "$lte": lat + 0.01},
            "longitude": {"$gte": lon - 0.01, "$lte": lon + 0.01}
        })
        
        # Get weather data (simplified features)
        weather_collection = request.app.state.mongodb.weather_data
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


# --- API Endpoints ---
@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"status": "RainSafe API is running!"}


@app.post("/report", status_code=201)
async def create_report(request: Request, report: Report):
    """Submit a flood report"""
    try:
        report_data = report.model_dump()
        report_data["created_at"] = datetime.now(timezone.utc)

        reports_collection = request.app.state.mongodb.reports
        new_report = await reports_collection.insert_one(report_data)
        print(f"✅ Inserted report with ID: {new_report.inserted_id}")

        created_report = await reports_collection.find_one({"_id": new_report.inserted_id})
        if not created_report:
            raise ValueError("Report was inserted but not found!")

        created_report["_id"] = str(created_report["_id"])
        return {"message": "Report received successfully!", "data": created_report}

    except Exception as e:
        import traceback
        print("❌ Error in /report:", str(e))
        traceback.print_exc()
        return {"error": str(e)}


@app.get("/risk", response_model=RiskResponse)
async def get_risk(request: Request, lat: float, lon: float):
    """Get flood risk assessment for a location"""
    try:
        threshold_result = await check_thresholds(request, lat, lon)
        features = await gather_features_for_prediction(request, lat, lon)
        
        # Get ML prediction
        ml_risk = "Low"  # Default
        if request.app.state.predictor:
            ml_risk = request.app.state.predictor.predict(features)

        # Hybrid risk decision
        if "High" in [threshold_result["risk"], ml_risk]:
            final_risk = "High"
        elif "Medium" in [threshold_result["risk"]]:
            final_risk = "Medium"
        else:
            final_risk = ml_risk

        return {
            "risk_level": final_risk,
            "source": "hybrid-historical",
            "details": {
                "threshold_assessment": threshold_result["risk"],
                "ml_assessment": ml_risk,
                "threshold_details": threshold_result["details"],
            },
        }
    except Exception as e:
        import traceback
        print("❌ Error in /risk:", str(e))
        traceback.print_exc()
        return {
            "risk_level": "Unknown",
            "source": "error",
            "details": {"error": str(e)}
        }


@app.get("/dashboard-data")
async def get_dashboard_data(request: Request):
    """Get dashboard data for frontend"""
    try:
        reports_collection = request.app.state.mongodb.reports
        recent_reports = await reports_collection.find().sort("created_at", -1).limit(50).to_list(length=50)

        map_points = []
        for report in recent_reports:
            # Determine risk level based on water level
            water_level = report.get("water_level", "")
            if water_level in ["Knee-deep", "Waist-deep", "Chest-deep", "Above head"]:
                risk_level = "High"
            elif water_level in ["Ankle-deep"]:
                risk_level = "Medium"
            else:
                risk_level = "Low"

            map_points.append({
                "id": str(report["_id"]),
                "latitude": report["latitude"],
                "longitude": report["longitude"],
                "risk_level": risk_level,
                "source": "user-report",
                "details": report["description"]
            })

        return {"map_points": map_points, "charts_data": {}}

    except Exception as e:
        import traceback
        print("❌ Error in /dashboard-data:", str(e))
        traceback.print_exc()
        return {"map_points": [], "charts_data": {}, "error": str(e)}


@app.post("/alerts")
async def send_alert(request: Request, alert: Alert):
    """Send a flood alert"""
    try:
        timestamp = datetime.now(timezone.utc)
        print(f"--- 🚨 ALERT TRIGGERED ---")
        print(f"Time: {timestamp}, Recipient: {alert.recipient}, "
              f"Location: {alert.location_name}, Risk: {alert.risk_level}")

        # Convert alert to dict and add timestamp
        alert_record = alert.model_dump()
        alert_record["sent_at"] = timestamp
        
        # Try to insert into MongoDB, but don't fail if it doesn't work
        try:
            alerts_collection = request.app.state.mongodb.alerts
            result = await alerts_collection.insert_one(alert_record)
            print(f"✅ Alert inserted into MongoDB with ID: {result.inserted_id}")
            alert_record["_id"] = str(result.inserted_id)
        except Exception as db_error:
            print(f"⚠️ MongoDB insertion failed: {db_error}")
            print("📝 Alert will be logged locally only")
        
        return {"status": "Alert logged successfully", "data": alert_record}
        
    except Exception as e:
        import traceback
        print("❌ Error in /alerts:", str(e))
        traceback.print_exc()
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)