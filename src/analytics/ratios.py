"""Pure profitability, leverage, and efficiency KPI formulas."""


def ratio(numerator, denominator, multiplier=1.0):
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator * multiplier


def net_profit_margin(net_profit, sales):
    return ratio(net_profit, sales, 100)


def operating_profit_margin(operating_profit, sales):
    return ratio(operating_profit, sales, 100)


def opm_cross_check(computed, source, tolerance=1.0):
    if computed is None or source is None:
        return False
    return abs(computed - source) > tolerance


def return_on_equity(net_profit, equity_capital, reserves):
    equity = (equity_capital or 0) + (reserves or 0)
    return None if equity <= 0 else net_profit / equity * 100


def return_on_capital_employed(ebit, equity_capital, reserves, borrowings):
    capital = (equity_capital or 0) + (reserves or 0) + (borrowings or 0)
    return None if capital <= 0 else ebit / capital * 100


def return_on_assets(net_profit, total_assets):
    return ratio(net_profit, total_assets, 100)


def debt_to_equity(borrowings, equity_capital, reserves):
    equity = (equity_capital or 0) + (reserves or 0)
    if borrowings == 0:
        return 0.0
    return None if equity <= 0 else borrowings / equity


def high_leverage_flag(value, sector):
    return bool(value is not None and value > 5 and sector != "Financials")


def interest_coverage(operating_profit, other_income, interest):
    return ratio((operating_profit or 0) + (other_income or 0), interest)


def interest_coverage_label(value):
    return "Debt Free" if value is None else "Covered"


def interest_warning(value):
    return value is not None and value < 1.5


def net_debt(borrowings, investments):
    return (borrowings or 0) - (investments or 0)


def asset_turnover(sales, total_assets):
    return ratio(sales, total_assets)
