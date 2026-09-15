import streamlit as st
from src.dashboard.utils.db import get_companies, get_documents


def render():
    st.title("Annual Reports")
    ticker = st.selectbox("Company", get_companies().company_id.tolist())
    data = get_documents(ticker)
    if data.empty:
        st.info("Report unavailable")
        return
    for _, row in data.iterrows():
        url = row.get("annual_report")
        if isinstance(url, str) and url.startswith("http"):
            st.link_button(f"Annual report {row['year']}", url)
        else:
            st.error(f"{row['year']}: Report unavailable")