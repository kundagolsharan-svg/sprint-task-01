import streamlit as st
import plotly.graph_objects as go
from src.dashboard.utils.db import get_peers


def render():
    st.title("Peer Comparison")
    groups = ["Automobiles", "Consumer Finance", "FMCG", "IT Services", "Life Insurance", "Oil & Gas", "Pharmaceuticals", "Power & Utilities", "Private Banks", "Public Sector Banks", "Steel"]
    group = st.selectbox("Peer group", groups)
    data = get_peers(group)
    st.dataframe(data, use_container_width=True)
    if not data.empty:
        selected = st.selectbox("Company", sorted(data.company_id.unique()))
        metrics = data[data.company_id == selected]
        figure = go.Figure(go.Bar(x=metrics.metric, y=metrics.percentile_rank))
        figure.update_yaxes(range=[0, 1]); st.plotly_chart(figure, use_container_width=True)