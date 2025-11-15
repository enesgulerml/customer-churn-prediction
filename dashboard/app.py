# dashboard/app.py

import streamlit as st
import requests
import json

# --- API and Model Information ---

API_URL = "http://localhost:8000/predict"

# --- Streamlit Interface ---

st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="💔",
    layout="centered"
)

st.title("💔 Customer Churn Prediction (v4.0)")
st.write("---")
st.write(
    "This Streamlit 'Dashboard' (v4.0) consumes the FastAPI 'Motor' (v3.0). "
    "The API is running in a separate Docker container."
)

# --- User Input (Input Form) ---
st.header("Enter Customer's RFM Features:")
st.write(
    "These are the *engineered features* that our API expects, "
    "not the raw data."
)

# Split the form into columns
col1, col2 = st.columns(2)

with col1:
    # According to the 'ChurnInput' model in app/schema.py
    frequency = st.number_input("Frequency (Total Invoices)",
                                min_value=1, value=5, step=1)

    country = st.text_input("Country",
                          value="United Kingdom")

with col2:
    monetary = st.number_input("Monetary (Total Spend)",
                              min_value=0.01, value=150.75, format="%.2f")


# --- Prediction Button and API Request ---

if st.button("💔 Predict Churn Status"):

    # 1. Convert user input to the JSON format our API expects
    api_input = {
        "Frequency": frequency,
        "Monetary": monetary,
        "Country": country
    }

    try:
        # 2. Send a POST request to FastAPI (http://localhost:8000/predict)
        response = requests.post(API_URL, json=api_input)
        response.raise_for_status()

        # 3. Retrieve JSON response from API
        prediction = response.json()
        churn_status = prediction.get("CHURN")

        # 4. Print the result beautifully on the screen
        if churn_status == 1:
            st.error("### 💔 **Prediction: CHURN** 💔")
            st.write("This customer is likely to churn.")
        else:
            st.success("### 🎉 **Prediction: NO CHURN** 🎉")
            st.write("This customer is likely to stay.")

        st.write("---")

        st.subheader("API Response (JSON):")
        st.json(prediction)

    except requests.exceptions.ConnectionError:
        st.error(
            "Connection Error: Could not connect to the API (v3.0).\n\n"
            "**Is the FastAPI Docker container running?**\n\n"
            "Please run the following command in a separate terminal:\n\n"
            "`docker run -d --rm -p 8000:80 -v ${pwd}/models:/app/models titanic-api:v3`"
        )
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.subheader("Data Sent (JSON):")
        st.json(api_input)