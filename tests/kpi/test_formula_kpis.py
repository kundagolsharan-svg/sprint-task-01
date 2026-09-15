import pytest

from src.analytics.cagr import cagr
from src.analytics.cashflow_kpis import capital_allocation_pattern, capex_intensity, cfo_quality, fcf_conversion, free_cash_flow
from src.analytics.ratios import asset_turnover, debt_to_equity, high_leverage_flag, interest_coverage, interest_coverage_label, net_profit_margin, opm_cross_check, operating_profit_margin, return_on_assets, return_on_capital_employed, return_on_equity


def test_net_margin_normal(): assert net_profit_margin(20, 100) == 20

def test_net_margin_zero_sales(): assert net_profit_margin(20, 0) is None

def test_opm_normal(): assert operating_profit_margin(25, 100) == 25

def test_opm_mismatch(): assert opm_cross_check(25, 20)

def test_roe_normal(): assert return_on_equity(20, 50, 50) == 20

def test_roe_negative_equity(): assert return_on_equity(20, -100, 20) is None

def test_roce_normal(): assert return_on_capital_employed(30, 50, 50, 50) == 20

def test_roa_zero_assets(): assert return_on_assets(20, 0) is None

def test_debt_free_is_zero(): assert debt_to_equity(0, 100, 50) == 0

def test_debt_equity_normal(): assert debt_to_equity(50, 100, 100) == 0.25

def test_high_leverage_non_financial(): assert high_leverage_flag(6, "Energy")

def test_financial_high_leverage_suppressed(): assert not high_leverage_flag(6, "Financials")

def test_icr_zero_interest(): assert interest_coverage(20, 5, 0) is None

def test_icr_debt_free_label(): assert interest_coverage_label(None) == "Debt Free"

def test_cagr_normal(): assert cagr(100, 121, 2)[0] == pytest.approx(10)

def test_cagr_turnaround(): assert cagr(-10, 20, 2)[1] == "TURNAROUND"

def test_cagr_decline_loss(): assert cagr(10, -2, 2)[1] == "DECLINE_TO_LOSS"

def test_cagr_both_negative(): assert cagr(-10, -2, 2)[1] == "BOTH_NEGATIVE"

def test_cagr_zero_base(): assert cagr(0, 10, 2)[1] == "ZERO_BASE"

def test_cagr_insufficient():
    assert cagr(None, 10, 2)[1] == "INSUFFICIENT"
