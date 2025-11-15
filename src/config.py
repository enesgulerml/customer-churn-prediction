# src/config.py

from pathlib import Path

# === 1. File Paths (Dynamic and Absolute) ===

SRC_ROOT = Path(__file__).parent

PROJECT_ROOT = SRC_ROOT.parent

# --- Raw Bus ---
RAW_DATA_FILE_NAME = "online_retail_II.xlsx"
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / RAW_DATA_FILE_NAME

# --- Post-Engineering Data Path ---
ENGINEERED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "customer_features.csv"

# --- Model Output Path ---
MODEL_OUTPUT_PATH = PROJECT_ROOT / "models" / "churn_model.joblib"

# --- Prediction Output Path ---
SUBMISSION_PATH = PROJECT_ROOT / "reports" / "churn_predictions.csv"


# === 2. Dataset Columns ===
COL_CUSTOMER_ID = "Customer ID"
COL_INVOICE_DATE = "InvoiceDate"
COL_INVOICE = "Invoice"
COL_QUANTITY = "Quantity"
COL_PRICE = "Price"
COL_COUNTRY = "Country"


# === 3. Feature Engineering Settings ===
ANALYSIS_DATE = "2011-12-10"

# Settings for RFM Analysis (Recency, Frequency, Monetary)
RFM_F_BINS = [0, 1, 2, 5, 10, 1000] # Frequency
RFM_M_BINS = [0, 100, 500, 1000, 2000, 100000] # Monetary

# CHURN DEFINITION: If X days have passed since your last purchase
CHURN_THRESHOLD_DAYS = 60


# === 4. Model and Pipeline Settings ===

# TARGET VARIABLE
TARGET_VARIABLE = "CHURN"


NUMERICAL_FEATURES = ["Frequency", "Monetary"]
CATEGORICAL_FEATURES = ["Country"]


# === 5. Other Settings ===
TEST_SIZE = 0.2
RANDOM_STATE = 42

# MLFlow (v2.0)
MLFLOW_EXPERIMENT_NAME = "Customer Churn Prediction"

# === 6. Model Hyperparameters ===

XGB_PARAMS = {
    'objective': 'binary:logistic',
    'eval_metric': 'logloss',
    'n_estimators': 150,
    'max_depth': 4,
    'learning_rate': 0.1,
    'colsample_bytree': 0.7,
    'subsample': 0.7,
    'scale_pos_weight': 1,
    'random_state': RANDOM_STATE
}