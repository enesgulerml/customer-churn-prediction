# test/test_api_e2e.py

import pytest
import requests
import subprocess
import time
import os
from pathlib import Path

# === Test Configuration ===
# This test requires Docker to be running and the 'churn-api:v3' image
# to be built locally before running pytest.

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Define constants for our test service
IMAGE_NAME = "churn-api:latest"
CONTAINER_NAME = "test_churn_api_service"
API_URL = "http://127.0.0.1:8000"
HEALTH_CHECK_URL = f"{API_URL}/"
PREDICT_URL = f"{API_URL}/predict"
MODEL_PATH = PROJECT_ROOT / "models"


@pytest.fixture(scope="module")
def api_service():
    """
    pytest Fixture: Manages the lifecycle of the v3.0 API container.

    This fixture will:
    1. (Setup) Start the 'churn-api:v3' Docker container.
    2. Wait 10 seconds for the Uvicorn server to boot.
    3. Run a health check to ensure the API is live.
    4. 'yield' control back to the test function.
    5. (Teardown) Stop and remove the container after tests are done.
    """

    # --- Setup ---
    print("\n[Setup] Starting v3.0 API Docker container...")

    # Get the absolute path for the volume mount
    # ${pwd} in PowerShell is not reliable inside pytest/Python
    model_volume_mount = f"{PROJECT_ROOT.resolve()}/models:/app/models"

    start_command = [
        "docker", "run",
        "-d",  # Detached mode
        "--rm",  # Automatically remove on stop
        "--name", CONTAINER_NAME,  # Name the container for easy stop
        "-p", "8000:80",  # Map port 8000 (host) to 80 (container)
        "-v", model_volume_mount,  # Mount the models directory
        IMAGE_NAME
    ]

    try:
        subprocess.run(start_command, check=True, capture_output=True)
        print(f"[Setup] Container '{CONTAINER_NAME}' started.")
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Failed to start Docker container. Is the '{IMAGE_NAME}' "
                    f"image built? Is Docker running? Error: {e.stderr.decode()}")

    # Wait for the Uvicorn server inside the container to boot up
    time.sleep(10)  # 10 seconds should be enough

    # --- Health Check ---
    # Try to connect to the API 5 times before failing
    retries = 5
    for i in range(retries):
        try:
            response = requests.get(HEALTH_CHECK_URL, timeout=5)
            if response.status_code == 200:
                print("[Setup] Health check passed. API is live.")
                break
            time.sleep(2)
        except requests.exceptions.ConnectionError:
            if i == retries - 1:
                pytest.fail("E2E Test Failed: Could not connect to the API "
                            "after 10+ seconds.")
            time.sleep(2)

    # 'yield' passes control to the test function
    yield PREDICT_URL

    # --- Teardown ---
    print(f"\n[Teardown] Stopping container '{CONTAINER_NAME}'...")
    subprocess.run(["docker", "stop", CONTAINER_NAME], capture_output=True)
    print("[Teardown] Container stopped and removed.")


# Mark this as a 'slow' test, just like the integration test
@pytest.mark.slow
def test_api_predict_endpoint_no_churn(api_service):
    """
    Test v5.3 (E2E Test):
    Sends a "low-churn-risk" passenger to the live API
    and asserts the (expected) "NO CHURN" (0) response.
    """
    # Arrange: Define a high-value customer
    payload = {
        "Frequency": 20,
        "Monetary": 5000.50,
        "Country": "United Kingdom"
    }

    # Act: Send the POST request to the fixture's URL
    response = requests.post(api_service, json=payload)

    # Assert
    assert response.status_code == 200

    data = response.json()
    assert "CHURN" in data
    assert data["CHURN"] == 0  # High-value customers should not churn


@pytest.mark.slow
def test_api_predict_endpoint_with_churn(api_service):
    """
    Test v5.3 (E2E Test):
    Sends a "high-churn-risk" passenger to the live API
    and asserts the (expected) "CHURN" (1) response.
    """
    # Arrange: Define a low-value, infrequent customer
    payload = {
        "Frequency": 1,
        "Monetary": 10.20,
        "Country": "France"
    }

    # Act: Send the POST request to the fixture's URL
    response = requests.post(api_service, json=payload)

    # Assert
    assert response.status_code == 200

    data = response.json()
    assert "CHURN" in data
    # We can't be 100% sure this passenger churns (F1 is 0.77),
    # but for a test, we assume our features work.
    # If this test fails, it might mean the model logic changed.
    assert data["CHURN"] == 1  # Low-value customers are likely to churn


@pytest.mark.slow
def test_api_schema_validation_error(api_service):
    """
    Test v5.3 (E2E Test):
    Sends *invalid* data (string instead of int) to the API
    and asserts that FastAPI's Pydantic validation
    correctly returns a 422 (Unprocessable Entity) error.
    """
    # Arrange: Define a payload with incorrect data types
    payload = {
        "Frequency": "this-is-not-an-integer",  # <-- Invalid type
        "Monetary": 5000.50,
        "Country": "United Kingdom"
    }

    # Act
    response = requests.post(api_service, json=payload)

    # Assert
    # A 422 error means FastAPI's Pydantic schema validation
    # (our 'app/schema.py') successfully caught the bad data
    # *before* it ever reached our model.
    assert response.status_code == 422