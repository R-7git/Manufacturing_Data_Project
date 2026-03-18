import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="MFG Sensor Analytics", layout="wide")

st.title("🏭 Real-Time Manufacturing Sensor Dashboard")

# Snowflake Connection
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

conn = get_conn()

# Query Gold Data
query = "SELECT * FROM V_SENSOR_ANALYTICS"
df = pd.read_sql(query, conn)

# Sidebar filters
sensor_list = df['SENSOR_ID'].unique()
selected_sensor = st.sidebar.multiselect("Filter by Sensor ID", sensor_list, default=sensor_list)

filtered_df = df[df['SENSOR_ID'].isin(selected_sensor)]

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Metric Distribution")
    fig1 = px.box(filtered_df, x="METRIC_NAME", y="METRIC_VALUE", color="METRIC_NAME")
    st.plotly_chart(fig1)

with col2:
    st.subheader("Sensor Health Summary")
    st.dataframe(filtered_df.describe())

st.subheader("Raw Gold Records")
st.write(filtered_df)