import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest

st.set_page_config(page_title="Tactical Fleet Maintenance Copilot", layout="wide")

st.title("🎖️ Tactical Vehicle Fleet Health & Predictive Maintenance System")
st.caption("AI-Powered Workshop Analytics, Failure Prediction & Decision Support")

# 1. Synthetic Data Ingestion
@st.cache_data
def load_vehicle_data():
    np.random.seed(42)
    n_samples = 350
    
    data = {
        'Vehicle_ID': [f"MIL-TRK-{101 + (i % 12)}" for i in range(n_samples)],
        'Vehicle_Age_Years': np.random.randint(2, 12, n_samples),
        'Mileage_KM': np.sort(np.random.randint(8000, 150000, n_samples)),
        'Engine_Temp_C': np.random.normal(loc=86, scale=4, size=n_samples),
        'Suspension_Vibration_g': np.random.normal(loc=1.1, scale=0.25, size=n_samples),
        'Oil_Pressure_PSI': np.random.normal(loc=44, scale=3, size=n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Inject Synthetic Faults
    anomaly_idx = np.random.choice(n_samples, size=30, replace=False)
    df.loc[anomaly_idx, 'Engine_Temp_C'] += np.random.uniform(22, 38, size=30)
    df.loc[anomaly_idx, 'Suspension_Vibration_g'] += np.random.uniform(2.2, 4.0, size=30)
    df.loc[anomaly_idx, 'Oil_Pressure_PSI'] -= np.random.uniform(14, 22, size=30)
    
    return df

uploaded_file = st.sidebar.file_uploader("Upload Military Telemetry CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = load_vehicle_data() # Uses synthetic data if no file uploaded

# 2. AI Anomaly Engine
features = ['Engine_Temp_C', 'Suspension_Vibration_g', 'Oil_Pressure_PSI', 'Mileage_KM']
model = IsolationForest(contamination=0.08, random_state=42)
df['Anomaly_Score'] = model.fit_predict(df[features])

df['Health_Status'] = df['Anomaly_Score'].apply(
    lambda x: '⚠️ High Risk (Needs Maintenance)' if x == -1 else '✅ Operational'
)

# Automated AI Recommendation Logic
def generate_recommendation(row):
    if row['Health_Status'] == '✅ Operational':
        return "System Normal. Routine inspection at scheduled interval."
    reasons = []
    if row['Engine_Temp_C'] > 100:
        reasons.append("Coolant flush & radiator thermal check required.")
    if row['Suspension_Vibration_g'] > 2.5:
        reasons.append("Inspect damper bushings, shocks, and wheel bearings.")
    if row['Oil_Pressure_PSI'] < 32:
        reasons.append("Immediate oil pump & seal leakage audit.")
    if not reasons:
        reasons.append("General drivetrain stress detected. Perform workshop diagnosis.")
    return " | ".join(reasons)

df['AI_Maintenance_Action'] = df.apply(generate_recommendation, axis=1)

# 3. Top Metrics Bar
c1, c2, c3, c4 = st.columns(4)
c1.metric("Monitored Fleet Vehicles", len(df['Vehicle_ID'].unique()))
c2.metric("Total Operational Records", len(df))
high_risk_df = df[df['Health_Status'] == '⚠️ High Risk (Needs Maintenance)']
c3.metric("Vehicles Flagged for Service", len(high_risk_df))
c4.metric("Avg Fleet Mileage", f"{int(df['Mileage_KM'].mean()):,} KM")

st.markdown("---")

# 4. Fleet Telemetry Chart
st.subheader("📊 Mileage vs Thermal Stress Analysis")
fig = px.scatter(
    df, 
    x='Mileage_KM', 
    y='Engine_Temp_C', 
    color='Health_Status',
    size='Suspension_Vibration_g',
    hover_data=['Vehicle_ID', 'Vehicle_Age_Years', 'AI_Maintenance_Action'],
    color_discrete_map={'✅ Operational': '#2ecc71', '⚠️ High Risk (Needs Maintenance)': '#e74c3c'}
)
st.plotly_chart(fig, use_container_width=True)

# 5. Workshop Actionable Table & CSV Download
st.subheader("🚨 Priority Maintenance Action List")
st.dataframe(
    high_risk_df[['Vehicle_ID', 'Vehicle_Age_Years', 'Mileage_KM', 'Engine_Temp_C', 'Suspension_Vibration_g', 'Oil_Pressure_PSI', 'AI_Maintenance_Action']], 
    use_container_width=True
)

# Export Feature
csv_data = high_risk_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Export Maintenance Schedule Report (CSV)",
    data=csv_data,
    file_name="military_fleet_maintenance_report.csv",
    mime="text/csv"
)
