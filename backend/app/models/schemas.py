"""
Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Report(BaseModel):
    """Flood report submission model"""
    latitude: float = Field(..., description="Latitude coordinate", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude coordinate", ge=-180, le=180)
    description: str = Field(..., description="Description of the flood condition", min_length=10)
    water_level: Optional[str] = Field(None, description="Water level (e.g., 'Ankle-deep', 'Knee-deep')")


class ReportResponse(BaseModel):
    """Response model for report submission"""
    message: str
    data: dict


class Alert(BaseModel):
    """Flood alert model"""
    location_name: str = Field(..., description="Name of the location")
    risk_level: str = Field(..., description="Risk level (Low, Medium, High)")
    recipient: str = Field(..., description="Alert recipient")


class RiskResponse(BaseModel):
    """Risk assessment response model"""
    risk_level: str = Field(..., description="Final risk assessment")
    source: str = Field(..., description="Assessment source")
    details: dict = Field(..., description="Detailed assessment information")


class WeatherData(BaseModel):
    """Weather data model"""
    city_name: str
    coordinates: dict
    current_weather: dict
    forecast_data: list
    fetched_at: datetime


class MapPoint(BaseModel):
    """Map point for dashboard"""
    id: str
    latitude: float
    longitude: float
    risk_level: str
    source: str
    details: str


class DashboardResponse(BaseModel):
    """Dashboard data response model"""
    map_points: list[MapPoint]
    charts_data: dict
