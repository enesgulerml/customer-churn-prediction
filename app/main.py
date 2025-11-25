# app/main.py

import joblib
import pandas as pd
from fastapi import FastAPI
from app.schema import ChurnInput, PredictionResponse
import sys

from src.config import MODEL_OUTPUT_PATH

# --- Installing the Application and Model ---
app = FastAPI(
    title="Customer Churn Prediction API",
)


@app.on_event("startup")
def load_model():
    """
    When starting the API, v2.1 (XGBoost @ 0.7710) loads from the special 'models/' sections and assigns them to 'app.state.model'.
    """
    print("API is starting and loading v2.1 Churn model...")
    try:
        app.state.model = joblib.load(MODEL_OUTPUT_PATH)
        print(f"Model successfully loaded from {MODEL_OUTPUT_PATH}.")
    except FileNotFoundError:
        print(f"ERROR: Model not found at {MODEL_OUTPUT_PATH}.")
        print("Please make sure to run 'python -m src.train' before running the API.")
        app.state.model = None
    except Exception as e:
        print(f"A critical error occurred while loading the model: {e}")
        app.state.model = None
        sys.exit(1)


# --- API Endpoints ---

@app.get("/", tags=["Health Check"])
def read_root():
    """The root endpoint checks whether the API is running."""
    if app.state.model is None:
        return {"status": "error", "message": "Model could not be loaded!"}
    return {"status": "ok", "message": "Churn Prediction API is running!"}


@app.post("/predict",
          response_model=PredictionResponse,
          tags=["Prediction"])
def predict_churn(churn_input: ChurnInput):
    """
    It takes the 'engineered' attributes (F, M, Country) and predicts the 'CHURN' status (1 or 0).
    Thanks to Pydantic (ChurnInput schema), the incoming data is guaranteed to be in the correct format.
    """
    if app.state.model is None:
        return {"error": "Model is not loaded."}

    # 1. Convert Pydantic model (ChurnInput) to a DataFrame
    input_data = pd.DataFrame([churn_input.model_dump()])

    # 2. Predict
    prediction = app.state.model.predict(input_data)[0]

    # 3. The result is based on the Pydantic response model (PredictionResponse)
    return {"CHURN": prediction}