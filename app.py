import streamlit as st
import pandas as pd
import joblib
import os
import matplotlib.pyplot as plt

# -------------------------
# Load model and dataset
# -------------------------
model_path = os.path.join(os.path.dirname(__file__), "flight_delay_model.joblib")
model = joblib.load(model_path)

# Load dataset to extract carriers & airports
data_path = os.path.join(os.path.dirname(__file__), "flight_delays.csv")
df = pd.read_csv(data_path)

carriers = sorted(df['carrier'].dropna().unique())
airports = sorted(df['airport'].dropna().unique())

# -------------------------
# Streamlit UI
# -------------------------
st.title("🛫 Flight Delay Prediction System")
st.write("Predict if a flight will be delayed based on historical patterns.")

# Sidebar Inputs
with st.sidebar:
    st.header("✈️ Flight Details")

    month = st.slider("Month", 1, 12, 8)
    carrier = st.selectbox("Carrier", carriers)
    airport = st.selectbox("Airport", airports)
    arr_flights = st.number_input("Arriving Flights", min_value=1, value=10)
    carrier_delay = st.number_input("Carrier Delay (minutes)", min_value=0.0, value=5.0)
    weather_delay = st.number_input("Weather Delay (minutes)", min_value=0.0, value=1.0)
    nas_delay = st.number_input("NAS Delay (minutes)", min_value=0.0, value=0.0)
    security_delay = st.number_input("Security Delay (minutes)", min_value=0.0, value=0.0)
    late_aircraft_delay = st.number_input("Late Aircraft Delay (minutes)", min_value=0.0, value=3.0)

# -------------------------
# Prediction
# -------------------------
if st.button("🚀 Predict Delay"):
    input_data = {
        'month': month,
        'carrier': carrier,
        'airport': airport,
        'arr_flights': arr_flights,
        'carrier_delay': carrier_delay,
        'weather_delay': weather_delay,
        'nas_delay': nas_delay,
        'security_delay': security_delay,
        'late_aircraft_delay': late_aircraft_delay
    }
    
    df_input = pd.DataFrame([input_data])
    prob = model.predict_proba(df_input)[0][1]
    pred = model.predict(df_input)[0]

    st.subheader("Prediction Result")
    if pred == 1:
        st.error(f"✈️ **Delayed** (Probability: {prob:.1%})")
    else:
        st.success(f"✅ **On-Time** (Probability: {1-prob:.1%})")

# -------------------------
# Feature Importances
# -------------------------
st.subheader("🔑 Feature Importances (from Random Forest)")
classifier = model.named_steps['classifier']

if hasattr(classifier, "feature_importances_"):
    # Get feature names from pipeline
    preprocessor = model.named_steps['preprocessor']
    cat_features = preprocessor.named_transformers_['cat'].get_feature_names_out(['carrier', 'airport'])
    num_features = ['month', 'arr_flights', 'carrier_delay', 'weather_delay', 'nas_delay', 'security_delay', 'late_aircraft_delay']
    feature_names = list(num_features) + list(cat_features)

    importances = classifier.feature_importances_
    importance_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
    importance_df = importance_df.sort_values('importance', ascending=False).head(10)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(importance_df['feature'], importance_df['importance'])
    ax.invert_yaxis()
    ax.set_xlabel("Importance")
    ax.set_title("Top 10 Feature Importances")
    st.pyplot(fig)
else:
    st.info("Feature importance not available for this model.")
