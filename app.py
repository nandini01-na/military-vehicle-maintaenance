import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import re

# Set Page Config
st.set_page_config(
    page_title="Army Fleet Maintenance & Telematics AI",
    page_icon="🎖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Command Center UI
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. BASE FLEET DATASET (15 UNITS: Unit A to Unit O)
# ---------------------------------------------------------
@st.cache_data
def get_base_fleet():
    raw_data = [
        {"Unit": "Unit A", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107753W", "Dt_Induction": "09-Jun-2021", "Dt_In": "26-Oct-2023", "Dt_Out": "28-Jan-2024", "KM_In": 22131, "KM_Out": 22137, "Defect": "AXLE NOISY, AIR FILTER DIRTY, RADIATOR LEAKING, HUB SEAL WORN OUT", "Repair_Activity": "REPAIRED, AIR FILTER NEW FITTED, RADIATOR ASSY NEW FITTED, HUB SEAL NEW FITTED"},
        {"Unit": "Unit A", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107753W", "Dt_Induction": "09-Jun-2021", "Dt_In": "13-Nov-2023", "Dt_Out": "22-Feb-2024", "KM_In": 22238, "KM_Out": 22243, "Defect": "ROTARY SWITCH NOT WORK, ISOLETOR SWITCH NOT WORK, AIR FILTER DIRTY, CLUTCH HARD", "Repair_Activity": "ROTARY SWITCH REPAIRED, ISOLETOR SWITCH NEW FITTED, AIR FILTER NEW FITTED, CLUTCH ADJUSTED"},
        {"Unit": "Unit B", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-2021", "Dt_In": "06-Mar-2025", "Dt_Out": "08-Mar-2025", "KM_In": 30502, "KM_Out": 30509, "Defect": "AIR COMPRESSURE LEAK, BRAKE POOR", "Repair_Activity": "AIR COMPRESSOR CANEBLIZED FROM CL-V VEH, REAR BRAKE BOOSTER FITTED, BRAKE ADJUSTED"},
        {"Unit": "Unit B", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-2021", "Dt_In": "21-May-2025", "Dt_Out": "28-Jul-2025", "KM_In": 30732, "KM_Out": 30739, "Defect": "VEH PULLING POWER WEAK, SOLENOID SWITCH NOT WORK", "Repair_Activity": "CLUTCH PLATE & MASTER CYLINDER NEW FITTED, SOLENOID SWITCH NEW FITTED"},
        {"Unit": "Unit C", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-2021", "Dt_In": "15-Sep-2025", "Dt_Out": "15-Sep-2025", "KM_In": 31022, "KM_Out": 31028, "Defect": "DOOR GLASS MECHANISM NOT WORK, MAIN SWITCH NOT WORK, STEERING GEAR BOX OIL LEAKING", "Repair_Activity": "DOOR GLASS REPAIRED, CHANGE OVER SWITCH NEW FITTED, STEERING SEAL KIT ZF NEW FITTED"},
        {"Unit": "Unit D", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-2021", "Dt_In": "09-Jul-2026", "Dt_Out": "12-Jul-2026", "KM_In": 32237, "KM_Out": 32243, "Defect": "AXLE NOISY, PROPELLER SHAFT NOISY, DOOR LOCK NOT WORK", "Repair_Activity": "AXLE REPAIRED, PROPELLER SHAFT NUT FITTED, DOOR LOCK REPAIRED"},
        {"Unit": "Unit E", "Nomenclature": "2.5 TON", "Veh_BA_No": "22C-109902P", "Dt_Induction": "24-Feb-2022", "Dt_In": "13-Nov-2025", "Dt_Out": "16-Nov-2025", "KM_In": 10847, "KM_Out": 10849, "Defect": "ISOLATOR SWITCH NOT WORK, BRAKE POOR", "Repair_Activity": "ISOLATOR SWITCH REPAIRED, BRAKE ADJUSTED"},
        {"Unit": "Unit F", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "05-Sep-2023", "Dt_Out": "27-Oct-2023", "KM_In": 60740, "KM_Out": 60742, "Defect": "STARTING TROUBLE", "Repair_Activity": "INJECTOR OVERHAUL & FUEL FEED PUMP REPAIRED"},
        {"Unit": "Unit G", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "10-Feb-2025", "Dt_Out": "14-Feb-2025", "KM_In": 66343, "KM_Out": 66348, "Defect": "MAIN GEAR BOX NOISY, RADIATOR LEKING, BRAKE POOR, CABIN LIFTING PUMP NOT WORK", "Repair_Activity": "MAIN GEAR BOX SHAFT REPLACED, GAS WELDING, BRAKE ADJUSTED, RAM HYDRAULIC FITTED"},
        {"Unit": "Unit H", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "17-Apr-2025", "Dt_Out": "18-Aug-2025", "KM_In": 66487, "KM_Out": 66490, "Defect": "ENGINE OVERHEATING, HAND BRAKE AIR PRESSURE LEAKING", "Repair_Activity": "WATER PUMP MAJOR SERVICE KIT FITTED, PRESSURE LEAKING RECTIFIED"},
        {"Unit": "Unit I", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "18-Nov-2025", "Dt_Out": "24-Feb-2026", "KM_In": 68064, "KM_Out": 68068, "Defect": "GEAR SHIFTING HARD, STARTING TROUBLE", "Repair_Activity": "GEAR BOX SERVICING, FUEL TANK & PIPE LINE CLEANED"},
        {"Unit": "Unit J", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "19-Mar-2026", "Dt_Out": "20-Mar-2026", "KM_In": 68221, "KM_Out": 68229, "Defect": "BRAKE POOR", "Repair_Activity": "BRAKE ADJUSTED"},
        {"Unit": "Unit K", "Nomenclature": "ALS", "Veh_BA_No": "19D-208745N", "Dt_Induction": "29-May-2019", "Dt_In": "26-Oct-2023", "Dt_Out": "26-Oct-2023", "KM_In": 27321, "KM_Out": 27329, "Defect": "BRAKE POOR", "Repair_Activity": "BRAKE ADJUSTED"},
        {"Unit": "Unit L", "Nomenclature": "ALS", "Veh_BA_No": "19D-208745N", "Dt_Induction": "29-May-2019", "Dt_In": "14-Jan-2025", "Dt_Out": "18-Jan-2025", "KM_In": 29103, "KM_Out": 29109, "Defect": "ROAD SPRING BROCKEN, SUSPENSION NOISY", "Repair_Activity": "ROAD SPRING LEAF & U BOLT FITTED, SUSPENSION REPAIR"},
        {"Unit": "Unit M", "Nomenclature": "ALS", "Veh_BA_No": "19D-202808W", "Dt_Induction": "29-May-2019", "Dt_In": "06-Aug-2023", "Dt_Out": "07-Aug-2023", "KM_In": 25562, "KM_Out": 25670, "Defect": "BRAKE POOR, HEAD LIGHT NOT WORK", "Repair_Activity": "BRAKE ADJUSTED, HEAD LIGHT REPAIRED"},
        {"Unit": "Unit N", "Nomenclature": "ALS", "Veh_BA_No": "19D-202808W", "Dt_Induction": "29-May-2019", "Dt_In": "24-Aug-2023", "Dt_Out": "24-Aug-2023", "KM_In": 26020, "KM_Out": 26025, "Defect": "ROAD SPRING BROCKEN", "Repair_Activity": "ROAD SPRING NO.6 LEAF NEW FITTED"},
        {"Unit": "Unit O", "Nomenclature": "5 KL W/B", "Veh_BA_No": "14P-029330Y", "Dt_Induction": "16-Jun-2014", "Dt_In": "01-Jul-2025", "Dt_Out": "01-Jul-2025", "KM_In": 21800, "KM_Out": 21809, "Defect": "FAN BELT BROCKEN, WATER PUMP NOT WORK", "Repair_Activity": "FAN BELT NEW FITTED, WATER PUMP REPAIRED"}
    ]
    return pd.DataFrame(raw_data)

if "fleet_data_store" not in st.session_state:
    st.session_state.fleet_data_store = get_base_fleet()

# ---------------------------------------------------------
# 2. FEATURE ENGINEERING & NLP SUBSYSTEM PARSING
# ---------------------------------------------------------
def parse_features(df):
    current_year = datetime.now().year
    
    # Calculate Vintage
    def get_vintage(dt):
        try:
            return max(0.5, round(current_year - pd.to_datetime(dt, errors='coerce').year, 1))
        except:
            return 5.0

    df['Vintage_Years'] = df['Dt_Induction'].apply(get_vintage)
    
    # Vintage Buckets
    df['Vintage_Category'] = df['Vintage_Years'].apply(
        lambda v: "0-5 Years" if v <= 5 else ("5-10 Years" if v <= 10 else ("10-15 Years" if v <= 15 else "15+ Years"))
    )
    
    # Mileage Buckets
    df['KM_In_Num'] = pd.to_numeric(df['KM_In'], errors='coerce').fillna(25000)
    df['Mileage_Category'] = df['KM_In_Num'].apply(
        lambda k: "0-25k KM" if k <= 25000 else ("25k-50k KM" if k <= 50000 else ("50k-75k KM" if k <= 75000 else ("75k-1 Lakh KM" if k <= 100000 else "Beyond 1 Lakh KM")))
    )

    # Subsystem & Action Classifier
    subsystems, actions, risk_scores = [], [], []
    for _, row in df.iterrows():
        d = str(row.get('Defect', '')).upper()
        r = str(row.get('Repair_Activity', '')).upper()
        
        if any(w in d for w in ['ENGINE', 'RADIATOR', 'WATER PUMP', 'FAN BELT', 'OVERHEAT', 'COOLANT']):
            sub = "Thermal & Cooling"
        elif any(w in d for w in ['GEAR', 'CLUTCH', 'AXLE', 'PROPELLER', 'DRIVE']):
            sub = "Transmission & Drivetrain"
        elif any(w in d for w in ['SPRING', 'SUSPENSION', 'HUB SEAL', 'LEAF']):
            sub = "Suspension & Running Gear"
        elif any(w in d for w in ['BRAKE', 'AIR PRESSURE', 'COMPRESS', 'BOOSTER']):
            sub = "Braking & Pneumatics"
        elif any(w in d for w in ['SWITCH', 'LIGHT', 'WIPER', 'BATTERY', 'SOLENOID', 'DOOR']):
            sub = "Electrical & Body"
        else:
            sub = "General Chassis"
            
        if any(w in r for w in ['NEW FITTED', 'REPLACED', 'CANNIBALIZED', 'FITTED', 'OVERHAUL', 'KIT']):
            act = "⚙️ Spare Part Replaced"
            risk = 35 + min(row['Vintage_Years'] * 2.5, 30)
        else:
            act = "🔧 Servicing & Adjustment"
            risk = 15 + min(row['Vintage_Years'] * 1.5, 20)
            
        subsystems.append(sub)
        actions.append(act)
        risk_scores.append(round(min(95, max(10, risk)), 1))
        
    df['Subsystem'] = subsystems
    df['Action_Type'] = actions
    df['AI_Failure_Risk_%'] = risk_scores
    df['Tactical_Status'] = df['AI_Failure_Risk_%'].apply(
        lambda r: "🟢 Mission Ready (P1)" if r < 40 else ("🟡 Field Limit (P2)" if r < 65 else "🔴 Critical Workshop Grounded (P3)")
    )
    return df

df_full = parse_features(st.session_state.fleet_data_store.copy())

# ---------------------------------------------------------
# 3. SIDEBAR CONTROLS: INGESTION, FILTERS & ADD RECORD
# ---------------------------------------------------------
st.sidebar.title("🎖️ Command Controls")

units_15 = [f"Unit {chr(65 + i)}" for i in range(15)]

# File Uploader (.xlsx / .csv)
uploaded_file = st.sidebar.file_uploader("📂 Ingest Unit Workshop File (.xlsx / .csv)", type=["xlsx", "csv"])
if uploaded_file:
    try:
        new_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        st.session_state.fleet_data_store = new_df
        st.sidebar.success("✅ New Fleet File Loaded!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error parsing file: {e}")

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filters")

sel_unit = st.sidebar.selectbox("Filter Unit (15 Units)", ["All Units"] + units_15)
sel_variant = st.sidebar.selectbox("Filter Vehicle Type", ["All Vehicles"] + sorted(list(df_full['Nomenclature'].unique())))
sel_sub = st.sidebar.selectbox("Filter Subsystem Defect", ["All Subsystems"] + sorted(list(df_full['Subsystem'].unique())))
sel_vin = st.sidebar.selectbox("Filter Vintage (Age)", ["All Vintage", "0-5 Years", "5-10 Years", "10-15 Years", "15+ Years"])
sel_mil = st.sidebar.selectbox("Filter Mileage Range", ["All Mileage", "0-25k KM", "25k-50k KM", "50k-75k KM", "75k-1 Lakh KM", "Beyond 1 Lakh KM"])

# Sidebar Form: Add New Defect Record
st.sidebar.markdown("---")
st.sidebar.subheader("➕ Add / Update Defect Record")
with st.sidebar.form("add_new_defect_form", clear_on_submit=True):
    in_unit = st.selectbox("Assigned Unit", units_15)
    in_nom = st.selectbox("Vehicle Platform", ["2.5 TON", "ALS", "5 KL W/B", "Specialist Veh"])
    in_ba = st.text_input("BA No", "22C-998811K")
    in_ind = st.text_input("Induction Date", "10-Jan-2022")
    in_km = st.number_input("Odometer (KM In)", value=28000, step=500)
    in_def = st.text_input("Defect Description", "BRAKE POOR, RADIATOR LEAKING")
    in_rep = st.text_input("Repair Activity Carried Out", "RADIATOR NEW FITTED, BRAKE ADJUSTED")
    if st.form_submit_button("Submit Record"):
        new_row = pd.DataFrame([{
            "Unit": in_unit, "Nomenclature": in_nom, "Veh_BA_No": in_ba,
            "Dt_Induction": in_ind, "Dt_In": datetime.now().strftime("%d-%b-%Y"),
            "Dt_Out": datetime.now().strftime("%d-%b-%Y"), "KM_In": in_km,
            "KM_Out": in_km + 5, "Defect": in_def, "Repair_Activity": in_rep
        }])
        st.session_state.fleet_data_store = pd.concat([st.session_state.fleet_data_store, new_row], ignore_index=True)
        st.rerun()

# Apply Filters
dff = df_full.copy()
if sel_unit != "All Units": dff = dff[dff['Unit'] == sel_unit]
if sel_variant != "All Vehicles": dff = dff[dff['Nomenclature'] == sel_variant]
if sel_sub != "All Subsystems": dff = dff[dff['Subsystem'] == sel_sub]
if sel_vin != "All Vintage": dff = dff[dff['Vintage_Category'] == sel_vin]
if sel_mil != "All Mileage": dff = dff[dff['Mileage_Category'] == sel_mil]

# ---------------------------------------------------------
# 4. TOP SUMMARY METRICS
# ---------------------------------------------------------
st.title("🎖️ Army Fleet Telematics & Predictive Maintenance Dashboard")
st.caption(f"Active Filter: **{sel_unit}** | Platform: **{sel_variant}** | Subsystem: **{sel_sub}**")

k1, k2, k3, k4, k5 = st.columns(5)
tot_v = len(dff['Veh_BA_No'].unique())
ready_v = len(dff[dff['Tactical_Status'].str.contains("🟢")])
lim_v = len(dff[dff['Tactical_Status'].str.contains("🟡")])
gnd_v = len(dff[dff['Tactical_Status'].str.contains("🔴")])
avg_risk = round(dff['AI_Failure_Risk_%'].mean(), 1) if len(dff) > 0 else 0

k1.metric("Monitored Vehicles", f"{tot_v} Vehs", f"{len(dff)} Defect Logs")
k2.metric("Avg Failure Risk", f"{avg_risk}%", "AI Risk Score")
k3.metric("🟢 Mission Ready", f"{ready_v}", f"{(ready_v/max(1, len(dff))*100):.0f}%")
k4.metric("🟡 Minor Adjustments", f"{lim_v}", "Field Fixes")
k5.metric("🔴 Workshop Grounded", f"{gnd_v}", "Awaiting Spares")

st.markdown("---")

# ---------------------------------------------------------
# 5. VISUAL ANALYTICS & INTERACTIVE TABS
# ---------------------------------------------------------
tab_analytics, tab_vm, tab_diag, tab_docket = st.tabs([
    "📊 Subsystem Defect Analytics", 
    "📈 Vintage & Mileage Analysis", 
    "🔮 AI Vehicle Diagnostics", 
    "📋 Digital Maintenance Docket (Editable)"
])

with tab_analytics:
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Subsystem Defects (By Repair Nature)")
        if not dff.empty:
            fig_sub = px.histogram(
                dff, x='Subsystem', color='Action_Type', barmode='group',
                color_discrete_map={'⚙️ Spare Part Replaced': '#ef4444', '🔧 Servicing & Adjustment': '#3b82f6'},
                title=f"Defects by Mechanical Assembly ({sel_unit} | {sel_variant})"
            )
            fig_sub.update_layout(xaxis_tickangle=-20)
            st.plotly_chart(fig_sub, use_container_width=True)
        else:
            st.info("No records matching active filters.")

    with g2:
        st.subheader("Vehicle Variant Defect Load")
        if not dff.empty:
            fig_var = px.histogram(
                dff, x='Nomenclature', color='Subsystem',
                title="Breakdown Distribution by Vehicle Platform"
            )
            st.plotly_chart(fig_var, use_container_width=True)
        else:
            st.info("No records matching active filters.")

with tab_vm:
    v1, v2 = st.columns(2)
    with v1:
        st.subheader("Mileage Range vs Defect Frequency")
        if not dff.empty:
            fig_mil = px.histogram(
                dff, x='Mileage_Category', color='Action_Type',
                category_orders={'Mileage_Category': ["0-25k KM", "25k-50k KM", "50k-75k KM", "75k-1 Lakh KM", "Beyond 1 Lakh KM"]},
                title="Odometer Mileage Stress Bands"
            )
            st.plotly_chart(fig_mil, use_container_width=True)
        else:
            st.info("No records available.")

    with v2:
        st.subheader("Vintage (Age) vs Subsystem Breakdowns")
        if not dff.empty:
            fig_vin = px.histogram(
                dff, x='Vintage_Category', color='Subsystem',
                category_orders={'Vintage_Category': ["0-5 Years", "5-10 Years", "10-15 Years", "15+ Years"]},
                title="Age-Induced Degradation Curve"
            )
            st.plotly_chart(fig_vin, use_container_width=True)
        else:
            st.info("No records available.")

with tab_diag:
    st.subheader("🔮 Individual Vehicle Audit & Failure Diagnostic")
    vehs = sorted(list(dff['Veh_BA_No'].unique()))
    if vehs:
        c_v1, c_v2 = st.columns([1, 2])
        t_veh = c_v1.selectbox("Select Target BA Number", vehs)
        v_data = dff[dff['Veh_BA_No'] == t_veh]
        
        with c_v1:
            st.info(f"""
            ### 🪖 Vehicle Profile
            * **BA Number:** `{t_veh}`
            * **Platform:** {v_data['Nomenclature'].iloc[0]}
            * **Unit:** {v_data['Unit'].iloc[0]}
            * **Vintage:** {v_data['Vintage_Years'].iloc[0]} Years
            * **Cumulative Mileage:** {int(v_data['KM_In_Num'].max()):,} KM
            * **AI Failure Probability:** **{v_data['AI_Failure_Risk_%'].iloc[-1]}%**
            * **Status:** {v_data['Tactical_Status'].iloc[-1]}
            """)
            
        with c_v2:
            st.markdown("#### 📜 Workshop History Trail")
            st.dataframe(v_data[['Dt_In', 'KM_In', 'Defect', 'Repair_Activity', 'Subsystem', 'Action_Type']], use_container_width=True)
            
            # AI Prescriptive Recommendation Logic
            text = " ".join(v_data['Defect'].tolist()).upper()
            recs = []
            if "BRAKE" in text or "PRESSURE" in text:
                recs.append("🔴 **Braking Circuit:** Repeat brake adjustment noted. Conduct pressure test on booster & unloader valve before next deployment.")
            if "SPRING" in text or "SUSPENSION" in text:
                recs.append("🟡 **Suspension Assembly:** Leaf stress flagged. Torque U-bolts and inspect rubber bump stops.")
            if "RADIATOR" in text or "ENGINE" in text or "WATER PUMP" in text:
                recs.append("🔴 **Thermal Cooling:** Temperature anomalies logged. Conduct coolant flush and thermostat check.")
            if not recs:
                recs.append("🟢 **Nominal Operation:** System operating within normal field bounds.")
                
            st.success("### 🧠 AI Maintenance Recommendation:\n" + "\n\n".join(recs))

with tab_docket:
    st.subheader("📋 Digital Maintenance Docket & Editable Job-Card")
    st.caption("Double click any cell to edit details directly, or add new rows at the bottom.")
    
    cols = ['Veh_BA_No', 'Unit', 'Nomenclature', 'Vintage_Category', 'Mileage_Category', 'KM_In', 'Defect', 'Repair_Activity', 'Subsystem', 'Action_Type', 'AI_Failure_Risk_%', 'Tactical_Status']
    
    edited_df = st.data_editor(dff[cols], num_rows="dynamic", use_container_width=True)
    
    csv_bytes = edited_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Docket (CSV)",
        data=csv_bytes,
        file_name=f"Official_Army_Fleet_Docket_{datetime.now().strftime('%d_%b_%Y')}.csv",
        mime="text/csv"
    )
