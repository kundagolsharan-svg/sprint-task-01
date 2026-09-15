import streamlit as st
import plotly.express as px
from src.dashboard.utils.db import get_pl, get_companies


def render():
    st.title("Trend Analysis")
    ticker = st.selectbox("Company", get_companies().company_id.tolist())
    data = get_pl(ticker)
    metric = st.multiselect("Metrics", ["sales", "net_profit", "operating_profit"], default=["sales", "net_profit"])
    if metric:
        st.plotly_chart(px.line(data, x="year", y=metric, markers=True), use_container_width=True)