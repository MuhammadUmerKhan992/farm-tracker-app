import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime
from PIL import Image

# --- 1. System Config & UI Theme ---
st.set_page_config(page_title="Makhdoom Farms Enterprise", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    h1, h2, h3, h4 { color: #4DA8DA; }
    div.stButton > button:first-child { background-color: #12232E; color: #4DA8DA; border: 1px solid #4DA8DA; font-weight: bold;}
    div.stButton > button:first-child:hover { background-color: #4DA8DA; color: #12232E; }
    .metric-card { background-color: #12232E; padding: 15px; border-radius: 10px; border-left: 5px solid #4DA8DA; margin-bottom: 15px;}
    </style>
""", unsafe_allow_html=True)

# --- 2. Advanced Database Engine ---
PROFILES_FILE = 'makhdoom_profiles.json'
LOGS_FILE = 'makhdoom_logs.json'
CONFIG_FILE = 'makhdoom_configs.json'
FINANCE_FILE = 'makhdoom_finances.json'
STAFF_FILE = 'makhdoom_staff.json'
ASSETS_DIR = 'makhdoom_assets'

# Ensure asset directory exists for photos
os.makedirs(ASSETS_DIR, exist_ok=True)

def load_json(file_path, default_data):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f: return json.load(f)
        except: return default_data
    return default_data

def save_json(file_path, data):
    with open(file_path, 'w') as f: json.dump(data, f)

# Initialize states
if 'profiles' not in st.session_state: st.session_state['profiles'] = load_json(PROFILES_FILE, [])
if 'logs' not in st.session_state: st.session_state['logs'] = load_json(LOGS_FILE, [])
if 'finances' not in st.session_state: st.session_state['finances'] = load_json(FINANCE_FILE, [])
if 'staff' not in st.session_state: st.session_state['staff'] = load_json(STAFF_FILE, {"employees": [], "payroll": []})
if 'configs' not in st.session_state: st.session_state['configs'] = load_json(CONFIG_FILE, {
    "Cow": ["Weight (kg)", "Milk Yield (Liters)", "Vaccination"],
    "Sheep": ["Weight (kg)", "Wool Quality Rating"]
})

# --- 3. Main Navigation ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3105/3105151.png", width=80)
st.sidebar.title("Makhdoom Farms")
st.sidebar.markdown("*Executive Dashboard*")
st.sidebar.divider()

menu = st.sidebar.radio("Modules:", [
    "📊 Executive Overview", 
    "🐄 Animal Registry", 
    "📈 Progress & Analytics", 
    "💰 Financial Ledger",
    "👷 Staff & Payroll",
    "⚙️ System Settings"
])

# --- PAGE 1: EXECUTIVE OVERVIEW ---
if menu == "📊 Executive Overview":
    st.header("🏢 Executive Operations Center")
    
    # Financial Quick-Glance
    if st.session_state['finances']:
        df_fin = pd.DataFrame(st.session_state['finances'])
        df_fin['Amount'] = pd.to_numeric(df_fin['Amount'])
        total_in = df_fin[df_fin['Type'] == 'Income']['Amount'].sum()
        total_out = df_fin[df_fin['Type'] == 'Expense']['Amount'].sum()
        net = total_in - total_out
    else:
        total_in, total_out, net = 0, 0, 0

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f"<div class='metric-card'><h4>Total Livestock</h4><h2>{len(st.session_state['profiles'])}</h2></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='metric-card'><h4>Active Staff</h4><h2>{len(st.session_state['staff']['employees'])}</h2></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='metric-card'><h4>Gross Income</h4><h2 style='color: #4CAF50;'>Rs {total_in:,.0f}</h2></div>", unsafe_allow_html=True)
    with col4: st.markdown(f"<div class='metric-card'><h4>Net Profit</h4><h2 style='color: {'#4CAF50' if net >= 0 else '#F44336'};'>Rs {net:,.0f}</h2></div>", unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📋 Active Animal Roster (With Photos)")
    
    if not st.session_state['profiles']:
        st.info("System empty. Register animals in the 'Animal Registry'.")
    else:
        # Display as visual cards
        cols = st.columns(4)
        for idx, p in enumerate(st.session_state['profiles']):
            with cols[idx % 4]:
                st.markdown(f"**{p['ID']}** - {p['Type']}")
                if 'Photo' in p and p['Photo'] and os.path.exists(p['Photo']):
                    st.image(p['Photo'], use_container_width=True)
                else:
                    st.info("No photo available")
                st.caption(f"Breed: {p.get('Breed', 'N/A')}")
                st.markdown("---")

# --- PAGE 2: ANIMAL REGISTRY ---
elif menu == "🐄 Animal Registry":
    st.header("🐄 Livestock Profile Registry")
    
    tab1, tab2 = st.tabs(["➕ Register New Animal", "❌ Terminate Record"])
    
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
                    a_breed = st.text_input("Breed / Lineage")
                with col2:
                    a_dob = st.date_input("Date of Birth / Acquisition")
                    a_photo = st.file_uploader("Upload Animal Photo (Optional)", type=['jpg', 'jpeg', 'png'])
                
                if st.form_submit_button("Register to Database"):
                    if a_id:
                        if any(p['ID'] == a_id for p in st.session_state['profiles']):
                            st.error("Tag ID already exists!")
                        else:
                            photo_path = ""
                            if a_photo is not None:
                                photo_path = os.path.join(ASSETS_DIR, f"{a_id}_{a_photo.name}")
                                with open(photo_path, "wb") as f:
                                    f.write(a_photo.getbuffer())
                            
                            st.session_state['profiles'].append({
                                "ID": a_id, "Type": a_type, "Breed": a_breed, 
                                "Date_Registered": str(a_dob), "Photo": photo_path
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
                st.session_state['logs'] = [L for L in st.session_state['logs'] if L['ID'] != del_id]
                save_json(PROFILES_FILE, st.session_state['profiles'])
                save_json(LOGS_FILE, st.session_state['logs'])
                st.success("Record terminated.")
                st.rerun()

# --- PAGE 3: PROGRESS & ANALYTICS ---
elif menu == "📈 Progress & Analytics":
    st.header("📈 Progress Tracking & Analytics")
    
    tab1, tab2 = st.tabs(["📝 Log Daily Metrics", "📊 View Analytics"])
    
    with tab1:
        if not st.session_state['profiles']: st.warning("No animals registered.")
        else:
            selected_id = st.selectbox("Select Animal Tag:", [p['ID'] for p in st.session_state['profiles']])
            animal_type = next(p['Type'] for p in st.session_state['profiles'] if p['ID'] == selected_id)
            available_metrics = st.session_state['configs'].get(animal_type, [])
            
            with st.form("log_form", clear_on_submit=True):
                log_date = st.date_input("Date", datetime.today())
                metric = st.selectbox("Metric to Log", available_metrics)
                c1, c2 = st.columns(2)
                with c1: value = st.text_input("Measured Value (Numbers preferred for graphing)")
                with c2: notes = st.text_input("Notes")
                
                if st.form_submit_button("Submit Log") and value:
                    st.session_state['logs'].append({
                        "Date": str(log_date), "ID": selected_id, "Metric": metric, "Value": value, "Notes": notes
                    })
                    save_json(LOGS_FILE, st.session_state['logs'])
                    st.success("Log recorded!")

    with tab2:
        if not st.session_state['logs']: st.info("No data logged.")
        else:
            analyze_id = st.selectbox("Select Animal to Analyze:", [p['ID'] for p in st.session_state['profiles']], key='ana_id')
            animal_logs = [L for L in st.session_state['logs'] if L['ID'] == analyze_id]
            
            if animal_logs:
                df_logs = pd.DataFrame(animal_logs).sort_values(by="Date")
                metrics_logged = df_logs['Metric'].unique()
                selected_metric = st.selectbox("Metric to Visualize:", metrics_logged)
                
                graph_df = df_logs[df_logs['Metric'] == selected_metric].copy()
                graph_df['Numeric_Value'] = pd.to_numeric(graph_df['Value'], errors='coerce')
                
                if graph_df['Numeric_Value'].notna().sum() > 0:
                    fig = px.line(graph_df, x='Date', y='Numeric_Value', markers=True, title=f"{analyze_id} - {selected_metric}")
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#FAFAFA"))
                    fig.update_traces(line_color='#4DA8DA', marker=dict(size=8, color='#FAFAFA'))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(graph_df, use_container_width=True)
            else:
                st.warning("No logs for this animal.")

# --- PAGE 4: FINANCIAL LEDGER ---
elif menu == "💰 Financial Ledger":
    st.header("💰 Master Financial Ledger")
    
    tab1, tab2, tab3 = st.tabs(["Financial Dashboard", "Add Transaction", "Transaction History"])
    
    with tab1:
        if not st.session_state['finances']:
            st.info("No financial records yet.")
        else:
            df_fin = pd.DataFrame(st.session_state['finances'])
            df_fin['Amount'] = pd.to_numeric(df_fin['Amount'])
            
            fig = px.pie(df_fin, values='Amount', names='Category', title="Cash Flow by Category", hole=0.4)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#FAFAFA"))
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        with st.form("finance_form", clear_on_submit=True):
            f_date = st.date_input("Transaction Date")
            f_type = st.radio("Type", ["Income", "Expense"], horizontal=True)
            f_cat = st.selectbox("Category", ["Animal Sale", "Milk/Product Sale", "Feed/Medicine", "Equipment/Maintenance", "Staff Salary", "Other"])
            f_amt = st.number_input("Amount (Rs)", min_value=0.0, step=100.0)
            f_notes = st.text_input("Details / Invoice #")
            
            if st.form_submit_button("Log Transaction"):
                if f_amt > 0:
                    st.session_state['finances'].append({
                        "Date": str(f_date), "Type": f_type, "Category": f_cat, "Amount": f_amt, "Notes": f_notes
                    })
                    save_json(FINANCE_FILE, st.session_state['finances'])
                    st.success("Transaction logged to master ledger!")
                else:
                    st.error("Amount must be greater than 0.")

    with tab3:
        if st.session_state['finances']:
            df_fin = pd.DataFrame(st.session_state['finances']).sort_values(by="Date", ascending=False)
            st.dataframe(df_fin, use_container_width=True, hide_index=True)

# --- PAGE 5: STAFF & PAYROLL ---
elif menu == "👷 Staff & Payroll":
    st.header("👷 Human Resources & Payroll")
    
    tab1, tab2, tab3 = st.tabs(["Staff Directory", "Process Payroll", "Payroll History"])
    
    with tab1:
        with st.expander("➕ Register New Employee"):
            with st.form("staff_form"):
                e_name = st.text_input("Full Name")
                e_role = st.text_input("Job Role (e.g., Herder, Vet, Guard)")
                e_salary = st.number_input("Monthly Salary (Rs)", min_value=0, step=1000)
                e_join = st.date_input("Join Date")
                
                if st.form_submit_button("Register Staff"):
                    if e_name:
                        st.session_state['staff']['employees'].append({
                            "Name": e_name, "Role": e_role, "Salary": e_salary, "Joined": str(e_join)
                        })
                        save_json(STAFF_FILE, st.session_state['staff'])
                        st.success(f"{e_name} added to staff directory.")
        
        if st.session_state['staff']['employees']:
            st.subheader("Current Personnel")
            st.dataframe(pd.DataFrame(st.session_state['staff']['employees']), use_container_width=True, hide_index=True)

    with tab2:
        if not st.session_state['staff']['employees']: st.warning("Add staff members first.")
        else:
            with st.form("pay_form"):
                p_name = st.selectbox("Select Employee", [e['Name'] for e in st.session_state['staff']['employees']])
                p_date = st.date_input("Payment Date")
                p_type = st.radio("Payment Type", ["Monthly Salary", "Advance", "Bonus"], horizontal=True)
                p_amt = st.number_input("Payment Amount (Rs)", min_value=0, step=500)
                
                if st.form_submit_button("Record Payment"):
                    st.session_state['staff']['payroll'].append({
                        "Date": str(p_date), "Employee": p_name, "Type": p_type, "Amount": p_amt
                    })
                    # Automatically add this to the Financial Ledger as an expense
                    st.session_state['finances'].append({
                        "Date": str(p_date), "Type": "Expense", "Category": "Staff Salary", "Amount": p_amt, "Notes": f"{p_type} for {p_name}"
                    })
                    save_json(STAFF_FILE, st.session_state['staff'])
                    save_json(FINANCE_FILE, st.session_state['finances'])
                    st.success("Payroll processed and added to Master Financial Ledger!")

    with tab3:
        if st.session_state['staff']['payroll']:
            st.dataframe(pd.DataFrame(st.session_state['staff']['payroll']).sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)

# --- PAGE 6: SYSTEM SETTINGS ---
elif menu == "⚙️ System Settings":
    st.header("⚙️ Core Architecture")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Initialize Animal Categories")
        new_cat = st.text_input("New Species/Category")
        if st.button("Add Category") and new_cat not in st.session_state['configs']:
            st.session_state['configs'][new_cat] = []
            save_json(CONFIG_FILE, st.session_state['configs'])
            st.success("Category initialized!")
            st.rerun()

    with col2:
        st.subheader("Define Trackable Metrics")
        types = list(st.session_state['configs'].keys())
        if types:
            target_cat = st.selectbox("Target Category", types)
            new_field = st.text_input(f"New Metric for {target_cat}")
            if st.button("Add Metric") and new_field not in st.session_state['configs'][target_cat]:
                st.session_state['configs'][target_cat].append(new_field)
                save_json(CONFIG_FILE, st.session_state['configs'])
                st.success("Metric added!")
                st.rerun()
