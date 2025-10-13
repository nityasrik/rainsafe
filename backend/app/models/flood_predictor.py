"""
Flood predictor wrapper with lazy loading and robust fallbacks.
"""

from __future__ import annotations

import os
import pickle
from typing import List

import numpy as np

from config.settings import MODEL_PATH, SCALER_PATH


class FloodPredictor:
    def __init__(self) -> None:
        self._model = None
        self._scaler = None
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """
        Load model and scaler from disk if available. Fall back to dummy behavior.
        """
        try:
            if os.path.exists(SCALER_PATH):
                with open(SCALER_PATH, "rb") as f:
                    self._scaler = pickle.load(f)
            if os.path.exists(MODEL_PATH):
                with open(MODEL_PATH, "rb") as f:
                    self._model = pickle.load(f)
            if self._model is not None:
                print("--- FloodPredictor: loaded model artifacts ---")
            else:
                print("--- FloodPredictor: model file missing; using dummy predictions ---")
        except Exception as e:
            # On any load failure, null out artifacts and continue in dummy mode
            print(f"⚠️ FloodPredictor: failed to load artifacts: {e}. Using dummy.")
            self._model = None
            self._scaler = None

    def predict(self, features: List[List[float]]) -> List[str]:
        """
        Predict risk labels for a list of feature vectors.
        Returns labels among {"Low", "Medium", "High"}.
        """
        if not isinstance(features, list) or (features and not isinstance(features[0], (list, tuple, np.ndarray))):
            raise ValueError("features must be a list of feature vectors")

        if self._scaler is not None:
            try:
                features = self._scaler.transform(features)
            except Exception as e:
                print(f"⚠️ FloodPredictor: scaler.transform failed: {e}. Proceeding without scaling.")

        if self._model is None:
            # Dummy heuristic: if rainfall or reports high → bump risk
            preds = []
            for vec in features:
                try:
                    # expected order: [temp, humidity, rain_1h_mm, pressure, reports_in_vicinity, rainfall_next_3_hours]
                    rain = float(vec[2]) if len(vec) > 2 else 0.0
                    reports = float(vec[4]) if len(vec) > 4 else 0.0
                    next3h = float(vec[5]) if len(vec) > 5 else 0.0
                    score = rain + 0.5 * reports + 0.5 * next3h
                    if score >= 8:
                        preds.append("High")
                    elif score >= 2:
                        preds.append("Medium")
                    else:
                        preds.append("Low")
                except Exception:
                    preds.append("Low")
            return preds

        try:
            raw = self._model.predict(features)
            # Normalize to canonical labels
            normalized = []
            for r in raw:
                if isinstance(r, bytes):
                    r = r.decode("utf-8", errors="ignore")
                label = str(r)
                if label.lower().startswith("h"):
                    normalized.append("High")
                elif label.lower().startswith("m"):
                    normalized.append("Medium")
                elif label.lower().startswith("l"):
                    normalized.append("Low")
                else:
                    normalized.append("Low")
            return normalized
        except Exception as e:
            print(f"⚠️ FloodPredictor: model.predict failed: {e}. Falling back to dummy.")
            return ["Low"] * len(features)