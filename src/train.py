# src/train.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from joblib import dump
import sys
import datetime
import mlflow
import mlflow.sklearn
import warnings
from warnings import filterwarnings
filterwarnings('ignore')

from src.config import (
    MODEL_OUTPUT_PATH,
    ENGINEERED_DATA_PATH,
    TEST_SIZE,
    RANDOM_STATE,
    TARGET_VARIABLE,
    MLFLOW_EXPERIMENT_NAME,
    CHURN_THRESHOLD_DAYS,
    XGB_PARAMS
)
from src.feature_engineering import create_customer_features, save_customer_features
from src.pipeline import create_pipeline


def run_training():
    """
    v2.0 - Manages the main training and feature engineering flow.

    1. Runs the feature engineering (and saves 'customer_features.csv').
    2. Reads the processed data.
    3. Splits the data into train/test.
    4. Trains the pipeline (model).
    5. Records the entire process in MLFlow.
    """
    print("===== Starting the Training Process (v2.0 - with MLFlow) =====")

    # === Start the MLFlow Experiment ===
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_name = f"run_churn_{current_time}"

    with mlflow.start_run(run_name=run_name):

        # --- MLFlow Registration Step 1: Parameters ---
        print("Saving parameters to MLFlow...")
        mlflow.log_param("test_size", TEST_SIZE)
        mlflow.log_param("random_state", RANDOM_STATE)
        mlflow.log_param("churn_threshold_days", CHURN_THRESHOLD_DAYS)
        print("Saving XGBoost hyperparameters to MLFlow...")
        mlflow.log_params(XGB_PARAMS)

        # --- Steps 1 & 2: Feature Engineering (Heart of the Project) ---
        print("Feature engineering (RFM + Churn) begins...")
        try:
            # Calculates the RFM and creates the CHURN.
            features_df = create_customer_features()

            save_customer_features(features_df)

            print(f"Feature engineering completed. Processed data saved: {ENGINEERED_DATA_PATH}")
        except Exception as e:
            print(f"ERROR: Feature engineering step failed: {e}")
            sys.exit(1)

        # --- Steps 3 & 4: Separating Data ---
        FEATURES_TO_DROP = [TARGET_VARIABLE, "Recency"]

        X = features_df.drop(columns=FEATURES_TO_DROP)
        y = features_df[TARGET_VARIABLE]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=y
        )
        print(f"Data was split into training and test sets. (Stratified)")
        print(f"Leakage prevented: 'Recency' column was manually omitted.")

        # --- Step 5: Create the Pipeline ---
        pipeline = create_pipeline()

        # --- Step 6: Train the Pipeline ---
        print("Pipeline training (fit) begins...")
        pipeline.fit(X_train, y_train)
        print("Pipeline training has been completed.")

        # --- Step 7: Calculate Metrics (F1-Score instead of Accuracy) ---
        preds = pipeline.predict(X_test)
        f1 = f1_score(y_test, preds)
        print(f"F1 Score of the model on the test data: {f1:.4f}")

        # --- MLFlow Recording Step 2: Metrics ---
        print("Saving metrics to MLFlow...")
        mlflow.log_metric("f1_score", f1)

        # --- Step 8: Save Model (Local + MLFlow) ---

        MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        dump(pipeline, MODEL_OUTPUT_PATH)
        print(f"The trained model (pipeline) is saved to: {MODEL_OUTPUT_PATH}")

        # MLFlow Registration
        print("Saving model (artifact) to MLFlow...")
        mlflow.sklearn.log_model(
            sk_model=pipeline,
            artifact_path="model_churn",
            input_example=X_train.head()
        )

        print("===== Training Process Completed (MLFlow) =====")


if __name__ == "__main__":
    run_training()