"""CAGR calculations with explicit financial sign transitions."""


def cagr(start, end, years):
    if years <= 0 or start is None or end is None:
        return None, "INSUFFICIENT"
    if start == 0:
        return None, "ZERO_BASE"
    if start > 0 and end > 0:
        return ((end / start) ** (1 / years) - 1) * 100, None
    if start > 0 and end <= 0:
        return None, "DECLINE_TO_LOSS"
    if start < 0 and end > 0:
        return None, "TURNAROUND"
    return None, "BOTH_NEGATIVE"


def window_cagr(values, years):
    ordered = sorted((year, value) for year, value in values if year != "TTM")
    if len(ordered) <= years:
        return None, "INSUFFICIENT"
    return cagr(ordered[-years - 1][1], ordered[-1][1], years)
