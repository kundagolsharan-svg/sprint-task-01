import streamlit as st
import plotly.express as px
from src.dashboard.utils.db import get_ratios, get_sectors


def render():
    st.title("Nifty 100 Analytics")
    ratios = get_ratios()
    latest = ratios[ratios.year != "TTM"].sort_values("year").groupby("company_id").tail(1)
    sectors = get_sectors()
    cols = st.columns(6)
    values = [latest.return_on_equity_pct.mean(), latest.debt_to_equity.median(), latest.company_id.nunique(), latest.revenue_cagr_5yr.median(), int((latest.debt_to_equity == 0).sum()), latest.composite_quality_score.median()]
    for col, label, value in zip(cols, ["Average ROE", "Median D/E", "Total Companies", "Median Revenue CAGR", "Debt-Free Companies", "Median Composite"], values):
        col.metric(label, "N/A" if value != value else f"{value:.1f}")
    st.plotly_chart(px.pie(sectors, names="broad_sector", title="Sector Breakdown"), use_container_width=True)
    st.subheader("Top 5 Companies")
    st.dataframe(latest.nlargest(5, "composite_quality_score"), use_container_width=True)