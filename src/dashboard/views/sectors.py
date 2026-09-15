import streamlit as st
import plotly.express as px
from src.dashboard.utils.db import get_sectors, get_ratios


def render():
    st.title("Sector Analysis")
    sectors = get_sectors()
    selected = st.selectbox("Sector", sorted(sectors.broad_sector.dropna().unique()))
    members = sectors[sectors.broad_sector == selected]
    ratios = get_ratios()
    latest = ratios[ratios.year != "TTM"].sort_values("year").groupby("company_id").tail(1)
    data = members.merge(latest, on="company_id", how="left")
    data["bubble_size"] = data["free_cash_flow_cr"].abs().fillna(0) + 1
    chart_data = data.dropna(subset=["revenue_cagr_5yr", "return_on_equity_pct"])
    if chart_data.empty:
        st.info("No sector companies have enough data for the selected chart.")
    else:
        st.plotly_chart(px.scatter(chart_data, x="revenue_cagr_5yr", y="return_on_equity_pct", size="bubble_size", color="sub_sector", hover_name="company_id", hover_data=["free_cash_flow_cr"]), use_container_width=True)
    st.subheader("Sector Median KPIs")
    medians = data.set_index("company_id")[["return_on_equity_pct", "return_on_capital_employed_pct"]].median().dropna()
    if medians.empty:
        st.info("No median KPI data is available for this sector.")
    else:
        st.bar_chart(medians)
    st.dataframe(data[["company_id", "sub_sector", "revenue_cagr_5yr", "return_on_equity_pct", "free_cash_flow_cr"]], use_container_width=True)