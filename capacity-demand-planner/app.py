import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import json

st.set_page_config(layout="wide", page_title="MLB IT Capacity Planner")

st.title("⚾ MLB IT Workforce Capacity & Demand Planner")
st.write("Enterprise-grade workforce capacity analytics powered by Supabase, Make.com, and Python.")

# --- SIDEBAR INPUTS ---
st.sidebar.header("1. Scenario Simulation")
multiplier = st.sidebar.slider("Simulate Demand Multiplier", min_value=0.5, max_value=2.0, value=1.0, step=0.05,
                               help="Simulate a percentage change in inbound tickets, calls, and tech bar visits.")

calendar_text = st.sidebar.text_area(
    "Quick Calendar Override Notes (Optional):",
    placeholder="e.g., Opening Day next week, prep for spike on Wednesday.",
    height=100
)

# --- THE TRIGGER BUTTON ---
if st.button("Generate Capacity Forecast", type="primary"):
    with st.spinner("Executing enterprise data warehouse pipelines..."):
        
        # --- SAFE AND SANITIZED ---
        # The sensitive webhook URL has been replaced with a placeholder.
        make_webhook_url = "YOUR_WEBHOOK_URL_HERE" 
        
        payload = {
            "multiplier": multiplier,
            "calendar_text": calendar_text
        }
        
        try:
            response = requests.post(make_webhook_url, json=payload)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                except Exception as json_err:
                    st.error(f"Failed to decode JSON from Python: {json_err}")
                    st.text(f"Raw Response: {response.text}")
                    st.stop()
                
                if isinstance(result, dict) and "python_payload" in result:
                    payload_source = result["python_payload"]
                else:
                    payload_source = result
                
                if isinstance(payload_source, str):
                    try: payload_source = json.loads(payload_source)
                    except: pass
                
                forecast_results = payload_source.get("forecast_results", [])
                weekly_summary = payload_source.get("weekly_summary", {})
                ai_summary = result.get("ai_summary", "No AI executive summary provided.")
                
                # --- DISPLAY ---
                st.info(f"🤖 **AI Executive Briefing:** {ai_summary}")
                st.write("---")
                
                if weekly_summary and weekly_summary.get("total_demand", 0) > 0:
                    st.header("📊 Weekly Capacity Totals")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1: st.metric("Total Forecasted Demand", f"{weekly_summary.get('total_demand', 0)} hrs")
                    with col2: st.metric("Total Available Capacity", f"{weekly_summary.get('total_capacity', 0)} hrs")
                    with col3:
                        gap = weekly_summary.get('net_gap', 0)
                        st.metric("Net Staffing Gap", f"{gap} hrs", delta=f"{gap} hrs", delta_color="normal" if gap >= 0 else "inverse")
                    with col4:
                        d_tot = weekly_summary.get('total_demand', 0)
                        c_tot = weekly_summary.get('total_capacity', 0)
                        util = round((d_tot / c_tot * 100), 1) if c_tot > 0 else 0
                        st.metric("Average Team Utilization", f"{util}%")
                
                st.write("---")
                
                if forecast_results:
                    st.header("📈 Daily Capacity vs. Demand Trend")
                    df = pd.DataFrame(forecast_results)
                    chart_col, gap_col = st.columns([2, 1])
                    
                    with chart_col:
                        st.subheader("Labor Hours Overview")
                        df_melted = df.melt(id_vars=['date'], value_vars=['demand_hours', 'capacity_hours'], var_name='Metric', value_name='Hours')
                        df_melted['Metric'] = df_melted['Metric'].replace({'demand_hours': 'Forecasted Demand', 'capacity_hours': 'Available Capacity'})
                        fig = px.bar(df_melted, x='date', y='Hours', color='Metric', barmode='group', color_discrete_map={'Forecasted Demand': '#EF553B', 'Available Capacity': '#636EFA'})
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with gap_col:
                        st.subheader("Daily Staffing Risk Audit")
                        risk_df = df[['date', 'gap_hours', 'utilization_percent', 'risk_level']]
                        st.table(risk_df.style.map(lambda val: 'background-color: #ffcccc;' if val == 'Critical' or (isinstance(val, (int, float)) and val < 0) else ('background-color: #ffe6cc;' if val == 'High' else ('background-color: #ccffcc;' if val == 'Low' or (isinstance(val, (int, float)) and val >= 0) else '')), subset=['gap_hours', 'risk_level']))
                    
                    st.write("---")
                    st.header("🔍 Labor Demand Drivers")
                    driver_data = [{"Date": r['date'], "Driver": driver, "Hours": hours} for r in forecast_results for driver, hours in r.get('drivers', {}).items()]
                    driver_df = pd.DataFrame(driver_data)
                    col_pie, col_stacked = st.columns([1, 1])
                    
                    with col_pie:
                        st.subheader("Total Weekly Labor Distribution")
                        fig_pie = px.pie(driver_df, values='Hours', names='Driver', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                    with col_stacked:
                        st.subheader("Daily Driver Breakdowns")
                        fig_stacked = px.bar(driver_df, x='Date', y='Hours', color='Driver', title="Daily Hourly Workload Composition", color_discrete_sequence=px.colors.qualitative.Safe)
                        st.plotly_chart(fig_stacked, use_container_width=True)
                else:
                    st.warning("⚠️ Note: Forecast results are empty. Check if Supabase contains active data for the target dates.")

            else:
                st.error(f"Make.com Webhook error: Status Code {response.status_code}")
                st.write(response.text)
        except Exception as e:
            st.error(f"Failed to communicate with Make.com pipeline: {e}")

