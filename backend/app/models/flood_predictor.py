"""
Flood risk predictor with optional ML model and heuristic fallback
"""

from __future__ import annotations

import os
import pickle
from typing import List, Optional

from config.settings import MODEL_PATH, SCALER_PATH, FEATURES_PATH, RISK_THRESHOLDS


class FloodPredictor:
    """Predict flood risk level from features.

    Tries to load pre-trained artifacts (scaler/model). If unavailable, falls back
    to a clear, explainable heuristic so the system remains functional.
    """

    def __init__(self) -> None:
        self.model: Optional[object] = None
        self.scaler: Optional[object] = None
        self.feature_names: Optional[List[str]] = None

        # Best-effort: load artifacts if present
        try:
            if MODEL_PATH and os.path.exists(MODEL_PATH):
                with open(MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
            if SCALER_PATH and os.path.exists(SCALER_PATH):
                with open(SCALER_PATH, "rb") as f:
                    self.scaler = pickle.load(f)
            if FEATURES_PATH and os.path.exists(FEATURES_PATH):
                with open(FEATURES_PATH, "rb") as f:
                    self.feature_names = pickle.load(f)
        except Exception as e:
            print(f"⚠️ ML artifact load failed, will use heuristic as needed: {e}")

    def predict(self, features: List[float]) -> str:
        """Return 'Low' | 'Medium' | 'High'."""
        try:
            vector = [features]
            if self.scaler is not None:
                try:
                    vector = self.scaler.transform(vector)
                except Exception as e:
                    print(f"⚠️ Scaling failed, continuing without scaler: {e}")

            if self.model is not None:
                try:
                    y = self.model.predict(vector)
                    pred = y[0]
                    # Common cases: numeric classes {0,1,2} or string labels
                    if isinstance(pred, (int, float)):
                        if pred >= 2:
                            return "High"
                        if pred >= 1:
                            return "Medium"
                        return "Low"
                    if isinstance(pred, str):
                        pred_upper = pred.capitalize()
                        if pred_upper in {"Low", "Medium", "High"}:
                            return pred_upper
                except Exception as e:
                    print(f"⚠️ Model prediction failed, using heuristic: {e}")

            return self._heuristic_predict(features)
        except Exception as e:
            print(f"⚠️ Prediction error, using heuristic: {e}")
            return self._heuristic_predict(features)

    def _heuristic_predict(self, features: List[float]) -> str:
        """Simple, transparent rules using provided features.

        Expected features: [temp_c, humidity_pct, rain_1h_mm, pressure_hpa, recent_reports]
        """
        # Defensive unpacking with defaults
        temp = features[0] if len(features) > 0 and features[0] is not None else 25.0
        humidity = features[1] if len(features) > 1 and features[1] is not None else 50.0
        rain_mm = features[2] if len(features) > 2 and features[2] is not None else 0.0
        pressure = features[3] if len(features) > 3 and features[3] is not None else 1013.0
        recent_reports = int(features[4]) if len(features) > 4 and features[4] is not None else 0

        heavy_rain_thresh = float(RISK_THRESHOLDS["WEATHER_THRESHOLDS"]["heavy_rain"])  # mm/h
        humidity_high_thresh = float(RISK_THRESHOLDS["WEATHER_THRESHOLDS"]["humidity_high"])  # %

        # High risk indicators
        if rain_mm >= heavy_rain_thresh * 2:
            return "High"
        if recent_reports >= 5:
            return "High"

        # Medium risk indicators
        if rain_mm >= heavy_rain_thresh:
            return "Medium"
        if humidity >= humidity_high_thresh:
            return "Medium"
        if recent_reports >= 2:
            return "Medium"

        return "Low"
