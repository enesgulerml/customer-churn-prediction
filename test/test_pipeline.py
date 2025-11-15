# test/test_pipeline.py

import pytest
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from src.pipeline import create_pipeline


def test_create_pipeline_returns_pipeline_object():
    """
    Test 1: Does our function return a 'Pipeline' object?
    """

    # Act
    pipeline = create_pipeline()

    # Assert
    assert isinstance(pipeline, Pipeline)


def test_create_pipeline_has_correct_steps():
    """
    Test 2 (Architecture): Does the pipeline have two main steps, 'preprocessor' and 'classifier'?
    """

    # Act
    pipeline = create_pipeline()

    # Assert
    assert "preprocessor" in pipeline.named_steps
    assert "classifier" in pipeline.named_steps


def test_create_pipeline_uses_xgboost_by_default():
    """
    Test 3 (Model): Our 'winning' model is XGBoost.
    Is the final step of the pipeline really 'XGBClassifier'?
    """

    # Act
    pipeline = create_pipeline()

    # Assert
    classifier_step = pipeline.named_steps['classifier']
    assert isinstance(classifier_step, XGBClassifier)