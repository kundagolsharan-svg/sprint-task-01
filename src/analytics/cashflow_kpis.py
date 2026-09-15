"""Cash-flow quality and capital-allocation formulas."""


def free_cash_flow(cfo, cfi):
    return (cfo or 0) + (cfi or 0)


def cfo_quality(cfo, pat):
    if cfo is None or pat in (None, 0):
        return None, None
    value = cfo / pat
    label = "High Quality" if value > 1 else "Moderate" if value >= 0.5 else "Accrual Risk"
    return value, label


def capex_intensity(investing_activity, sales):
    if sales in (None, 0):
        return None, None
    value = abs(investing_activity or 0) / sales * 100
    label = "Asset Light" if value < 3 else "Moderate" if value <= 8 else "Capital Intensive"
    return value, label


def fcf_conversion(fcf, operating_profit):
    if operating_profit in (None, 0):
        return None
    return fcf / operating_profit * 100


def _sign(value):
    return "+" if (value or 0) >= 0 else "-"


def capital_allocation_pattern(cfo, cfi, cff, cfo_pat_ratio=None):
    signs = (_sign(cfo), _sign(cfi), _sign(cff))
    labels = {
        ("+", "-", "-"): "Reinvestor",
        ("+", "+", "-"): "Liquidating Assets",
        ("-", "+", "+"): "Distress Signal",
        ("-", "-", "+"): "Growth Funded by Debt",
        ("+", "+", "+"): "Cash Accumulator",
        ("-", "-", "-"): "Pre-Revenue",
        ("+", "-", "+"): "Mixed",
    }
    if signs == ("+", "-", "-") and cfo_pat_ratio is not None and cfo_pat_ratio > 1:
        return "Shareholder Returns"
    return labels.get(signs, "Mixed")
