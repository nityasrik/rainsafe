from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any  # Added Dict, Any for charts_data
from datetime import datetime
from enum import Enum


# --- Enums for consistency and validation ---


class WaterLevel(str, Enum):
    """Enum for water level options."""

    ANKLE_DEEP = "Ankle-deep"
    KNEE_DEEP = "Knee-deep"
    WAIST_DEEP = "Waist-deep"
    CHEST_DEEP = "Chest-deep"
    ABOVE_HEAD = "Above head"


class RiskLevel(str, Enum):
    """Enum for risk level options."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    UNKNOWN = "Unknown"


class AssessmentSource(str, Enum):
    """Enum for risk assessment sources."""

    USER_REPORT = "user-report"
    HYBRID_HISTORICAL = "hybrid-historical"
    ML_PREDICTION = "ml-prediction"
    ERROR = "error"


# --- Report Models ---


class ReportBase(BaseModel):
    """Base model for a flood report, containing common fields."""

    latitude: float = Field(..., description="Latitude coordinate", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude coordinate", ge=-180, le=180)
    description: str = Field(
        ...,
        description="Description of the flood condition",
        min_length=10,
        max_length=500,
    )
    water_level: Optional[WaterLevel] = Field(None, description="Estimated water level")


class ReportCreate(ReportBase):
    """Model for creating a new flood report."""

    pass


class Report(ReportBase):
    """Full report model, including database fields."""

    id: str = Field(..., alias="_id")
    created_at: datetime = Field(..., description="Timestamp of when the report was created")
    # Added nlp_analysis as it's part of your report creation flow
    nlp_analysis: Dict[str, Any] = Field({}, description="NLP analysis results of the description")

    class Config:
        orm_mode = True  # This is usually for ORM integration, keep if intended
        allow_population_by_field_name = True


class ReportResponse(BaseModel):
    """Response model for report submission."""

    message: str
    data: Report


# --- Alert Models ---


class Alert(BaseModel):
    """Flood alert model."""

    location_name: str = Field(..., description="Name of the location")
    risk_level: RiskLevel = Field(..., description="Risk level")
    recipient: EmailStr = Field(..., description="Alert recipient's email address")
    # Add optional fields for when receiving from DB/API response
    id: Optional[str] = Field(None, alias="_id", description="Unique identifier for the alert")
    sent_at: Optional[datetime] = Field(None, description="Timestamp when the alert was sent")


# --- Risk Assessment Models ---


class RiskAssessmentDetails(BaseModel):
    """Detailed breakdown of the risk assessment."""

    threshold_assessment: RiskLevel
    ml_assessment: RiskLevel
    user_reports_found: int
    weather_data_found: bool
    contributing_factors: List[str] = Field(
        ..., description="List of factors contributing to the risk assessment"
    )  # Changed from 'trigger'
    recommendation: str = Field(..., description="Recommendation based on the final risk level")
    error: Optional[str] = None


class RiskResponse(BaseModel):
    """Risk assessment response model."""

    risk_level: RiskLevel = Field(..., description="Final risk assessment")
    source: AssessmentSource = Field(..., description="Assessment source")
    details: RiskAssessmentDetails = Field(..., description="Detailed assessment information")


# --- Weather Data Models ---


class Coordinates(BaseModel):
    """Model for geographic coordinates."""

    type: str = "Point"
    coordinates: List[float]


class CurrentWeather(BaseModel):
    """Model for current weather conditions."""

    temp: float
    humidity: int
    weather_condition: str
    rain_1h_mm: float
    pressure: int
    wind_speed: float


class WeatherData(BaseModel):
    """Weather data model for a city."""

    city_name: str
    coordinates: Coordinates
    current_weather: CurrentWeather
    forecast_data: List[dict]  # Keeping forecast_data as a list of dicts for now
    fetched_at: datetime


# --- Dashboard Models ---


class MapPoint(BaseModel):
    """Map point for the dashboard."""

    id: str
    latitude: float
    longitude: float
    risk_level: RiskLevel
    source: AssessmentSource
    details: str


class DashboardResponse(BaseModel):
    """Dashboard data response model."""

    map_points: List[MapPoint]
    charts_data: Dict[str, Any]  # Changed from dict to Dict[str, Any]
