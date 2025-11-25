# 📉 Customer Churn Prediction & Retention System

![Python](https://img.shields.io/badge/Python-3.10-blue)
![XGBoost](https://img.shields.io/badge/Model-XGBoost-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-009688)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)
![Tests](https://img.shields.io/badge/Tests-Pytest_%26_E2E-brightgreen)

## 📖 Overview
This repository hosts a robust **Predictive Analytics Pipeline** designed to identify customers at risk of churning. Using the **Online Retail II** dataset, the system analyzes historical transaction behavior to predict future disengagement.

The goal is to empower marketing teams with actionable intelligence, shifting from reactive measures to **proactive retention strategies**.

**Technical Highlights:**
* **Advanced Feature Engineering:** Transformation of raw transactional data into behavioral features (RFM, Tenure, Average Basket Size).
* **Modular Pipeline:** Decoupled architecture separating data processing, training (`src/pipeline.py`), and inference.
* **Production-Grade Serving:** Model served via high-performance **FastAPI**, containerized with **Docker**.
* **Rigorous Testing:** Includes both Unit Tests for the pipeline and E2E Tests for the API.

---

## 📂 Project Structure

```text
customer-churn-prediction/
│
├── app/                  # Inference Service
│   ├── main.py           # FastAPI Entry Point
│   └── schema.py         # Pydantic Data Validation
│
├── dashboard/            # Business Dashboard
│   └── app.py            # Streamlit Interface for Marketing Teams
│
├── src/                  # ML Core Logic
│   ├── feature_engineering.py  # 🧠 Feature Extraction (The "Secret Sauce")
│   ├── pipeline.py       # Orchestration of Data Flow
│   ├── train.py          # Model Training & MLflow Logging
│   └── config.py         # Central Configuration
│
├── tests/                # Quality Assurance
│   ├── test_pipeline.py  # Unit Tests for Data Processing
│   └── test_api_e2e.py   # Integration Tests for Dockerized API
│
├── Dockerfile            # Container Configuration
└── requirements.txt      # Dependencies
```

## 🛠️ Installation & Setup
Prerequisites
* Python 3.10+
* Docker (Required for E2E tests and Serving)
* Dataset: [Online Retail II](https://www.kaggle.com/code/ekrembayar/rfm-analysis-online-retail-ii) (Place the .xlsx file in data/raw/)

1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/enesgulerml/customer-churn-prediction.git
cd customer-churn-prediction

# Create Virtual Environment
conda create -n churn-prediction python=3.10 -y
conda activate churn-prediction

# Install Dependencies
pip install -r requirements.txt
pip install -e .
```

## ⚡ Workflow & Pipeline
This project implements a modular pipeline design.
### Phase 1: Feature Engineering & Training
The raw data is complex transactional logs. The pipeline aggregates this into a customer-level view.

1. Execute Pipeline: This command runs data cleaning, feature extraction, and model training.

```bash
python -m src.train
```
Artifacts will be logged to MLflow and the local models/ directory.

### Phase 2: Docker Deployment
Deploy the trained model as a microservice.

1. Build Image: We tag the image as v3 to align with our integration tests.
```bash
docker build -t churn-api:latest .
```

2. Run Container: We map port 8000 to avoid conflicts with other local services.
```bash
docker run -d --rm -p 8000:80 churn-api:latest
```
👉 API Docs: http://localhost:8000/docs

### Phase 3: Business Dashboard
Launch the interface to visualize churn probabilities.
```bash
streamlit run dashboard/app.py
```

## 🧪 Testing Strategy
This project maintains a high standard of code quality through automated testing.

1. Unit Tests (Pipeline Logic)
Validates that feature engineering (e.g., Tenure calculation) works as expected.
```bash
pytest tests/test_pipeline.py
```

2. E2E Tests (API Integration)

Validates that the Dockerized API accepts requests and returns valid predictions. Note: These tests automatically attempt to start a Docker container named churn-api:v3. Ensure the image is built before running.

```bash
# Build image first (if not done)
docker build -t churn-api:v3 .

# Run E2E tests
pytest tests/test_api_e2e.py
```

## 📊 Feature Engineering Logic
The model's performance relies on derived features:
* Recency: Days since last purchase.
* Frequency: Number of distinct orders.
* Monetary: Total Customer Lifetime Value (CLTV).
* Tenure: Days since the first purchase.
* Basket Size: Average items per order.