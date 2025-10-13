"""
RainSafe Backend - Main Application (with Dependency Injection)
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from typing import List, Optional

import motor.motor_asyncio
from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# --- Import our services and schemas ---
from app.services.risk_service import RiskAssessmentService
from app.models.schemas import (
    ReportCreate, ReportResponse, RiskResponse, Alert, DashboardResponse,
    Report, MapPoint, RiskLevel, AssessmentSource,
    RiskAssessmentDetails, WaterLevel
)
from app.models.flood_predictor import FloodPredictor
from config.settings import RISK_THRESHOLDS
from app.utils.database import db

# Load environment variables
load_dotenv()

# --- Dependency Injection Setup ---
def get_risk_service() -> RiskAssessmentService:
    """
    Dependency provider for the RiskAssessmentService.
    FastAPI will call this function for endpoints that need the service.
    """
    return RiskAssessmentService(database=db)

# --- Lifespan function for startup and shutdown ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan for startup and shutdown events."""
    print("🚀 Starting RainSafe API...")

    if not await db.connect():
        raise RuntimeError("Failed to connect to MongoDB during startup.")

    try:
        app.state.predictor = FloodPredictor()  # <-- Enable the real ML model here!
        print("✅ Flood predictor (ML) model loaded successfully.")
    except Exception as e:
        print(f"⚠️ ML predictor initialization failed: {e}. Running without ML predictions.")
        app.state.predictor = None

    yield

    print("🛑 Shutting down RainSafe API...")
    await db.disconnect()

# Initialize FastAPI with the lifespan manager
app = FastAPI(
    title="RainSafe API",
    version="1.2.0",
    description="A scalable and testable API for flood risk assessment.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints (Now using Dependency Injection) ---
@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"status": "RainSafe API is running!"}

@app.post("/report", response_model=ReportResponse, status_code=201)
async def create_report(
    report: ReportCreate,
    risk_service: RiskAssessmentService = Depends(get_risk_service)
):
    """Submit a new flood report with non-blocking NLP analysis."""
    try:
        report_data = report.model_dump()
        report_data["created_at"] = datetime.now(timezone.utc)

        nlp_analysis = await risk_service.analyze_description_with_nlp(report.description)
        report_data["nlp_analysis"] = nlp_analysis

        reports_collection = db.get_collection("reports")
        new_report_result = await reports_collection.insert_one(report_data)

        created_report_doc = await reports_collection.find_one({"_id": new_report_result.inserted_id})
        if not created_report_doc:
            raise HTTPException(status_code=500, detail="Failed to retrieve newly created report.")

        created_report_doc["_id"] = str(created_report_doc["_id"])

        return ReportResponse(message="Report received and analyzed successfully!", data=Report(**created_report_doc))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating report: {str(e)}")

@app.get("/risk", response_model=RiskResponse)
async def get_risk(
    lat: float,
    lon: float,
    request: Request,
    risk_service: RiskAssessmentService = Depends(get_risk_service)
):
    """Get a user-friendly, hybrid flood risk assessment for a location."""
    try:
        threshold_result = await risk_service.check_thresholds(lat, lon)
        ml_features_data = await risk_service.gather_features_for_prediction(lat, lon)

        ml_risk_level = RiskLevel.UNKNOWN
        # --- ML integration: Convert predictor output string to enum (LOW/HIGH/UNKNOWN) ---
        if request.app.state.predictor:
            raw_prediction = request.app.state.predictor.predict([ml_features_data["features"]])[0]
            if raw_prediction == "High":
                ml_risk_level = RiskLevel.HIGH
            elif raw_prediction == "Low":
                ml_risk_level = RiskLevel.LOW
            else:
                ml_risk_level = RiskLevel.UNKNOWN
        else:
            print("INFO: ML predictor is disabled or failed to load. ml_assessment will be 'Unknown'.")

        final_risk = RiskLevel.LOW
        if threshold_result["risk"] == RiskLevel.HIGH.value or ml_risk_level == RiskLevel.HIGH:
            final_risk = RiskLevel.HIGH
        elif threshold_result["risk"] == RiskLevel.MEDIUM.value or ml_risk_level == RiskLevel.MEDIUM:
            final_risk = RiskLevel.MEDIUM
        else:
            final_risk = RiskLevel.LOW

        recommendations = {
            RiskLevel.LOW: "Conditions appear safe. Remain aware of weather changes.",
            RiskLevel.MEDIUM: "Potential for localized flooding. Exercise caution.",
            RiskLevel.HIGH: "High flood risk detected. Avoid travel in this area.",
            RiskLevel.UNKNOWN: "Could not determine risk. Please check conditions manually."
        }

        contributing_factors = []
        if "trigger" in threshold_result["details"]:
            contributing_factors.append(threshold_result["details"]["trigger"])

        if request.app.state.predictor and ml_risk_level != RiskLevel.UNKNOWN:
            contributing_factors.append(f"ML assessment: {ml_risk_level.value}")
        elif ml_features_data["weather_data_found"] and not request.app.state.predictor:
            contributing_factors.append("Recent weather data available (ML model disabled)")

        if not contributing_factors:
            contributing_factors.append("No specific factors identified.")

        return RiskResponse(
            risk_level=final_risk,
            source=AssessmentSource.HYBRID_HISTORICAL,
            details=RiskAssessmentDetails(
                threshold_assessment=RiskLevel(threshold_result["risk"]),
                ml_assessment=ml_risk_level,
                user_reports_found=threshold_result["details"].get("user_reports_found", 0),
                weather_data_found=ml_features_data["weather_data_found"],
                contributing_factors=contributing_factors,
                recommendation=recommendations.get(final_risk, recommendations[RiskLevel.UNKNOWN]),
                error=threshold_result["details"].get("error")
            ),
        )
    except Exception as e:
        return RiskResponse(
            risk_level=RiskLevel.UNKNOWN,
            source=AssessmentSource.ERROR,
            details=RiskAssessmentDetails(
                threshold_assessment=RiskLevel.UNKNOWN,
                ml_assessment=RiskLevel.UNKNOWN,
                user_reports_found=0,
                weather_data_found=False,
                contributing_factors=["An unexpected error occurred"],
                recommendation="Please try again later.",
                error=f"Error getting risk assessment: {str(e)}"
            )
        )

