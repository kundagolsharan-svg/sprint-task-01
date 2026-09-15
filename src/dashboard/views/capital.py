import streamlit as st
import plotly.express as px
from src.dashboard.utils.db import get_capital_allocation


def render():
    st.title("Capital Allocation Map")
    data = get_capital_allocation()
    counts = data.groupby(["pattern_label", "company_id"], as_index=False).size()
    st.plotly_chart(px.treemap(counts, path=["pattern_label", "company_id"], values="size"), use_container_width=True)
    st.dataframe(data, use_container_width=True)