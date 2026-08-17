import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import re

# Page Configuration
st.set_page_config(
    page_title="Indian Army | Fleet Diagnostics Portal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Professional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .metric-box {
        background: #1e293b;
        padding: 16px 20px;
        border-radius: 8px;
        border: 1px solid #334155;
        border-left: 4px solid #38bdf8;
    }
    .action-card {
        background: #0f172a;
        padding: 18px;
        border-radius: 8px;
        border: 1px solid #1e293b;
        margin-bottom: 12px;
    }
    .badge-green {
        background-color: #14532d;
        color: #4ade80;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
    .badge-red {
        background-color: #7f1d1d;
        color: #f87171;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. BULLETPROOF UNIVERSAL AUTO-MAPPER (ZERO CRASHES)
# ---------------------------------------------------------
def bulletproof_load_and_clean(raw_df):
    df = raw_df.copy()
    
    # Lowercase string stripped column map
    normalized_cols = {str(c).strip().lower(): c for c in df.columns}
    
    def find_col(patterns, default_name):
        for pat in patterns:
            for clean_c, orig_c in normalized_cols.items():
                if re.search(pat, clean_c):
                    return orig_c
        return None

    # Map core columns
    c_unit = find_col([r'unit', r'regiment', r'battalion'], 'Unit')
    c_nom = find_col([r'nom', r'type', r'variant', r'make', r'model'], 'Nomenclature')
    c_ba = find_col([r'ba.*no', r'veh.*no', r'regn', r'number'], 'Veh_BA_No')
    c_ind = find_col([r'induct', r'vintage', r'yom', r'mfg'], 'Dt_Induction')
    c_km = find_col([r'km.*in', r'odometer', r'mileage'], 'KM_In')
    c_def = find_col([r'defect', r'fault', r'complaint', r'problem'], 'Defect')
    c_rep = find_col([r'repair', r'activity', r'action', r'work'], 'Repair_Activity')
    c_dt_in = find_col([r'dt.*in', r'date.*in'], 'Dt_In')
    c_dt_out = find_col([r'dt.*out', r'date.*out'], 'Dt_Out')

    # Create standard dataframe safely
    clean_dict = {}
    clean_dict['Unit'] = df[c_unit].astype(str) if c_unit else [f"Unit {chr(65 + i%15)}" for i in range(len(df))]
    clean_dict['Nomenclature'] = df[c_nom].astype(str) if c_nom else "2.5 TON"
    clean_dict['Veh_BA_No'] = df[c_ba].astype(str) if c_ba else [f"IA-{2001+i}" for i in range(len(df))]
    clean_dict['Dt_Induction'] = df[c_ind].astype(str) if c_ind else "01-Jan-2020"
    clean_dict['KM_In'] = pd.to_numeric(df[c_km], errors='coerce').fillna(25000) if c_km else 25000
    clean_dict['Defect'] = df[c_def].astype(str) if c_def else "Routine Checkup"
    clean_dict['Repair_Activity'] = df[c_rep].astype(str) if c_rep else "Servicing & Adjustments"
    clean_dict['Dt_In'] = df[c_dt_in].astype(str) if c_dt_in else "01-Jan-2024"
    clean_dict['Dt_Out'] = df[c_dt_out].astype(str) if c_dt_out else "05-Jan-2024"

    res_df = pd.DataFrame(clean_dict)
    
    # 1. Vintage Calculation
    current_year = 2026
    def extract_vintage(val):
        try:
            val_str = str(val)
            years = re.findall(r'\b(19\d\d|20\d\d)\b', val_str)
            if years:
                return max(1.0, float(current_year - int(years[-1])))
            dt = pd.to_datetime(val, errors='coerce')
            if pd.notnull(dt):
                return max(1.0, float(current_year - dt.year))
        except:
            pass
        return 5.0

    res_df['Vintage_Years'] = res_df['Dt_Induction'].apply(extract_vintage)
    res_df['Vintage_Band'] = res_df['Vintage_Years'].apply(
        lambda v: "0-5 Years" if v <= 5 else ("5-10 Years" if v <= 10 else ("10-15 Years" if v <= 15 else "15+ Years"))
    )

    # 2. Mileage Band
    res_df['KM_In_Num'] = pd.to_numeric(res_df['KM_In'], errors='coerce').fillna(25000)
    res_df['Mileage_Band'] = res_df['KM_In_Num'].apply(
        lambda k: "0-25k KM" if k <= 25000 else ("25k-50k KM" if k <= 50000 else ("50k-75k KM" if k <= 75000 else ("75k-1 Lakh KM" if k <= 100000 else "Beyond 1 Lakh KM")))
    )

    # 3. Subsystem Classification
    def categorize_subsystem(d):
        d_up = str(d).upper()
        if any(k in d_up for k in ['ENGINE', 'RADIATOR', 'WATER PUMP', 'FAN BELT', 'OVERHEAT', 'COOLANT']):
            return "Thermal & Cooling"
        elif any(k in d_up for k in ['GEAR', 'CLUTCH', 'AXLE', 'PROPELLER', 'DRIVE', 'TRANSMISSION']):
            return "Transmission & Drivetrain"
        elif any(k in d_up for k in ['SPRING', 'SUSPENSION', 'HUB SEAL', 'LEAF', 'DAMPER']):
            return "Suspension & Running Gear"
        elif any(k in d_up for k in ['BRAKE', 'AIR PRESSURE', 'COMPRESS', 'BOOSTER']):
            return "Braking & Pneumatics"
        elif any(k in d_up for k in ['SWITCH', 'LIGHT', 'WIPER', 'BATTERY', 'SOLENOID', 'DOOR']):
            return "Electrical & Body"
        return "General Chassis"

    res_df['Subsystem'] = res_df['Defect'].apply(categorize_subsystem)

    # 4. Action Type
    def categorize_action(r):
        r_up = str(r).upper()
        if any(k in r_up for k in ['NEW FITTED', 'REPLACED', 'CANNIBALIZED', 'FITTED', 'OVERHAUL', 'KIT ZF', 'FITTED']):
            return "⚙️ Part Replaced"
        return "🔧 Routine Serviced / Adjusted"

    res_df['Action_Type'] = res_df['Repair_Activity'].apply(categorize_action)

    # 5. AI Risk Score
    def calc_risk(row):
        base = 20
        if row['Action_Type'] == '⚙️ Part Replaced': base += 35
        base += min(row['Vintage_Years'] * 2.5, 25)
        base += min((row['KM_In_Num'] / 10000) * 2, 20)
        return min(95, round(base, 1))

    res_df['AI_Failure_Risk_%'] = res_df.apply(calc_risk, axis=1)
    res_df['Fleet_Status'] = res_df['AI_Failure_Risk_%'].apply(
        lambda r: "🟢 Mission Ready" if r < 50 else ("🟡 Minor Attention" if r < 70 else "🔴 Workshop Grounded")
    )

    return res_df

# ---------------------------------------------------------
# 2. DEFAULT BENCHMARK DATASET
# ---------------------------------------------------------
@st.cache_data
def load_default_data():
    raw = [
        {"Unit": "Unit A", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107753W", "Dt_Induction": "09-Jun-2021", "Dt_In": "26-Oct-2023", "Dt_Out": "28-Jan-2024", "KM_In": 22131, "Defect": "AXLE NOISY, AIR FILTER DIRTY, RADIATOR LEAKING, HUB SEAL WORN OUT", "Repair_Activity": "REPAIRED, AIR FILTER NEW FITTED, RADIATOR ASSY NEW FITTED, HUB SEAL NEW FITTED"},
        {"Unit": "Unit A", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107753W", "Dt_Induction": "09-Jun-2021", "Dt_In": "13-Nov-2023", "Dt_Out": "22-Feb-2024", "KM_In": 22238, "Defect": "ROTARY SWITCH NOT WORK, ISOLETOR SWITCH NOT WORK, AIR FILTER DIRTY, CLUTCH HARD", "Repair_Activity": "ROTARY SWITCH REPAIRED, ISOLETOR SWITCH NEW FITTED, AIR FILTER NEW FITTED, CLUTCH ADJUSTED"},
        {"Unit": "Unit B", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-2021", "Dt_In": "06-Mar-2025", "Dt_Out": "08-Mar-2025", "KM_In": 30502, "Defect": "AIR COMPRESSURE LEAK, BRAKE POOR", "Repair_Activity": "AIR COMPRESSOR CANEBLIZED FROM CL-V VEH, REAR BRAKE BOOSTER FITTED, BRAKE ADJUSTED"},
        {"Unit": "Unit B", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-2021", "Dt_In": "21-May-2025", "Dt_Out": "28-Jul-2025", "KM_In": 30732, "Defect": "VEH PULLING POWER WEAK, SOLENOID SWITCH NOT WORK", "Repair_Activity": "CLUTCH PLATE & MASTER CYLINDER NEW FITTED, SOLENOID SWITCH NEW FITTED"},
        {"Unit": "Unit C", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-2021", "Dt_In": "15-Sep-2025", "Dt_Out": "15-Sep-2025", "KM_In": 31022, "Defect": "DOOR GLASS MECHANISM NOT WORK, MAIN SWITCH NOT WORK, STEERING GEAR BOX OIL LEAKING", "Repair_Activity": "DOOR GLASS REPAIRED, CHANGE OVER SWITCH NEW FITTED, STEERING SEAL KIT ZF NEW FITTED"},
        {"Unit": "Unit D", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-2021", "Dt_In": "09-Jul-2026", "Dt_Out": "12-Jul-2026", "KM_In": 32237, "Defect": "AXLE NOISY, PROPELLER SHAFT NOISY, DOOR LOCK NOT WORK", "Repair_Activity": "AXLE REPAIRED, PROPELLER SHAFT NUT FITTED, DOOR LOCK REPAIRED"},
        {"Unit": "Unit E", "Nomenclature": "2.5 TON", "Veh_BA_No": "22C-109902P", "Dt_Induction": "24-Feb-2022", "Dt_In": "13-Nov-2025", "Dt_Out": "16-Nov-2025", "KM_In": 10847, "Defect": "ISOLATOR SWITCH NOT WORK, BRAKE POOR", "Repair_Activity": "ISOLATOR SWITCH REPAIRED, BRAKE ADJUSTED"},
        {"Unit": "Unit F", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "05-Sep-2023", "Dt_Out": "27-Oct-2023", "KM_In": 60740, "Defect": "STARTING TROUBLE", "Repair_Activity": "INJECTOR OVERHAUL & FUEL FEED PUMP REPAIRED"},
        {"Unit": "Unit G", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "10-Feb-2025", "Dt_Out": "14-Feb-2025", "KM_In": 66343, "Defect": "MAIN GEAR BOX NOISY, RADIATOR LEKING, BRAKE POOR, CABIN LIFTING PUMP NOT WORK", "Repair_Activity": "MAIN GEAR BOX SHAFT REPLACED, GAS WELDING, BRAKE ADJUSTED, RAM HYDRAULIC FITTED"},
        {"Unit": "Unit H", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "17-Apr-2025", "Dt_Out": "18-Aug-2025", "KM_In": 66487, "Defect": "ENGINE OVERHEATING, HAND BRAKE AIR PRESSURE LEAKING", "Repair_Activity": "WATER PUMP MAJOR SERVICE KIT FITTED, PRESSURE LEAKING RECTIFIED"},
        {"Unit": "Unit I", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "18-Nov-2025", "Dt_Out": "24-Feb-2026", "KM_In": 68064, "Defect": "GEAR SHIFTING HARD, STARTING TROUBLE", "Repair_Activity": "GEAR BOX SERVICING, FUEL TANK & PIPE LINE CLEANED"},
        {"Unit": "Unit J", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "19-Mar-2026", "Dt_Out": "20-Mar-2026", "KM_In": 68221, "Defect": "BRAKE POOR", "Repair_Activity": "BRAKE ADJUSTED"},
        {"Unit": "Unit K", "Nomenclature": "ALS", "Veh_BA_No": "19D-208745N", "Dt_Induction": "29-May-2019", "Dt_In": "26-Oct-2023", "Dt_Out": "26-Oct-2023", "KM_In": 27321, "Defect": "BRAKE POOR", "Repair_Activity": "BRAKE ADJUSTED"},
        {"Unit": "Unit L", "Nomenclature": "ALS", "Veh_BA_No": "19D-208745N", "Dt_Induction": "29-May-2019", "Dt_In": "14-Jan-2025", "Dt_Out": "18-Jan-2025", "KM_In": 29103, "Defect": "ROAD SPRING BROCKEN, SUSPENSION NOISY", "Repair_Activity": "ROAD SPRING LEAF & U BOLT FITTED, SUSPENSION REPAIR"},
        {"Unit": "Unit M", "Nomenclature": "ALS", "Veh_BA_No": "19D-202808W", "Dt_Induction": "29-May-2019", "Dt_In": "06-Aug-2023", "Dt_Out": "07-Aug-2023", "KM_In": 25562, "Defect": "BRAKE POOR, HEAD LIGHT NOT WORK", "Repair_Activity": "BRAKE ADJUSTED, HEAD LIGHT REPAIRED"},
        {"Unit": "Unit N", "Nomenclature": "ALS", "Veh_BA_No": "19D-202808W", "Dt_Induction": "29-May-2019", "Dt_In": "24-Aug-2023", "Dt_Out": "24-Aug-2023", "KM_In": 26020, "Defect": "ROAD SPRING BROCKEN", "Repair_Activity": "ROAD SPRING NO.6 LEAF NEW FITTED"},
        {"Unit": "Unit O", "Nomenclature": "5 KL W/B", "Veh_BA_No": "14P-029330Y", "Dt_Induction": "16-Jun-2014", "Dt_In": "01-Jul-2025", "Dt_Out": "01-Jul-2025", "KM_In": 21800, "Defect": "FAN BELT BROCKEN, WATER PUMP NOT WORK", "Repair_Activity": "FAN BELT NEW FITTED, WATER PUMP REPAIRED"}
    ]
    return pd.DataFrame(raw)

if "fleet_storage" not in st.session_state:
    st.session_state.fleet_storage = load_default_data()

# ---------------------------------------------------------
# 3. SIDEBAR: UPLOADER & MULTI-FILTERS
# ---------------------------------------------------------
st.sidebar.title("🎖️ Army Fleet Command")
st.sidebar.caption("Tactical Decision Support & Telematics")

# Flexible Upload
file_up = st.sidebar.file_uploader("📂 Ingest Workshop Log Sheet (.xlsx / .csv)", type=["xlsx", "csv"])
if file_up:
    try:
        new_df = pd.read_csv(file_up) if file_up.name.endswith('.csv') else pd.read_excel(file_up)
        st.session_state.fleet_storage = new_df
        st.sidebar.success("✅ Log File Successfully Ingested!")
    except Exception as e:
        st.sidebar.error(f"Upload error: {e}")

# Process entire dataset with bulletproof cleaner
df_full = bulletproof_load_and_clean(st.session_state.fleet_storage)

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filters")

units_15 = [f"Unit {chr(65 + i)}" for i in range(15)]
sel_unit = st.sidebar.selectbox("Filter Formation / Unit", ["All Units"] + units_15)
sel_nom = st.sidebar.selectbox("Filter Vehicle Variant", ["All Vehicles"] + sorted(list(df_full['Nomenclature'].unique())))
sel_sub = st.sidebar.selectbox("Filter Subsystem Defect", ["All Subsystems"] + sorted(list(df_full['Subsystem'].unique())))
sel_vin = st.sidebar.selectbox("Filter Vintage (Age)", ["All Vintage", "0-5 Years", "5-10 Years", "10-15 Years", "15+ Years"])
sel_mil = st.sidebar.selectbox("Filter Mileage Band", ["All Mileage", "0-25k KM", "25k-50k KM", "50k-75k KM", "75k-1 Lakh KM", "Beyond 1 Lakh KM"])

# Apply Filters
dff = df_full.copy()
if sel_unit != "All Units": dff = dff[dff['Unit'] == sel_unit]
if sel_nom != "All Vehicles": dff = dff[dff['Nomenclature'] == sel_nom]
if sel_sub != "All Subsystems": dff = dff[dff['Subsystem'] == sel_sub]
if sel_vin != "All Vintage": dff = dff[dff['Vintage_Band'] == sel_vin]
if sel_mil != "All Mileage": dff = dff[dff['Mileage_Band'] == sel_mil]

# Add Record Form
st.sidebar.markdown("---")
st.sidebar.subheader("➕ Quick Defect Entry")
with st.sidebar.form("quick_add_form", clear_on_submit=True):
    q_unit = st.selectbox("Unit", units_15)
    q_nom = st.selectbox("Vehicle Platform", ["2.5 TON", "ALS", "5 KL W/B", "Specialist Veh"])
    q_ba = st.text_input("BA No", "22C-998811K")
    q_ind = st.text_input("Induction Date", "10-Jan-2022")
    q_km = st.number_input("Odometer (KM In)", value=28000, step=500)
    q_def = st.text_input("Defect", "BRAKE POOR, RADIATOR LEAKING")
    q_rep = st.text_input("Repair Work Done", "RADIATOR NEW FITTED, BRAKE ADJUSTED")
    if st.form_submit_button("Add Entry"):
        row = pd.DataFrame([{"Unit": q_unit, "Nomenclature": q_nom, "Veh_BA_No": q_ba, "Dt_Induction": q_ind, "KM_In": q_km, "Defect": q_def, "Repair_Activity": q_rep}])
        st.session_state.fleet_storage = pd.concat([st.session_state.fleet_storage, row], ignore_index=True)
        st.rerun()

# ---------------------------------------------------------
# 4. EXECUTIVE DASHBOARD & SUMMARY CARDS
# ---------------------------------------------------------
st.title("🛡️ Indian Army Fleet Diagnostics & Telematics")
st.caption(f"Active Filter: **{sel_unit}** | Platform: **{sel_nom}** | Subsystem: **{sel_sub}**")

k1, k2, k3, k4 = st.columns(4)
n_vehs = len(dff['Veh_BA_No'].unique())
n_logs = len(dff)
n_parts = len(dff[dff['Action_Type'] == '⚙️ Part Replaced'])
n_serv = len(dff[dff['Action_Type'] == '🔧 Routine Serviced / Adjusted'])

k1.metric("Formation Fleet Size", f"{n_vehs} Vehicles", f"{n_logs} Total Logs")
k2.metric("Component Failures", f"{n_parts} Incidents", "Parts Replaced")
k3.metric("Routine Field Fixes", f"{n_serv} Incidents", "Adjusted / Serviced")
k4.metric("Avg Failure Risk", f"{dff['AI_Failure_Risk_%'].mean():.1f}%" if n_logs > 0 else "0%", "Health Index")

st.markdown("---")

# ---------------------------------------------------------
# 5. USER-FRIENDLY VISUAL GRAPHS (CLEAN HIGH CONTRAST)
# ---------------------------------------------------------
tab_charts, tab_predict, tab_docket = st.tabs([
    "📊 Subsystem & Mileage Analytics", 
    "🔮 AI Predictive Action & Vehicle Audit", 
    "📋 Digital Maintenance Docket (Editable)"
])

with tab_charts:
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Subsystem Defect Load (By Repair Nature)")
        if not dff.empty:
            sub_agg = dff.groupby(['Subsystem', 'Action_Type']).size().reset_index(name='Defect Count')
            fig_sub = px.bar(
                sub_agg,
                x='Subsystem',
                y='Defect Count',
                color='Action_Type',
                barmode='group',
                color_discrete_map={
                    '⚙️ Part Replaced': '#ef4444',
                    '🔧 Routine Serviced / Adjusted': '#38bdf8'
                },
                text='Defect Count'
            )
            fig_sub.update_layout(
                xaxis_title="",
                yaxis_title="Incident Count",
                legend_title="",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_sub, use_container_width=True)
        else:
            st.info("No matching records found for active filters.")

    with c2:
        st.subheader("Mileage Range Failure Frequency")
        if not dff.empty:
            mil_agg = dff.groupby(['Mileage_Band', 'Nomenclature']).size().reset_index(name='Incidents')
            fig_mil = px.bar(
                mil_agg,
                x='Mileage_Band',
                y='Incidents',
                color='Nomenclature',
                barmode='stack',
                category_orders={'Mileage_Band': ["0-25k KM", "25k-50k KM", "50k-75k KM", "75k-1 Lakh KM", "Beyond 1 Lakh KM"]},
                text='Incidents'
            )
            fig_mil.update_layout(
                xaxis_title="",
                yaxis_title="Incidents",
                legend_title="",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_mil, use_container_width=True)
        else:
            st.info("No records matching active filters.")

# ---------------------------------------------------------
# 6. CLEAR AI PREDICTIVE ACTION BLOCK (ACTIONABLE)
# ---------------------------------------------------------
with tab_predict:
    st.subheader("🔮 Individual Vehicle Health Audit & Action Recommendations")
    
    vehs_list = sorted(list(dff['Veh_BA_No'].unique()))
    if vehs_list:
        p_col1, p_col2 = st.columns([1, 2])
        
        target_veh = p_col1.selectbox("Select Vehicle BA No", vehs_list)
        v_rows = dff[dff['Veh_BA_No'] == target_veh]
        
        with p_col1:
            st.markdown(f"""
            <div class="metric-box">
                <h4 style="margin:0 0 10px 0; color:#38bdf8;">🪖 Vehicle Identity</h4>
                <p><b>BA Number:</b> <code>{target_veh}</code></p>
                <p><b>Platform:</b> {v_rows['Nomenclature'].iloc[0]}</p>
                <p><b>Assigned Unit:</b> {v_rows['Unit'].iloc[0]}</p>
                <p><b>Vintage (Age):</b> {v_rows['Vintage_Years'].iloc[0]} Years</p>
                <p><b>Odometer:</b> {int(v_rows['KM_In_Num'].max()):,} KM</p>
                <p><b>Failure Probability:</b> <span style="color:#ef4444; font-weight:700;">{v_rows['AI_Failure_Risk_%'].iloc[-1]}%</span></p>
                <p><b>Fleet Status:</b> {v_rows['Fleet_Status'].iloc[-1]}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with p_col2:
            st.markdown("#### 🛠️ AI Prescriptive Action Directives")
            
            # Simple & Clear AI Reasoning Block
            all_def = " ".join(v_rows['Defect'].tolist()).upper()
            
            actions_found = []
            if "BRAKE" in all_def or "PRESSURE" in all_def or "BOOSTER" in all_def:
                actions_found.append({
                    "title": "Braking & Pneumatic Circuit Deterioration",
                    "root_cause": "Frequent brake adjustments and pressure drops logged. Indicates worn booster diaphragm or master cylinder bypass.",
                    "action": "Conduct immediate booster pressure bench test. Overhaul front/rear brake shoes before long-haul convoy deployment.",
                    "urgency": "🔴 High Priority (Immediate Workshop Overhaul)"
                })
            if "SPRING" in all_def or "SUSPENSION" in all_def or "AXLE" in all_def:
                actions_found.append({
                    "title": "Suspension & Running Gear Fatigue",
                    "root_cause": "Road spring leaf breakage / noisy axle recorded. Indicates high stress under cross-country terrain payload.",
                    "action": "Torque U-bolts to factory specs. Check rubber bump stops and inspect damper bushings.",
                    "urgency": "🟡 Medium Priority (Unit Field Inspection)"
                })
            if "RADIATOR" in all_def or "ENGINE" in all_def or "WATER PUMP" in all_def or "FAN BELT" in all_def:
                actions_found.append({
                    "title": "Thermal Cooling System Vulnerability",
                    "root_cause": "Coolant leaks and starting trouble logged. High risk of engine seizure in extreme ambient temperatures.",
                    "action": "Flush radiator circuit, replace water pump service kit, and tighten PTO belt tensioner pulley.",
                    "urgency": "🔴 High Priority (Preventive Component Replacement)"
                })
            if not actions_found:
                actions_found.append({
                    "title": "Nominal Operating State",
                    "root_cause": "No chronic failure patterns detected in historical telemetry logs.",
                    "action": "Proceed with standard 5,000 KM lubrication and fluid top-up schedule.",
                    "urgency": "🟢 Normal Routine"
                })

            for act in actions_found:
                st.markdown(f"""
                <div class="action-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <h4 style="margin:0; color:#f1f5f9;">{act['title']}</h4>
                        <span style="font-size:12px; font-weight:600;">{act['urgency']}</span>
                    </div>
                    <p style="margin:4px 0; color:#94a3b8; font-size:14px;"><b>⚠️ Root Cause:</b> {act['root_cause']}</p>
                    <p style="margin:4px 0; color:#38bdf8; font-size:14px;"><b>✅ Required Action:</b> {act['action']}</p>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("#### 📜 Chronological Workshop Defect History")
            st.dataframe(
                v_rows[['Dt_In', 'KM_In', 'Defect', 'Repair_Activity', 'Subsystem', 'Action_Type']], 
                use_container_width=True
            )

# ---------------------------------------------------------
# 7. EDITABLE DOCKET & EXPORT
# ---------------------------------------------------------
with tab_docket:
    st.subheader("📋 Digital Maintenance Docket & Editable Job-Card")
    st.caption("Double-click cells to modify, add new entries, or export the filtered docket directly.")
    
    cols_to_show = ['Veh_BA_No', 'Unit', 'Nomenclature', 'Vintage_Band', 'Mileage_Band', 'KM_In', 'Defect', 'Repair_Activity', 'Subsystem', 'Action_Type', 'AI_Failure_Risk_%', 'Fleet_Status']
    
    edited_data = st.data_editor(dff[cols_to_show], num_rows="dynamic", use_container_width=True)
    
    csv_bytes = edited_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Official Maintenance Docket (CSV)",
        data=csv_bytes,
        file_name=f"Army_Maintenance_Docket_{datetime.now().strftime('%d_%b_%Y')}.csv",
        mime="text/csv"
    )
