# src/feature_engineering.py

import pandas as pd
import sys
from pathlib import Path

from src.data_processing import load_and_clean_data
from src.config import (
    PROJECT_ROOT,
    ENGINEERED_DATA_PATH,
    ANALYSIS_DATE,
    COL_CUSTOMER_ID,
    COL_INVOICE_DATE,
    COL_INVOICE,
    CHURN_THRESHOLD_DAYS,
    TARGET_VARIABLE,  # 'CHURN'
    COL_COUNTRY
)


def create_customer_features() -> pd.DataFrame:
    """
    v1.0 - Derives customer-based features (RFM) from raw transaction data.

    1. Loads clean transaction data (from data_processing).
    2. Determines the analysis date (from 'config.py').
    3. Calculates Recency, Frequency, and Monetary for each customer.
    4. Defines the 'CHURN' target variable based on 'Recency'.

    return: Customer-based, ready-to-train DataFrame.
    """

    # 1. Load clean data
    df = load_and_clean_data()
    if df is None:
        print("ERROR: Could not load clean data. Stopping feature engineering.")
        sys.exit(1)

    print("Clean data loaded. RFM calculations starting...")

    # 2. Determine Analysis Date
    analysis_date = pd.to_datetime(ANALYSIS_DATE)

    # 3. Calculate RFM Properties
    rfm = df.groupby(COL_CUSTOMER_ID).agg(
        Recency=(COL_INVOICE_DATE, lambda x: (analysis_date - x.max()).days),
        Frequency=(COL_INVOICE, lambda x: x.nunique()),
        Monetary=('TotalPrice', lambda x: x.sum()),

        Country=(COL_COUNTRY, 'first')
    )

    # Zero spend or zero frequency is meaningless, clear them
    rfm = rfm[(rfm['Monetary'] > 0) & (rfm['Frequency'] > 0)]
    rfm.reset_index(inplace=True)

    print(f"RFM features {len(rfm)} are calculated for the customer.")

    # 4. Create Target Variable (CHURN)
    rfm[TARGET_VARIABLE] = rfm['Recency'].apply(
        lambda x: 1 if x > CHURN_THRESHOLD_DAYS else 0
    )

    print(f"The target variable 'CHURN' was created based on the {CHURN_THRESHOLD_DAYS} day threshold.")

    # We can discard the 'Customer ID' which is no longer necessary for analysis.
    rfm = rfm.drop(COL_CUSTOMER_ID, axis=1)

    return rfm


def save_customer_features(df: pd.DataFrame):
    """
    Saves the engineered customer specification table to the 'data/processed/' folder.
    """
    try:
        print(f"Saving processed data: {ENGINEERED_DATA_PATH}")
        ENGINEERED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Save DataFrame as CSV
        df.to_csv(ENGINEERED_DATA_PATH, index=False)
        print("Processed data was saved successfully.")

    except Exception as e:
        print(f"Error occurred while saving processed data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("--- Launching Feature Engineering Flow ---")
    features_df = create_customer_features()
    save_customer_features(features_df)

    print("\n--- Processed Data Summary (First 5 Rows) ---")
    print(features_df.head())
    print("\n--- Processed Data Information ---")
    print(features_df.info())
    print(f"\nProcessed data is saved to {ENGINEERED_DATA_PATH}.")
    print("--- Feature Engineering Flow Completed ---")