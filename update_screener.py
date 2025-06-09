
import os
import json
import requests
import csv

api_key = os.getenv("FINNHUB_KEY") or "d13ic11r01qs7glhpq6gd13ic11r01qs7glhpq70"

def get_sp500_tickers():
    with open("sp500.csv") as f:
        return [row["Symbol"] for row in csv.DictReader(f)]

def get_profile(symbol):
    url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={api_key}"
    return requests.get(url).json()

def get_metrics(symbol):
    url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={api_key}"
    return requests.get(url).json().get("metric", {})

results = []

for symbol in get_sp500_tickers():
    profile = get_profile(symbol)
    name = profile.get("name", symbol)

    metrics = get_metrics(symbol)
    pe = metrics.get("peNormalizedAnnual")
    peg = metrics.get("pegAnnual")
    fcf_yield = metrics.get("freeCashFlowYieldAnnual")

    # Debug output (visible in GitHub Actions logs)
    print(f"{symbol}: PE={pe}, PEG={peg}, FCF={fcf_yield}")

    reason = []
    score = 0
    available = 0

    if pe is not None:
        available += 1
        if pe < 20:
            score += 1
            reason.append("✅ P/E < 20")
        else:
            reason.append("❌ P/E ≥ 20")
    else:
        reason.append("⚠️ P/E unavailable")

    if peg is not None:
        available += 1
        if peg < 1.5:
            score += 1
            reason.append("✅ PEG < 1.5")
        else:
            reason.append("❌ PEG ≥ 1.5")
    else:
        reason.append("⚠️ PEG unavailable")

    if fcf_yield is not None:
        available += 1
        if fcf_yield > 5:
            score += 1
            reason.append("✅ FCF Yield > 5%")
        else:
            reason.append("❌ FCF Yield ≤ 5%")
    else:
        reason.append("⚠️ FCF Yield unavailable")

    # Adjust verdict based on score and available metrics
    if available == 0:
        verdict = "⚠️ No data"
    elif score == available:
        verdict = "✅ Bargain"
    elif score >= 2:
        verdict = "⚠️ Watchlist"
    else:
        verdict = "❌ Overvalued"

    results.append({
        "Symbol": symbol,
        "Name": name,
        "P/E": round(pe, 2) if pe is not None else None,
        "PEG": round(peg, 2) if peg is not None else None,
        "FCF Yield (%)": round(fcf_yield, 2) if fcf_yield is not None else None,
        "Verdict": verdict,
        "VerdictReason": " | ".join(reason)
    })

with open("latest.json", "w") as f:
    json.dump(results, f, indent=2)
