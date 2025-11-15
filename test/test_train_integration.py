# test/test_train_integration.py

import pytest
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from pathlib import Path

# Import the core components to be tested
from src.feature_engineering import create_customer_features
from src.pipeline import create_pipeline
from src.config import (
    TEST_SIZE,
    RANDOM_STATE,
    TARGET_VARIABLE,
    ENGINEERED_DATA_PATH
)


# Mark this test as 'slow'
# This allows running only fast unit tests with 'pytest -m "not slow"'
@pytest.mark.slow
def test_full_training_integration_pipeline():
    """
    Test v5.2 (Integration Test):
    Validates the entire v1.0 (Engineering) and v2.1 (Training) pipeline.

    This test ensures that:
    1. 'create_customer_features()' runs successfully (incl. data_processing).
    2. 'create_pipeline()' (XGBoost) runs successfully.
    3. The two components integrate correctly during 'pipeline.fit()'.
    4. The data leakage (`Recency` column) is correctly handled.
    5. The resulting F1 score meets the minimum performance threshold.

    Note: This test requires the raw data file (e.g., 'online_retail_II.xlsx')
    to be present in the 'data/raw/' directory.
    """

    # --- 1. Arrange ---
    # Attempt to run the full feature engineering pipeline.
    try:
        features_df = create_customer_features()
    except FileNotFoundError:
        pytest.fail(
            "Integration Test Failed: Raw data file (Excel) not found in 'data/raw/'. "
            "This test requires the raw data to run."
        )
    except Exception as e:
        pytest.fail(f"Integration Test Failed: 'create_customer_features' "
                    f"raised an exception: {e}")

    # --- 2. Act ---
    # Replicate the core logic from 'src/train.py'

    # Define features to drop (explicitly handling leakage)
    FEATURES_TO_DROP = [TARGET_VARIABLE, "Recency"]

    # Validate that expected columns exist before dropping
    assert "Recency" in features_df.columns, "Feature 'Recency' not found."
    assert TARGET_VARIABLE in features_df.columns, "Target 'CHURN' not found."

    X = features_df.drop(columns=FEATURES_TO_DROP)
    y = features_df[TARGET_VARIABLE]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y
    )

    pipeline = create_pipeline()
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    f1 = f1_score(y_test, preds)

    # --- 3. Assert ---
    # Verify the integrity and performance of the integrated pipeline

    print(f"\nIntegration Test F1 Score: {f1}")

    # Assertion 1: Check for Data Leakage
    assert f1 != 1.0000, "F1 Score is 1.0000! Data leakage is present."

    # Assertion 2: Check for complete model failure (worse than baseline)
    # Assumes a 50/50 baseline F1 of 0.50
    assert f1 > 0.50, (f"F1 Score ({f1}) is below the 0.50 baseline. "
                       f"The model is performing worse than random guessing.")

    # Assertion 3: Check for performance regression
    # This is a specific threshold based on our v2.1 (XGBoost) model.
    # If we improve the model, this threshold should be increased.
    expected_f1_threshold = 0.75
    assert f1 > expected_f1_threshold, (
        f"F1 Score ({f1:.4f}) is below the expected threshold of "
        f"{expected_f1_threshold}. A model regression may have occurred."
    )