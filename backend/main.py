"""
RainSafe Backend - Main Application (with Dependency Injection)
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.models.flood_predictor import FloodPredictor
from app.models.schemas import (
    AssessmentSource,
    Report,
    ReportCreate,
    ReportResponse,
    RiskAssessmentDetails,
    RiskLevel,
    RiskResponse,
)
from app.services.risk_service import RiskAssessmentService
from app.utils.database import db

# Load environment variables
load_dotenv()


def get_risk_service() -> RiskAssessmentService:
    """Dependency provider for the RiskAssessmentService."""
    return RiskAssessmentService(database=db)


@asynccontextmanager
async def lifespan(fapi_app: FastAPI):
    """Manage application lifespan for startup and shutdown events."""
    print("🚀 Starting RainSafe API...")

    if not await db.connect():
        raise RuntimeError("Failed to connect to MongoDB during startup.")

    try:
        fapi_app.state.predictor = FloodPredictor()
        print("✅ Flood predictor (ML) model loaded successfully.")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(
            f"⚠️ ML predictor initialization failed: {exc}. "
            "Running without ML predictions."
        )
        fapi_app.state.predictor = None

    yield

    print("🛑 Shutting down RainSafe API...")
    await db.disconnect()


app = FastAPI(
    title="RainSafe API",
    version="1.2.0",
    description="A scalable and testable API for flood risk assessment.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"status": "RainSafe API is running!"}


@app.post("/report", response_model=ReportResponse, status_code=201)
async def create_report(
    report: ReportCreate,
    risk_service: RiskAssessmentService = Depends(get_risk_service),
):
    """Submit a new flood report with non-blocking NLP analysis."""
    try:
        report_data = report.model_dump()
        report_data["created_at"] = datetime.now(timezone.utc)

        nlp_analysis = await risk_service.analyze_description_with_nlp(
            report.description
        )
        report_data["nlp_analysis"] = nlp_analysis

        reports_collection = db.get_collection("reports")
        new_report_result = await reports_collection.insert_one(report_data)

        created_report_doc = await reports_collection.find_one(
            {"_id": new_report_result.inserted_id}
        )
        if not created_report_doc:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve newly created report.",
            )

        created_report_doc["_id"] = str(created_report_doc["_id"])

        return ReportResponse(
            message="Report received and analyzed successfully!",
            data=Report(**created_report_doc),
        )

    except Exception as exc:  # pylint: disable=broad-exception-caught
        raise HTTPException(
            status_code=500, detail=f"Error creating report: {str(exc)}"
        ) from exc


@app.get("/risk", response_model=RiskResponse)
async def get_risk(
    lat: float,
    lon: float,
    request: Request,
    risk_service: RiskAssessmentService = Depends(get_risk_service),
):
    """Get a user-friendly, hybrid flood risk assessment for a location."""
    try:
        threshold_result = await risk_service.check_thresholds(lat, lon)
        ml_features_data = await risk_service.gather_features_for_prediction(lat, lon)

        ml_risk_level = RiskLevel.UNKNOWN
        if request.app.state.predictor:
            raw_prediction = request.app.state.predictor.predict(
                [ml_features_data["features"]]
            )[0]
            if raw_prediction == "High":
                ml_risk_level = RiskLevel.HIGH
            elif raw_prediction == "Low":
                ml_risk_level = RiskLevel.LOW
            else:
                ml_risk_level = RiskLevel.UNKNOWN
        else:
            print(
                "INFO: ML predictor is disabled or failed to load. "
                "ml_assessment will be 'Unknown'."
            )

        final_risk = RiskLevel.LOW
        if (
            threshold_result["risk"] == RiskLevel.HIGH.value
            or ml_risk_level == RiskLevel.HIGH
        ):
            final_risk = RiskLevel.HIGH
        elif (
            threshold_result["risk"] == RiskLevel.MEDIUM.value
            or ml_risk_level == RiskLevel.MEDIUM
        ):
            final_risk = RiskLevel.MEDIUM
        else:
            final_risk = RiskLevel.LOW

        recommendations = {
            RiskLevel.LOW: ("Conditions appear safe. Remain aware of weather changes."),
            RiskLevel.MEDIUM: ("Potential for localized flooding. Exercise caution."),
            RiskLevel.HIGH: ("High flood risk detected. Avoid travel in this area."),
            RiskLevel.UNKNOWN: (
                "Could not determine risk. Please check conditions manually."
            ),
        }

        contributing_factors = []
        if "trigger" in threshold_result["details"]:
            contributing_factors.append(threshold_result["details"]["trigger"])

        if request.app.state.predictor and ml_risk_level != RiskLevel.UNKNOWN:
            contributing_factors.append(f"ML assessment: {ml_risk_level.value}")
        elif ml_features_data["weather_data_found"] and not request.app.state.predictor:
            contributing_factors.append(
                "Recent weather data available (ML model disabled)"
            )

        if not contributing_factors:
            contributing_factors.append("No specific factors identified.")

        return RiskResponse(
            risk_level=final_risk,
            source=AssessmentSource.HYBRID_HISTORICAL,
            details=RiskAssessmentDetails(
                threshold_assessment=RiskLevel(threshold_result["risk"]),
                ml_assessment=ml_risk_level,
                user_reports_found=threshold_result["details"].get(
                    "user_reports_found", 0
                ),
                weather_data_found=ml_features_data["weather_data_found"],
                contributing_factors=contributing_factors,
                recommendation=recommendations.get(
                    final_risk, recommendations[RiskLevel.UNKNOWN]
                ),
                error=threshold_result["details"].get("error"),
            ),
        )
    except Exception as exc:  # pylint: disable=broad-exception-caught
        raise HTTPException(
            status_code=500, detail=f"Error getting risk assessment: {str(exc)}"
        ) from exc
