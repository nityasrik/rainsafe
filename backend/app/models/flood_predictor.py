# app/models/flood_predictor.py
import pickle
import pandas as pd
from typing import List, Dict, Any

class FloodPredictor:
    def __init__(self, model_path='data/ml_artifacts/model.pkl', scaler_path='data/ml_artifacts/scaler.pkl', features_path='data/ml_artifacts/model_features.pkl'):
        """
        Loads the trained model, scaler, and feature list from disk.
        """
        print("--- Initializing FloodPredictor ---")
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
                
            with open(features_path, 'rb') as f:
                self.feature_names = pickle.load(f)
            
            print("✅ Model, scaler, and features loaded successfully.")
            # The model predicts 0 (No Flood) or 1 (Flood)
            self.risk_map = {0: "Low", 1: "High"}
        except FileNotFoundError as e:
            print(f"❌ ERROR: Could not load model artifacts. File not found: {e}")
            self.model = None
            self.scaler = None
            self.feature_names = []
        except Exception as e:
            print(f"❌ ERROR: An unexpected error occurred while loading model artifacts: {e}")
            self.model = None
            self.scaler = None
            self.feature_names = []


    def predict(self, features: List[Dict[str, Any]]) -> List[str]:
        """
        Takes a list of feature dictionaries, prepares them, scales them, 
        and returns a list of risk predictions.
        """
        if not self.model or not self.scaler:
            print("⚠️ Prediction skipped: Model or scaler not loaded.")
            return ["Unknown"] * len(features)

        # Create a DataFrame from the incoming live data
        live_df = pd.DataFrame(features)
        
        # One-hot encode any categorical features
        live_df = pd.get_dummies(live_df)
        
        # Reindex to match the columns the model was trained on.
        # This adds any missing one-hot encoded columns (and fills them with 0) 
        # and ensures the column order is identical to the training data.
        live_df_reindexed = live_df.reindex(columns=self.feature_names, fill_value=0)
        
        # Scale the live data using the loaded scaler
        live_df_scaled = self.scaler.transform(live_df_reindexed)
        
        # Make a prediction
        prediction_results = self.model.predict(live_df_scaled)
        
        # Return the human-readable risk levels
        return [self.risk_map.get(pred, "Unknown") for pred in prediction_results]