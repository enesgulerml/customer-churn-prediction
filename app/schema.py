# app/schema.py

from pydantic import BaseModel, Field
from typing import Optional


# === Architecture ===

# The data model that our API will receive FROM THE EXTERNAL (INPUT)
class ChurnInput(BaseModel):
    # From NUMERICAL_FEATURES in config.py
    Frequency: int = Field(..., description="Total number of unique invoices (F)")
    Monetary: float = Field(..., description="Total monetary value of purchases (M)")

    # From CATEGORICAL_FEATURES in config.py
    Country: str = Field(..., description="Customer's primary country")



# The response model that our API will give OUTPUT
class PredictionResponse(BaseModel):
    # From TARGET_VARIABLE in config.py
    CHURN: int = Field(..., description="Predicted churn status (1 for Churn, 0 for No Churn)")