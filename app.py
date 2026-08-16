import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest

st.set_page_config(page_title="Military Fleet Maintenance & Documentation System", layout="wide")

st.title("🎖️ Army Fleet Tactical Maintenance & AI Documentation Portal")
st.caption("Predictive Maintenance, Defect Categorization & Automated Documentation System")

# 1. Dataset Generator / Excel Reader
@st.cache_data
def generate_military_fleet_data():
    np.random.seed(101)
    n_samples = 250
    regiments = ['7th Armored Regiment', '14th Field Regiment', '22nd Engineer Regiment', '10th Logistics Battalion']
    models = ['Ashok Leyland Stallion (ALS)', 'TATA 2.5 Ton']
    
    data = {
        'Vehicle_ID': [f"IA-TRK-{2001 + i}" for i in range(n_samples)],
        'Vehicle_Model': np.random.choice(models, n_samples),
        'Regiment': np.random.choice(regiments, n_samples),
        'Vintage_Years': np.random.randint(2, 18, n_samples),
        'Mileage_KM': np.sort(np.random.randint(5000, 180000, n_samples)),
        'Engine_Temp_C': np.random.normal(loc=85, scale=5, size=n_samples),
        'Suspension_Vibration_g': np.random.normal(loc=1.2, scale=0.3, size=n_samples),
        'Oil_Pressure_PSI': np.random.normal(loc=45, scale=4, size=n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Inject Synthetic Faults
    anomaly_idx = np.random.choice(n_samples, size=35, replace=False)
    df.loc[anomaly_idx, 'Engine_Temp_C'] += np.random.uniform(20, 35, size=35)
    df.loc[anomaly_idx, 'Suspension_Vibration_g'] += np.random.uniform(2.0, 3.8, size=35)
    df.loc[anomaly_idx, 'Oil_Pressure_PSI'] -= np.random.uniform(15, 25, size=35)
    
    return df

# Sidebar Data Ingestion (Excel & CSV Support)
st.sidebar.header("📂 Data Ingestion & Filters")
uploaded_file = st.sidebar.file_uploader("Upload Defect / Fleet Data (Excel or CSV)", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.sidebar.success("✅ Real Regiment Data Loaded!")
else:
    df = generate_military_fleet_data()

# Regiment Filter
selected_regiment = st.sidebar.selectbox("Select Regiment View", ["All Regiments"] + list(df['Regiment'].unique()))
if selected_regiment != "All Regiments":
    df = df[df['Regiment'] == selected_regiment]

# 2. AI Anomaly Engine & Defect Level Classification
features = ['Engine_Temp_C', 'Suspension_Vibration_g', 'Oil_Pressure_PSI', 'Mileage_KM', 'Vintage_Years']
model = IsolationForest(contamination=0.1, random_state=42)
df['Anomaly_Score'] = model.fit_predict(df[features])

def categorize_defect(row):
    if row['Anomaly_Score'] == 1:
        return "✅ Operational", "Routine Unit Check", "None"
    
    # Check severity for User-Level vs Workshop-Level
    major_triggers = 0
    actions = []
    
    if row['Engine_Temp_C'] > 105:
        major_triggers += 1
        actions.append("Coolant circuit overhaul / Radiator flush")
    elif row['Engine_Temp_C'] > 95:
        actions.append("Driver Level: Check coolant level & fan belt tension")
        
    if row['Suspension_Vibration_g'] > 2.8:
        major_triggers += 1
        actions.append("Workshop Level: Damper & leaf spring replacement")
    elif row['Suspension_Vibration_g'] > 2.0:
        actions.append("Driver Level: Suspension greasing & wheel alignment")

    if row['Oil_Pressure_PSI'] < 28:
        major_triggers += 1
        actions.append("Workshop Level: Oil pump & pressure seal replacement")
    elif row['Oil_Pressure_PSI'] < 35:
        actions.append("Driver Level: Oil level top-up & filter check")

    if major_triggers >= 1 or row['Vintage_Years'] > 12:
        return "🔴 Major Defect", "Workshop Level Intervention", " | ".join(actions)
    else:
        return "🟡 Minor Defect", "User Level Intervention", " | ".join(actions)

results = df.apply(categorize_defect, axis=1)
df['Health_Status'] = [r[0] for r in results]
df['Intervention_Level'] = [r[1] for r in results]
df['Automated_Action_Note'] = [r[2] for r in results]

# 3. Key Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Regiment Fleet Strength", len(df))
c2.metric("Operational Vehicles", len(df[df['Health_Status'] == '✅ Operational']))
c3.metric("User Level (Minor Defects)", len(df[df['Health_Status'] == '🟡 Minor Defect']))
c4.metric("Workshop Level (Major Defects)", len(df[df['Health_Status'] == '🔴 Major Defect']))

st.markdown("---")

# 4. Interactive Fleet Visuals
st.subheader("📈 Vehicle Health & Vintage vs Mileage Analytics")
fig = px.scatter(
    df, 
    x='Mileage_KM', 
    y='Engine_Temp_C', 
    color='Health_Status',
    size='Vintage_Years',
    hover_data=['Vehicle_ID', 'Vehicle_Model', 'Intervention_Level', 'Automated_Action_Note'],
    color_discrete_map={
        '✅ Operational': '#2ecc71', 
        '🟡 Minor Defect': '#f1c40f',
        '🔴 Major Defect': '#e74c3c'
    }
)
st.plotly_chart(fig, use_container_width=True)

# 5. Automated Documentation & Action Work-sheet
st.subheader("📋 Automated Maintenance Docket & Defect Report")

def_filter = st.radio("Filter Defect List", ["All Flagged Vehicles", "Workshop Level Only", "User Level Only"], horizontal=True)

if def_filter == "Workshop Level Only":
    report_df = df[df['Intervention_Level'] == 'Workshop Level Intervention']
elif def_filter == "User Level Only":
    report_df = df[df['Intervention_Level'] == 'User Level Intervention']
else:
    report_df = df[df['Health_Status'] != '✅ Operational']

st.dataframe(
    report_df[['Vehicle_ID', 'Vehicle_Model', 'Regiment', 'Vintage_Years', 'Mileage_KM', 'Health_Status', 'Intervention_Level', 'Automated_Action_Note']], 
    use_container_width=True
)

# Automated Export for Army Documentation
csv_data = report_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Automated Workshop Inspection Docket (CSV)",
    data=csv_data,
    file_name="Automated_Regiment_Defect_Docket.csv",
    mime="text/csv"
)
