
import yfinance as yf
import csv
import json

def get_sp500_tickers():
    with open("sp500.csv") as f:
        return [row["Symbol"].replace(".", "-") for row in csv.DictReader(f)]

def get_metrics(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        name = info.get("shortName", ticker)
        pe = info.get("forwardPE") or info.get("trailingPE")
        peg = info.get("pegRatio")

        # Estimate FCF yield if possible
        cashflow = stock.cashflow
        if "Total Cash From Operating Activities" in cashflow.index and "Capital Expenditures" in cashflow.index:
            op_cashflow = cashflow.loc["Total Cash From Operating Activities"].values[0]
            capex = cashflow.loc["Capital Expenditures"].values[0]
            fcf = op_cashflow + capex  # capex is negative
        else:
            fcf = None

        market_cap = info.get("marketCap")
        fcf_yield = (fcf / market_cap * 100) if fcf and market_cap else None

        return {
            "Symbol": ticker,
            "Name": name,
            "P/E": round(pe, 2) if pe else None,
            "PEG": round(peg, 2) if peg else None,
            "FCF Yield (%)": round(fcf_yield, 2) if fcf_yield else None
        }
    except Exception as e:
        print(f"Error for {ticker}: {e}")
        return {
            "Symbol": ticker,
            "Name": ticker,
            "P/E": None,
            "PEG": None,
            "FCF Yield (%)": None
        }

results = []

for ticker in get_sp500_tickers():
    data = get_metrics(ticker)

    score = 0
    reasons = []

    pe = data["P/E"]
    peg = data["PEG"]
    fcf_yield = data["FCF Yield (%)"]

    if pe is not None:
        if pe < 20:
            score += 1
            reasons.append("✅ P/E < 20")
        else:
            reasons.append("❌ P/E ≥ 20")
    else:
        reasons.append("⚠️ P/E unavailable")

    if peg is not None:
        if peg < 1.5:
            score += 1
            reasons.append("✅ PEG < 1.5")
        else:
            reasons.append("❌ PEG ≥ 1.5")
    else:
        reasons.append("⚠️ PEG unavailable")

    if fcf_yield is not None:
        if fcf_yield > 5:
            score += 1
            reasons.append("✅ FCF Yield > 5%")
        else:
            reasons.append("❌ FCF Yield ≤ 5%")
    else:
        reasons.append("⚠️ FCF Yield unavailable")

    if score == 3:
        verdict = "✅ Bargain"
    elif score == 2:
        verdict = "⚠️ Watchlist"
    elif score == 0 and all(v is None for v in [pe, peg, fcf_yield]):
        verdict = "⚠️ No data"
    else:
        verdict = "❌ Overvalued"

    data["Verdict"] = verdict
    data["VerdictReason"] = " | ".join(reasons)
    results.append(data)

with open("latest.json", "w") as f:
    json.dump(results, f, indent=2)
