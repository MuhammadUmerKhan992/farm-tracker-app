import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime

# --- 1. System Config & UI Theme ---
st.set_page_config(page_title="Makhdoom Farms Enterprise", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    h1, h2, h3, h4 { color: #4DA8DA; }
    div.stButton > button:first-child { background-color: #12232E; color: #4DA8DA; border: 1px solid #4DA8DA; }
    div.stButton > button:first-child:hover { background-color: #4DA8DA; color: #12232E; }
    .st-bb { border-bottom-color: #4DA8DA; }
    </style>
""", unsafe_allow_html=True)

# --- 2. Advanced Data Engine (Time-Series Architecture) ---
PROFILES_FILE = 'makhdoom_profiles.json'
LOGS_FILE = 'makhdoom_logs.json'
CONFIG_FILE = 'makhdoom_configs.json'

def load_json(file_path, default_data):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except: return default_data
    return default_data

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f)

# Initialize states
if 'profiles' not in st.session_state:
    st.session_state['profiles'] = load_json(PROFILES_FILE, [])
if 'logs' not in st.session_state:
    st.session_state['logs'] = load_json(LOGS_FILE, [])
if 'configs' not in st.session_state:
    st.session_state['configs'] = load_json(CONFIG_FILE, {
        "Cow": ["Weight (kg)", "Milk Yield (Liters)", "Vaccination"],
        "Sheep": ["Weight (kg)", "Wool Quality Rating"]
    })

# --- 3. Main Navigation ---
st.title("🚜 Makhdoom Farms Enterprise System")
menu = st.sidebar.radio("Command Center:", [
    "Overview Dashboard", 
    "Animal Registry", 
    "Log Daily Progress", 
    "Progress Tracker (Analytics)", 
    "System Settings"
])

# --- PAGE 1: OVERVIEW DASHBOARD ---
if menu == "Overview Dashboard":
    st.header("🗃️ Farm Operations Center")
    if not st.session_state['profiles']:
        st.info("System empty. Register your first animal in the 'Animal Registry'.")
    else:
        df_profiles = pd.DataFrame(st.session_state['profiles'])
        
        # High-level metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Livestock", len(df_profiles))
        c2.metric("Total Categories", df_profiles['Type'].nunique())
        c3.metric("Total Data Logs", len(st.session_state['logs']))
        c4.metric("System Status", "Online")
        
        st.divider()
        st.subheader("📋 Active Animal Roster")
        st.dataframe(df_profiles, use_container_width=True, hide_index=True)

# --- PAGE 2: ANIMAL REGISTRY (Add/Delete Profiles) ---
elif menu == "Animal Registry":
    st.header("📋 Animal Profile Registry")
    
    tab1, tab2 = st.tabs(["Register New Animal", "Remove Animal"])
    
    with tab1:
        types = list(st.session_state['configs'].keys())
        if not types:
            st.warning("Configure animal categories in System Settings first.")
        else:
            with st.form("register_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    a_id = st.text_input("Official Tag / ID (Required)")
                    a_type = st.selectbox("Species/Category", types)
                with col2:
                    a_breed = st.text_input("Breed / Lineage")
                    a_dob = st.date_input("Date of Birth / Acquisition")
                
                if st.form_submit_button("Register to Database"):
                    if a_id:
                        if any(p['ID'] == a_id for p in st.session_state['profiles']):
                            st.error("Tag ID already exists!")
                        else:
                            st.session_state['profiles'].append({
                                "ID": a_id, "Type": a_type, "Breed": a_breed, 
                                "Date_Registered": str(a_dob)
                            })
                            save_json(PROFILES_FILE, st.session_state['profiles'])
                            st.success(f"{a_id} registered successfully!")
                    else:
                        st.error("Tag ID is required.")
                        
    with tab2:
        if st.session_state['profiles']:
            del_id = st.selectbox("Select Animal to Remove:", [p['ID'] for p in st.session_state['profiles']])
            if st.button("🚨 Terminate Record"):
                st.session_state['profiles'] = [p for p in st.session_state['profiles'] if p['ID'] != del_id]
                # Also delete associated logs
                st.session_state['logs'] = [L for L in st.session_state['logs'] if L['ID'] != del_id]
                save_json(PROFILES_FILE, st.session_state['profiles'])
                save_json(LOGS_FILE, st.session_state['logs'])
                st.success("Record and all associated history terminated.")
                st.rerun()

# --- PAGE 3: LOG DAILY PROGRESS ---
elif menu == "Log Daily Progress":
    st.header("📝 Log Daily Metrics & Progress")
    
    if not st.session_state['profiles']:
        st.warning("No animals in registry to log progress for.")
    else:
        # Step 1: Select Animal
        selected_id = st.selectbox("Select Animal Tag:", [p['ID'] for p in st.session_state['profiles']])
        
        # Determine animal type to show the correct fields
        animal_type = next(p['Type'] for p in st.session_state['profiles'] if p['ID'] == selected_id)
        available_metrics = st.session_state['configs'].get(animal_type, [])
        
        st.divider()
        st.subheader(f"New Log Entry for {selected_id} ({animal_type})")
        
        with st.form("log_form", clear_on_submit=True):
            log_date = st.date_input("Log Date", datetime.today())
            metric = st.selectbox("Metric to Log", available_metrics)
            
            # Use columns for value and notes
            c1, c2 = st.columns(2)
            with c1: value = st.text_input("Measured Value (e.g., 500, 'Healthy', 15.5)")
            with c2: notes = st.text_input("Additional Notes (Optional)")
            
            if st.form_submit_button("Submit Log"):
                if value:
                    new_log = {
                        "Date": str(log_date),
                        "ID": selected_id,
                        "Metric": metric,
                        "Value": value,
                        "Notes": notes
                    }
                    st.session_state['logs'].append(new_log)
                    save_json(LOGS_FILE, st.session_state['logs'])
                    st.success("Progress log recorded successfully!")
                else:
                    st.error("Please enter a value to log.")

# --- PAGE 4: PROGRESS TRACKER (ANALYTICS) ---
elif menu == "Progress Tracker (Analytics)":
    st.header("📈 Individual Progress Analytics")
    
    if not st.session_state['logs']:
        st.info("No progress data logged yet. Add logs to see charts.")
    else:
        selected_id = st.selectbox("Select Animal to Analyze:", [p['ID'] for p in st.session_state['profiles']])
        
        # Filter logs just for this animal
        animal_logs = [L for L in st.session_state['logs'] if L['ID'] == selected_id]
        
        if not animal_logs:
            st.warning(f"No log history found for {selected_id}.")
        else:
            df_logs = pd.DataFrame(animal_logs)
            # Sort by date chronologically
            df_logs = df_logs.sort_values(by="Date")
            
            # Show Raw Data History
            st.subheader("📋 Complete Log History")
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Advanced Graphing
            st.subheader("📊 Visual Progress")
            metrics_logged = df_logs['Metric'].unique()
            selected_metric = st.selectbox("Select Metric to Visualize:", metrics_logged)
            
            graph_df = df_logs[df_logs['Metric'] == selected_metric].copy()
            
            # Try to convert values to numbers for graphing (e.g., 500kg -> 500)
            graph_df['Numeric_Value'] = pd.to_numeric(graph_df['Value'], errors='coerce')
            
            # Check if there is graphable numeric data
            if graph_df['Numeric_Value'].notna().sum() > 0:
                fig = px.line(graph_df, x='Date', y='Numeric_Value', markers=True, 
                              title=f"{selected_id}: {selected_metric} over Time")
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
                    font=dict(color="#FAFAFA"), margin=dict(t=40, b=20, l=0, r=0)
                )
                fig.update_traces(line_color='#4DA8DA', marker=dict(size=8, color='#FAFAFA'))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"The metric '{selected_metric}' does not contain numeric data (like weights or volumes) to graph.")

# --- PAGE 5: SYSTEM SETTINGS ---
elif menu == "System Settings":
    st.header("⚙️ System Architecture Settings")
    st.write("Configure the operational parameters for your facility.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Add Animal Category")
        new_cat = st.text_input("New Species/Category")
        if st.button("Initialize Category"):
            if new_cat and new_cat not in st.session_state['configs']:
                st.session_state['configs'][new_cat] = []
                save_json(CONFIG_FILE, st.session_state['configs'])
                st.success(f"Category '{new_cat}' initialized!")
                st.rerun()

    with col2:
        st.subheader("Define Trackable Metrics")
        types = list(st.session_state['configs'].keys())
        if types:
            target_cat = st.selectbox("Target Category", types)
            new_field = st.text_input(f"New Metric for {target_cat} (e.g., Weight (kg))")
            if st.button("Add Tracking Metric"):
                if new_field and new_field not in st.session_state['configs'][target_cat]:
                    st.session_state['configs'][target_cat].append(new_field)
                    save_json(CONFIG_FILE, st.session_state['configs'])
                    st.success(f"Metric added to {target_cat}!")
                    st.rerun()