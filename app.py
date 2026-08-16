import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Military Fleet Tactical Maintenance & AI Documentation Portal", layout="wide")

st.title("🎖️ Army Fleet Tactical Maintenance & AI Defect Documentation Portal")
st.caption("AI-Powered Workshop Telematics, Failure Diagnostics & Work-Docket Generation")

# 1. Real Military Defect Log Ingestion
@st.cache_data
def get_official_fleet_data():
    raw_data = [
        # Vehicle 1: 2.5 TON (19C-107753W)
        {"S_No": 1, "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107753W", "Dt_Induction": "09-Jun-21", "Dt_In": "26-Oct-23", "Dt_Out": "28-Jan-24", "KM_In": 22131, "KM_Out": 22137, "Defect": "AXLE NOISY, AIR FILTER DIRTY, RADIATOR LEAKING, HUB SEAL WORN OUT", "Repair_Activity": "REPAIRED, AIR FILTER NEW FITTED, RADIATOR ASSY NEW FITTED, HUB SEAL NEW FITTED"},
        {"S_No": 1, "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107753W", "Dt_Induction": "09-Jun-21", "Dt_In": "13-Nov-23", "Dt_Out": "22-Feb-24", "KM_In": 22238, "KM_Out": 22243, "Defect": "ROTARY SWITCH NOT WORK, ISOLETOR SWITCH NOT WORK, AIR FILTER DIRTY, CLUTCH HARD", "Repair_Activity": "ROTARY SWITCH REPAIRED, ISOLETOR SWITCH NEW FITTED, AIR FILTER NEW FITTED, CLUTCH ADJUSTED"},
        # Vehicle 2: 2.5 TON (19C-107906X)
        {"S_No": 2, "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-21", "Dt_In": "06-Mar-25", "Dt_Out": "08-Mar-25", "KM_In": 30502, "KM_Out": 30509, "Defect": "AIR COMPRESSURE LEAK, BRAKE POOR", "Repair_Activity": "AIR COMPRESSOR CANEBLIZED FROM CL-V VEH, BOTH REAR BRAKE BOOSTER CANNIBALIZED, ALL FOUR WHEEL BRAKE ADJUSTED"},
        {"S_No": 2, "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-21", "Dt_In": "21-May-25", "Dt_Out": "28-Jul-25", "KM_In": 30732, "KM_Out": 30739, "Defect": "VEH PULLING POWER WEAK, SOLENOID SWITCH NOT WORK", "Repair_Activity": "CLUTCH PLATE & CLUTCH MASTER CYLINDER NEW FITTED, SOLENOID SWITCH NEW FITTED"},
        {"S_No": 2, "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-21", "Dt_In": "15-Sep-25", "Dt_Out": "15-Sep-25", "KM_In": 31022, "KM_Out": 31028, "Defect": "DOOR GLASS MECHANISM NOT WORK, MAIN SWITCH NOT WORK, STEERING GEAR BOX OIL LEAKING", "Repair_Activity": "DOOR GLASS MECH REPAIRED, CHANGE OVER SWITCH NEW FITTED, STEERING GEAR BOX REMOVED & SEAL KIT ZF NEW FITTED"},
        {"S_No": 2, "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-21", "Dt_In": "09-Jul-26", "Dt_Out": "12-Jul-26", "KM_In": 32237, "KM_Out": 32243, "Defect": "AXLE NOISY, PROPELLER SHAFT NOISY, DOOR LOCK NOT WORK", "Repair_Activity": "AXLE REPAIRED, PROPELLER SHAFT REMOVED & NUT NEW FITTED, DOOR LOCK REPAIRED"},
        # Vehicle 3: 2.5 TON (22C-109902P)
        {"S_No": 3, "Nomenclature": "2.5 TON", "Veh_BA_No": "22C-109902P", "Dt_Induction": "24-Feb-22", "Dt_In": "13-Nov-25", "Dt_Out": "16-Nov-25", "KM_In": 10847, "KM_Out": 10849, "Defect": "ISOLATOR SWITCH NOT WORK, BRAKE POOR", "Repair_Activity": "ISOLATOR SWITCH REPAIRED, BRAKE ADJUSTED"},
        # Vehicle 4: ALS (13D-192836W)
        {"S_No": 4, "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-14", "Dt_In": "05-Sep-23", "Dt_Out": "27-Oct-23", "KM_In": 60740, "KM_Out": 60742, "Defect": "STARTING TROUBLE", "Repair_Activity": "ALL INJECTOR OVERHAUL & FUEL FEED PUMP REPAIRED"},
        {"S_No": 4, "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-14", "Dt_In": "10-Feb-25", "Dt_Out": "14-Feb-25", "KM_In": 66343, "KM_Out": 66348, "Defect": "MAIN GEAR BOX NOISY, RADIATOR LEKING, BRAKE POOR, CABIN LIFTING PUMP NOT WORK", "Repair_Activity": "MAIN GEAR BOX MAIN SHAFT & REVERSE SHAFT REPLACED, GAS WELDING/FLASHING, ALL FOUR WHEEL BRAKE ADJUSTED, RAM HYDRAULIC NEW FITTED"},
        {"S_No": 4, "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-14", "Dt_In": "17-Apr-25", "Dt_Out": "18-Aug-25", "KM_In": 66487, "KM_Out": 66490, "Defect": "ENGINE OVERHEATING, HAND BRAKE AIR PRESSURE LEAKING", "Repair_Activity": "WATER PUMP MAJOR SERVICE KIT & FLUID ELEMENT NEW FITTED, PRESSURE LEAKING RECTIFIED"},
        {"S_No": 4, "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-14", "Dt_In": "18-Nov-25", "Dt_Out": "24-Feb-26", "KM_In": 68064, "KM_Out": 68068, "Defect": "GEAR SHIFTING HARD, STARTING TROUBLE", "Repair_Activity": "GEAR BOX SERVICING CARRIED OUT, FUEL TANK & PIPE LINE CLEANED"},
        {"S_No": 4, "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-14", "Dt_In": "19-Mar-26", "Dt_Out": "20-Mar-26", "KM_In": 68221, "KM_Out": 68229, "Defect": "BRAKE POOR", "Repair_Activity": "BRAKE ADJUSTED"},
        # Vehicle 5: ALS (19D-208745N)
        {"S_No": 5, "Nomenclature": "ALS", "Veh_BA_No": "19D-208745N", "Dt_Induction": "29-May-19", "Dt_In": "26-Oct-23", "Dt_Out": "26-Oct-23", "KM_In": 27321, "KM_Out": 27329, "Defect": "BRAKE POOR", "Repair_Activity": "BRAKE ADJUSTED"},
        {"S_No": 5, "Nomenclature": "ALS", "Veh_BA_No": "19D-208745N", "Dt_Induction": "29-May-19", "Dt_In": "14-Jan-25", "Dt_Out": "18-Jan-25", "KM_In": 29103, "KM_Out": 29109, "Defect": "ROAD SPRING BROCKEN, SUSPENSION NOISY", "Repair_Activity": "ROAD SPRING LEAF & U BOLT NEW FITTED, SUSPENSION REPAIR CARRIED OUT"},
        {"S_No": 5, "Nomenclature": "ALS", "Veh_BA_No": "19D-208745N", "Dt_Induction": "29-May-19", "Dt_In": "20-Jan-26", "Dt_Out": "23-Jan-26", "KM_In": 32253, "KM_Out": 32258, "Defect": "BRAKE POOR, DOOR GLASS MECHENISM NOT WORK, WIPER MOTOR N/W, SOLENOID SWITCH NOT WORK", "Repair_Activity": "FRONT BRAKE SHOES & UNLOADER VALVE REPLACED, DOOR GLASS & WIPER MOTOR REPAIRED"},
        # Vehicle 6: ALS (19D-202808W)
        {"S_No": 6, "Nomenclature": "ALS", "Veh_BA_No": "19D-202808W", "Dt_Induction": "29-May-19", "Dt_In": "06-Aug-23", "Dt_Out": "07-Aug-23", "KM_In": 25562, "KM_Out": 25670, "Defect": "BRAKE POOR, HEAD LIGHT NOT WORK", "Repair_Activity": "BRAKE ADJUSTED, HEAD LIGHT REPAIRED"},
        {"S_No": 6, "Nomenclature": "ALS", "Veh_BA_No": "19D-202808W", "Dt_Induction": "29-May-19", "Dt_In": "24-Aug-23", "Dt_Out": "24-Aug-23", "KM_In": 26020, "KM_Out": 26025, "Defect": "ROAD SPRING BROCKEN", "Repair_Activity": "ROAD SPRING NO.6 LEAF NEW FITTED"},
        {"S_No": 6, "Nomenclature": "ALS", "Veh_BA_No": "19D-202808W", "Dt_Induction": "29-May-19", "Dt_In": "05-Jul-24", "Dt_Out": "06-Jul-24", "KM_In": 29334, "KM_Out": 29336, "Defect": "GEAR SHIFTING HARD, HUB SEAL WORN OUT, HAND BRAKE NOT WORK", "Repair_Activity": "GEAR BOX SERVICING, HUB SEAL NEW FITTED, HAND BRAKE REPAIR"},
        {"S_No": 6, "Nomenclature": "ALS", "Veh_BA_No": "19D-202808W", "Dt_Induction": "29-May-19", "Dt_In": "25-May-26", "Dt_Out": "25-May-26", "KM_In": 33879, "KM_Out": 33885, "Defect": "SUSPENSION NOISY", "Repair_Activity": "SUSPENSION CHECKED REPAIR & DEFECT CARRIED OUT"},
        # Vehicle 7: 5 KL W/B (14P-029330Y)
        {"S_No": 7, "Nomenclature": "5 KL W/B", "Veh_BA_No": "14P-029330Y", "Dt_Induction": "16-Jun-14", "Dt_In": "05-Jun-23", "Dt_Out": "05-Jun-23", "KM_In": 18885, "KM_Out": 18889, "Defect": "WATER PUMP NOT WORK, WIPER BLADE PERISHED", "Repair_Activity": "WATER PUMP REPAIRED, WIPER BLADE NEW FITTED"},
        {"S_No": 7, "Nomenclature": "5 KL W/B", "Veh_BA_No": "14P-029330Y", "Dt_Induction": "16-Jun-14", "Dt_In": "05-Feb-25", "Dt_Out": "05-Feb-25", "KM_In": 21587, "KM_Out": 21590, "Defect": "BRAKE POOR", "Repair_Activity": "BRAKE SHOE NEW FITTED AND BRAKE ADJUSTED"},
        {"S_No": 7, "Nomenclature": "5 KL W/B", "Veh_BA_No": "14P-029330Y", "Dt_Induction": "16-Jun-14", "Dt_In": "01-Jul-25", "Dt_Out": "01-Jul-25", "KM_In": 21800, "KM_Out": 21809, "Defect": "FAN BELT BROCKEN", "Repair_Activity": "FAN BELT NEW FITTED & PTO BELT TENSIONER PULLEY NUT TIGHTEN"}
    ]
    return pd.DataFrame(raw_data)

