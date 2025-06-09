
import os
import json
import requests
import csv

api_key = "d13ic11r01qs7glhpq6gd13ic11r01qs7glhpq70"

def get_sp500_tickers():
    with open("sp500.csv") as f:
        return [row["Symbol"] for row in csv.DictReader(f)]

def get_fundamentals(symbol):
    url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={api_key}"
    r = requests.get(url)
    return r.json().get("metric", {})

tickers = get_sp500_tickers()
results = []

for symbol in tickers:
    metrics = get_fundamentals(symbol)
    pe = metrics.get("peNormalizedAnnual")
    peg = metrics.get("pegAnnual")
    fcf_yield = metrics.get("freeCashFlowYieldAnnual")

    reason = []
    if pe is not None:
        reason.append("✅ P/E < 20" if pe < 20 else "❌ P/E ≥ 20")
    if peg is not None:
        reason.append("✅ PEG < 1.5" if peg < 1.5 else "❌ PEG ≥ 1.5")
    if fcf_yield is not None:
        reason.append("✅ FCF Yield > 5%" if fcf_yield > 5 else "❌ FCF Yield ≤ 5%")

    pass_count = sum(1 for r in reason if r.startswith("✅"))
    verdict = "✅ Bargain" if pass_count == 3 else "⚠️ Watchlist" if pass_count == 2 else "❌ Overvalued"

    results.append({
        "Symbol": symbol,
        "Name": symbol,
        "P/E": round(pe, 2) if pe else None,
        "PEG": round(peg, 2) if peg else None,
        "FCF Yield (%)": round(fcf_yield, 2) if fcf_yield else None,
        "Verdict": verdict,
        "VerdictReason": " | ".join(reason)
    })

with open("latest.json", "w") as f:
    json.dump(results, f, indent=2)
