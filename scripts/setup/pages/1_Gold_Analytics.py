import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
import os
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv # <--- ADD THIS

# Load the .env file explicitly
load_dotenv()

st.set_page_config(page_title="MFG Gold Analytics", layout="wide")

# --- 1. Connection Logic (Points to Gold Layer) ---
@st.cache_resource
def get_conn():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse="MFG_WH", 
        database="DW_DB", 
        schema="RPT_SCHEMA"
    )

st.title("🏭 Plant Manager: Gold Sensor Intelligence")

# --- 2. Live Dashboard Container ---
placeholder = st.empty()

while True:
    with placeholder.container():
        try:
            conn = get_conn()
            
            # QUERY 1: Pull from the Cleaned GOLD Layer
            # Note: We now use standard columns (SENSOR_ID, etc.) instead of JSON pathing
            query = """
            SELECT 
                SENSOR_ID,
                METRIC_NAME,
                METRIC_VALUE,
                LAST_UPDATED_AT as TS,
                -- Logic to match your Gold Health Status
                CASE 
                    WHEN METRIC_VALUE > 90 THEN 'CRITICAL'
                    WHEN METRIC_VALUE > 75 THEN 'WARNING'
                    ELSE 'HEALTHY'
                END as STATUS
            FROM DW_DB.RPT_SCHEMA.DW_SENSOR_MASTER
            ORDER BY TS DESC
            LIMIT 500
            """
            df = pd.read_sql(query, conn)

            if df.empty:
                st.warning("Gold Layer is empty. Ensure 'dbt run' has finished!")
            else:
                # --- 3. TOP LEVEL METRICS ---
                # Calculate Critical Alerts in the last hour
                one_hour_ago = pd.Timestamp.now() - pd.Timedelta(hours=1)
                critical_count = len(df[(df['STATUS'] == 'CRITICAL') & (df['TS'] > one_hour_ago)])
                avg_vibe = df[df['METRIC_NAME'].str.contains('Vibration', case=False)]['METRIC_VALUE'].mean()

                m1, m2, m3 = st.columns(3)
                m1.metric("🚨 Critical Alerts (Last 1hr)", f"{critical_count}", delta="-2" if critical_count < 5 else "Action Required", delta_color="inverse")
                m2.metric("📊 Avg Plant Vibration", f"{avg_vibe:.2f} Hz")
                m3.metric("📡 Active Sensors", len(df['SENSOR_ID'].unique()))

                st.divider()

                # --- 4. Filters & Layout ---
                sensor_list = df['SENSOR_ID'].unique()
                selected_sensor = st.sidebar.multiselect("Select Assets", sensor_list, default=sensor_list)
                filtered_df = df[df['SENSOR_ID'].isin(selected_sensor)]

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Asset Health Distribution")
                    fig1 = px.violin(filtered_df, x="METRIC_NAME", y="METRIC_VALUE", color="STATUS", box=True)
                    st.plotly_chart(fig1, use_container_width=True)

                with col2:
                    st.subheader("Historical Trend (Gold Layer)")
                    fig2 = px.line(filtered_df, x="TS", y="METRIC_VALUE", color="SENSOR_ID", markers=True)
                    st.plotly_chart(fig2, use_container_width=True)

                st.subheader("Cleaned Master Records")
                st.dataframe(filtered_df.head(10), use_container_width=True)

        except Exception as e:
            st.error(f"Operational Error: {e}")
        
        time.sleep(10) # Gold layer updates less frequently than Bronze, 10s is plenty
        st.rerun()
