import streamlit as st
import plotly.graph_objects as go
from src.dashboard.utils.db import get_companies, get_pl, get_ratios, get_sectors, get_pros_cons


def render():
    st.title("Company Profile")
    companies = get_companies()
    ticker = st.selectbox("Company", companies.company_id.tolist())
    company = companies[companies.company_id == ticker].iloc[0]
    ratios = get_ratios(ticker)
    pl = get_pl(ticker)
    sector = get_sectors(); sector = sector[sector.company_id == ticker]
    st.subheader(f"{company.company_name} ({ticker})")
    st.caption(f"{sector.broad_sector.iloc[0] if not sector.empty else 'N/A'} | {sector.sub_sector.iloc[0] if not sector.empty else 'N/A'}")
    latest = ratios[ratios.year != "TTM"].tail(1)
    if latest.empty:
        st.info("Ticker not found - please try another")
        return
    cols = st.columns(6)
    for col, label, field in zip(cols, ["ROE", "ROCE", "NPM", "D/E", "Revenue CAGR 5yr", "FCF"], ["return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct", "debt_to_equity", "revenue_cagr_5yr", "free_cash_flow_cr"]):
        value = latest.iloc[0].get(field)
        col.metric(label, "N/A" if value is None else f"{value:.2f}")
    figure = go.Figure()
    figure.add_bar(x=pl.year, y=pl.sales, name="Revenue")
    figure.add_bar(x=pl.year, y=pl.net_profit, name="Net Profit")
    st.plotly_chart(figure, use_container_width=True)
    st.dataframe(get_pros_cons(ticker), use_container_width=True)