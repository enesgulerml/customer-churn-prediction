# src/pipeline.py

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from src.config import (
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    RANDOM_STATE,
    XGB_PARAMS
)


def create_pipeline() -> Pipeline:
    """
    Creates the scikit-learn pipeline, which includes all data processing and modeling steps, for customer data created with 'feature_engineering'.

    return: Training-ready scikit-learn Pipeline object
    """

    # === 1. Sub-Pipeline for Numerical Properties ===
    # (recency, frequency, monetary_value...)
    # Step 1: Fill missing values with median (if any)
    # Step 2: Standardize the data (StandardScaler)
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    # === 2. Sub-Pipeline for Categorical Features ===
    # (country...)
    # Step 1: Fill missing values with the most frequent value (mode)
    # Step 2: Convert columns to vectors with One-Hot Encoding
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    # === 3. ColumnTransformer ===
    # Manages which pipeline will be applied to which column.
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, NUMERICAL_FEATURES),
            ('cat', categorical_transformer, CATEGORICAL_FEATURES)
        ],
        remainder='drop'
    )

    # === 4. Main Pipeline (Big Picture) ===
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', XGBClassifier(**XGB_PARAMS))
    ])

    print("Successfully created scikit-learn pipeline (for Churn Model).")
    return model_pipeline