# Sidebar - Real Excel / CSV Upload
st.sidebar.header("📁 Ingestion & Filters")
uploaded_file = st.sidebar.file_uploader("Upload Military Telemetry Sheet (.xlsx or .csv)", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("✅ Real Workshop File Processed!")
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")
        df = get_official_fleet_data()
else:
    df = get_official_fleet_data()

# 2. AI Defect Classifier & Intervention Level Reasoning
def ai_analyze_defect(defect_str):
    d = str(defect_str).upper()
    
    # Critical workshop major triggers
    major_keywords = ['ENGINE OVERHEATING', 'RADIATOR', 'GEAR BOX', 'AXLE', 'ROAD SPRING', 'STEERING GEAR BOX', 'CLUTCH PLATE', 'WATER PUMP']
    # User / Driver field level triggers
    minor_keywords = ['AIR FILTER', 'SWITCH', 'WIPER', 'DOOR', 'HEAD LIGHT', 'BRAKE POOR', 'FAN BELT']
    
    is_major = any(k in d for k in major_keywords)
    
    if "ENGINE" in d or "RADIATOR" in d or "WATER PUMP" in d or "FAN BELT" in d:
        subsystem = "Thermal / Cooling System"
    elif "GEAR" in d or "CLUTCH" in d or "AXLE" in d or "PROPELLER" in d:
        subsystem = "Transmission & Drivetrain"
    elif "SPRING" in d or "SUSPENSION" in d or "HUB SEAL" in d:
        subsystem = "Suspension & Running Gear"
    elif "BRAKE" in d or "COMPRESSURE" in d or "AIR PRESSURE" in d:
        subsystem = "Braking & Pneumatics"
    elif "SWITCH" in d or "LIGHT" in d or "WIPER" in d:
        subsystem = "Electrical & Auxiliaries"
    else:
        subsystem = "General Chassis"

    if is_major:
        intervention = "🔴 Workshop Level (Major Overhaul)"
        action = f"Immediate component inspection, assembly overhaul / replacement needed for: {subsystem}"
    else:
        intervention = "🟡 User Level (Field Maintenance)"
        action = f"Driver / Unit level inspection, lubrication, tensioning & adjustments for: {subsystem}"
        
    return subsystem, intervention, action

analysis_results = df['Defect'].apply(ai_analyze_defect)
df['Subsystem_Affected'] = [r[0] for r in analysis_results]
df['Intervention_Level'] = [r[1] for r in analysis_results]
df['AI_Predictive_Action'] = [r[2] for r in analysis_results]

# Nomenclature & Vehicle Filter
selected_nom = st.sidebar.selectbox("Filter Vehicle Type", ["All Types"] + list(df['Nomenclature'].unique()))
if selected_nom != "All Types":
    df_filtered = df[df['Nomenclature'] == selected_nom]
else:
    df_filtered = df

selected_veh = st.sidebar.selectbox("Filter Specific Vehicle BA No", ["All Vehicles"] + list(df_filtered['Veh_BA_No'].unique()))
if selected_veh != "All Vehicles":
    df_filtered = df_filtered[df_filtered['Veh_BA_No'] == selected_veh]

# 3. High-Level Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Unique Fleet Monitored", len(df['Veh_BA_No'].unique()))
c2.metric("Total Defect Logs Ingested", len(df_filtered))
c3.metric("Workshop Level Major Defects", len(df_filtered[df_filtered['Intervention_Level'].str.contains("Workshop")]))
c4.metric("User Level Field Defects", len(df_filtered[df_filtered['Intervention_Level'].str.contains("User")]))

st.markdown("---")

# 4. Analytics Visualizations
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Defects by Subsystem")
    fig_sub = px.bar(
        df_filtered['Subsystem_Affected'].value_counts().reset_index(),
        x='Subsystem_Affected',
        y='count',
        labels={'Subsystem_Affected': 'Subsystem', 'count': 'Defect Occurrences'},
        color='Subsystem_Affected',
        title="Breakdown by Critical Subsystem"
    )
    st.plotly_chart(fig_sub, use_container_width=True)

with col_right:
    st.subheader("📈 Mileage (KM In) vs Vehicle Defect Profile")
    fig_scatter = px.scatter(
        df_filtered,
        x='KM_In',
        y='Nomenclature',
        color='Intervention_Level',
        size='KM_In',
        hover_data=['Veh_BA_No', 'Defect', 'AI_Predictive_Action'],
        color_discrete_map={
            '🔴 Workshop Level (Major Overhaul)': '#e74c3c',
            '🟡 User Level (Field Maintenance)': '#f39c12'
        },
        title="Odometer Mileage vs Intervention Severity"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# 5. Automated AI Defect Docket & Documentation
st.subheader("📋 Automated Workshop Maintenance Docket & Job-Card")

st.dataframe(
    df_filtered[['Veh_BA_No', 'Nomenclature', 'KM_In', 'Dt_In', 'Dt_Out', 'Defect', 'Repair_Activity', 'Subsystem_Affected', 'Intervention_Level', 'AI_Predictive_Action']],
    use_container_width=True
)

# One-Click CSV Export for Army Documentation
csv_data = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Official Maintenance Docket Report (CSV)",
    data=csv_data,
    file_name=f"Army_Fleet_Maintenance_Docket_{datetime.now().strftime('%d_%b_%Y')}.csv",
    mime="text/csv"
)
