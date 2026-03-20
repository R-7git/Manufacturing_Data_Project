import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
import os
import time

st.set_page_config(page_title="MFG Sensor Analytics", layout="wide")

# --- 1. Connection Logic ---
@st.cache_resource
def get_conn():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse="COMPUTE_WH",  # Uses your active warehouse
        database="MFG_BRONZE_DB", 
        schema="KAFKA_INGEST"
    )

# --- 2. Live Dashboard Container ---
st.title("🏭 Real-Time Manufacturing Sensor Dashboard")
placeholder = st.empty()

while True:
    with placeholder.container():
        try:
            conn = get_conn()
            
            # Use the FULL PATH seen in your Snowflake Database Explorer
            query = """
            SELECT 
                RECORD_CONTENT:sensor_id::STRING as SENSOR_ID,
                RECORD_CONTENT:metric_name::STRING as METRIC_NAME,
                RECORD_CONTENT:metric_value::FLOAT as CURRENT_VALUE,
                RECORD_CONTENT:status::STRING as STATUS,
                RECORD_CONTENT:ingestion_timestamp::TIMESTAMP as TS
            FROM MFG_BRONZE_DB.KAFKA_INGEST.MFG_SENSOR_STREAM
            ORDER BY TS DESC
            LIMIT 200
            """
            df = pd.read_sql(query, conn)

            if df.empty:
                st.warning("Table is connected but empty. Start your producer script!")
            else:
                # --- 3. Filters ---
                sensor_list = df['SENSOR_ID'].unique()
                selected_sensor = st.sidebar.multiselect("Filter by Sensor", sensor_list, default=sensor_list)
                filtered_df = df[df['SENSOR_ID'].isin(selected_sensor)]

                # --- 4. Layout ---
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Metric Distribution")
                    fig1 = px.box(filtered_df, x="METRIC_NAME", y="CURRENT_VALUE", color="STATUS")
                    st.plotly_chart(fig1, use_container_width=True)

                with col2:
                    st.subheader("Vibration Trend")
                    fig2 = px.line(filtered_df, x="TS", y="CURRENT_VALUE", color="SENSOR_ID")
                    st.plotly_chart(fig2, use_container_width=True)

                st.subheader("Live Raw Records")
                st.dataframe(filtered_df.head(20), use_container_width=True)

        except Exception as e:
            st.error(f"Error: {e}")
        
        # Refresh every 5 seconds
        time.sleep(5)
        st.rerun()
