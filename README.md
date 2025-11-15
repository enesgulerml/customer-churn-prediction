# End-to-End Customer Churn Prediction (v3.0)

This project transforms a raw, transactional Excel dataset (`online_retail_II.xlsx`) into a "Google-level," production-ready MLOps pipeline. It moves beyond the "kaos" of notebooks into a fully engineered, reproducible, and decoupled system.

The core of this project is **v1.0 (Feature Engineering)**, which converts raw transaction logs into a customer-centric table (RFM + Churn features). This engineered dataset is then used for **v2.0 (Experiment Tracking)** and **v3.0 (API Serving)**.

* **v1.0: Feature Engineering (RFM + Churn)**
* **v2.0: Experiment Tracking (MLFlow + XGBoost)**
* **v3.0: API Serving (FastAPI)**
* **v3.1: Docker**
* **V4.0: Streamlit UI**
=======
* **v4.0: Streamlit UI** 

---

## 🚀 Project Structure

The repository is organized based on professional data science standards to ensure separation of concerns:

```
customer-churn-prediction/
│
├── app/                  <- (v3.0) API service code
│   ├── __init__.py
│   ├── main.py           <- (FastAPI "motor" - serves predictions)
│   └── schema.py         <- (Pydantic "contract" - defines API inputs/outputs)
│
├── data/
│   ├── raw/
│   │   └── online_retail_II.xlsx <- (Raw data, *not* tracked by Git)
│   └── processed/
│       └── customer_features.csv <- (Engineered data, *not* tracked by Git)
│
├── models/
│   └── churn_model.joblib    <- (Trained XGBoost pipeline, *not* tracked by Git)
│
├── mlruns/                 <- (v2.0) MLFlow experiment logs, *not* tracked by Git)
│
├── notebooks/
│   └── 01-Data-Exploration.ipynb <- (EDA and prototyping notebook)
│
├── src/                  <- (v1.0 & v2.0) All training & engineering source code
│   │
│   ├── __init__.py
│   ├── config.py             <- (All settings, paths, and hyperparameters)
│   ├── data_processing.py    <- (Raw data cleaning functions)
│   ├── feature_engineering.py  <- (RFM + Churn creation functions)
│   ├── pipeline.py           <- (Scikit-learn + XGBoost pipeline definition)
│   └── train.py              <- (Main training script - "Orchestrator")
│
├── .gitignore                <- (Tells Git to ignore data, models, logs)
├── environment.yml           <- (Conda environment dependencies)
├── setup.py                  <- (Makes the 'src' folder an installable package)
└── README.md                 <- (This file - The project user manual)
```

---

## 🛠️ Installation & Setup (v1.0)

Follow these steps to set up the project environment on your local machine.

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/enesgulerml/customer-churn-prediction.git](https://github.com/enesgulerml/customer-churn-prediction.git)
    cd customer-churn-prediction
    ```

2.  **Download the Data:**
    * This project uses the **Online Retail II** dataset.
    * Download the `online_retail_II.xlsx` file.
    * Place the file inside the `data/raw/` directory (you may need to create these folders).

3.  **Create Conda Environment:**
    This command reads the `environment.yml` file to create an isolated environment with all libraries (including `xgboost`, `mlflow`, `fastapi`, and `openpyxl`).
    ```bash
    conda env create -f environment.yml
    conda activate customer-churn-prediction
    ```

4.  **Install the Project Package:**
    This is the crucial "Google-level" step that makes your `src` code importable (solves `ModuleNotFoundError`).
    ```bash
    pip install -e .
    ```
    Note: If you encounter environment-specific errors (like conda not found or docker memory issues), please check our TROUBLESHOOTING.md guide.

---

## ⚡ How to Use

Once installed, the project provides three main functions: Training (v2.1), API (v3.0), and (soon) Dashboard (v4.0).

### 1. v2.1: Train Model & Track (MLFlow)

This is the main "orchestrator" script. It runs the entire pipeline:
1.  **Data Processing:** Cleans the raw Excel data.
2.  **Feature Engineering:** Calculates RFM features and creates the `CHURN` target variable.
3.  **Training:** Trains the XGBoost model.
4.  **Tracking:** Logs all parameters (like `CHURN_THRESHOLD_DAYS`) and the `F1 Score` (e.g., `0.7710`) to MLFlow.

```bash
python -m src.train
```

To view the results and compare different runs (e.g., `RandomForest` vs. `XGBoost`), launch the MLFlow dashboard:
```bash
mlflow ui
```
(Go to `http://127.0.0.1:5000` in your browser)

### 2. v3.0: Serve Model (FastAPI)

This runs the v3.0 API server. It loads the `churn_model.joblib` (trained in the step above) and serves it.

**Architecture Note:** This API expects *already-engineered features* (`Frequency`, `Monetary`, `Country`), not raw data.

1.  Make sure you have a trained model in `models/churn_model.joblib` (by running `python -m src.train` first).
2.  Run the server from the project root:
    ```bash
    uvicorn app.main:app --reload
    ```

### 2. v3.1: Serve Model (FastAPI + Docker)

This project is designed to serve the API (v3.0) as a production-ready **Docker Container**.

The `Dockerfile` packages the entire application (`src` and `app`), installs all dependencies, and starts the `uvicorn` server. The `.dockerignore` file ensures that no data, models, or logs are incorrectly copied into the image, following the "Code in Image, Data on Volume" principle.

#### 1. Build the v3.1 API Image
(If you encounter a `cannot allocate memory` error, please see our [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide.)
```bash
docker build -t churn-api:v3 .
```

#### 2. Run the API Server (Docker)
This command runs the API in "detached" mode (`-d`), maps your local port `8000` to the container's port `80` (`-p 8000:80`), and crucially, mounts the `models/` directory (`-v`) so the API can load the `churn_model.joblib`.

```bash
docker run -d --rm \
  -p 8000:80 \
  -v ${pwd}/models:/app/models \
  churn-api:v3
```
Once running, you can access the documentation at **`http://localhost:8000/docs`**.

---

### 3. v4.0: View Dashboard (Streamlit)

This repository also includes a v4.0 interactive dashboard (`dashboard/app.py`).

This dashboard is a **decoupled frontend**. It does *not* load the model. It acts as a client that sends HTTP requests to the **v3.1 API Container** (which must be running).

#### How to Run the Dashboard

This requires **two separate terminals** running simultaneously:

**➡️ Terminal 1: Run the API Server (v3.1)**
(If not already running) Start the FastAPI Docker container. This is the "Motor".
```bash
docker run -d --rm \
  -p 8000:80 \
  -v ${pwd}/models:/app/models \
  churn-api:v3
```

**➡️ Terminal 2: Run the Streamlit App (v4.0)**
Activate the conda environment and run the Streamlit app. This is the "Dashboard".
```bash
conda activate customer-churn-prediction
python -m streamlit run dashboard/app.py
```
Your browser will open `http://localhost:8501`, where you can interact with the live system.
