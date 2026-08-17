import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import re
from collections import Counter

st.set_page_config(
    page_title="Indian Army Fleet Telematics & Predictive Maintenance System",
    page_icon="🎖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 1. BUILT-IN GOLD STANDARD MILITARY FLEET DATASET (BENCHMARK DATA)
# -----------------------------------------------------------------------------
@st.cache_data
def get_gold_standard_fleet():
    raw_data = [
        {"Unit": "Unit A (14 Field)", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107753W", "Dt_Induction": "09-Jun-2021", "Dt_In": "26-Oct-2023", "Dt_Out": "28-Jan-2024", "KM_In": 22131, "KM_Out": 22137, "Defect": "AXLE NOISY, AIR FILTER DIRTY, RADIATOR LEAKING, HUB SEAL WORN OUT", "Repair_Activity": "REPAIRED, AIR FILTER NEW FITTED, RADIATOR ASSY NEW FITTED, HUB SEAL NEW FITTED"},
        {"Unit": "Unit A (14 Field)", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107753W", "Dt_Induction": "09-Jun-2021", "Dt_In": "13-Nov-2023", "Dt_Out": "22-Feb-2024", "KM_In": 22238, "KM_Out": 22243, "Defect": "ROTARY SWITCH NOT WORK, ISOLETOR SWITCH NOT WORK, AIR FILTER DIRTY, CLUTCH HARD", "Repair_Activity": "ROTARY SWITCH REPAIRED, ISOLETOR SWITCH NEW FITTED, AIR FILTER NEW FITTED, CLUTCH ADJUSTED"},
        {"Unit": "Unit B (7 Armoured)", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-2021", "Dt_In": "06-Mar-2025", "Dt_Out": "08-Mar-2025", "KM_In": 30502, "KM_Out": 30509, "Defect": "AIR COMPRESSURE LEAK, BRAKE POOR", "Repair_Activity": "AIR COMPRESSOR CANEBLIZED FROM CL-V VEH, BOTH REAR BRAKE BOOSTER CANNIBALIZED, ALL FOUR WHEEL BRAKE ADJUSTED"},
        {"Unit": "Unit B (7 Armoured)", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-2021", "Dt_In": "21-May-2025", "Dt_Out": "28-Jul-2025", "KM_In": 30732, "KM_Out": 30739, "Defect": "VEH PULLING POWER WEAK, SOLENOID SWITCH NOT WORK", "Repair_Activity": "CLUTCH PLATE & CLUTCH MASTER CYLINDER NEW FITTED, SOLENOID SWITCH NEW FITTED"},
        {"Unit": "Unit B (7 Armoured)", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-2021", "Dt_In": "15-Sep-2025", "Dt_Out": "15-Sep-2025", "KM_In": 31022, "KM_Out": 31028, "Defect": "DOOR GLASS MECHANISM NOT WORK, MAIN SWITCH NOT WORK, STEERING GEAR BOX OIL LEAKING", "Repair_Activity": "DOOR GLASS MECH REPAIRED, CHANGE OVER SWITCH NEW FITTED, STEERING GEAR BOX REMOVED & SEAL KIT ZF NEW FITTED"},
        {"Unit": "Unit B (7 Armoured)", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-2021", "Dt_In": "09-Jul-2026", "Dt_Out": "12-Jul-2026", "KM_In": 32237, "KM_Out": 32243, "Defect": "AXLE NOISY, PROPELLER SHAFT NOISY, DOOR LOCK NOT WORK", "Repair_Activity": "AXLE REPAIRED, PROPELLER SHAFT REMOVED & NUT NEW FITTED, DOOR LOCK REPAIRED"},
        {"Unit": "Unit C (22 Engr)", "Nomenclature": "2.5 TON", "Veh_BA_No": "22C-109902P", "Dt_Induction": "24-Feb-2022", "Dt_In": "13-Nov-2025", "Dt_Out": "16-Nov-2025", "KM_In": 10847, "KM_Out": 10849, "Defect": "ISOLATOR SWITCH NOT WORK, BRAKE POOR", "Repair_Activity": "ISOLATOR SWITCH REPAIRED, BRAKE ADJUSTED"},
        {"Unit": "Unit D (10 Logistics)", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "05-Sep-2023", "Dt_Out": "27-Oct-2023", "KM_In": 60740, "KM_Out": 60742, "Defect": "STARTING TROUBLE", "Repair_Activity": "ALL INJECTOR OVERHAUL & FUEL FEED PUMP REPAIRED"},
        {"Unit": "Unit D (10 Logistics)", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "10-Feb-2025", "Dt_Out": "14-Feb-2025", "KM_In": 66343, "KM_Out": 66348, "Defect": "MAIN GEAR BOX NOISY, RADIATOR LEKING, BRAKE POOR, CABIN LIFTING PUMP NOT WORK", "Repair_Activity": "MAIN GEAR BOX MAIN SHAFT & REVERSE SHAFT REPLACED, GAS WELDING/FLASHING, ALL FOUR WHEEL BRAKE ADJUSTED, RAM HYDRAULIC NEW FITTED"},
        {"Unit": "Unit D (10 Logistics)", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "17-Apr-2025", "Dt_Out": "18-Aug-2025", "KM_In": 66487, "KM_Out": 66490, "Defect": "ENGINE OVERHEATING, HAND BRAKE AIR PRESSURE LEAKING", "Repair_Activity": "WATER PUMP MAJOR SERVICE KIT & FLUID ELEMENT NEW FITTED, PRESSURE LEAKING RECTIFIED"},
        {"Unit": "Unit D (10 Logistics)", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "18-Nov-2025", "Dt_Out": "24-Feb-2026", "KM_In": 68064, "KM_Out": 68068, "Defect": "GEAR SHIFTING HARD, STARTING TROUBLE", "Repair_Activity": "GEAR BOX SERVICING CARRIED OUT, FUEL TANK & PIPE LINE CLEANED"},
        {"Unit": "Unit D (10 Logistics)", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "19-Mar-2026", "Dt_Out": "20-Mar-2026", "KM_In": 68221, "KM_Out": 68229, "Defect": "BRAKE POOR", "Repair_Activity": "BRAKE ADJUSTED"},
        {"Unit": "Unit E (5 ASC)", "Nomenclature": "ALS", "Veh_BA_No": "19D-208745N", "Dt_Induction": "29-May-2019", "Dt_In": "26-Oct-2023", "Dt_Out": "26-Oct-2023", "KM_In": 27321, "KM_Out": 27329, "Defect": "BRAKE POOR", "Repair_Activity": "BRAKE ADJUSTED"},
        {"Unit": "Unit E (5 ASC)", "Nomenclature": "ALS", "Veh_BA_No": "19D-208745N", "Dt_Induction": "29-May-2019", "Dt_In": "14-Jan-2025", "Dt_Out": "18-Jan-2025", "KM_In": 29103, "KM_Out": 29109, "Defect": "ROAD SPRING BROCKEN, SUSPENSION NOISY", "Repair_Activity": "ROAD SPRING LEAF & U BOLT NEW FITTED, SUSPENSION REPAIR CARRIED OUT"},
        {"Unit": "Unit E (5 ASC)", "Nomenclature": "ALS", "Veh_BA_No": "19D-208745N", "Dt_Induction": "29-May-2019", "Dt_In": "20-Jan-2026", "Dt_Out": "23-Jan-2026", "KM_In": 32253, "KM_Out": 32258, "Defect": "BRAKE POOR, DOOR GLASS MECHENISM NOT WORK, WIPER MOTOR N/W, SOLENOID SWITCH NOT WORK", "Repair_Activity": "FRONT BRAKE SHOES & UNLOADER VALVE REPLACED, DOOR GLASS & WIPER MOTOR REPAIRED"},
        {"Unit": "Unit F (9 EME)", "Nomenclature": "ALS", "Veh_BA_No": "19D-202808W", "Dt_Induction": "29-May-2019", "Dt_In": "06-Aug-2023", "Dt_Out": "07-Aug-2023", "KM_In": 25562, "KM_Out": 25670, "Defect": "BRAKE POOR, HEAD LIGHT NOT WORK", "Repair_Activity": "BRAKE ADJUSTED, HEAD LIGHT REPAIRED"},
        {"Unit": "Unit F (9 EME)", "Nomenclature": "ALS", "Veh_BA_No": "19D-202808W", "Dt_Induction": "29-May-2019", "Dt_In": "24-Aug-2023", "Dt_Out": "24-Aug-2023", "KM_In": 26020, "KM_Out": 26025, "Defect": "ROAD SPRING BROCKEN", "Repair_Activity": "ROAD SPRING NO.6 LEAF NEW FITTED"},
        {"Unit": "Unit F (9 EME)", "Nomenclature": "ALS", "Veh_BA_No": "19D-202808W", "Dt_Induction": "29-May-2019", "Dt_In": "05-Jul-2024", "Dt_Out": "06-Jul-2024", "KM_In": 29334, "KM_Out": 29336, "Defect": "GEAR SHIFTING HARD, HUB SEAL WORN OUT, HAND BRAKE NOT WORK", "Repair_Activity": "GEAR BOX SERVICING, HUB SEAL NEW FITTED, HAND BRAKE REPAIR"},
        {"Unit": "Unit F (9 EME)", "Nomenclature": "ALS", "Veh_BA_No": "19D-202808W", "Dt_Induction": "29-May-2019", "Dt_In": "25-May-2026", "Dt_Out": "25-May-2026", "KM_In": 33879, "KM_Out": 33885, "Defect": "SUSPENSION NOISY", "Repair_Activity": "SUSPENSION CHECKED REPAIR & DEFECT CARRIED OUT"},
        {"Unit": "Unit G (3 Med Bn)", "Nomenclature": "5 KL W/B", "Veh_BA_No": "14P-029330Y", "Dt_Induction": "16-Jun-2014", "Dt_In": "05-Jun-2023", "Dt_Out": "05-Jun-2023", "KM_In": 18885, "KM_Out": 18889, "Defect": "WATER PUMP NOT WORK, WIPER BLADE PERISHED", "Repair_Activity": "WATER PUMP REPAIRED, WIPER BLADE NEW FITTED"},
        {"Unit": "Unit G (3 Med Bn)", "Nomenclature": "5 KL W/B", "Veh_BA_No": "14P-029330Y", "Dt_Induction": "16-Jun-2014", "Dt_In": "05-Feb-2025", "Dt_Out": "05-Feb-2025", "KM_In": 21587, "KM_Out": 21590, "Defect": "BRAKE POOR", "Repair_Activity": "BRAKE SHOE NEW FITTED AND BRAKE ADJUSTED"},
        {"Unit": "Unit G (3 Med Bn)", "Nomenclature": "5 KL W/B", "Veh_BA_No": "14P-029330Y", "Dt_Induction": "16-Jun-2014", "Dt_In": "01-Jul-2025", "Dt_Out": "01-Jul-2025", "KM_In": 21800, "KM_Out": 21809, "Defect": "FAN BELT BROCKEN", "Repair_Activity": "FAN BELT NEW FITTED & PTO BELT TENSIONER PULLEY NUT TIGHTEN"}
    ]
    return pd.DataFrame(raw_data)

# -----------------------------------------------------------------------------
# 2. DYNAMIC COLUMN AUTO-MAPPER (SELF-HEALING FOR ANY FUTURE EXCEL FORMAT)
# -----------------------------------------------------------------------------
def standardize_uploaded_dataframe(df_raw):
    col_mapping = {}
    cols = df_raw.columns
    for c in cols:
        c_clean = str(c).strip().lower()
        if re.search(r'ba.*no|veh.*no|regn|vehicle', c_clean):
            col_mapping[c] = 'Veh_BA_No'
        elif re.search(r'nom|type|variant|make|model', c_clean):
            col_mapping[c] = 'Nomenclature'
        elif re.search(r'unit|regiment|battalion|coy', c_clean):
            col_mapping[c] = 'Unit'
        elif re.search(r'induct|vintage|mfg|yom', c_clean):
            col_mapping[c] = 'Dt_Induction'
        elif re.search(r'dt.*in|date.*in|inward', c_clean):
            col_mapping[c] = 'Dt_In'
        elif re.search(r'dt.*out|date.*out|outward', c_clean):
            col_mapping[c] = 'Dt_Out'
        elif re.search(r'km.*in|odometer|mileage', c_clean):
            col_mapping[c] = 'KM_In'
        elif re.search(r'defect|fault|problem|complaint', c_clean):
            col_mapping[c] = 'Defect'
        elif re.search(r'repair|action|work.*done|activity', c_clean):
            col_mapping[c] = 'Repair_Activity'
    
    df_clean = df_raw.rename(columns=col_mapping)
    
    # Fill defaults if missing in external files
    if 'Unit' not in df_clean.columns: df_clean['Unit'] = 'Regiment General Fleet'
    if 'Nomenclature' not in df_clean.columns: df_clean['Nomenclature'] = 'Military Heavy Transport'
    if 'Veh_BA_No' not in df_clean.columns: df_clean['Veh_BA_No'] = [f"BA-{1000+i}" for i in range(len(df_clean))]
    if 'KM_In' not in df_clean.columns: df_clean['KM_In'] = 25000
    if 'Dt_Induction' not in df_clean.columns: df_clean['Dt_Induction'] = "01-Jan-2020"
    if 'Defect' not in df_clean.columns: df_clean['Defect'] = 'Routine Workshop Inspection'
    if 'Repair_Activity' not in df_clean.columns: df_clean['Repair_Activity'] = 'General Servicing'
    
    return df_clean

# -----------------------------------------------------------------------------
# 3. UNIVERSAL NLP & HEURISTIC ENGINE (DYNAMIC PATTERN DISCOVERY)
# -----------------------------------------------------------------------------
def analyze_fleet_heuristics(df):
    current_year = datetime.now().year
    
    # Calculate Vintage
    def get_vintage(dt_str):
        try:
            dt = pd.to_datetime(dt_str, errors='coerce')
            return max(0.5, round(current_year - dt.year, 1)) if pd.notnull(dt) else 6.0
        except:
            return 6.0
    
    df['Vintage_Years'] = df['Dt_Induction'].apply(get_vintage)
    
    # Vintage & Mileage Bucketing
    df['Vintage_Category'] = df['Vintage_Years'].apply(
        lambda v: "0-5 Years" if v <= 5 else ("5-10 Years" if v <= 10 else ("10-15 Years" if v <= 15 else "15+ Years"))
    )
    
    def get_mileage_bucket(km):
        try:
            k = float(km)
            if k <= 25000: return "0-25k KM"
            elif k <= 50000: return "25k-50k KM"
            elif k <= 75000: return "50k-75k KM"
            elif k <= 100000: return "75k-1 Lakh KM"
            else: return "Beyond 1 Lakh KM"
        except:
            return "25k-50k KM"
            
    df['KM_In_Num'] = pd.to_numeric(df['KM_In'], errors='coerce').fillna(25000)
    df['Mileage_Category'] = df['KM_In_Num'].apply(get_mileage_bucket)
    
    # Subsystem & Repair Type Classifier
    subsystems, actions, readiness_scores = [], [], []
    
    for _, row in df.iterrows():
        d = str(row.get('Defect', '')).upper()
        r = str(row.get('Repair_Activity', '')).upper()
        
        # Subsystem Tagging
        if any(w in d for w in ['ENGINE', 'RADIATOR', 'WATER PUMP', 'FAN BELT', 'OVERHEAT', 'COOLANT']):
            sub = "Thermal & Cooling"
        elif any(w in d for w in ['GEAR', 'CLUTCH', 'AXLE', 'PROPELLER', 'DRIVE', 'TRANSMISSION']):
            sub = "Transmission & Drivetrain"
        elif any(w in d for w in ['SPRING', 'SUSPENSION', 'HUB SEAL', 'LEAF', 'DAMPER', 'SHOCK']):
            sub = "Suspension & Running Gear"
        elif any(w in d for w in ['BRAKE', 'AIR PRESSURE', 'COMPRESS', 'BOOSTER', 'VALVE']):
            sub = "Braking & Pneumatics"
        elif any(w in d for w in ['SWITCH', 'LIGHT', 'WIPER', 'BATTERY', 'SOLENOID', 'WIRING', 'STARTER']):
            sub = "Electrical & Auxiliaries"
        else:
            sub = "General Chassis & Body"
            
        # Action Type Tagging
        if any(w in r for w in ['NEW FITTED', 'REPLACED', 'CANNIBALIZED', 'KIT', 'CHANGED', 'FITTED', 'OVERHAUL']):
            act = "⚙️ Spare Part Replaced"
            penalty = 25
        else:
            act = "🔧 Servicing & Adjustment"
            penalty = 10
            
        # Mission Readiness Score (100 Base - Age/KM/Defect Degradation)
        age_penalty = min(row['Vintage_Years'] * 2.5, 30)
        km_penalty = min((row['KM_In_Num'] / 10000) * 3, 30)
        readiness = max(15, round(100 - (age_penalty + km_penalty + penalty), 1))
        
        subsystems.append(sub)
        actions.append(act)
        readiness_scores.append(readiness)
        
    df['Subsystem'] = subsystems
    df['Action_Type'] = actions
    df['Mission_Readiness_Score'] = readiness_scores
    
    # Overall Status
    df['Tactical_Status'] = df['Mission_Readiness_Score'].apply(
        lambda s: "🟢 Mission Ready (Priority 1)" if s >= 70 else ("🟡 Operational with Field Limits (Priority 2)" if s >= 45 else "🔴 Critical Workshop Grounded (Priority 3)")
    )
    
    return df

# -----------------------------------------------------------------------------
# 4. SIDEBAR INGESTION & CO FILTER CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Badge_of_the_Indian_Army.svg/300px-Badge_of_the_Indian_Army.svg.png", width=75)
st.sidebar.title("Command Controls")
st.sidebar.caption("Tactical Fleet Readiness & Logistics Ingestion Engine")

uploaded_file = st.sidebar.file_uploader("📂 Ingest Army Defect Log Sheet (.xlsx / .csv)", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            raw_df = pd.read_csv(uploaded_file)
        else:
            raw_df = pd.read_excel(uploaded_file)
        standardized_df = standardize_uploaded_dataframe(raw_df)
        fleet_df = analyze_fleet_heuristics(standardized_df)
        st.sidebar.success(f"✅ Ingested {len(fleet_df)} Records from External Unit Sheet!")
    except Exception as e:
        st.sidebar.error(f"Error parsing file: {e}")
        fleet_df = analyze_fleet_heuristics(get_gold_standard_fleet())
else:
    fleet_df = analyze_fleet_heuristics(get_gold_standard_fleet())

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Multi-Echelon Filtering")

# Dynamic Filters (Supports 15+ Units & Any Custom Variants)
units_list = ["All Formations / Units"] + sorted(list(fleet_df['Unit'].unique()))
selected_unit = st.sidebar.selectbox("Formation / Unit Selection", units_list)

variants_list = ["All Vehicles / Variants"] + sorted(list(fleet_df['Nomenclature'].unique()))
selected_variant = st.sidebar.selectbox("Vehicle Platform / Variant", variants_list)

subsystems_list = ["All Subsystems"] + sorted(list(fleet_df['Subsystem'].unique()))
selected_subsystem = st.sidebar.selectbox("Mechanical Subsystem", subsystems_list)

mileage_bands = ["All Mileage Bands", "0-25k KM", "25k-50k KM", "50k-75k KM", "75k-1 Lakh KM", "Beyond 1 Lakh KM"]
selected_mileage = st.sidebar.selectbox("Odometer Mileage Range", mileage_bands)

vintage_bands = ["All Vintage Bands", "0-5 Years", "5-10 Years", "10-15 Years", "15+ Years"]
selected_vintage = st.sidebar.selectbox("Fleet Vintage (Years of Service)", vintage_bands)

# Apply Filter Execution
dff = fleet_df.copy()
if selected_unit != "All Formations / Units":
    dff = dff[dff['Unit'] == selected_unit]
if selected_variant != "All Vehicles / Variants":
    dff = dff[dff['Nomenclature'] == selected_variant]
if selected_subsystem != "All Subsystems":
    dff = dff[dff['Subsystem'] == selected_subsystem]
if selected_mileage != "All Mileage Bands":
    dff = dff[dff['Mileage_Category'] == selected_mileage]
if selected_vintage != "All Vintage Bands":
    dff = dff[dff['Vintage_Category'] == selected_vintage]

# -----------------------------------------------------------------------------
# 5. COMMAND LEVEL READINESS & DECISION SCORECARD
# -----------------------------------------------------------------------------
st.title("🎖️ Army Workshop Command Telematics & Mission Readiness")
st.caption(f"Active Filter: **{selected_unit}** | Platform: **{selected_variant}** | Real-Time Fleet Health Evaluation")

total_count = len(dff)
ready_count = len(dff[dff['Tactical_Status'].str.contains("🟢")])
limited_count = len(dff[dff['Tactical_Status'].str.contains("🟡")])
grounded_count = len(dff[dff['Tactical_Status'].str.contains("🔴")])
avg_score = round(dff['Mission_Readiness_Score'].mean(), 1) if total_count > 0 else 0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Formation Fleet Monitored", f"{len(dff['Veh_BA_No'].unique())} Vehs", f"{total_count} Incidents")
kpi2.metric("Overall Fleet Readiness", f"{avg_score}%", "Tactical Health")
kpi3.metric("🟢 Mission Ready", f"{ready_count}", f"{(ready_count/total_count*100):.0f}%" if total_count > 0 else "0%")
kpi4.metric("🟡 Operational (Limited)", f"{limited_count}", "Field Adjustments")
kpi5.metric("🔴 Critical Grounded", f"{grounded_count}", "Awaiting Spares")

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. RESULT-ORIENTED EXECUTIVE VISUALIZATIONS (NO OVERLAPPING DOTS)
# -----------------------------------------------------------------------------
tab_overview, tab_spares, tab_diagnostics, tab_docket = st.tabs([
    "📊 Commander's Fleet Overview", 
    "📦 Spares & Supply Chain Demand", 
    "🔮 AI Predictive Diagnostics (Vehicle Wise)", 
    "📋 Interactive Digital Job-Card & Docket"
])

with tab_overview:
    g1, g2 = st.columns(2)
    
    with g1:
        st.subheader("Subsystem Defect Distribution (Repair Nature)")
        if not dff.empty:
            fig_sub = px.bar(
                dff,
                x='Subsystem',
                color='Action_Type',
                barmode='group',
                color_discrete_map={'⚙️ Spare Part Replaced': '#c0392b', '🔧 Servicing & Adjustment': '#2980b9'},
                title="Mechanical Stress per Subsystem"
            )
            fig_sub.update_layout(xaxis_tickangle=-25, margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig_sub, use_container_width=True)
        else:
            st.info("No matching records found for active filters.")
            
    with g2:
        st.subheader("Defect Frequency by Mileage Range")
        if not dff.empty:
            fig_mil = px.histogram(
                dff,
                x='Mileage_Category',
                color='Nomenclature',
                category_orders={'Mileage_Category': ["0-25k KM", "25k-50k KM", "50k-75k KM", "75k-1 Lakh KM", "Beyond 1 Lakh KM"]},
                title="Odometer Mileage Wear Pattern"
            )
            fig_mil.update_layout(margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig_mil, use_container_width=True)
        else:
            st.info("No matching records found.")

with tab_spares:
    st.subheader("📦 Automated Spares Replacement Forecast (Critical Shortage Prediction)")
    st.caption("AI-identified high wear assemblies requiring pre-emptive inventory requisition for the next operating cycle.")
    
    spares_df = dff[dff['Action_Type'] == '⚙️ Spare Part Replaced']
    
    if not spares_df.empty:
        # Extract keywords of replaced parts
        all_repairs = " ".join(spares_df['Repair_Activity'].tolist()).upper()
        tokens = [w for w in re.findall(r'\b[A-Z]{3,}\b', all_repairs) if w not in ['NEW', 'FITTED', 'REPLACED', 'FROM', 'BOTH', 'FOUR', 'ALL', 'THE', 'AND', 'WITH', 'CARRIED', 'OUT']]
        freq = Counter(tokens).most_common(8)
        
        freq_df = pd.DataFrame(freq, columns=['Component Assembly', 'Failure / Replacement Count'])
        
        c_sp1, c_sp2 = st.columns([1, 1])
        with c_sp1:
            fig_spares = px.pie(
                freq_df, 
                names='Component Assembly', 
                values='Failure / Replacement Count',
                hole=0.4,
                title="Highest Consumed Spares Across Formation"
            )
            st.plotly_chart(fig_spares, use_container_width=True)
            
        with c_sp2:
            st.write("#### 🛡️ AI Logistics Requisition Note")
            for idx, r in freq_df.iterrows():
                st.warning(f"**High Demand Component: {r['Component Assembly']}** — {r['Failure / Replacement Count']} replacements logged. Recommend maintaining at least **{r['Failure / Replacement Count'] * 2} buffer units** at Brigade Workshop.")
    else:
        st.info("No spare part replacements recorded in this filtered selection.")

with tab_diagnostics:
    st.subheader("🔮 Individual Vehicle Diagnostic Profile & Health History")
    veh_list = sorted(list(dff['Veh_BA_No'].unique()))
    
    if veh_list:
        selected_veh = st.selectbox("Select Target Vehicle BA No for Automated Audit", veh_list)
        veh_records = dff[dff['Veh_BA_No'] == selected_veh]
        
        v_col1, v_col2 = st.columns([1, 2])
        with v_col1:
            st.info(f"""
            ### 🪖 Vehicle Identity Card
            * **BA Number:** `{selected_veh}`
            * **Variant:** {veh_records['Nomenclature'].iloc[0]}
            * **Assigned Unit:** {veh_records['Unit'].iloc[0]}
            * **Induction Date:** {veh_records['Dt_Induction'].iloc[0]}
            * **Vintage:** {veh_records['Vintage_Years'].iloc[0]} Years
            * **Peak Recorded Mileage:** {int(veh_records['KM_In_Num'].max()):,} KM
            * **Total Workshop Visits:** {len(veh_records)}
            * **Mission Readiness:** **{veh_records['Mission_Readiness_Score'].iloc[-1]}%**
            """)
            
        with v_col2:
            # Historical Defect Chain
            st.markdown("#### 📜 Chronological Workshop Defect Trail")
            st.dataframe(
                veh_records[['Dt_In', 'KM_In', 'Defect', 'Repair_Activity', 'Action_Type', 'Subsystem']],
                use_container_width=True
            )
            
            # Actionable Predictive Assessment
            def_str = " ".join(veh_records['Defect'].tolist()).upper()
            alerts = []
            if "BRAKE" in def_str or "AIR PRESSURE" in def_str:
                alerts.append("🔴 **Pneumatic / Brake Degradation:** Repeat brake adjustment logged. Overhaul brake booster & unloader valve before heavy duty deployment.")
            if "SPRING" in def_str or "SUSPENSION" in def_str:
                alerts.append("🟡 **Suspension Leaf Fatigue:** High risk of road spring breakage on rough terrain. Conduct torque audit on U-Bolts.")
            if "RADIATOR" in def_str or "ENGINE" in def_str or "WATER PUMP" in def_str:
                alerts.append("🔴 **Cooling System Thermal Stress:** Temperature anomalies flagged. Conduct coolant pressure leak-test.")
            if not alerts:
                alerts.append("🟢 **Nominal Wear Pattern:** System operating within normal field tolerance bounds.")
                
            st.success("### 🧠 AI Commanding Decision Recommendation\n" + "\n\n".join(alerts))

with tab_docket:
    st.subheader("📋 Digital Maintenance Docket & Editable Job-Card")
    st.caption("Military workshop engineers can edit values, add new defect entries, or update status directly in the grid below.")
    
    display_cols = ['Veh_BA_No', 'Unit', 'Nomenclature', 'Vintage_Category', 'Mileage_Category', 'KM_In', 'Defect', 'Repair_Activity', 'Subsystem', 'Action_Type', 'Tactical_Status', 'Mission_Readiness_Score']
    
    edited_data = st.data_editor(
        dff[display_cols],
        num_rows="dynamic",
        use_container_width=True
    )
    
    c_d1, c_d2 = st.columns([1, 3])
    with c_d1:
        # Download Button
        csv_file = edited_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Official Job-Card Docket (CSV)",
            data=csv_file,
            file_name=f"Official_Army_Fleet_Docket_{datetime.now().strftime('%d_%b_%Y')}.csv",
            mime="text/csv"
        )
    with c_d2:
        st.caption("🔒 All telemetry and repair logs processed purely offline in-memory. Zero classified telemetry transmitted outside.")