@app.get("/dashboard-data", response_model=DashboardResponse)
async def get_dashboard_data(
    risk_service: RiskAssessmentService = Depends(get_risk_service),
    start_time: Optional[datetime] = Query(None, description="Start date/time for filtering reports (ISO format)"),
    end_time: Optional[datetime] = Query(None, description="End date/time for filtering reports (ISO format)")
):
    """Get dashboard data for frontend."""
    try:
        reports_collection = db.get_collection("reports")

        query = {}
        if not start_time and not end_time:
            start_time = datetime.now(timezone.utc) - timedelta(hours=48)
            end_time = datetime.now(timezone.utc)
        elif not end_time:
            end_time = datetime.now(timezone.utc)
        elif not start_time:
            start_time = end_time - timedelta(hours=48)

        if start_time:
            query["created_at"] = {"$gte": start_time}
        if end_time:
            if "created_at" in query:
                query["created_at"]["$lte"] = end_time
            else:
                query["created_at"] = {"$lte": end_time}

        recent_reports_docs = await reports_collection.find(query).sort("created_at", -1).limit(50).to_list(length=50)

        map_points: List[MapPoint] = []
        for report_doc in recent_reports_docs:
            report_id = str(report_doc.get("_id"))

            water_level_str = report_doc.get("water_level")
            report_risk_level = RiskLevel.LOW
            if water_level_str:
                try:
                    water_level_enum = WaterLevel(water_level_str)
                    if water_level_enum in [WaterLevel.KNEE_DEEP, WaterLevel.WAIST_DEEP, WaterLevel.CHEST_DEEP, WaterLevel.ABOVE_HEAD]:
                        report_risk_level = RiskLevel.HIGH
                    elif water_level_enum == WaterLevel.ANKLE_DEEP:
                        report_risk_level = RiskLevel.MEDIUM
                except ValueError:
                    print(f"Warning: Unknown water_level '{water_level_str}' in report {report_id}")

            map_points.append(
                MapPoint(
                    id=report_id,
                    latitude=report_doc["latitude"],
                    longitude=report_doc["longitude"],
                    risk_level=report_risk_level,
                    source=AssessmentSource.USER_REPORT,
                    details=report_doc["description"]
                )
            )

        return DashboardResponse(map_points=map_points, charts_data={})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dashboard data: {str(e)}")

@app.post("/alerts", response_model=Alert, status_code=200)
async def send_alert(
    alert_data: Alert,
    risk_service: RiskAssessmentService = Depends(get_risk_service)
):
    """Send a flood alert and log it."""
    try:
        alert_record = alert_data.model_dump()
        alert_record["sent_at"] = datetime.now(timezone.utc)

        alerts_collection = db.get_collection("alerts")
        result = await alerts_collection.insert_one(alert_record)

        alert_record["_id"] = str(result.inserted_id)

        return Alert(**alert_record)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send/log alert: {str(e)}")
