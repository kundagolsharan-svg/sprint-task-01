import pytest

from src.etl.normaliser import normalize_ticker, normalize_year


@pytest.mark.parametrize("value, expected", [(" abb ", "ABB"), ("NSE: tcs", "NSETCS"), ("M&M", "M&M"), ("itc.ns", "ITC.NS"), ("Tata Motors", "TATAMOTORS"), ("bse-500", "BSE-500"), ("reliance/", "RELIANCE"), ("  hdfc-bank ", "HDFC-BANK"), ("abc_123", "ABC123"), ("a b c", "ABC"), (None, None), ("", None), (float("nan"), None), ("&", "&"), ("abc.xyz", "ABC.XYZ"), ("nse:infy", "NSEINFY"), (" 1 ", "1"), ("-", "-"), ("a/b", "AB"), ("a+b", "AB")])
def test_normalize_ticker(value, expected):
    assert normalize_ticker(value) == expected


@pytest.mark.parametrize("value, expected", [("Dec 2012", 2012), ("Mar-13", 2013), ("2024-01-01", 2024), ("FY 49", 2049), ("TTM", "TTM"), ("FY 99", 1999), ("March 2020", 2020), ("2011", 2011), (2018, 2018), ("Q4 2023", 2023), ("Sep-24", 2024), ("Apr 2001", 2001), ("FY 50", 1950), ("FY 00", 2000), ("Year 1998", 1998), (" 2022 ", 2022), ("December 2010", 2010), ("Jan-09", 2009), ("FY 47", 2047), ("Q1 2015", 2015), (None, None)])
def test_normalize_year(value, expected):
    assert normalize_year(value) == expected