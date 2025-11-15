# src/data_processing.py

import pandas as pd
import sys

# We import from our 'config.py' file (from our control panel)
from src.config import (
    RAW_DATA_PATH,
    COL_CUSTOMER_ID,
    COL_INVOICE_DATE,
    COL_QUANTITY,
    COL_PRICE
)


def load_and_clean_data() -> pd.DataFrame:
    """
    v1.0 - Loads raw Excel data and performs initial basic cleaning.

    This function runs BEFORE the 'feature_engineering' phase.
    Its primary purpose is:
    1. Read the raw Excel data.
    2. Discard rows with no 'Customer ID' (NaN) (we cannot group them).
    3. Discard returns (negative Quantity) and zero-priced data (analysis noise).

    return: Cleaned DataFrame ready for 'feature_engineering'
    """
    print(f"Loading data: {RAW_DATA_PATH}")
    try:
        excel_data = pd.read_excel(RAW_DATA_PATH, sheet_name=None)

        df = pd.concat(excel_data.values(), ignore_index=True)

        print(f"{len(excel_data)} sheets in Excel have been successfully merged and uploaded.")

    except FileNotFoundError:
        print(f"ERROR: Raw data file not found: {RAW_DATA_PATH}")
        print("Please make sure to copy the raw data file to the 'data/raw/' folder.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        sys.exit(1)

    # === Cleanup Step 1: 'Customer ID' Missing Data ===
    initial_rows = len(df)
    df.dropna(subset=[COL_CUSTOMER_ID], inplace=True)
    cleaned_rows = len(df)
    print(f"{initial_rows - cleaned_rows} rows without 'Customer ID' were discarded.")

    # Convert 'Customer ID' from float (e.g. 13085.0) to integer (e.g. 13085)
    df[COL_CUSTOMER_ID] = df[COL_CUSTOMER_ID].astype(int)

    # === Cleaning Step 2: Noise Cleaning ===

    # Discard Returns (eg: Quantity < 0)
    df = df[df[COL_QUANTITY] > 0]

    # Throw away those with a price of 0
    df = df[df[COL_PRICE] > 0]

    print("Returns (Negative Quantity) and 0 Price lines were discarded.")

    # === Cleaning Step 3: Total Price Column ===
    # Calculate the 'Monetary' value which is critical for feature engineering
    df['TotalPrice'] = df[COL_QUANTITY] * df[COL_PRICE]

    print("Basic cleanup completed. 'TotalPrice' column created.")

    return df


if __name__ == "__main__":
    df = load_and_clean_data()
    print("\nCleaned Data Summary:")
    print(df.info())
    print("\nCleaned Data First 5 Rows:")
    print(df.head())
    print(f"\nA total of {len(df)} cleared transaction rows remain.")