import streamlit as st
from src.dashboard.utils.db import get_ratios


def render():
    st.title("Screener")
    data = get_ratios(); data = data[data.year != "TTM"].sort_values("year").groupby("company_id").tail(1)
    roe = st.sidebar.slider("ROE minimum", 0.0, 100.0, 0.0)
    de = st.sidebar.slider("D/E maximum", 0.0, 20.0, 20.0)
    fcf = st.sidebar.slider("FCF minimum", -100000.0, 100000.0, -100000.0)
    result = data[(data.return_on_equity_pct >= roe) & (data.debt_to_equity <= de) & (data.free_cash_flow_cr >= fcf)]
    st.write(f"{len(result)} companies match your filters")
    st.download_button("Download CSV", result.to_csv(index=False), "screener_results.csv", "text/csv")
    st.dataframe(result, use_container_width=True)