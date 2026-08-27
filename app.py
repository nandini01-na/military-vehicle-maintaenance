import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import re

# 1. PAGE CONFIG & FORCED GLOBAL THEME
st.set_page_config(
    page_title="Indian Army | Fleet Diagnostics Portal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. BULLETPROOF CSS (IDENTICAL ACROSS ALL BROWSERS & LIGHT/DARK MODES)
st.markdown("""
<style>
    /* Force exact base background and text color on all devices */
    .stApp {
        background-color: #0e1117 !important;
        color: #f8fafc !important;
    }
    
    /* Metrics Box - Fixed Colors */
    .metric-card-fixed {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-left: 4px solid #38bdf8 !important;
        padding: 16px !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important;
    }
    .metric-title {
        color: #94a3b8 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        margin-bottom: 4px !important;
    }
    .metric-value {
        color: #f8fafc !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        margin-bottom: 4px !important;
    }
    .metric-sub {
        font-size: 12px !important;
        font-weight: 600 !important;
    }

    /* AI Directive Cards - Fixed Colors */
    .action-card-fixed {
        background-color: #1e293b !important;
        border: 1px solid #475569 !important;
        padding: 14px 18px !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
    }
    .action-card-title {
        color: #f8fafc !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        margin: 0 0 6px 0 !important;
    }
    .action-card-cause {
        color: #cbd5e1 !important;
        font-size: 13px !important;
        margin: 4px 0 !important;
    }
    .action-card-sol {
        color: #38bdf8 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        margin: 4px 0 !important;
    }

    /* Tab bar headers visible everywhere */
    .stTabs [data-baseweb="tab"] {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom-color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. DEFAULT RULES STORE
# ---------------------------------------------------------
default_rules = [
    {
        "Keywords": "BRAKE, AIR PRESSURE, BOOSTER",
        "Subsystem": "Braking & Pneumatics",
        "Root_Cause": "Air pressure leakage / booster diaphragm fatigue under heavy payload.",
        "Action_Directive": "Perform booster bench test & overhaul brake shoe lining.",
        "Urgency": "🔴 High Priority"
    },
    {
        "Keywords": "RADIATOR, ENGINE, WATER PUMP, COOLANT, OVERHEAT",
        "Subsystem": "Thermal & Cooling",
        "Root_Cause": "Coolant leakage & thermal stress in extreme ambient temperatures.",
        "Action_Directive": "Flush radiator circuit & replace water pump major service kit.",
        "Urgency": "🔴 High Priority"
    },
    {
        "Keywords": "SPRING, SUSPENSION, LEAF, AXLE",
        "Subsystem": "Suspension & Running Gear",
        "Root_Cause": "Cross-country terrain payload fatigue on suspension leaves.",
        "Action_Directive": "Re-torque U-bolts to factory specs & inspect rubber bump stops.",
        "Urgency": "🟡 Medium Priority"
    },
    {
        "Keywords": "GEAR, CLUTCH, PROPELLER, TRANSMISSION",
        "Subsystem": "Transmission & Drivetrain",
        "Root_Cause": "Clutch plate slip / gearbox shaft excessive play.",
        "Action_Directive": "Overhaul clutch master cylinder & conduct gearbox servicing.",
        "Urgency": "🔴 High Priority"
    }
]

if "co_rules" not in st.session_state:
    st.session_state.co_rules = pd.DataFrame(default_rules)

if "risk_threshold_high" not in st.session_state:
    st.session_state.risk_threshold_high = 65
if "risk_threshold_med" not in st.session_state:
    st.session_state.risk_threshold_med = 40

# ---------------------------------------------------------
# 4. BULLETPROOF DATA INGESTION & CLEANER
# ---------------------------------------------------------
def bulletproof_clean(raw_df):
    df = raw_df.copy()
    norm_cols = {str(c).strip().lower(): c for c in df.columns}
    
    def find_col(patterns):
        for pat in patterns:
            for clean_c, orig_c in norm_cols.items():
                if re.search(pat, clean_c):
                    return orig_c
        return None

    c_unit = find_col([r'unit', r'regiment'])
    c_nom = find_col([r'nom', r'type', r'variant', r'make'])
    c_ba = find_col([r'ba.*no', r'veh.*no', r'number'])
    c_ind = find_col([r'induct', r'vintage', r'yom'])
    c_km = find_col([r'km.*in', r'odometer', r'mileage'])
    c_def = find_col([r'defect', r'fault', r'complaint'])
    c_rep = find_col([r'repair', r'activity', r'action'])
    c_dt_in = find_col([r'dt.*in', r'date.*in'])
    c_dt_out = find_col([r'dt.*out', r'date.*out'])

    clean_dict = {
        'Unit': df[c_unit].astype(str) if c_unit else [f"Unit {chr(65 + i%15)}" for i in range(len(df))],
        'Nomenclature': df[c_nom].astype(str) if c_nom else "2.5 TON",
        'Veh_BA_No': df[c_ba].astype(str) if c_ba else [f"IA-{2001+i}" for i in range(len(df))],
        'Dt_Induction': df[c_ind].astype(str) if c_ind else "01-Jan-2020",
        'KM_In': pd.to_numeric(df[c_km], errors='coerce').fillna(25000) if c_km else 25000,
        'Defect': df[c_def].astype(str) if c_def else "Routine Checkup",
        'Repair_Activity': df[c_rep].astype(str) if c_rep else "Servicing & Adjustments",
        'Dt_In': df[c_dt_in].astype(str) if c_dt_in else "01-Jan-2024",
        'Dt_Out': df[c_dt_out].astype(str) if c_dt_out else "05-Jan-2024"
    }
    res_df = pd.DataFrame(clean_dict)
    
    # Vintage
    def extract_vintage(val):
        try:
            years = re.findall(r'\b(19\d\d|20\d\d)\b', str(val))
            if years: return max(1.0, float(2026 - int(years[-1])))
            dt = pd.to_datetime(val, errors='coerce')
            if pd.notnull(dt): return max(1.0, float(2026 - dt.year))
        except: pass
        return 5.0

    res_df['Vintage_Years'] = res_df['Dt_Induction'].apply(extract_vintage)
    res_df['Vintage_Band'] = res_df['Vintage_Years'].apply(
        lambda v: "0-5 Years" if v <= 5 else ("5-10 Years" if v <= 10 else ("10-15 Years" if v <= 15 else "15+ Years"))
    )

    # Mileage
    res_df['KM_In_Num'] = pd.to_numeric(res_df['KM_In'], errors='coerce').fillna(25000)
    res_df['Mileage_Band'] = res_df['KM_In_Num'].apply(
        lambda k: "0-25k KM" if k <= 25000 else ("25k-50k KM" if k <= 50000 else ("50k-75k KM" if k <= 75000 else ("75k-1 Lakh KM" if k <= 100000 else "Beyond 1 Lakh KM")))
    )

    # Subsystem mapping via rules
    def match_subsystem(d):
        d_up = str(d).upper()
        for _, r in st.session_state.co_rules.iterrows():
            kws = [k.strip().upper() for k in str(r['Keywords']).split(',')]
            if any(kw in d_up for kw in kws if kw):
                return r['Subsystem']
        return "General Chassis"

    res_df['Subsystem'] = res_df['Defect'].apply(match_subsystem)

    # Action nature
    res_df['Action_Type'] = res_df['Repair_Activity'].apply(
        lambda r: "⚙️ Part Replaced" if any(k in str(r).upper() for k in ['NEW FITTED', 'REPLACED', 'CANNIBALIZED', 'FITTED', 'OVERHAUL', 'KIT']) else "🔧 Routine Serviced / Adjusted"
    )

    # Failure Risk
    def calc_risk(row):
        base = 20
        if row['Action_Type'] == '⚙️ Part Replaced': base += 35
        base += min(row['Vintage_Years'] * 2.5, 25)
        base += min((row['KM_In_Num'] / 10000) * 2, 20)
        return min(95, round(base, 1))

    res_df['AI_Failure_Risk_%'] = res_df.apply(calc_risk, axis=1)
    
    h_th = st.session_state.risk_threshold_high
    m_th = st.session_state.risk_threshold_med
    res_df['Fleet_Status'] = res_df['AI_Failure_Risk_%'].apply(
        lambda r: "🔴 Workshop Grounded" if r >= h_th else ("🟡 Minor Attention" if r >= m_th else "🟢 Mission Ready")
    )
    return res_df

# ---------------------------------------------------------
# 5. DATA STORE
# ---------------------------------------------------------
@st.cache_data
def get_default_data():
    raw = [
        {"Unit": "Unit A", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107753W", "Dt_Induction": "09-Jun-2021", "Dt_In": "26-Oct-2023", "Dt_Out": "28-Jan-2024", "KM_In": 22131, "Defect": "AXLE NOISY, AIR FILTER DIRTY, RADIATOR LEAKING, HUB SEAL WORN OUT", "Repair_Activity": "REPAIRED, AIR FILTER NEW FITTED, RADIATOR ASSY NEW FITTED, HUB SEAL NEW FITTED"},
        {"Unit": "Unit B", "Nomenclature": "2.5 TON", "Veh_BA_No": "19C-107906X", "Dt_Induction": "09-Jun-2021", "Dt_In": "06-Mar-2025", "Dt_Out": "08-Mar-2025", "KM_In": 30502, "Defect": "AIR COMPRESSURE LEAK, BRAKE POOR", "Repair_Activity": "AIR COMPRESSOR CANEBLIZED FROM CL-V VEH, REAR BRAKE BOOSTER FITTED, BRAKE ADJUSTED"},
        {"Unit": "Unit C", "Nomenclature": "2.5 TON", "Veh_BA_No": "22C-109902P", "Dt_Induction": "24-Feb-2022", "Dt_In": "13-Nov-2025", "Dt_Out": "16-Nov-2025", "KM_In": 10847, "Defect": "ISOLATOR SWITCH NOT WORK, BRAKE POOR", "Repair_Activity": "ISOLATOR SWITCH REPAIRED, BRAKE ADJUSTED"},
        {"Unit": "Unit D", "Nomenclature": "ALS", "Veh_BA_No": "13D-192836W", "Dt_Induction": "20-Aug-2014", "Dt_In": "05-Sep-2023", "Dt_Out": "27-Oct-2023", "KM_In": 60740, "Defect": "STARTING TROUBLE, MAIN GEAR BOX NOISY", "Repair_Activity": "INJECTOR OVERHAUL, GEAR BOX MAIN SHAFT REPLACED"},
        {"Unit": "Unit E", "Nomenclature": "ALS", "Veh_BA_No": "19D-208745N", "Dt_Induction": "29-May-2019", "Dt_In": "14-Jan-2025", "Dt_Out": "18-Jan-2025", "KM_In": 29103, "Defect": "ROAD SPRING BROCKEN, SUSPENSION NOISY", "Repair_Activity": "ROAD SPRING LEAF & U BOLT FITTED"},
        {"Unit": "Unit G", "Nomenclature": "5 KL W/B", "Veh_BA_No": "14P-029330Y", "Dt_Induction": "16-Jun-2014", "Dt_In": "01-Jul-2025", "Dt_Out": "01-Jul-2025", "KM_In": 21800, "Defect": "FAN BELT BROCKEN, WATER PUMP NOT WORK", "Repair_Activity": "FAN BELT NEW FITTED, WATER PUMP REPAIRED"}
    ]
    return pd.DataFrame(raw)

if "fleet_storage" not in st.session_state:
    st.session_state.fleet_storage = get_default_data()

# ---------------------------------------------------------
# 6. SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.title("🎖️ Command Controls")

file_up = st.sidebar.file_uploader("📂 Ingest Workshop Log (.xlsx / .csv)", type=["xlsx", "csv"])
if file_up:
    try:
        new_df = pd.read_csv(file_up) if file_up.name.endswith('.csv') else pd.read_excel(file_up)
        st.session_state.fleet_storage = new_df
        st.sidebar.success("✅ Log File Loaded!")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

df_full = bulletproof_clean(st.session_state.fleet_storage)

units_15 = [f"Unit {chr(65 + i)}" for i in range(15)]
sel_unit = st.sidebar.selectbox("Formation / Unit", ["All Units"] + units_15)
sel_nom = st.sidebar.selectbox("Vehicle Variant", ["All Vehicles"] + sorted(list(df_full['Nomenclature'].unique())))
sel_sub = st.sidebar.selectbox("Subsystem", ["All Subsystems"] + sorted(list(df_full['Subsystem'].unique())))

dff = df_full.copy()
if sel_unit != "All Units": dff = dff[dff['Unit'] == sel_unit]
if sel_nom != "All Vehicles": dff = dff[dff['Nomenclature'] == sel_nom]
if sel_sub != "All Subsystems": dff = dff[dff['Subsystem'] == sel_sub]

# ---------------------------------------------------------
# 7. MAIN HEADER & FIXED CONTRAST KPIS
# ---------------------------------------------------------
st.title("🛡️ Indian Army Fleet Diagnostics & Telematics")
st.caption(f"Active Unit: **{sel_unit}** | Platform: **{sel_nom}** | Subsystem: **{sel_sub}**")

k1, k2, k3, k4 = st.columns(4)
n_vehs = len(dff['Veh_BA_No'].unique())
n_logs = len(dff)
n_parts = len(dff[dff['Action_Type'] == '⚙️ Part Replaced'])
n_serv = len(dff[dff['Action_Type'] == '🔧 Routine Serviced / Adjusted'])
avg_r = f"{dff['AI_Failure_Risk_%'].mean():.1f}%" if n_logs > 0 else "0%"

with k1:
    st.markdown(f"""<div class="metric-card-fixed"><div class="metric-title">Formation Fleet Size</div><div class="metric-value">{n_vehs} Vehs</div><div class="metric-sub" style="color:#38bdf8;">{n_logs} Total Logs</div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="metric-card-fixed" style="border-left-color:#ef4444 !important;"><div class="metric-title">Component Failures</div><div class="metric-value">{n_parts}</div><div class="metric-sub" style="color:#f87171;">Parts Replaced</div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="metric-card-fixed" style="border-left-color:#38bdf8 !important;"><div class="metric-title">Routine Field Fixes</div><div class="metric-value">{n_serv}</div><div class="metric-sub" style="color:#38bdf8;">Adjusted / Serviced</div></div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="metric-card-fixed" style="border-left-color:#f59e0b !important;"><div class="metric-title">Avg Failure Risk</div><div class="metric-value">{avg_r}</div><div class="metric-sub" style="color:#f59e0b;">Tactical Health Index</div></div>""", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# 8. VISUAL ANALYTICS & HIGH-CONTRAST TABS
# ---------------------------------------------------------
tab_charts, tab_predict, tab_docket, tab_admin = st.tabs([
    "📊 Subsystem & Mileage Analytics", 
    "🔮 AI Predictive Action & Vehicle Audit", 
    "📋 Digital Maintenance Docket",
    "⚙️ CO Command & Rules Backend"
])

with tab_charts:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Subsystem Defect Load")
        if not dff.empty:
            sub_agg = dff.groupby(['Subsystem', 'Action_Type']).size().reset_index(name='Count')
            fig_sub = px.bar(
                sub_agg, x='Subsystem', y='Count', color='Action_Type', barmode='group',
                color_discrete_map={'⚙️ Part Replaced': '#ef4444', '🔧 Routine Serviced / Adjusted': '#38bdf8'},
                text='Count'
            )
            # Force dark solid background & white fonts for Plotly
            fig_sub.update_layout(
                plot_bgcolor='#1e293b', paper_bgcolor='#1e293b',
                font=dict(color='#f8fafc'), xaxis=dict(color='#cbd5e1', gridcolor='#334155'),
                yaxis=dict(color='#cbd5e1', gridcolor='#334155'), legend=dict(font=dict(color='#f8fafc'))
            )
            st.plotly_chart(fig_sub, use_container_width=True)
    with c2:
        st.subheader("Mileage Range Distribution")
        if not dff.empty:
            mil_agg = dff.groupby(['Mileage_Band', 'Nomenclature']).size().reset_index(name='Incidents')
            fig_mil = px.bar(
                mil_agg, x='Mileage_Band', y='Incidents', color='Nomenclature',
                category_orders={'Mileage_Band': ["0-25k KM", "25k-50k KM", "50k-75k KM", "75k-1 Lakh KM", "Beyond 1 Lakh KM"]},
                text='Incidents'
            )
            fig_mil.update_layout(
                plot_bgcolor='#1e293b', paper_bgcolor='#1e293b',
                font=dict(color='#f8fafc'), xaxis=dict(color='#cbd5e1', gridcolor='#334155'),
                yaxis=dict(color='#cbd5e1', gridcolor='#334155'), legend=dict(font=dict(color='#f8fafc'))
            )
            st.plotly_chart(fig_mil, use_container_width=True)

with tab_predict:
    vehs_list = sorted(list(dff['Veh_BA_No'].unique()))
    if vehs_list:
        p1, p2 = st.columns([1, 2])
        target_veh = p1.selectbox("Select Target BA Number", vehs_list)
        v_rows = dff[dff['Veh_BA_No'] == target_veh]
        
        with p1:
            st.markdown(f"""
            <div class="metric-card-fixed">
                <div class="metric-title" style="color:#38bdf8 !important; font-size:15px !important; font-weight:700 !important;">🪖 Vehicle Identity</div>
                <p style="color:#cbd5e1; margin:4px 0;"><b>BA No:</b> <code style="color:#38bdf8;">{target_veh}</code></p>
                <p style="color:#cbd5e1; margin:4px 0;"><b>Platform:</b> {v_rows['Nomenclature'].iloc[0]}</p>
                <p style="color:#cbd5e1; margin:4px 0;"><b>Unit:</b> {v_rows['Unit'].iloc[0]}</p>
                <p style="color:#cbd5e1; margin:4px 0;"><b>Vintage:</b> {v_rows['Vintage_Years'].iloc[0]} Years</p>
                <p style="color:#cbd5e1; margin:4px 0;"><b>Odometer:</b> {int(v_rows['KM_In_Num'].max()):,} KM</p>
                <p style="color:#cbd5e1; margin:4px 0;"><b>Failure Risk:</b> <b style="color:#ef4444;">{v_rows['AI_Failure_Risk_%'].iloc[-1]}%</b></p>
                <p style="color:#cbd5e1; margin:4px 0;"><b>Status:</b> {v_rows['Fleet_Status'].iloc[-1]}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with p2:
            st.markdown("#### 🛠️ AI Prescriptive Action Directives")
            def_text = " ".join(v_rows['Defect'].tolist()).upper()
            
            matched = False
            for _, rule in st.session_state.co_rules.iterrows():
                kws = [k.strip().upper() for k in str(rule['Keywords']).split(',')]
                if any(k in def_text for k in kws if k):
                    matched = True
                    st.markdown(f"""
                    <div class="action-card-fixed">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div class="action-card-title">{rule['Subsystem']}</div>
                            <span style="font-weight:700; font-size:12px;">{rule['Urgency']}</span>
                        </div>
                        <div class="action-card-cause"><b>⚠️ Root Cause:</b> {rule['Root_Cause']}</div>
                        <div class="action-card-sol"><b>✅ Required Workshop Action:</b> {rule['Action_Directive']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            if not matched:
                st.info("System operating within nominal field tolerances. Standard routine service applies.")

with tab_docket:
    st.subheader("📋 Digital Maintenance Docket")
    cols_show = ['Veh_BA_No', 'Unit', 'Nomenclature', 'Vintage_Band', 'Mileage_Band', 'KM_In', 'Defect', 'Repair_Activity', 'Subsystem', 'Action_Type', 'AI_Failure_Risk_%', 'Fleet_Status']
    edited_data = st.data_editor(dff[cols_show], num_rows="dynamic", use_container_width=True)
    st.download_button("📥 Download Official Docket (CSV)", edited_data.to_csv(index=False).encode('utf-8'), "Army_Maintenance_Docket.csv", "text/csv")

with tab_admin:
    st.subheader("⚙️ Commanding Officer — System Rules & Action Configurator")
    st.caption("As Commanding Officer, you can modify failure trigger keywords, prescriptive action orders, and risk thresholds below.")

    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.session_state.risk_threshold_high = st.slider("🔴 High Risk / Workshop Grounded Threshold (%)", 50, 90, st.session_state.risk_threshold_high)
    with r_col2:
        st.session_state.risk_threshold_med = st.slider("🟡 Medium Risk / Minor Attention Threshold (%)", 20, 60, st.session_state.risk_threshold_med)

    st.markdown("#### 📜 Live Prescriptive Action Rules Matrix")
    updated_rules = st.data_editor(st.session_state.co_rules, num_rows="dynamic", use_container_width=True)
    st.session_state.co_rules = updated_rules
